#!/usr/bin/env bash

export PYTHONPATH=$PWD

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
        $0 infra       Run CDK commands (defaults to synth)
        $0 help        Print this message

EOF
}

header() {
  echo
  echo "====== $1 ===================================="
  echo
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

  header 'Running pytest tests'
  pytest

  header 'Running fmindexer tests'
  pushd fmindexer.rs >/dev/null
  test/run.sh
  popd

  header 'Synthesizing CDK stack'
  cdk_with_args synth
}

check() {
  activate-venv

  header 'Type checking orca'
  pushd orca >/dev/null
  ty check
  popd >/dev/null

  header 'Type checking buoy'
  pushd buoy >/dev/null
  ty check
  popd >/dev/null

  header 'Type checking port'
  pushd port >/dev/null
  ty check
  popd >/dev/null

  header 'Running fmindexer cargo check'
  pushd fmindexer.rs >/dev/null
  cargo check
  popd >/dev/null
}

run-local() {
  docker compose up --build "$@"
}

install-cdk() {
  npm i
}

cdk_with_args() {
  install-cdk

  activate-venv
  pushd infra >/dev/null
  pip install -r requirements.txt
  npx cdk "$@"
  popd >/dev/null
}

infra() {
  header 'CDK infrastructure'
  if [[ "$#" == 0 ]]; then
    cdk_with_args synth
  else
    cdk_with_args "$@"
  fi
}

if [[ "$#" == 0 ]]; then
  usage
fi

"$@"
