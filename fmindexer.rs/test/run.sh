#!/usr/bin/env bash

set -euo pipefail

header() {
  local name=$(basename "$1")
  echo "$name ------------------------------"
}

footer() {
  header "$1" | sed 's/./-/g'
}

run-tests() {
  echo '======== Integration Tests =================='
  echo

  for test_case in "$PWD/test/"*.test.sh; do
    tmpdir=$(mktemp -d)
    pushd "$tmpdir" >/dev/null

    header "$test_case"
    bash "$test_case"
    footer "$test_case"
    echo

    popd >/dev/null
  done

  echo "Tests PASS!"
}

main() {
  cargo build --release
  export PATH="$PATH:$PWD/target/release:$PWD"

  cargo test

  # Integration tests in test/
  run-tests
}

main
