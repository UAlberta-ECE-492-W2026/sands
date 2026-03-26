'''
writer.py

This file is for testing purposes only.

- writes to the file that simulates the data in memory
- run during verilator simulation to send data to simulation

> python3 writer.py
'''

import struct
import time

pipe = open("mem_pipe", "wb")

i = 0

# Send 2 data packets to memory.
# Characters are mapped as A=1, C=2, G=3, T=4.
# This probe currently matches 53 occurrences in index.bin.
PAT_MAX_LEN = 150
CHAR_WIDTH = 3
PAT_WORDS = (PAT_MAX_LEN * CHAR_WIDTH + 31) // 32

pat = "CCCGT"
lookup = {
    "A": 1,
    "C": 2,
    "G": 3,
    "T": 4,
}

pat_codes = [lookup[ch] for ch in pat]
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

while (i < 2):
    i += 1
    packet = struct.pack(f"<{PAT_WORDS + 1}I", pat_len, *pattern_words)

    pipe.write(packet)
    pipe.flush()

    time.sleep(1)

pipe.close()
