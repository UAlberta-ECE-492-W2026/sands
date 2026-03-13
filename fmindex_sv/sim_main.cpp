#include "Vtb_FM_Index.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

vluint64_t main_time = 0;

// Required for Verilator when using --timing
double sc_time_stamp() {
    return main_time;
}

int main(int argc, char **argv) {

    Verilated::commandArgs(argc, argv);
    Vtb_FM_Index* top = new Vtb_FM_Index;

    Verilated::traceEverOn(true);

    VerilatedVcdC* tfp = new VerilatedVcdC;
    top->trace(tfp, 99);
    tfp->open("waveform.vcd");

    while (!Verilated::gotFinish()) {

        top->eval();
        tfp->dump(main_time);

        main_time++;
    }

    tfp->close();
    delete top;
}