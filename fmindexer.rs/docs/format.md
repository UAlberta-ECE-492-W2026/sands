# `build-sim` output format

The `build-sim` subcommand writes a binary FM-index file directly with
[`FMIndex::write`](../src/fm_index.rs).

## Command

```bash
fmindexer build-sim <input> <output>
```

`<input>` is read as raw bytes. If it does not already end with `$`, the
program appends a trailing `$` before building the index.

## File layout

The output file is a plain sequence of little-endian `u32` values with no
header, footer, or length prefix.

The layout is:

1. `counts[0]`
2. `counts[1]`
3. `counts[2]`
4. ...
5. `counts[counts.len() - 1]`
6. `occ[0]`
7. `occ[1]`
8. `occ[2]`
9. ...
10. `occ[occ.len() - 1]`

So the file is:

```text
counts serialized as u32 little-endian
then occ serialized as u32 little-endian
```

## Field meaning

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
