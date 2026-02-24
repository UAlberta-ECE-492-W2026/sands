import time
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from orca.app import config
from orca.app.auth import sign_payload
from orca.app.main import create_app


def _signed_headers(payload: bytes) -> dict[str, str]:
    timestamp = str(int(time.time()))
    return {
        "x-orca-timestamp": timestamp,
        "x-orca-signature": sign_payload(timestamp, payload),
    }


def _send(
    client: TestClient,
    method: str,
    url: str,
    body: bytes = b"",
    params: dict | None = None,
):
    return client.request(
        method,
        url,
        headers=_signed_headers(body),
        content=body,
        params=params,
    )


@pytest.fixture
def test_client() -> Iterator[TestClient]:
    config.SHARED_SECRET = "test-secret"
    app = create_app(enable_requeue_watcher=False)
    with TestClient(app) as client:
        yield client


__all__ = ["test_client", "_send"]
