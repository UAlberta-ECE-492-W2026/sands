#include "Vtop.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <cstdlib>
#include <iostream>
#include <cstdio>
#include <string>
#include <cstring>
#include <deque>
#include <map>
#include <cerrno>
#include <sys/stat.h>

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

struct Result {
    bool done;
    uint32_t l;
    uint32_t r;
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
    if (mkfifo(file, 0600) != 0) {
        perror("mkfifo");
        return 1;
    }

    // STEP 3: setup verilator simulation
    // STEP 3.1: innitialize verilator sim and memory pipe
    Verilated::commandArgs(argc, argv);
    auto* top = new Vtop;

    int pipe_fd = open("mem_pipe", O_RDONLY);
    if (pipe_fd < 0) {
        perror("open");
        return 1;
    }
    int flags = fcntl(pipe_fd, F_GETFL, 0);
    if (flags < 0 || fcntl(pipe_fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        perror("fcntl");
        return 1;
    }
    std::deque<Cmd> pending;
    std::map<uint32_t, Result> completed;
    std::map<uint32_t, vluint64_t> submit_times;
    bool input_closed = false;
    const bool benchmark_mode = std::getenv("FMINDEX_BENCHMARK") != nullptr;
    uint32_t next_submit_id = 0;
    uint32_t next_print_id = 0;
    bool batch_started = false;
    vluint64_t batch_start_time = 0;

    // STEP 3.2: innitialize waveform
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC; 
    //top->trace(tfp, 99);
    //tfp->open("waveform.vcd");

    // STEP 3.3: starting values for simulation
    top->query_valid = 0;
    top->query_id = 0;
    top->reset = 1;
    top->eval();
    top->reset = 0;

    // STEP 4: run verilator simulation
    while (!Verilated::gotFinish()) {

        // STEP 4.1: read from pipe
        if (!input_closed) {
            while (true) {
                Cmd cmd;
                int r = read(pipe_fd, &cmd, sizeof(cmd));
                if (r == static_cast<int>(sizeof(cmd))) {
                    pending.push_back(cmd);
                } else if (r == 0) {
                    input_closed = true;
                    break;
                } else if (r < 0 && errno == EAGAIN) {
                    break;
                } else if (r > 0) {
                    printf("Short read from pipe: %d bytes\n", r);
                    break;
                } else {
                    perror("read");
                    break;
                }
            }
        }

        if (!pending.empty() && top->query_ready) {
            Cmd cmd = pending.front();
            pending.pop_front();
            printf("Received: length=%u\n", cmd.pat_len);
            std::memcpy(top->query_pattern.data(), cmd.pattern, sizeof(cmd.pattern));
            top->query_pat_len = cmd.pat_len;
            top->query_id = next_submit_id;
            top->query_valid = 1;
            if (!batch_started) {
                batch_started = true;
                batch_start_time = main_time;
            }
            submit_times[next_submit_id] = main_time;
            next_submit_id++;
        } else {
            top->query_valid = 0;
        }

        // STEP 4.2: simulate rising edge of clock
        top->clk = 0;
        top->eval();
        //tfp->dump(main_time);

        top->clk = 1;
        top->eval();
        //tfp->dump(main_time);

        top->query_valid = 0;

        if (top->result_valid) {
            completed.emplace(
                top->result_query_id,
                Result{
                    top->result_done,
                    static_cast<uint32_t>(top->l_out),
                    static_cast<uint32_t>(top->r_out),
                }
            );
            if (benchmark_mode) {
                auto it = submit_times.find(top->result_query_id);
                if (it != submit_times.end()) {
                    printf("CYCLES\t%llu\n", static_cast<unsigned long long>(main_time - it->second + 1));
                }
            }
        }

        while (true) {
            auto it = completed.find(next_print_id);
            if (it == completed.end()) {
                break;
            }
            if (it->second.done) {
                printf("DONE: l=%u, r=%u\n", it->second.l, it->second.r);
            } else {
                printf("FAIL\n");
            }
            completed.erase(it);
            next_print_id++;
        }

        if (input_closed && pending.empty() && next_print_id == next_submit_id && completed.empty()) {
            if (benchmark_mode && batch_started) {
                printf("BATCH_CYCLES\t%llu\n", static_cast<unsigned long long>(main_time - batch_start_time + 1));
            }
            break;
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
    return 0;
}
