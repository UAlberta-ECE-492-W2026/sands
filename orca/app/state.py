import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import DEFAULT_FMI_PATH
from .diagnostics import trace_recorder


@dataclass
class ChunkInfo:
    job_id: str
    status: str = "pending"
    assigned_to: Optional[str] = None
    assigned_at: Optional[float] = None
    fmi_path: str = DEFAULT_FMI_PATH


@dataclass
class JobInfo:
    job_id: str
    fmi_path: str
    total_chunks: int
    completed_chunks: int = 0
    status: str = "pending"
    chunk_ids: List[str] = field(default_factory=list)


@dataclass
class PendingChunk:
    job_id: str
    fmi_path: str
    reads: List[str]


class OrchestratorState:
    def __init__(self) -> None:
        self.pending_chunks: asyncio.Queue[PendingChunk] = asyncio.Queue(maxsize=50)
        self.results = asyncio.Queue(maxsize=50)

        self.lock = asyncio.Lock()  # Lock for the following dicts
        self.chunk_store: Dict[str, ChunkInfo] = {}
        self.jobs: Dict[str, JobInfo] = {}
        self.sessions: Dict[str, dict] = {}


async def enqueue_chunks(
    state: OrchestratorState,
    job_id: str,
    fmi_path: str,
    reads: list[str],
) -> None:
    async with trace_recorder.span(
        "enqueue_chunks",
        args={"job_id": job_id},
    ):
        pending = PendingChunk(job_id=job_id, fmi_path=fmi_path, reads=reads)
        await state.pending_chunks.put(pending)


async def get_next_chunk_for_session(
    state: OrchestratorState, session_token: str
) -> Optional[dict]:
    async with trace_recorder.span(
        "get_next_chunk_for_session",
        args={"session": session_token},
    ):
        next_chunk = await state.pending_chunks.get()
        chunk_id = str(uuid.uuid4())
        chunk_payload = {
            "chunk_id": chunk_id,
            "job_id": next_chunk.job_id,
            "fmi_path": next_chunk.fmi_path,
            "reads": next_chunk.reads
        }

        async with state.lock:
            state.chunk_store[chunk_id] = ChunkInfo(job_id=next_chunk.job_id, status="in_flight")

        return chunk_payload
