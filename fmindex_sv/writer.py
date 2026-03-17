import struct
import time

pipe = open("mem_pipe", "wb")

i = 0
# while True:
while (i < 2):
    i += 1
    pat_len = 2
    pattern = 0b100001000000000000000000

    packet = struct.pack("BI", pat_len, pattern)

    pipe.write(packet)
    pipe.flush()

    time.sleep(1)

pipe.close()