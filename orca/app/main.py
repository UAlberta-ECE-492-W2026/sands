from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from .diagnostics import trace_recorder
from .routes import router
from .state import OrchestratorState


def create_app(enable_requeue_watcher: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if trace_recorder.enabled:
            await trace_recorder.start()
        try:
            yield
        finally:
            if trace_recorder.enabled:
                await trace_recorder.stop()

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
    app.state.state = OrchestratorState()
    app.state.chunk_watcher = None
    app.state.enqueue_worker = None
    app.state.trace_recorder = trace_recorder if trace_recorder.enabled else None
    return app


app = create_app()
