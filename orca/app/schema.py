from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RegisterPayload(BaseModel):
    buoy_id: str
    preferred_chunk_size: Optional[int] = Field(None, ge=1)


class RegisterResponse(BaseModel):
    session_token: str
    chunk_size: int
    fmi_path: str
    pending_chunks: int


class WorkResponse(BaseModel):
    chunk_id: str
    job_id: str
    reads: List[str]
    fmi_path: str


class ChunkResult(BaseModel):
    query: str
    positions: List[int]


class WorkResultRequest(BaseModel):
    chunk_id: str
    job_id: str
    results: List[ChunkResult]
    status: str = Field("ok")
    error: Optional[str] = None
