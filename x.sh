#!/usr/bin/env bash

export PYTHONPATH=$PWD

_abspath() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "$PWD" "$1" ;;
  esac
}

_header() {
  echo
  echo "====== $1 ===================================="
  echo
}

help() {
  usage
}

usage() {
  cat <<EOF
Run actions across the entire repository.

Usage:  $0 setup-venv  Setup your local venv
        $0 tests       Run all tests
        $0 check       Typecheck all code
        $0 run-local   Run locally (with docker-compose)
        $0 index-seq   Generate a sequence and build an SV index
        $0 sim         Run the SystemVerilog FM-index simulation
        $0 help        Print this message

EOF
}

activate-venv() {
  if ! test -d venv/; then
    echo "No venv/, run $0 setup-venv to create one"
    exit 1
  fi

  if test -f venv/bin/activate; then
    source venv/bin/activate
  else
    source venv/Scripts/activate
  fi
}

setup-venv() {
  if ! test -d venv/; then
    python3 -m venv venv
  else
    echo 'venv/ already exists, remove it if you need to rebuild'
  fi

  activate-venv

  pip install -r requirements.txt
  pip install -r requirements-dev.txt
}

tests() {
  activate-venv

  _header 'Running pytest tests'
  pytest

  _header 'Running fmindexer tests'
  pushd fmindexer.rs >/dev/null
  test/run.sh
  popd
}

check() {
  activate-venv

  _header 'Type checking orca'
  pushd orca >/dev/null
  ty check
  popd >/dev/null

  _header 'Type checking buoy'
  pushd buoy >/dev/null
  ty check
  popd >/dev/null

  _header 'Type checking port'
  pushd port >/dev/null
  ty check
  popd >/dev/null

  _header 'Running fmindexer cargo check'
  pushd fmindexer.rs >/dev/null
  cargo check
  popd >/dev/null
}

run-local() {
  docker compose up --build "$@"
}

index-seq() {
  if [[ "$#" -ne 2 ]]; then
    echo "Usage: $0 index-seq <length> <output.bin>" >&2
    exit 1
  fi

  local output
  output="$(_abspath "$2")"

  pushd fmindexer.rs >/dev/null
  cargo run -- build-sim <(python3 seqgen.py "$1") "$output"
  popd >/dev/null
}

sim() {
  if [[ "$#" -ne 1 ]]; then
    echo "Usage: $0 sim <index.bin>" >&2
    exit 1
  fi

  local index
  index="$(_abspath "$1")"

  pushd fmindex_sv >/dev/null
  INDEX_BIN="$index" ./run.sh
  popd >/dev/null
}

if [[ "$#" == 0 ]]; then
  usage
fi

"$@"
