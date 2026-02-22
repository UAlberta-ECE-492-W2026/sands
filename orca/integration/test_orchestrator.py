from __future__ import annotations

import asyncio
import json
import time

from fastapi.testclient import TestClient

from orca.app import config
from orca.app.state import requeue_expired_chunks_once

from orca.integration.conftest import _send


def test_register_ready_and_workflow(test_client: TestClient) -> None:
    reads = ["AAAA", "TTTT", "CCCC"]
    resp = _send(
        test_client,
        "POST",
        "/shortreads",
        body="\n".join(reads).encode(),
        params={"fmi_path": "/tmp/index"},
    )
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    register = {"buoy_id": "buoy"}
    resp = _send(
        test_client,
        "POST",
        "/register-ready",
        body=json.dumps(register).encode(),
    )
    assert resp.status_code == 200
    session = resp.json()["session_token"]

    work_resp = _send(test_client, "GET", f"/work/{session}")
    assert work_resp.status_code == 200
    assignment = work_resp.json()
    assert assignment["job_id"] == job_id

    result_payload = {
        "chunk_id": assignment["chunk_id"],
        "job_id": job_id,
        "status": "ok",
        "results": [{"query": "AAAA", "positions": [1, 2]}],
    }
    resp = _send(
        test_client,
        "POST",
        "/work/result",
        body=json.dumps(result_payload).encode(),
    )
    assert resp.status_code == 200

    job_info = test_client.get(f"/jobs/{job_id}")
    data = job_info.json()
    assert data["completed_chunks"] == data["total_chunks"] == 1


def test_requeues_expired_chunks(test_client: TestClient) -> None:
    config.SHARED_SECRET = "test-secret"
    resp = _send(
        test_client,
        "POST",
        "/shortreads",
        body="A".encode(),
        params={"fmi_path": "/tmp/index"},
    )
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    register = {"buoy_id": "buoy"}
    resp = _send(
        test_client,
        "POST",
        "/register-ready",
        body=json.dumps(register).encode(),
    )
    session = resp.json()["session_token"]

    work_resp = _send(test_client, "GET", f"/work/{session}")
    chunk_id = work_resp.json()["chunk_id"]

    state = test_client.app.state.state  # type: ignore[attr-defined]
    info = state.chunk_store[chunk_id]
    info.assigned_at = time.time() - config.CHUNK_TIMEOUT_SECONDS - 1
    assert info.status == "in_flight"
    assert info.assigned_to == session

    asyncio.run(
        requeue_expired_chunks_once(state, test_client.app.state.db)  # type: ignore[attr-defined]
    )

    assert state.chunk_store[chunk_id].status == "pending"
    assert state.chunk_store[chunk_id].assigned_to is None
    assert state.chunk_store[chunk_id].assigned_at is None
    assert chunk_id in state.pending_chunks

    work_resp = _send(test_client, "GET", f"/work/{session}")
    assert work_resp.status_code == 200
    assert work_resp.json()["chunk_id"] == chunk_id
    assert state.chunk_store[chunk_id].status == "in_flight"
    assert state.chunk_store[chunk_id].assigned_to == session
