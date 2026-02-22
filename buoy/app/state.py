from __future__ import annotations


class WorkerState:
    session_token: str | None = None
    chunk_size: int = 1000
    fmi_path: str = "/data/seq.fmi"
