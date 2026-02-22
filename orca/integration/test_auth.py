from __future__ import annotations

from fastapi.testclient import TestClient


def test_enforces_signature(test_client: TestClient) -> None:
    resp = test_client.post("/register-ready", json={"buoy_id": "x"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "signature required"
