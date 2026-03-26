#!/usr/bin/env bash

set -ex

PAT_MAX_LEN="${PAT_MAX_LEN:-150}"

if [[ "${SV_REBUILD:-0}" == "1" || ! -x obj_dir/Vtop ]]; then
  verilator -Wall --trace --cc FM_Index.sv top.sv ram.sv --exe sim_main.cpp --timing --top-module top -Wno-fatal -GPAT_MAX_LEN="${PAT_MAX_LEN}" -CFLAGS "-DPAT_MAX_LEN=${PAT_MAX_LEN}"
  make -C obj_dir -f Vtop.mk
fi

INDEX_BIN="${INDEX_BIN:-index.bin}"

./obj_dir/Vtop +INDEX_BIN="${INDEX_BIN}" &
PAT_MAX_LEN="${PAT_MAX_LEN}" python3 writer.py

wait
