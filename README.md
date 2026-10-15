# systolic-array-scaling
Parameterized VHDL systolic array for matrix multiplication, evaluating array scaling, input bandwidth limits, and FPGA resource costs.

# Systolic Array Scaling

A parameterized VHDL systolic array for matrix multiplication, used to study how array size and input supply affect performance and FPGA implementation cost.

## Project question

When we add more processing elements, how much performance do we gain if the array can receive only a limited number of input words per cycle?

We compare 2×2, 4×4, and 8×8 output-stationary arrays while computing the same complete 8×8 and 16×16 matrix products. Each array is tested with modeled input limits of 4, 8, and 16 combined words per cycle.

## Evaluation

We use Questa to verify matrix outputs and measure cycles, stalls, useful MACs per cycle, and processing-element utilization. We use Vivado to estimate FPGA resource use and timing for a consistent KV260 target. The input limits are part of our RTL experiment; they are not measurements of physical memory bandwidth.

## Documentation

See [Project Overview](docs/documentation.md) for the dataflow, tiling approach, experiment design, and connection to computer architecture concepts.

## Status

The project is in the design stage. RTL, testbenches, run instructions, and measured results will be added as they are completed.

## Team

- Ozlem Polat
- Thomas Martin
- Keith Kamer

EEL5764 Computer Architecture · University of Florida
