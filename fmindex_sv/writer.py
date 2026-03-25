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
# These are packed FM-index symbol codes, not raw ASCII letters.
# This probe currently matches 3028 occurrences in index.bin.
pat = [2, 5]
pat_len = len(pat)

while (i < 2):
    i += 1
    pattern = (pat[0] << 21) | (pat[1] << 18)

    packet = struct.pack("BI", pat_len, pattern)

    pipe.write(packet)
    pipe.flush()

    time.sleep(1)

pipe.close()
