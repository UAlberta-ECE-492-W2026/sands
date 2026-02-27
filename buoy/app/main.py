import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import Any

import httpx
from fastapi import FastAPI

from . import config
from .fmindexer import run_fmindexer_search
from .orca import (
    fetch_chunk as _fetch_chunk,
    register_with_orca as _register_with_orca,
    submit_results as _submit_results,
)
from .state import WorkerState


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.worker_task = asyncio.create_task(worker_loop())
    try:
        yield
    finally:
        if app.state.worker_task:
            app.state.worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await app.state.worker_task
        await app.state.http_client.aclose()


app = FastAPI(
    title="buoy",
    description="SANDS Working Node",
    version="0.2.0",
    lifespan=lifespan,
)
app.state.worker_state = WorkerState()
app.state.http_client = httpx.AsyncClient()


async def register_with_orca() -> None:
    await _register_with_orca(app.state.http_client, app.state.worker_state)


async def fetch_chunk() -> dict[str, Any] | None:
    return await _fetch_chunk(app.state.http_client, app.state.worker_state)


async def submit_results(
    chunk_id: str, job_id: str, results: list[dict[str, Any]]
) -> None:
    await _submit_results(app.state.http_client, chunk_id, job_id, results)


POLL_INTERVAL = config.POLL_INTERVAL
build_signature = config.build_signature
SHARED_SECRET = config.SHARED_SECRET


ResultPayload = tuple[str, str, list[dict[str, Any]]]


async def _input_fetcher(input_queue: asyncio.Queue[dict[str, Any]]) -> None:
    while True:
        if not app.state.worker_state.session_token:
            try:
                await register_with_orca()
            except Exception as exc:
                logging.error("register error: %s", exc)
                await asyncio.sleep(POLL_INTERVAL)
                continue

        try:
            chunk = await fetch_chunk()
        except Exception as exc:
            logging.error("fetch chunk error: %s", exc)
            await asyncio.sleep(POLL_INTERVAL)
            continue

        if not chunk:
            await asyncio.sleep(POLL_INTERVAL)
            continue

        chunk_id = chunk["chunk_id"]
        job_id = chunk["job_id"]
        logging.info("queued chunk %s job=%s", chunk_id, job_id)

        try:
            await input_queue.put(chunk)
        except asyncio.CancelledError:
            raise


async def _processing_worker(
    input_queue: asyncio.Queue[dict[str, Any]],
    results_queue: asyncio.Queue[ResultPayload],
) -> None:
    while True:
        chunk = await input_queue.get()
        chunk_id = chunk["chunk_id"]
        job_id = chunk["job_id"]

        logging.info("processing chunk %s job=%s", chunk_id, job_id)
        try:
            results = await run_fmindexer_search(
                chunk["fmi_path"], chunk.get("reads", [])
            )
        except Exception as exc:
            logging.error("fmindexer error chunk %s job=%s: %s", chunk_id, job_id, exc)
            continue

        try:
            await results_queue.put((chunk_id, job_id, results))
        except asyncio.CancelledError:
            raise


async def _submit_worker(results_queue: asyncio.Queue[ResultPayload]) -> None:
    while True:
        chunk_id, job_id, results = await results_queue.get()
        try:
            await submit_results(chunk_id, job_id, results)
        except Exception as exc:
            logging.error("submit error chunk %s job=%s: %s", chunk_id, job_id, exc)


async def worker_loop() -> None:
    input_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=3)
    results_queue: asyncio.Queue[ResultPayload] = asyncio.Queue(maxsize=3)

    fetch_task = asyncio.create_task(_input_fetcher(input_queue))
    process_task = asyncio.create_task(_processing_worker(input_queue, results_queue))
    submit_task = asyncio.create_task(_submit_worker(results_queue))
    tasks = (fetch_task, process_task, submit_task)

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "detail": "buoy is ready"}
