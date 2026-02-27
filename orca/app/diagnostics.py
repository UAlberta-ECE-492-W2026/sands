"""
Capture perfetto-compatible traces which can be viewed in perfetto.dev

Usage:

- Wrap your code with a trace_recorder.span

    async with trace_recorder.span("myspan", args={'a': 1}):
        await dothings()

- Then, when ORCA_TRACE_ENABLED is set, download the captured trace with:

    curl http://localhost:8000/diagnostics/trace >trace.json
"""

import asyncio
import time
import uuid
from typing import Any

from .config import (
    TRACE_ENABLED,
    TRACE_QUEUE_SIZE,
    TRACE_PID,
)


class _NullSpan:
    def __init__(self) -> None:
        self.args: dict[str, Any] = {}

    async def __aenter__(self) -> "_NullSpan":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False


class TraceSpan:
    def __init__(
        self,
        recorder: "TraceRecorder",
        name: str,
        tid: str,
        args: dict[str, Any] | None = None,
    ) -> None:
        self._recorder = recorder
        self.name = name
        self.tid = tid
        self.args = dict(args) if args else {}
        self._start_ns: int | None = None

    async def __aenter__(self) -> "TraceSpan":
        self._start_ns = time.perf_counter_ns()
        return self

    async def __aexit__(
        self, exc_type: Any, exc: Any, tb: Any
    ) -> bool:  # no-cover; simple instrumentation
        if self._start_ns is None:
            return False
        end_ns = time.perf_counter_ns()
        duration_ns = end_ns - self._start_ns
        if exc is not None:
            self.args.setdefault("error", str(exc))
        self._recorder._enqueue_event(
            name=self.name,
            start_ns=self._start_ns,
            duration_ns=duration_ns,
            tid=self.tid,
            args=self.args,
        )
        return False


class TraceRecorder:
    def __init__(
        self,
        enabled: bool = False,
        queue_size: int = 1024,
        pid: str = "orca",
    ) -> None:
        self.enabled = enabled
        self._queue_size = queue_size
        self._pid = pid
        self._queue: asyncio.Queue[dict[str, Any] | None] | None = None
        self._task: asyncio.Task | None = None
        self._buffer: list[dict[str, Any]] = []

    async def start(self) -> None:
        if not self.enabled or self._task:
            return
        self._queue = asyncio.Queue(maxsize=self._queue_size)
        self._task = asyncio.create_task(self._drain_loop())

    async def stop(self) -> None:
        if not self.enabled or not self._task or not self._queue:
            return
        await self._queue.put(None)
        await self._task
        self._task = None
        self._queue = None

    async def dump_trace(self, clear: bool = True) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        if self._queue:
            await self._queue.join()
        events = list(self._buffer)
        if clear:
            self._buffer.clear()
        return events

    async def _drain_loop(self) -> None:
        assert self._queue is not None
        while True:
            event = await self._queue.get()
            try:
                if event is None:
                    break
                self._buffer.append(event)
            finally:
                self._queue.task_done()

    def span(
        self,
        name: str,
        tid: str | None = None,
        args: dict[str, Any] | None = None,
    ) -> TraceSpan | _NullSpan:
        if not self.enabled:
            return _NullSpan()
        if tid is None:
            tid = f"{name}-{uuid.uuid4().hex}"
        return TraceSpan(self, name, tid, args)

    def _enqueue_event(
        self,
        name: str,
        start_ns: int,
        duration_ns: int,
        tid: str,
        args: dict[str, Any],
    ) -> None:
        if not self.enabled or not self._queue:
            return
        event = {
            "name": name,
            "ph": "X",
            "ts": start_ns // 1000,
            "dur": duration_ns // 1000,
            "pid": self._pid,
            "tid": tid,
            "args": args,
        }
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            # drop events if the queue is full to avoid backpressure
            pass


trace_recorder = TraceRecorder(
    enabled=TRACE_ENABLED, queue_size=TRACE_QUEUE_SIZE, pid=TRACE_PID
)
