# Orca

This is the orchestrator for the SANDS project. It distributes indexing tasks
across multiple nodes.

## Running the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once it is running, visit `http://localhost:8000/docs` to explore the
auto-generated OpenAPI UI.

## Configuration

- `ORCA_SHARED_SECRET`: shared HMAC secret (default `sands-shared-secret`).
- `ORCA_DB_PATH`: SQLite file path (default `orca_state.db`).
- `ORCA_DEFAULT_FMI_PATH`: fallback `.fmi` index path returned to buoys.
