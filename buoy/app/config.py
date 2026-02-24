import hashlib
import hmac
import os
import time
from typing import Dict

SHARED_SECRET = os.environ.get("ORCA_SHARED_SECRET", "sands-shared-secret")
ORCA_URL = os.environ.get("ORCA_URL", "http://localhost:8000")
BUOY_ID = os.environ.get("BUOY_ID", "buoy-1")
POLL_INTERVAL = float(os.environ.get("BUOY_POLL_INTERVAL", "1.5"))
FMINDEXER_BIN = os.environ.get("FMINDEXER_BIN", "fmindexer")


def build_signature(payload: bytes) -> Dict[str, str]:
    timestamp = str(int(time.time()))
    signature = hmac.new(
        SHARED_SECRET.encode("utf-8"),
        timestamp.encode("utf-8") + payload,
        hashlib.sha256,
    ).hexdigest()
    return {"x-orca-timestamp": timestamp, "x-orca-signature": signature}
