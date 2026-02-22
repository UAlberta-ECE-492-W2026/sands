from __future__ import annotations

import hashlib
import hmac
import time

from fastapi import HTTPException, status

from .config import MAX_TIMESTAMP_DRIFT, SHARED_SECRET


def sign_payload(timestamp: str, payload: bytes) -> str:
    return hmac.new(
        SHARED_SECRET.encode("utf-8"),
        timestamp.encode("utf-8") + payload,
        hashlib.sha256,
    ).hexdigest()


def verify_signature(headers: dict[str, str], payload: bytes) -> None:
    timestamp = headers.get("x-orca-timestamp")
    signature = headers.get("x-orca-signature")
    if not timestamp or not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="signature required"
        )
    try:
        ts = int(timestamp)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid timestamp"
        )
    now = int(time.time())
    if abs(now - ts) > MAX_TIMESTAMP_DRIFT:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="timestamp outside window"
        )
    expected = sign_payload(timestamp, payload)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature"
        )
