"""Bindings to the Orca API."""

import json
import logging
from typing import Any, Dict, List

import httpx

from .config import BUOY_ID, ORCA_URL, build_signature
from .state import WorkerState


async def register_with_orca(
    http_client: httpx.AsyncClient, worker_state: WorkerState
) -> None:
    payload = {
        "buoy_id": BUOY_ID,
        "preferred_chunk_size": worker_state.chunk_size,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature(body)
    resp = await http_client.post(
        f"{ORCA_URL}/register-ready", content=body, headers=headers, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    worker_state.session_token = data["session_token"]
    worker_state.chunk_size = data["chunk_size"]
    worker_state.fmi_path = data["fmi_path"]
    logging.info(
        "registered with orca chunk_size=%s session=%s",
        data["chunk_size"],
        data["session_token"],
    )


async def fetch_chunk(
    http_client: httpx.AsyncClient, worker_state: WorkerState
) -> Dict[str, Any] | None:
    token = worker_state.session_token
    if not token:
        return None
    headers = build_signature(b"")
    resp = await http_client.get(
        f"{ORCA_URL}/work/{token}", headers=headers, timeout=60
    )
    if resp.status_code == 204:
        return None
    if resp.status_code == 401:
        logging.warning("session rejected, re-registering")
        worker_state.session_token = None
        return None
    resp.raise_for_status()
    return resp.json()


async def submit_results(
    http_client: httpx.AsyncClient,
    chunk_id: str,
    job_id: str,
    results: List[Dict[str, Any]],
) -> None:
    payload = {
        "chunk_id": chunk_id,
        "job_id": job_id,
        "results": results,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature(body)
    resp = await http_client.post(
        f"{ORCA_URL}/work/result", content=body, headers=headers, timeout=30
    )
    resp.raise_for_status()
