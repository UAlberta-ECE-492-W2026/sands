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

## Experiment 2: Pipelined RAM requests

### What changed

This experiment pipelines the search-side RAM accesses in
[`fmindex_sv/FM_Index.sv`](/home/aolse/school/ece492/sands/fmindex_sv/FM_Index.sv).

The controller now:

- issues the three search reads for a pattern character back-to-back
- keeps the requests in flight while the RAM delay counter runs
- consumes the responses in order once they arrive
- still preserves the one-time bootstrap after reset

The simulator and benchmark harness were left unchanged except for the cycle
count reporting already added in Experiment 1.

### Results

```tsv
seq_len	pat_len	cycles
500	3	52
500	50	663
500	150	1963
1000	3	52
1000	50	663
1000	150	1963
50000	3	52
50000	50	663
50000	150	1963
```

### Observations

#### What improved

Compared with Experiment 1, the cycle count dropped substantially:

- `3` characters: `116 -> 52`
- `50` characters: `1479 -> 663`
- `150` characters: `4379 -> 1963`

That is the expected effect of overlapping the `Occ(char, l)`, `Occ(char, r)`,
and `C(char)` reads instead of waiting for each one to complete before issuing
the next.

#### Why `seq_len` still does not matter

The same FM-index property still holds:

- the search walks the pattern
- the sequence length only changes the index size and the interval values
- the number of per-character memory bursts is unchanged

So the benchmark still stays flat across `seq_len` for these inputs.

#### Why `pat_len` is still linear

We have reduced the constant factor, but the search is still fundamentally
character-by-character.

Each character still requires:

- one burst for the three RAM reads
- one control step to fold the responses into the next interval

So the total cycle count remains approximately linear in `pat_len`.

#### Where are we still wasting cycles?

The main remaining waste is the tail latency of each burst and the control
bubble around `CHECK` / `READ_CHAR`.

Specifically:

- the first response of each burst still has to wait for the RAM delay
- the controller still serializes a pattern character into a single burst
- we do not overlap one character's interval update with the next character's
  request setup yet

This is a better baseline, but it is still not fully hiding the RAM latency.
The next experiment should look at whether we can overlap the end of one burst
with the start of the next character, or otherwise reduce the `CHECK` bubble.
