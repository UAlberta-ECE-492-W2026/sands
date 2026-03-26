#!/usr/bin/env python3

from __future__ import annotations

import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path


CASES = 200
PAT_MAX_LEN = 150
SEED = 0x6B6D6B6D5F737663


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc


def build_binary(repo_root: Path) -> Path:
    build_dir = repo_root / "fmindexer.rs"
    run(
        ["cargo", "build", "--quiet"],
        cwd=build_dir,
    )
    return build_dir / "target" / "debug" / "fmindexer"


def rand_sequence(rng: random.Random, length: int) -> str:
    alphabet = "ACGT"
    seq = list(alphabet)
    while len(seq) < length:
        seq.append(rng.choice(alphabet))
    rng.shuffle(seq)
    return "".join(seq)


def rand_query(rng: random.Random, length: int) -> str:
    alphabet = "ACGT"
    return "".join(rng.choice(alphabet) for _ in range(length))


def parse_rust_search(stdout: str, stderr: str) -> tuple[int, int] | None:
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.fullmatch(r"low=(\d+), high=(\d+)", line)
        if match:
            return int(match.group(1)), int(match.group(2))

    for line in stderr.splitlines():
        if line.strip() == "No results":
            return None

    raise ValueError(f"could not parse fmindexer output:\nstdout:\n{stdout}\nstderr:\n{stderr}")


def parse_sv_search(output: str) -> tuple[int, int] | None:
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == "FAIL":
            return None
        match = re.fullmatch(r"DONE: l=(\d+), r=(\d+)", line)
        if match:
            return int(match.group(1)), int(match.group(2))
    raise ValueError(f"could not parse fmindex_sv output:\n{output}")


def build_index(bin_path: Path, seq_path: Path, out_path: Path, subcommand: str) -> None:
    run(
        [str(bin_path), subcommand, str(seq_path), str(out_path)],
        cwd=seq_path.parent,
    )


def run_sv(repo_root: Path, index_path: Path, pattern: str, rebuild: bool) -> tuple[int, int] | None:
    env = {
        "INDEX_BIN": str(index_path),
        "FMINDEX_PATTERN": pattern,
        "FMINDEX_REPEAT": "1",
        "FMINDEX_SLEEP_SECS": "0",
        "PAT_MAX_LEN": str(PAT_MAX_LEN),
    }
    if rebuild:
        env["SV_REBUILD"] = "1"

    proc = subprocess.run(
        ["./run.sh"],
        cwd=repo_root / "fmindex_sv",
        env={**os.environ, **env},
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"fmindex_sv/run.sh failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return parse_sv_search(proc.stdout)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: test.py <repo-root>")

    repo_root = Path(sys.argv[1]).resolve()
    fmindexer_bin = build_binary(repo_root)

    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory(prefix="fmindex-sv-compat-") as tmp:
        tmpdir = Path(tmp)
        for case_idx in range(CASES):
            print('.', end='', flush=True)
            seq_len = rng.randint(4, 48)
            query_len = rng.randint(1, 10)
            seq = rand_sequence(rng, seq_len)
            query = rand_query(rng, query_len)

            case_dir = tmpdir / f"case-{case_idx}"
            case_dir.mkdir()
            seq_path = case_dir / "seq.txt"
            rust_index_path = case_dir / "rust.fmi"
            sv_index_path = case_dir / "sv.fmi"

            seq_path.write_text(seq)
            build_index(fmindexer_bin, seq_path, rust_index_path, "build")
            build_index(fmindexer_bin, seq_path, sv_index_path, "build-sim")

            rust_output = run(
                [str(fmindexer_bin), "search", str(rust_index_path), query, "--no-list-all-outputs"],
                cwd=repo_root / "fmindexer.rs",
            )
            rust_result = parse_rust_search(rust_output.stdout, rust_output.stderr)
            sv_result = run_sv(repo_root, sv_index_path, query, rebuild=(case_idx == 0))

            if rust_result != sv_result:
                print()
                raise AssertionError(
                    f"case {case_idx} diverged\n"
                    f"sequence: {seq}\n"
                    f"query: {query}\n"
                    f"rust: {rust_result}\n"
                    f"sv: {sv_result}\n"
                    f"rust stdout:\n{rust_output.stdout}"
                )

    print(f"\nsv compatibility tests PASS ({CASES} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
