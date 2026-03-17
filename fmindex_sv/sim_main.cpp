#include "Vtb_FM_Index.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>

vluint64_t main_time = 0;

struct Cmd {
    // TODO add the stuff
    int pat_len;
    int pattern;
};

// Required for Verilator when using --timing
double sc_time_stamp() {
    return main_time;
}

int main(int argc, char **argv) {

    Verilated::commandArgs(argc, argv);
    Vtb_FM_Index* top = new Vtb_FM_Index;

    int pipe_fd = open("mem_pipe", O_RDONLY); //  | O_NONBLOCK

    Verilated::traceEverOn(true);

    VerilatedVcdC* tfp = new VerilatedVcdC;
    //top->trace(tfp, 99);
    //tfp->open("waveform.vcd");

    top->start = 0;
    top->reset = 1;
    top->eval();

    while (!Verilated::gotFinish()) {

        Cmd cmd;

        int r = read(pipe_fd, &cmd, sizeof(cmd));

        if (r == sizeof(cmd)) {
            printf("Received: pattern=%d length=%d\n", cmd.pattern, cmd.pat_len);
            top->we = 1;
            top->pattern = cmd.pattern;
            top->pat_len_in = cmd.pat_len;
            top->start = 1;
            top->reset = 0;
        } else {
            top->we = 0;
        }

        top->clk = 0;
        top->eval();
        //tfp->dump(main_time);

        top->clk = 1;
        top->eval();
        //tfp->dump(main_time);

        top->start = 0;

        main_time++;

        if (main_time > 10000000) {
            printf("Timeout\n");
            tfp->close();
            delete top;
            exit(1);
        }
    }

    //tfp->close();
    delete top;
}