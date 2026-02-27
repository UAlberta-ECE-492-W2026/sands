import os


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """Parse a boolean from an environment variable.

    Truthy values are '1', 'true', 'yes' and 'on'
    """
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


SHARED_SECRET = os.environ.get("ORCA_SHARED_SECRET", "sands-shared-secret")
DEFAULT_CHUNK_SIZE = int(os.environ.get("ORCA_DEFAULT_CHUNK_SIZE", "100000"))
MAX_TIMESTAMP_DRIFT = int(os.environ.get("ORCA_TIMESTAMP_DRIFT", "300"))
DEFAULT_FMI_PATH = os.environ.get("ORCA_DEFAULT_FMI_PATH", "/data/seq.fmi")

# Diagnostics settings (see diagnostics.py)
TRACE_ENABLED = _parse_bool(os.environ.get("ORCA_TRACE_ENABLED"), False)
TRACE_QUEUE_SIZE = int(os.environ.get("ORCA_TRACE_QUEUE_SIZE", "1024"))
TRACE_PID = os.environ.get("ORCA_TRACE_PID", "orca")
