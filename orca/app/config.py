from __future__ import annotations

import os

SHARED_SECRET = os.environ.get("ORCA_SHARED_SECRET", "sands-shared-secret")
DB_PATH = os.environ.get("ORCA_DB_PATH", "orca_state.db")
DEFAULT_CHUNK_SIZE = int(os.environ.get("ORCA_DEFAULT_CHUNK_SIZE", "100000"))
CHUNK_TIMEOUT_SECONDS = int(os.environ.get("ORCA_CHUNK_TIMEOUT", "180"))
REQUEUE_INTERVAL_SECONDS = int(os.environ.get("ORCA_REQUEUE_INTERVAL", "10"))
MAX_TIMESTAMP_DRIFT = int(os.environ.get("ORCA_TIMESTAMP_DRIFT", "300"))
DEFAULT_FMI_PATH = os.environ.get("ORCA_DEFAULT_FMI_PATH", "/data/seq.fmi")
