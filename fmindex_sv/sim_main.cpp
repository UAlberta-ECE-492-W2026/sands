#include "Vtop.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <iostream>
#include <cstdio>
#include <string>
#include <fstream>
#include <cstring>

#define SIM_LENGTH 10000000 // edit this value to change siumulation length
#ifndef PAT_MAX_LEN
#define PAT_MAX_LEN 150
#endif

static constexpr int CHAR_WIDTH = 3;
static constexpr int PAT_WORDS = (PAT_MAX_LEN * CHAR_WIDTH + 31) / 32;

vluint64_t main_time = 0;

struct Cmd {
    uint32_t pat_len;
    uint32_t pattern[PAT_WORDS];
};

// Required for Verilator when using --timing (do not delete)
double sc_time_stamp() {
    return main_time;
}

int main(int argc, char **argv) {

    // STEP 1: if old PIPE existed, delete it
    const char* file = "mem_pipe";

    if (std::remove(file) == 0) {
        printf("old pipe deleted\n");
    } else {
        printf("error deleting old pipe or old pipe does not exist\n");
    }

    // STEP 2: create new pipe file
    std::ofstream MyFile(file);

    if (!MyFile.is_open()) {
        printf("Error creating file");
        return 1;
    }

    MyFile.close();

    // STEP 3: setup verilator simulation
    // STEP 3.1: innitialize verilator sim and memory pipe
    Verilated::commandArgs(argc, argv);
    auto* top = new Vtop;

    int pipe_fd = open("mem_pipe", O_RDONLY);

    // STEP 3.2: innitialize waveform
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC; 
    //top->trace(tfp, 99);
    //tfp->open("waveform.vcd");

    // STEP 3.3: starting values for simulation
    top->start = 0;
    top->reset = 1;
    top->eval();

    // STEP 4: run verilator simulation
    while (!Verilated::gotFinish()) {

        Cmd cmd;

        // STEP 4.1: read from pipe
        int r = read(pipe_fd, &cmd, sizeof(cmd));

        // STEP 4.2: if data sent from pipe, add data to memory and start algorithm
        if (r == sizeof(cmd)) {
            printf("Received: length=%u\n", cmd.pat_len);
            std::memcpy(top->pattern.data(), cmd.pattern, sizeof(cmd.pattern));
            top->pat_len_in = cmd.pat_len;
            top->start = 1;
            top->reset = 0;
        }

        // STEP 4.3: simulate rising edge of clock
        top->clk = 0;
        top->eval();
        //tfp->dump(main_time);

        top->clk = 1;
        top->eval();
        //tfp->dump(main_time);

        top->start = 0;

        if (top->done) {
            printf("DONE: l=%d, r=%d\n", top->l_out, top->r_out);
        } else if (top->fail) {
            printf("FAIL\n");
        }

        main_time++;

        // STEP 4.4: ensure simulation doesn't run forever 
        // (excluding this will brick verilator, feel free to change time value if needed)
        if (main_time > SIM_LENGTH) {
            printf("Timeout\n");
            tfp->close();
            delete top;
            exit(1);
        }
    }

    //tfp->close();
    delete top;
}
