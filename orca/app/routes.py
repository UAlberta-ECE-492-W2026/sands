import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse

from .auth import verify_signature
from .config import DEFAULT_CHUNK_SIZE, DEFAULT_FMI_PATH
from .schema import (
    RegisterPayload,
    RegisterResponse,
    WorkResponse,
    WorkResultRequest,
)
from .state import (
    JobInfo,
    OrchestratorState,
    enqueue_chunks,
    get_next_chunk_for_session,
)
from .diagnostics import trace_recorder

router = APIRouter()


def _get_state(request: Request) -> OrchestratorState:
    return request.app.state.state


@router.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for checking the health. Your welcome :)"""
    return {"status": "ok", "detail": "orca is ready"}


@router.get("/diagnostics/trace", tags=["meta"])
async def diagnostics_trace(request: Request) -> JSONResponse:
    """For debugging, only available when ORCA_TRACE_ENABLED is set"""
    recorder = getattr(request.app.state, "trace_recorder", None)
    if not recorder or not recorder.enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tracing disabled"
        )
    events = await recorder.dump_trace()
    return JSONResponse(content={"traceEvents": events})


@router.post("/shortreads")
async def shortreads(
    request: Request,
    fmi_path: str = Query(
        ..., description="Path to the .fmi index to use for this job"
    ),
    chunk_size: Optional[int] = Query(
        None, description="Maximum chunk size (default 100000 reads)"
    ),
):
    """Called by port to upload a list of shortreads to align"""
    payload = await request.body()
    verify_signature(dict(request.headers), payload)

    payload_text = payload.decode("utf-8", errors="ignore")
    reads = [line for line in payload_text.splitlines() if line.strip()]
    if not reads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="no reads provided"
        )

    effective_chunk_size = max(1, chunk_size or DEFAULT_CHUNK_SIZE)
    num_chunks = (len(reads) + effective_chunk_size - 1) // effective_chunk_size
    job_identifier = str(uuid.uuid4())

    state = _get_state(request)
    async with state.lock:
        if job_identifier in state.jobs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="job already exists"
            )
        state.jobs[job_identifier] = JobInfo(
            job_id=job_identifier, fmi_path=fmi_path, total_chunks=num_chunks
        )

    for i in range(0, len(reads), effective_chunk_size):
        chunk = reads[i:i + effective_chunk_size]
        await enqueue_chunks(state, job_identifier, fmi_path, chunk)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "job_id": job_identifier,
            "chunks": num_chunks,
        },
    )


@router.post("/register-ready", response_model=RegisterResponse)
async def register_ready(request: Request) -> RegisterResponse:
    payload = await request.body()
    verify_signature(dict(request.headers), payload)
    data = RegisterPayload.model_validate_json(payload.decode())
    effective_chunk_size = (
        min(data.preferred_chunk_size, DEFAULT_CHUNK_SIZE)
        if data.preferred_chunk_size
        else DEFAULT_CHUNK_SIZE
    )
    session_token = str(uuid.uuid4())
    state = _get_state(request)
    async with state.lock:
        state.sessions[session_token] = {
            "buoy_id": data.buoy_id,
            "chunk_size": effective_chunk_size,
            "fmi_path": DEFAULT_FMI_PATH,
            "last_seen": time.time(),
        }
    return RegisterResponse(
        session_token=session_token,
        chunk_size=effective_chunk_size,
        fmi_path=DEFAULT_FMI_PATH,
    )


@router.get("/work/{session_token}", response_model=WorkResponse)
async def get_work(session_token: str, request: Request) -> Response | WorkResponse:
    verify_signature(dict(request.headers), b"")
    state = _get_state(request)
    session = state.sessions.get(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unknown session"
        )

    chunk_payload = await get_next_chunk_for_session(
        state, session_token
    )
    if not chunk_payload:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return WorkResponse(
        chunk_id=chunk_payload["chunk_id"],
        job_id=chunk_payload["job_id"],
        reads=chunk_payload["reads"],
        fmi_path=chunk_payload["fmi_path"],
    )


@router.post("/work/result")
async def work_result(request: Request) -> dict[str, str]:
    payload = await request.body()
    verify_signature(dict(request.headers), payload)
    data = WorkResultRequest.model_validate_json(payload.decode())

    span = trace_recorder.span(
        "routes.work_result",
        args={"chunk_id": data.chunk_id, "job_id": data.job_id},
    )
    async with span:
        state = _get_state(request)
        async with state.lock:
            chunk = state.chunk_store.get(data.chunk_id)
            if not chunk:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="unknown chunk"
                )
            if chunk.job_id != data.job_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="job mismatch"
                )
            if chunk.status != "in_flight":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="chunk not assigned"
                )

            # No error handling atm
            assert data.status == "ok"

            chunk.status = "completed"
            chunk.assigned_to = None
            chunk.assigned_at = None

            job = state.jobs.get(data.job_id)
            assert job
            job.completed_chunks += 1
            if job.completed_chunks >= job.total_chunks:
                job.status = "complete"

    return {"status": "ok", "chunk_id": data.chunk_id}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, request: Request) -> dict[str, Optional[str | int]]:
    job_info = _get_state(request).jobs.get(job_id)
    if not job_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="job not found"
        )
    return {
        "job_id": job_info.job_id,
        "fmi_path": job_info.fmi_path,
        "total_chunks": job_info.total_chunks,
        "completed_chunks": job_info.completed_chunks,
        "status": job_info.status,
    }
