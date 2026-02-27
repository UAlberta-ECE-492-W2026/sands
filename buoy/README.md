# Buoy

This is a node managed by orca. It is responsible for delegating to an actual
FM-index implementation and coordinating it's work with the orca orchestrator.

## Running the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Once it is running, visit `http://localhost:8001/docs` to explore the
auto-generated OpenAPI UI.

## Environment

- `ORCA_URL` (default `http://localhost:8000`)
- `ORCA_SHARED_SECRET` (must match Orca)
- `BUOY_ID` identifier sent during registration
- `FMINDEXER_BIN` path to the `fmindexer` binary (default `fmindexer` in `$PATH`)
