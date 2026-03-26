"""
writer.py

This file is for testing purposes only.

- writes to the file that simulates the data in memory
- run during verilator simulation to send data to simulation
"""

from __future__ import annotations

import argparse
import os
import struct
import time

pipe = open("mem_pipe", "wb")

i = 0

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pattern",
        default="CCCGT",
        help="DNA pattern string using A/C/G/T; defaults to CCCGT",
    )
    return parser.parse_args()


args = parse_args()

PAT_MAX_LEN = int(os.environ.get("FMINDEX_PAT_MAX_LEN", "150"))
CHAR_WIDTH = 3
PAT_WORDS = (PAT_MAX_LEN * CHAR_WIDTH + 31) // 32

lookup = {
    "A": 1,
    "C": 2,
    "G": 3,
    "T": 4,
}

for ch in args.pattern:
    if ch not in lookup:
        raise ValueError(f"pattern contains invalid character {ch!r}")

pat_codes = [lookup[ch] for ch in args.pattern]

repeat = int(os.environ.get("FMINDEX_REPEAT", "1"))
sleep_s = float(os.environ.get("FMINDEX_SLEEP_SECS", "0"))
pat_len = len(pat_codes)

if pat_len > PAT_MAX_LEN:
    raise ValueError("pattern is longer than PAT_MAX_LEN")

pattern_bits = 0
for idx, code in enumerate(reversed(pat_codes)):
    bit_pos = (PAT_MAX_LEN - 1 - idx) * CHAR_WIDTH
    pattern_bits |= code << bit_pos

pattern_words = [
    (pattern_bits >> (32 * word_idx)) & 0xFFFFFFFF
    for word_idx in range(PAT_WORDS)
]

while i < repeat:
    i += 1
    packet = struct.pack(f"<{PAT_WORDS + 1}I", pat_len, *pattern_words)

    pipe.write(packet)
    pipe.flush()

    if sleep_s:
        time.sleep(sleep_s)

pipe.close()
