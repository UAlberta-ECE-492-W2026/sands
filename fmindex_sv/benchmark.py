#!/usr/bin/env python3

from __future__ import annotations

import os
import random
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fmindex_sv.test import build_binary, build_index, rand_sequence


SEQ_LENS = (500, 1_000, 50_000)
PAT_LENS = (3, 50, 150)
BATCH_SIZE = 4
SEED = 0x6B6D6B6D5F62656E


@dataclass(frozen=True)
class BenchCase:
    seq_len: int
    pat_len: int
    sequence: str
    patterns: tuple[str, ...]


def parse_cycles(output: str) -> int:
    batch_cycles: int | None = None
    last_cycles: int | None = None
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("BATCH_CYCLES\t"):
            batch_cycles = int(line.split("\t", 1)[1])
        elif line.startswith("CYCLES\t"):
            last_cycles = int(line.split("\t", 1)[1])
    if batch_cycles is not None:
        return batch_cycles
    if last_cycles is not None:
        return last_cycles
    raise ValueError(f"could not parse benchmark cycles from output:\n{output}")


def run_sv_benchmark(
    repo_root: Path,
    index_path: Path,
    patterns: tuple[str, ...],
    rebuild: bool,
) -> int:
    env = {
        "INDEX_BIN": str(index_path),
        "FMINDEX_REPEAT": "1",
        "FMINDEX_SLEEP_SECS": "0",
        "PAT_MAX_LEN": "150",
        "FMINDEX_BENCHMARK": "1",
    }
    if rebuild:
        env["SV_REBUILD"] = "1"

    args = ["./run.sh"]
    for pattern in patterns:
        args.extend(["--pattern", pattern])

    proc = subprocess.run(
        args,
        cwd=repo_root / "fmindex_sv",
        env={**os.environ, **env},
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"fmindex_sv/run.sh failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return parse_cycles(proc.stdout)


def make_cases(rng: random.Random) -> list[BenchCase]:
    cases: list[BenchCase] = []
    for seq_len in SEQ_LENS:
        sequence = rand_sequence(rng, seq_len)
        for pat_len in PAT_LENS:
            cases.append(
                BenchCase(
                    seq_len=seq_len,
                    pat_len=pat_len,
                    sequence=sequence,
                    patterns=tuple(sequence[:pat_len] for _ in range(BATCH_SIZE)),
                )
            )
    return cases


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: benchmark.py <repo-root>")

    repo_root = Path(sys.argv[1]).resolve()
    fmindexer_bin = build_binary(repo_root)

    rng = random.Random(SEED)
    cases = make_cases(rng)

    print("seq_len\tpat_len\tqueries\tcycles")

    with tempfile.TemporaryDirectory(prefix="fmindex-sv-bench-") as tmp:
        tmpdir = Path(tmp)
        for idx, case in enumerate(cases):
            case_dir = tmpdir / f"seq-{case.seq_len}-pat-{case.pat_len}"
            case_dir.mkdir()
            seq_path = case_dir / "seq.txt"
            sv_index_path = case_dir / "sv.fmi"
            seq_path.write_text(case.sequence)

            build_index(fmindexer_bin, seq_path, sv_index_path, "build-sim")
            cycles = run_sv_benchmark(
                repo_root,
                sv_index_path,
                case.patterns,
                rebuild=idx == 0,
            )
            print(f"{case.seq_len}\t{case.pat_len}\t{len(case.patterns)}\t{cycles}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
