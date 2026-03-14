This Text file gives the order of commands when compiling the digital logic for simulation.

start: running .sv files through verilator simulation
end: open the waveform in gtkwave

# step 1:
verilator -Wall --trace --cc <module>.sv <test bench>.sv --exe sim_main.cpp --timing --top-module <top_module> -Wno-fatal

# Step 2:
make -C obj_dir -f V<top_module>.mk

# step 3:
./obj_dir/<top_mopdule>  # exclude extension

# step 4:
gtkwave waveform.vcd &

# Step 5:
- the signals will not be on the waveform automatically, add them manually in the gui.