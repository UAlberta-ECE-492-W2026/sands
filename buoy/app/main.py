from __future__ import annotations

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


async def worker_loop() -> None:
    while True:
        try:
            if not app.state.worker_state.session_token:
                await register_with_orca()
            chunk = await fetch_chunk()
            if not chunk:
                await asyncio.sleep(POLL_INTERVAL)
                continue
            logging.info(
                "processing chunk %s job=%s", chunk["chunk_id"], chunk["job_id"]
            )
            results = await run_fmindexer_search(
                chunk["fmi_path"], chunk.get("reads", [])
            )
            await submit_results(
                chunk["chunk_id"],
                chunk["job_id"],
                results,
            )
        except Exception as exc:
            logging.error("worker loop error: %s", exc)
            await asyncio.sleep(POLL_INTERVAL)


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "detail": "buoy is ready"}
