# sands

SoC-Accelerated, Networked DNA Sequencing

## Setup

Orca, Buoy, and Port share a single repository-level dependency set. Create one
virtual environment at the repo root and install the base and developer
requirements:

```bash
$ ./x.sh setup-venv
$ source venv/bin/activate  # use `venv/Scripts/activate` on Windows
```

Each service README (see `orca/README.md`, `buoy/README.md`, and
`port/README.md`) still covers how to run that server once the shared
environment is active.

## Running and Testing

Use the main task runner, `x.sh`:

```bash
$ ./x.sh setup-venv  # Setup your local venv
$ ./x.sh tests       # Run all tests
$ ./x.sh check       # Typecheck all code
$ ./x.sh run-local   # Run locally (with docker-compose)
$ ./x.sh help        # Print this message

# Hardware Simulation
$ ./x.sh index-seq 1000 index.bin  # Generate a sequence and build an SV index
$ ./x.sh sim index.bin             # Run the SystemVerilog FM-index simulation (requires verliator)
```
