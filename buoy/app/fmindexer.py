import asyncio
import json
import logging
import os
import tempfile
from typing import Any, Dict, List

from .config import FMINDEXER_BIN


async def run_fmindexer_search(fmi_path: str, reads: List[str]) -> List[Dict[str, Any]]:
    if not reads:
        return []

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write("\n".join(reads))
        tmp.flush()
        tmp_path = tmp.name

    process = await asyncio.create_subprocess_exec(
        FMINDEXER_BIN,
        "search-many",
        fmi_path,
        tmp_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    os.unlink(tmp_path)
    if process.returncode != 0:
        raise RuntimeError(stderr.decode().strip())

    results: List[Dict[str, Any]] = []
    for line in stdout.decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError as exc:
            logging.warning("failed to parse fmindexer output: %s", exc)
    return results
