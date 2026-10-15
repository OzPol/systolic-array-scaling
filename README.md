# Systolic Array Scaling

A parameterized VHDL systolic array for matrix multiplication, used to study how array size and input supply affect performance and FPGA implementation cost.

## Project question

When we add more processing elements, how much performance do we gain if the array can receive only a limited number of input words per cycle?

We compare 2×2, 4×4, and 8×8 output-stationary arrays while computing the same complete 8×8 and 16×16 matrix products. Each array is tested with modeled input limits of 4, 8, and 16 combined words per cycle.

## Evaluation

We use Questa to verify matrix outputs and measure cycles, stalls, useful MACs per cycle, and processing-element utilization. We use Vivado to estimate FPGA resource use and timing for a consistent KV260 target. The input limits are part of our RTL experiment; they are not measurements of physical memory bandwidth.

## Documentation and project files

- [Project Overview](docs/documentation.md) — project motivation, dataflow, tiling, and connection to computer architecture concepts.
- [Architecture](docs/architecture.md) — PE dataflow, arithmetic widths, tiling, input staging, and stalls.
- [Experiment Plan](docs/experiments.md) — correctness checks, metrics, synthesis comparison, and result records.
- [Development Setup](docs/setup.md) — fixed settings and environment details to verify.
- [Configuration Matrix](experiments/configurations.csv) — the 18 planned combinations of matrix size, grid size, and input budget.

## Status

The project is in the design stage. RTL, testbenches, run instructions, and measured results will be added as they are completed.

The Questa and Vivado versions and exact KV260 part will be recorded after the tool environment is checked. The selectable input-budget staging described in the architecture is a proposed implementation choice; we will confirm its RTL interface while building the first 2×2 version.

## Team

- Ozlem Polat
- Thomas Martin
- Keith Kamer

EEL5764 Computer Architecture · University of Florida
