# FM_Index State Machine Overview

This document describes the control flow in [`fmindex_sv/FM_Index.sv`](/home/aolse/school/ece492/sands/fmindex_sv/FM_Index.sv).

The design is split into three parts:

1. A one-time bootstrap that reads the FM-index header after reset.
2. A slot scheduler that can keep multiple queries in flight at once.
3. A per-slot burst state machine that remembers which RAM transaction is in flight while the RAM delay counter runs.

## States Overview

- `IDLE` waits for a `query_valid` pulse once bootstrap has finished.
- `INIT` performs the one-time bootstrap after reset, loading the header words from addresses `0`, `1`, and `2`.
- `READ_CHAR` consumes one pattern character and starts the next request burst for that slot.
- `WAIT_OCC_L`, `WAIT_OCC_R`, and `WAIT_C_BASE` wait for the delayed RAM response that belongs to the current burst.
- `DONE_S` and `FAIL_S` are terminal states for a completed slot.

## Per-Slot Burst

The repeating search loop is:

1. `READ_CHAR` fetches the current pattern character from `pattern[pat_idx]`.
2. The character is latched into `cur_char` for the whole three-read burst.
3. If the character is zero, the slot either finishes when the pattern is fully consumed or fails immediately if zero appears early.
4. Otherwise it requests `Occ(cur_char, l)` and enters `WAIT_OCC_L`.
5. After the `Occ(cur_char, l)` response, the slot requests `Occ(cur_char, r)`.
6. After the `Occ(cur_char, r)` response, the slot requests `C(cur_char)`.
7. After the `C(cur_char)` response, the slot updates the search interval and either loops, finishes, or fails.

## Output Behavior

- `done` is asserted when the machine is in `DONE_S`.
- `fail` is asserted when the machine is in `FAIL_S`.
- `result_valid` pulses when a slot reaches `DONE_S` or `FAIL_S`.
- `result_done` and `result_fail` identify the result type.
- `result_query_id` tags that result so the simulator can print results back in submission order.
- `l_out` and `r_out` carry the completed interval for the emitted result.

## Control State Diagram

At a high-level, the per-slot FSM state diagram is given below. `WAIT_OCC_L`, `WAIT_OCC_R`, and `WAIT_C_BASE` are the burst-wait states, and the sequence diagram below shows how the RAM transactions line up with those state transitions.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> IDLE

    IDLE --> INIT: first query after reset
    IDLE --> READ_CHAR: later queries after bootstrap
    INIT --> READ_CHAR: bootstrap complete
    READ_CHAR --> FAIL_S: char == 0 and loop_count > 0
    READ_CHAR --> WAIT_OCC_L: char != 0 / issue Occ(cur_char, l)

    WAIT_OCC_L --> WAIT_OCC_R
    WAIT_OCC_R --> WAIT_C_BASE
    WAIT_C_BASE --> READ_CHAR: continue
    WAIT_C_BASE --> DONE_S: finished
    WAIT_C_BASE --> FAIL_S: empty interval
    READ_CHAR --> DONE_S: char == 0 and loop_count == 0

    DONE_S --> IDLE
    FAIL_S --> IDLE
```

## Memory Operation Flow

`WAIT_OCC_L`, `WAIT_OCC_R`, and `WAIT_C_BASE` serve two jobs:

1. Wait for the RAM delay to expire.
2. Perform the action associated with the completed memory request.

The request kind tells the slot state machine what to do when the response becomes available.

| `request kind` | Meaning | What happens when the response arrives |
| --- | --- | --- |
| `BOOT_MAGIC` | First bootstrap read | Check `ram_data` against `INDEX_MAGIC`. If valid, request the sequence length at address `1`. |
| `BOOT_LEN` | Read sequence length | Save `seq_len`, then request the alphabet length at address `2`. |
| `BOOT_ALPHA` | Read alphabet length | Save `sigma_m1`, mark bootstrap complete, and allow query slots to accept work. |
| `REQ_OCC_L` | Read `Occ(cur_char, l)` | Save `rank_l`, then request `Occ(cur_char, r)`. |
| `REQ_OCC_R` | Read `Occ(cur_char, r)` | Save `rank_r`, then request `C(cur_char)`. |
| `REQ_C_BASE` | Read `C(cur_char)` | Update `l` and `r`, then either loop, finish, or fail. |

## State and Sequence Diagram

The sequence diagram shows the request order and the state transitions into and
out of the burst-wait states. The bootstrap phase uses the first three header
words once after reset, then later pattern slots jump directly into
`READ_CHAR` and reuse the burst states for the recurring `Occ` and `C` lookups
during backward search.

Note the bootstrap addresses (header fields) which are read before alignment:
- `addr 0`: `INDEX_MAGIC`
- `addr 1`: `seq_len`
- `addr 2`: `sigma_m1`

```mermaid
sequenceDiagram
    participant FSM as FM_Index
    participant RAM as RAM

    Note over FSM,RAM: Bootstrap reads
    FSM->>FSM: IDLE -> INIT
    FSM->>RAM: request addr 0 (INDEX_MAGIC)
    FSM->>FSM: INIT -> WAIT_BOOT_MAGIC
    RAM-->>FSM: magic
    alt magic mismatch
        FSM->>FSM: WAIT_BOOT_MAGIC -> FAIL_S
    else magic ok
        FSM->>RAM: request addr 1 (seq_len)
        FSM->>FSM: WAIT_BOOT_MAGIC -> WAIT_BOOT_LEN
        RAM-->>FSM: seq_len
        FSM->>RAM: request addr 2 (sigma_m1)
        FSM->>FSM: WAIT_BOOT_LEN -> WAIT_BOOT_ALPHA
        RAM-->>FSM: sigma_m1
        FSM->>FSM: WAIT_BOOT_ALPHA -> READ_CHAR
    end

    Note over FSM,RAM: Operational reads
    loop per pattern character
        alt char == 0
            alt loop_count == 0
                FSM->>FSM: READ_CHAR -> DONE_S
            else early zero
                FSM->>FSM: READ_CHAR -> FAIL_S
            end
        else continue
            FSM->>RAM: request Occ(cur_char, l)
            FSM->>FSM: READ_CHAR -> WAIT_OCC_L
            RAM-->>FSM: rank_l
            FSM->>RAM: request Occ(cur_char, r)
            FSM->>FSM: WAIT_OCC_L -> WAIT_OCC_R
            RAM-->>FSM: rank_r
            FSM->>RAM: request C(cur_char)
            FSM->>FSM: WAIT_OCC_R -> WAIT_C_BASE
            RAM-->>FSM: c_base
            alt l >= r
                FSM->>FSM: WAIT_C_BASE -> FAIL_S
            else loop_count == 0
                FSM->>FSM: WAIT_C_BASE -> DONE_S
            else continue
                FSM->>FSM: WAIT_C_BASE -> READ_CHAR
            end
        end
    end
```

In the operational loop, a zero pattern symbol is only legal once the pattern
has been fully consumed. If `READ_CHAR` sees `char == 0` before `loop_count`
reaches zero, that slot now takes the `FAIL_S` branch immediately.

## RAM is Async

The RAM is modeled as delayed, not combinational.

- `RAM_DELAY_CYCLES` is the number of cycles between request acceptance and response availability.
- `RAM_FIFO_DEPTH` is the maximum number of pending reads the RAM will allow.
- The controller now keeps several query slots active at once, but each slot still issues one burst at a time.

In practice, `FM_Index` can keep the shared RAM queue busier by interleaving
multiple slots, but each slot still consumes one character burst at a time.
That means the remaining bottleneck is now more about dependency depth than
about a single-query stall bubble.
