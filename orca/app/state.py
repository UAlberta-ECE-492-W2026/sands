from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

from .config import CHUNK_TIMEOUT_SECONDS, DEFAULT_FMI_PATH, REQUEUE_INTERVAL_SECONDS
from .db import DatabaseStore
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


class OrchestratorState:
    def __init__(self) -> None:
        self.pending_chunks: Deque[str] = deque()
        self.chunk_store: Dict[str, ChunkInfo] = {}
        self.jobs: Dict[str, JobInfo] = {}
        self.sessions: Dict[str, dict] = {}
        self.lock = asyncio.Lock()


async def load_state_from_db(state: OrchestratorState, db: DatabaseStore) -> None:
    async with trace_recorder.span("load_state_from_db"):
        assert db.conn
        async with db.lock:
            cursor = await db.conn.execute(
                "SELECT job_id, fmi_path, total_chunks, completed_chunks, status FROM jobs"
            )
            jobs = await cursor.fetchall()
            for job_id, fmi_path, total_chunks, completed_chunks, status in jobs:
                state.jobs[job_id] = JobInfo(
                    job_id=job_id,
                    fmi_path=fmi_path,
                    total_chunks=total_chunks,
                    completed_chunks=completed_chunks,
                    status=status,
                )
        cursor = await db.conn.execute(
            "SELECT chunk_id, job_id, status, assigned_to, fmi_path FROM chunks WHERE status IN ('pending','in_flight')"
        )
        chunks = await cursor.fetchall()
        for chunk_id, job_id, status, assigned_to, fmi_path in chunks:
            info = ChunkInfo(
                job_id=job_id,
                status=status,
                assigned_to=assigned_to,
                fmi_path=fmi_path,
            )
            if status == "in_flight":
                info.status = "pending"
                info.assigned_to = None
                info.assigned_at = None
            state.chunk_store[chunk_id] = info
            state.pending_chunks.append(chunk_id)
            job = state.jobs.get(job_id)
            if job and chunk_id not in job.chunk_ids:
                job.chunk_ids.append(chunk_id)


async def enqueue_chunks(
    state: OrchestratorState,
    db: DatabaseStore,
    job_id: str,
    fmi_path: str,
    reads: list[str],
) -> None:
    async with trace_recorder.span(
        "enqueue_chunks",
        args={"job_id": job_id, "chunk_payload": str(len(reads))},
    ):
        async with state.lock:
            job = state.jobs.setdefault(
                job_id,
                JobInfo(job_id=job_id, fmi_path=fmi_path, total_chunks=0, chunk_ids=[]),
            )
            job.total_chunks += 1
            chunk_id = str(uuid.uuid4())
            job.chunk_ids.append(chunk_id)
            state.chunk_store[chunk_id] = ChunkInfo(job_id=job_id, fmi_path=fmi_path)
            state.pending_chunks.append(chunk_id)
        reads_blob = "\n".join(reads)
        await db.insert_chunk(chunk_id, job_id, reads_blob, fmi_path)


async def get_next_chunk_for_session(
    state: OrchestratorState, db: DatabaseStore, session_token: str
) -> Optional[dict]:
    async with trace_recorder.span(
        "get_next_chunk_for_session",
        args={"session": session_token},
    ):
        chunk_payload: Optional[dict] = None
        async with state.lock:
            while state.pending_chunks:
                chunk_id = state.pending_chunks.popleft()
                info = state.chunk_store.get(chunk_id)
                if not info or info.status != "pending":
                    continue
                info.status = "in_flight"
                info.assigned_to = session_token
                info.assigned_at = time.time()
                chunk_payload = {
                    "chunk_id": chunk_id,
                    "job_id": info.job_id,
                    "fmi_path": info.fmi_path,
                }
                break
        if not chunk_payload:
            return None
        await db.update_chunk_assignment(
            chunk_payload["chunk_id"], "in_flight", session_token
        )
        return chunk_payload


async def requeue_expired_chunks_once(
    state: OrchestratorState, db: DatabaseStore
) -> None:
    async with trace_recorder.span("requeue_expired_chunks_once"):
        expired: List[str] = []
        async with state.lock:
            now = time.time()
            for chunk_id, info in list(state.chunk_store.items()):
                if info.status == "in_flight" and info.assigned_at:
                    if now - info.assigned_at > CHUNK_TIMEOUT_SECONDS:
                        info.status = "pending"
                        info.assigned_to = None
                        info.assigned_at = None
                        expired.append(chunk_id)
                        state.pending_chunks.append(chunk_id)
        if expired:
            now_iso = datetime.now(timezone.utc).isoformat()
            async with db.lock:
                assert db.conn
                for chunk_id in expired:
                    await db.conn.execute(
                        "UPDATE chunks SET status = ?, assigned_to = NULL, updated_at = ? WHERE chunk_id = ?",
                        ("pending", now_iso, chunk_id),
                    )
                await db.conn.commit()


async def requeue_expired_chunks(state: OrchestratorState, db: DatabaseStore) -> None:
    while True:
        await requeue_expired_chunks_once(state, db)
        await asyncio.sleep(REQUEUE_INTERVAL_SECONDS)
