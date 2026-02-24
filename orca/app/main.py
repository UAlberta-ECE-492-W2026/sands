from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from typing import Optional

from fastapi import FastAPI, Request

from .config import DB_PATH
from .db import DatabaseStore
from .diagnostics import trace_recorder
from .routes import router
from .state import (
    OrchestratorState,
    load_state_from_db,
    process_enqueue_queue,
    requeue_expired_chunks,
)


def create_app(db_path: str = DB_PATH, enable_requeue_watcher: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await app.state.db.init()
        if trace_recorder.enabled:
            await trace_recorder.start()
        await load_state_from_db(app.state.state, app.state.db)
        enqueue_worker: Optional[asyncio.Task] = asyncio.create_task(
            process_enqueue_queue(app.state.state, app.state.db)
        )
        app.state.enqueue_worker = enqueue_worker
        watcher: Optional[asyncio.Task] = None
        if enable_requeue_watcher:
            watcher = asyncio.create_task(
                requeue_expired_chunks(app.state.state, app.state.db)
            )
            app.state.chunk_watcher = watcher
        try:
            yield
        finally:
            if enqueue_worker:
                enqueue_worker.cancel()
                with suppress(asyncio.CancelledError):
                    await enqueue_worker
            if enable_requeue_watcher and watcher:
                watcher.cancel()
                with suppress(asyncio.CancelledError):
                    await watcher
            if trace_recorder.enabled:
                await trace_recorder.stop()
            await app.state.db.close()

    app = FastAPI(
        title="orca",
        description="SANDS Root Orchestrator",
        version="0.2.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def trace_requests_middleware(request: Request, call_next):
        recorder = getattr(request.app.state, "trace_recorder", None)
        if not recorder or not recorder.enabled:
            return await call_next(request)
        span = recorder.span(
            f"{request.method} {request.url.path}",
            tid="request",
            args={"method": request.method, "path": request.url.path},
        )
        async with span:
            try:
                response = await call_next(request)
            except Exception as exc:
                span.args["error"] = str(exc)
                raise
            span.args["status_code"] = response.status_code
            return response

    app.include_router(router)
    app.state.db = DatabaseStore(db_path)
    app.state.state = OrchestratorState()
    app.state.chunk_watcher = None
    app.state.enqueue_worker = None
    app.state.trace_recorder = trace_recorder if trace_recorder.enabled else None
    return app


app = create_app()
