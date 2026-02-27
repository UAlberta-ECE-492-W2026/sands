import json

from fastapi.testclient import TestClient

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
    assert isinstance(data["duration_seconds"], (int, float))
    assert data["duration_seconds"] >= 0
