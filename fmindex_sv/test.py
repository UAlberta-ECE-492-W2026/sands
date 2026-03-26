#!/usr/bin/env python3

from __future__ import annotations

import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass


CASES = 200
PAT_MAX_LEN = 150
SEED = 0x6B6D6B6D5F737663


@dataclass(frozen=True)
class CaseSpec:
    name: str
    sequence: str
    patterns: tuple[str, ...]


def run(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
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
    if check and proc.returncode != 0:
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


def run_rust_search(bin_path: Path, index_path: Path, query: str, cwd: Path) -> tuple[int, int] | None:
    proc = run(
        [str(bin_path), "search", str(index_path), query, "--no-list-all-outputs"],
        cwd=cwd,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return parse_rust_search(proc.stdout, proc.stderr)


def parse_sv_searches(output: str) -> list[tuple[int, int] | None]:
    results: list[tuple[int, int] | None] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == "FAIL":
            results.append(None)
            continue
        match = re.fullmatch(r"DONE: l=(\d+), r=(\d+)", line)
        if match:
            results.append((int(match.group(1)), int(match.group(2))))
    if not results:
        raise ValueError(f"could not parse fmindex_sv output:\n{output}")
    return results


def build_index(bin_path: Path, seq_path: Path, out_path: Path, subcommand: str) -> None:
    run(
        [str(bin_path), subcommand, str(seq_path), str(out_path)],
        cwd=seq_path.parent,
    )


def run_sv(
    repo_root: Path,
    index_path: Path,
    patterns: tuple[str, ...],
    rebuild: bool,
) -> list[tuple[int, int] | None]:
    env = {
        "INDEX_BIN": str(index_path),
        "FMINDEX_REPEAT": "1",
        "FMINDEX_SLEEP_SECS": "0",
        "PAT_MAX_LEN": str(PAT_MAX_LEN),
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
    return parse_sv_searches(proc.stdout)


def run_case(
    repo_root: Path,
    fmindexer_bin: Path,
    tmpdir: Path,
    case: CaseSpec,
    *,
    rebuild: bool,
) -> None:
    case_dir = tmpdir / case.name
    case_dir.mkdir()
    seq_path = case_dir / "seq.txt"
    sv_index_path = case_dir / "sv.fmi"
    seq_path.write_text(case.sequence)

    build_index(fmindexer_bin, seq_path, sv_index_path, "build-sim")

    rust_index_path = case_dir / "rust.fmi"
    build_index(fmindexer_bin, seq_path, rust_index_path, "build")
    rust_results = [
        run_rust_search(
            fmindexer_bin,
            rust_index_path,
            pattern,
            repo_root / "fmindexer.rs",
        )
        for pattern in case.patterns
    ]

    sv_result = run_sv(
        repo_root,
        sv_index_path,
        case.patterns,
        rebuild=rebuild,
    )

    if rust_results != sv_result:
        raise AssertionError(
            f"case {case.name} diverged\n"
            f"sequence: {case.sequence}\n"
            f"patterns: {case.patterns}\n"
            f"rust: {rust_results}\n"
            f"sv: {sv_result}\n"
        )


def make_compatibility_cases(rng: random.Random) -> list[CaseSpec]:
    cases: list[CaseSpec] = []
    for case_idx in range(CASES):
        seq_len = rng.randint(4, 48)
        query_len = rng.randint(1, 10)
        cases.append(
            CaseSpec(
                name=f"compat-{case_idx}",
                sequence=rand_sequence(rng, seq_len),
                patterns=(rand_query(rng, query_len),),
            )
        )
    return cases


def make_empty_sequence_cases() -> list[CaseSpec]:
    seq = ""
    return [
        CaseSpec(name="empty-seq-a", sequence=seq, patterns=("A",)),
        CaseSpec(name="empty-seq-ac", sequence=seq, patterns=("AC",)),
    ]


def make_empty_pattern_cases() -> list[CaseSpec]:
    return [
        CaseSpec(name="empty-pattern", sequence="ACGT", patterns=("",)),
        CaseSpec(name="empty-pattern-empty-seq", sequence="", patterns=("",)),
    ]


def make_multi_pattern_cases() -> list[CaseSpec]:
    return [
        CaseSpec(
            name="multi-pattern-a",
            sequence="ACGTACGT",
            patterns=("AC", "GT"),
        ),
        CaseSpec(
            name="multi-pattern-b",
            sequence="GATTACA",
            patterns=("GA", "", "TA"),
        ),
    ]


def run_suite(
    name: str,
    cases: list[CaseSpec],
    repo_root: Path,
    fmindexer_bin: Path,
    tmpdir: Path,
    *,
    rebuild_first_case: bool = False,
) -> None:
    print(f"{name}: ", end="", flush=True)
    for idx, case in enumerate(cases):
        run_case(
            repo_root,
            fmindexer_bin,
            tmpdir,
            case,
            rebuild=rebuild_first_case and idx == 0,
        )
        print('.', end='', flush=True)
    print()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: test.py <repo-root>")

    repo_root = Path(sys.argv[1]).resolve()
    fmindexer_bin = build_binary(repo_root)

    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory(prefix="fmindex-sv-compat-") as tmp:
        tmpdir = Path(tmp)
        compatibility_cases = make_compatibility_cases(rng)
        run_suite(
            "compatibility",
            compatibility_cases,
            repo_root,
            fmindexer_bin,
            tmpdir,
            rebuild_first_case=True,
        )
        run_suite(
            "empty-sequence",
            make_empty_sequence_cases(),
            repo_root,
            fmindexer_bin,
            tmpdir,
        )
        run_suite(
            "empty-pattern",
            make_empty_pattern_cases(),
            repo_root,
            fmindexer_bin,
            tmpdir,
            rebuild_first_case=False,
        )
        run_suite(
            "multi-pattern",
            make_multi_pattern_cases(),
            repo_root,
            fmindexer_bin,
            tmpdir,
            rebuild_first_case=False,
        )

    print(f"PASS: compatibility={CASES}, empty-sequence=2, empty-pattern=2, multi-pattern=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
