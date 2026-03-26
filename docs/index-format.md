# `build-sim` output format

The `build-sim` subcommand writes a binary FM-index file directly with
[`FMIndex::write`](../fmindexer.rs/src/fm_index.rs).

## Command

```bash
fmindexer build-sim <input> <output>
```

`<input>` is read as raw bytes. If it does not already end with `$`, the
program appends a trailing `$` before building the index.

## File layout

The output file is a sequence of little-endian `u32` values with a 3-word
header followed by the FM-index tables.

The layout is:

1. `magic`
2. `sequence_length`
3. `alphabet_length`
4. `counts[0]`
5. `counts[1]`
6. `counts[2]`
7. ...
8. `counts[counts.len() - 1]`
9. `occ[0]`
10. `occ[1]`
11. `occ[2]`
12. ...
13. `occ[occ.len() - 1]`

So the file is:

```text
[magic][sequence_length][alphabet_length][counts...][occ...]
```

## Field meaning

### `magic`

`magic` identifies the simulator format and is always `0x31444946`, which is
the ASCII string `FID1` in little-endian form.

### `sequence_length`

`sequence_length` is the FM-index text length, including the trailing `$`.

### `alphabet_length`

`alphabet_length` is the number of symbols in the sorted alphabet, excluding
`$`.

### `counts`

`counts` is the FM-index `C` table. It stores one entry per byte in the sorted
alphabet of the input sequence, excluding `$`.

For each alphabet symbol `alphabet[i]`, `counts[i]` is:

```text
1 + number of bytes in the sequence that are strictly smaller than alphabet[i]
```

The implementation starts at `1` because the sentinel `$` is treated as the
first position.

> Note that `alphabet` does not contain any `$` symbol. Ie. `counts.len()`
> equals 4 for the standard ACGT DNA alphabet.

### `occ`

`occ` is the occurrence table flattened row by row.

If `alphabet.len() == k` (`k` usually is 4) and the input sequence length is `n`, then:

```text
occ.len() == k * (n + 1)
```

The first `k` entries are all zero. After that, each block of `k` entries
contains the cumulative counts after consuming one more character of the BWT.

The simulator uses `alphabet_length` to compute the row width and
`sequence_length` to determine the maximum prefix length.

Indexing is:

```text
occ[row * k + col]
```

where `row` is the prefix length in the BWT and `col` is the symbol index in
the sorted alphabet.

## Notes

- `build-sim` does not use `postcard` serialization (like `build` does).
- The output does not include the BWT, the suffix array, or the alphabet.
- The file is intended for the simulator path, not for the normal `search`
  command, which expects the `build` (`postcard`) format.
