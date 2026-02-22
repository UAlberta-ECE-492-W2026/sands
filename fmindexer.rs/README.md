# Node

This is a software node which runs the FM-index as requested by the orchestrator, orca.

## Building

You will need to have [installed a Rust
toolchain](https://rust-lang.org/learn/get-started/). Then you can run the
project with:

```
cargo run --release -- --help
cargo run --release -- build <input.txt> <output.fmi>
cargo run --release -- search <index.fmi> <query>
cargo run --release -- search-many <index.fmi> <queries.txt>  # newline-delimited query file
```

## Testing

Tests can be run with (from the repo root):

```
$ x.sh tests
```

More tests can be added as rust unit tests, or integration tests as a
`mytest.test.sh` script in the `test/` directory.
