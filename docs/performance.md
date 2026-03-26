# Performance Log

This file is an append-only experiment log for the `fmindex_sv` simulator.

## Experiment 1: Baseline async RAM, no pipelining

### How to benchmark

Run:

```bash
./x.sh sv-benchmark
```

This benchmark:

- builds a simulator index for each test sequence
- runs the SV searcher once per `(sequence length, pattern length)` pair
- records the number of clock cycles reported by the simulator
- prints the results as TSV

The current benchmark matrix is:

- sequence lengths: `500`, `1000`, `50000`
- pattern lengths: `3`, `50`, `150`

### What we are measuring

We are measuring end-to-end search latency in clock cycles for the current SV
implementation.

This is intentionally a coarse measurement:

- it includes the bootstrap phase for the first search in the simulator run
- it includes the current RAM wait behavior
- it does not yet separate compute cycles from memory stalls

### Current implementation

The current search path is not pipelined.

- `FM_Index` issues one RAM request at a time.
- The controller waits for the delayed response before issuing the next request.
- The RAM model itself can accept multiple pending requests, but the search FSM
  does not use that capacity yet.

This means the current design is a useful baseline for estimating how much of
the total latency is dominated by memory round trips.

### Results

```tsv
seq_len	pat_len	cycles
500	3	116
500	50	1479
500	150	4379
1000	3	116
1000	50	1479
1000	150	4379
50000	3	116
50000	50	1479
50000	150	4379
```

### Observations

#### Why do we not depend on `seq_len`?

The cycle count is flat across `seq_len` in this benchmark.

That is what we expect from an FM-index search:

- the search walks the pattern, not the full sequence
- the sequence length mainly affects the size of the index and the search
  interval bounds, not the number of pattern iterations

So, for a fixed pattern length, the simulator is mostly doing the same work
whether the indexed sequence is `500` bases or `50000` bases.

#### Why does increasing `pat_len` increase cycles linearly?

The current implementation processes one pattern symbol at a time.

Each character drives roughly the same memory sequence:

- read `Occ(char, l)`
- read `Occ(char, r)`
- read `C(char)`
- update the interval

That gives a near-linear relationship between pattern length and cycle count.
The benchmark data reflects that directly:

- `3 -> 116` cycles
- `50 -> 1479` cycles
- `150 -> 4379` cycles

#### Where are we wasting cycles?

The obvious waste is memory latency.

The current design pays the full RAM delay for each request and does not overlap
requests with useful work. In practice:

- `MEM_WAIT` is spent mostly counting down delay cycles
- the search FSM is idle while waiting for each response
- there is no prefetching or request pipelining yet

This makes the baseline easy to reason about, but it leaves performance on the
table. The next experiment should focus on overlapping RAM requests with the
search state machine so we can hide some of that delay.

### Next experiment

The next likely improvement is to pipeline RAM requests where possible and
measure how much of the per-pattern latency disappears once the controller can
keep more than one read in flight.
