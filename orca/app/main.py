from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from typing import Optional

from fastapi import FastAPI

from .config import DB_PATH
from .db import DatabaseStore
from .routes import router
from .state import (
    OrchestratorState,
    load_state_from_db,
    requeue_expired_chunks,
)


def create_app(db_path: str = DB_PATH, enable_requeue_watcher: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await app.state.db.init()
        await load_state_from_db(app.state.state, app.state.db)
        watcher: Optional[asyncio.Task] = None
        if enable_requeue_watcher:
            watcher = asyncio.create_task(
                requeue_expired_chunks(app.state.state, app.state.db)
            )
            app.state.chunk_watcher = watcher
        try:
            yield
        finally:
            if enable_requeue_watcher and watcher:
                watcher.cancel()
                with suppress(asyncio.CancelledError):
                    await watcher
            await app.state.db.close()

    app = FastAPI(
        title="orca",
        description="SANDS Root Orchestrator",
        version="0.2.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    app.state.db = DatabaseStore(db_path)
    app.state.state = OrchestratorState()
    app.state.chunk_watcher = None
    return app


app = create_app()
