"""CLI for submitting short-read jobs and checking status against Orca."""

from __future__ import annotations

import argparse
import hmac
import hashlib
import sys
import time
from pathlib import Path

import httpx

DEFAULT_SECRET = "sands-shared-secret"
DEFAULT_ORCA_URL = "http://localhost:8000"


def build_signature(secret: str, payload: bytes) -> dict[str, str]:
    timestamp = str(int(time.time()))
    mac = hmac.new(
        secret.encode("utf-8"), timestamp.encode("utf-8") + payload, hashlib.sha256
    )
    return {"X-Orca-Timestamp": timestamp, "X-Orca-Signature": mac.hexdigest()}


def load_reads(file_path: Path | None) -> str:
    if file_path:
        text = file_path.read_text().strip()
    else:
        text = sys.stdin.read().strip()
    if not text:
        raise SystemExit("no reads provided")
    return text


def submit_command(args: argparse.Namespace) -> None:
    reads = load_reads(args.reads)
    payload = reads.encode("utf-8")
    headers = build_signature(args.secret, payload)
    params = {"fmi_path": args.fmi_path}
    if args.chunk_size:
        params["chunk_size"] = str(args.chunk_size)
    if args.job_id:
        params["job_id"] = args.job_id
    response = httpx.post(
        f"{args.orca_url}/shortreads",
        content=payload,
        headers=headers,
        params=params,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    print(f"job_id: {data.get('job_id')} chunks: {data.get('chunks')}")


def status_command(args: argparse.Namespace) -> None:
    payload = b""
    headers = build_signature(args.secret, payload)
    response = httpx.get(
        f"{args.orca_url}/jobs/{args.job_id}", headers=headers, timeout=30
    )
    response.raise_for_status()
    data = response.json()
    print("job status:")
    for key, value in data.items():
        print(f"  {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(
        "orca-port", description="Port CLI for submitting reads to Orca"
    )
    parser.add_argument(
        "--orca-url", default=DEFAULT_ORCA_URL, help="Base URL for Orca API"
    )
    parser.add_argument("--secret", default=DEFAULT_SECRET, help="Shared HMAC secret")
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit_parser = subparsers.add_parser(
        "submit", help="Upload newline-delimited short reads"
    )
    submit_parser.add_argument(
        "--reads",
        type=Path,
        help="Path to newline-delimited reads file (default stdin)",
    )
    submit_parser.add_argument(
        "--fmi-path", default="/fmi/seq.fmi", help="Path to the .fmi index"
    )
    submit_parser.add_argument(
        "--chunk-size", type=int, help="Override chunk size (<=1000)"
    )
    submit_parser.add_argument("--job-id", help="Optional job identifier")
    submit_parser.set_defaults(handler=submit_command)

    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument(
        "--job-id", required=True, help="Job ID returned by submit"
    )
    status_parser.set_defaults(handler=status_command)

    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
