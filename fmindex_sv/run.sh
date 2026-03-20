#!/usr/bin/env bash

set -ex

verilator -Wall --trace --cc FM_Index.sv top.sv ram.sv --exe sim_main.cpp --timing --top-module top -Wno-fatal
make -C obj_dir -f Vtop.mk

./obj_dir/Vtop &
python3 writer.py

wait
