from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from buoy.app.main import (
    SHARED_SECRET,
    app,
    build_signature,
    fetch_chunk,
    register_with_orca,
    run_fmindexer_search,
)


class DummyProcess:
    def __init__(
        self, *, returncode: int = 0, stdout: bytes = b"", stderr: bytes = b""
    ) -> None:
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    async def communicate(self) -> tuple[bytes, bytes]:
        return self._stdout, self._stderr


class DummyTempFile:
    def __init__(self, path: Path, mode: str = "w+", **_: Any) -> None:
        self.name = str(path)
        self._file = open(self.name, mode)

    def write(self, value: str) -> int:
        return self._file.write(value)

    def flush(self) -> None:
        self._file.flush()

    def __enter__(self) -> "DummyTempFile":
        return self

    def __exit__(self, *_: Any) -> None:
        self._file.close()


class TemporaryFileFactory:
    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path
        self._counter = 0

    def __call__(self, *args: Any, **kwargs: Any) -> DummyTempFile:
        path = self._base_path / f"queries-{self._counter}.txt"
        self._counter += 1
        return DummyTempFile(path, **kwargs)


def _make_response(status_code: int, payload: Any | None = None) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.raise_for_status = Mock()
    response.json = Mock(return_value=payload)
    return response


def test_build_signature_matches_manual_hmac(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = b"short"
    timestamp = 1_700_000_000
    monkeypatch.setattr("buoy.app.config.time.time", lambda: timestamp)

    headers = build_signature(payload)

    expected_signature = hmac.new(
        SHARED_SECRET.encode("utf-8"),
        str(timestamp).encode("utf-8") + payload,
        hashlib.sha256,
    ).hexdigest()

    assert headers["x-orca-timestamp"] == str(timestamp)
    assert headers["x-orca-signature"] == expected_signature


@pytest.mark.asyncio
async def test_register_with_orca_updates_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "session_token": "sess-123",
        "chunk_size": 123,
        "fmi_path": "/data/index.fmi",
    }

    async def fake_post(*_: Any, **__: Any) -> Mock:
        return _make_response(200, payload)

    app.state.worker_state.session_token = None
    app.state.worker_state.chunk_size = 500
    monkeypatch.setattr(app.state.http_client, "post", fake_post)

    await register_with_orca()

    assert app.state.worker_state.session_token == payload["session_token"]
    assert app.state.worker_state.chunk_size == payload["chunk_size"]
    assert app.state.worker_state.fmi_path == payload["fmi_path"]


@pytest.mark.asyncio
async def test_fetch_chunk_returns_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    chunk_payload = {"chunk_id": "chunk-1", "job_id": "job-1"}

    async def fake_get(*_: Any, **__: Any) -> Mock:
        return _make_response(200, chunk_payload)

    app.state.worker_state.session_token = "session-token"
    monkeypatch.setattr(app.state.http_client, "get", fake_get)

    assert await fetch_chunk() == chunk_payload
    assert app.state.worker_state.session_token == "session-token"


@pytest.mark.asyncio
async def test_fetch_chunk_handles_idle_and_reauth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def idle_get(*_: Any, **__: Any) -> Mock:
        response = _make_response(204, None)
        response.json = Mock(side_effect=AssertionError("json not expected"))
        return response

    async def unauthorized_get(*_: Any, **__: Any) -> Mock:
        response = _make_response(401, None)
        response.json = Mock(side_effect=AssertionError("json not expected"))
        return response

    app.state.worker_state.session_token = "session-token"
    monkeypatch.setattr(app.state.http_client, "get", idle_get)
    assert await fetch_chunk() is None
    assert app.state.worker_state.session_token == "session-token"

    monkeypatch.setattr(app.state.http_client, "get", unauthorized_get)
    assert await fetch_chunk() is None
    assert app.state.worker_state.session_token is None


@pytest.mark.asyncio
async def test_run_fmindexer_search_parses_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    factory = TemporaryFileFactory(tmp_path)
    monkeypatch.setattr("buoy.app.fmindexer.tempfile.NamedTemporaryFile", factory)

    stdout = b"{" + b'"query":"read","positions":[1,2]}' + b"\n"
    process = DummyProcess(returncode=0, stdout=stdout, stderr=b"")

    async def fake_exec(*_: Any, **__: Any) -> DummyProcess:
        return process

    monkeypatch.setattr(
        "buoy.app.fmindexer.asyncio.create_subprocess_exec",
        fake_exec,
    )

    results = await run_fmindexer_search("/data/index.fmi", ["ATCG"])

    assert results == [{"query": "read", "positions": [1, 2]}]


@pytest.mark.asyncio
async def test_run_fmindexer_search_raises_on_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    factory = TemporaryFileFactory(tmp_path)
    monkeypatch.setattr("buoy.app.fmindexer.tempfile.NamedTemporaryFile", factory)

    process = DummyProcess(returncode=1, stdout=b"", stderr=b"index failure")

    async def fake_exec(*_: Any, **__: Any) -> DummyProcess:
        return process

    monkeypatch.setattr(
        "buoy.app.fmindexer.asyncio.create_subprocess_exec",
        fake_exec,
    )

    with pytest.raises(RuntimeError) as excinfo:
        await run_fmindexer_search("/data/index.fmi", ["ATCG"])

    assert "index failure" in str(excinfo.value)


@pytest.mark.asyncio
async def test_run_fmindexer_search_handles_missing_binary(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    factory = TemporaryFileFactory(tmp_path)
    monkeypatch.setattr("buoy.app.fmindexer.tempfile.NamedTemporaryFile", factory)

    async def fake_exec(*_: Any, **__: Any) -> DummyProcess:
        raise FileNotFoundError("fmindexer missing")

    monkeypatch.setattr(
        "buoy.app.fmindexer.asyncio.create_subprocess_exec",
        fake_exec,
    )

    with pytest.raises(FileNotFoundError):
        await run_fmindexer_search("/data/index.fmi", ["ATCG"])
