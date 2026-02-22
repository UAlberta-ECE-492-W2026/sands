from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import List, Optional

import aiosqlite


class DatabaseStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self.conn: Optional[aiosqlite.Connection] = None
        self.lock = asyncio.Lock()

    async def init(self) -> None:
        self.conn = await aiosqlite.connect(self.path)
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.execute("PRAGMA foreign_keys=ON")
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                fmi_path TEXT NOT NULL,
                total_chunks INTEGER NOT NULL,
                completed_chunks INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                chunk_size INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL REFERENCES jobs(job_id),
                reads TEXT NOT NULL,
                fmi_path TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_to TEXT,
                result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
        )
        await self.conn.commit()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    async def persist_job(
        self, job_id: str, fmi_path: str, total_chunks: int, chunk_size: int
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with self.lock:
            assert self.conn
            await self.conn.execute(
                "INSERT INTO jobs (job_id, fmi_path, total_chunks, completed_chunks, status, chunk_size, created_at) VALUES (?, ?, ?, 0, ?, ?, ?)",
                (job_id, fmi_path, total_chunks, "pending", chunk_size, now),
            )
            await self.conn.commit()

    async def insert_chunk(
        self, chunk_id: str, job_id: str, reads: str, fmi_path: str
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with self.lock:
            assert self.conn
            await self.conn.execute(
                "INSERT INTO chunks (chunk_id, job_id, reads, fmi_path, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (chunk_id, job_id, reads, fmi_path, "pending", now, now),
            )
            await self.conn.commit()

    async def update_chunk_assignment(
        self, chunk_id: str, status: str, assigned_to: Optional[str]
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with self.lock:
            assert self.conn
            await self.conn.execute(
                "UPDATE chunks SET status = ?, assigned_to = ?, updated_at = ? WHERE chunk_id = ?",
                (status, assigned_to, now, chunk_id),
            )
            await self.conn.commit()

    async def persist_chunk_result(
        self, chunk_id: str, results: List[dict], status: str
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with self.lock:
            assert self.conn
            await self.conn.execute(
                "UPDATE chunks SET status = ?, result = ?, updated_at = ? WHERE chunk_id = ?",
                (status, json.dumps(results), now, chunk_id),
            )
            await self.conn.commit()

    async def mark_chunk_complete(self, job_id: str) -> None:
        async with self.lock:
            assert self.conn
            await self.conn.execute(
                "UPDATE jobs SET completed_chunks = completed_chunks + 1 WHERE job_id = ?",
                (job_id,),
            )
            cursor = await self.conn.execute(
                "SELECT total_chunks, completed_chunks FROM jobs WHERE job_id = ?",
                (job_id,),
            )
            row = await cursor.fetchone()
            if row:
                total_chunks, completed_chunks = row
                status = (
                    "complete" if completed_chunks >= total_chunks else "in-progress"
                )
                await self.conn.execute(
                    "UPDATE jobs SET status = ? WHERE job_id = ?",
                    (status, job_id),
                )
            await self.conn.commit()

    async def fetch_reads_for_chunk(self, chunk_id: str) -> list[str]:
        async with self.lock:
            assert self.conn
            cursor = await self.conn.execute(
                "SELECT reads FROM chunks WHERE chunk_id = ?",
                (chunk_id,),
            )
            row = await cursor.fetchone()
        if not row:
            raise ValueError("chunk not found")
        target = row[0]
        if not target:
            return []
        return target.split("\n")
