# Experiment Plan

## Research question

For a fixed complete matrix multiplication, how do PE grid size and a modeled input-supply rate change cycle count, useful throughput, utilization, and FPGA cost?

The 2Ã—2 grid is the architectural baseline. We compare it with 4Ã—4 and 8Ã—8 grids under the same matrix inputs and input budget. We do not presume that the largest grid provides proportional speedup.

## Core sweep

| Variable | Values | Held constant within a comparison |
|---|---|---|
| Grid dimension $P$ | 2, 4, 8 | Same output-stationary RTL and PE arithmetic |
| Matrix dimension $N$ | 8, 16 | Same complete $N\times N$ product across grids |
| Combined input budget $B$ | 4, 8, 16 words/clock | Same RTL budget rule and test vectors |

The Cartesian product is **18 core configurations**, listed in [`configurations.csv`](configurations.csv). Each uses signed 16-bit operands and a 36-bit exact accumulator. For each $(N,B)$ pair, compare $P=4,8$ with $P=2$ using identical matrix contents. Directed correctness cases include zero, identity, signed extremes, and mixed signs; a fixed-seed random case supplies the principal repeatable performance workload. Record the seed and input-file checksum with every result. These tests do not add architectural configurations to the 18-row sweep.

## Measurement boundaries

- **Compute latency:** inclusive clock count from the first accepted input word of a complete product to the capture of the last completed output tile. It includes input staging, stalls, fill/drain, and tile transitions. It excludes subsequent serial readout.
- **Total latency:** clock count over the same start event through the final output word transferred over the serial result interface. Report this separately from compute latency.
- **Useful MACs:** count only PE multiply-accumulate events that contribute to the correct $N\times N$ result; the expected count is $N^3$ for every configuration.
- **Stall cycles:** count clocks during computation in which a pending boundary step is incomplete due to the modeled input budget and the grid does not advance. Keep fill/drain and tile-transition clocks distinguishable from budget stalls.
- **PE utilization:** useful MACs divided by $P^2\times\text{compute cycles}$.
- **Useful throughput:** $N^3/\text{compute cycles}$ in MACs per cycle.
- **Compute speedup:** the $P=2$ compute cycles divided by the candidate's compute cycles at the same $(N,B)$ and identical matrix input.
- **Scaling efficiency:** compute speedup divided by $P^2/4$, the PE-count increase relative to the 2Ã—2 baseline.

Counter values must agree with the testbench event log. A run is valid only if every output matches the independent full-width software reference, the MAC count is $N^3$, and no operand is lost or counted twice.

## FPGA evaluation

Synthesize the same top-level design at $P=2,4,8$ with the runtime budget option and a 10 ns constraint. Use the same KV260 part and synthesis settings for all three. Record LUTs, flip-flops, DSPs, block RAM, and the report stage for each value. Record timing slack after implementation where feasible. A zero BRAM count is a valid observation; it must not be inferred from the source code alone.

Compare useful throughput per DSP only after confirming the DSP count and simulation workload. Convert cycles to elapsed time or MACs/second at the constrained clock **only for implementations that meet timing**. Report a timing or resource failure directly. Do not infer power or energy from FPGA resource counts.

## Analysis and records

Produce (1) compute latency and PE utilization versus $P$, faceted by $N$ and $B$, and (2) useful throughput versus DSP use. Explain whether a difference is consistent with budget stalls, pipeline fill/drain, tile transitions, or resource/timing cost. The budget represents an RTL interface rule, not physical KV260 DRAM bandwidth.

For each run, retain at least: configuration ID, input seed/checksum, source commit, tool version, test result, compute and readout cycles, useful MACs, stall cycles, synthesis target and stage, and any applicable resource/timing figures. Commit reviewed summary tables and scripts; keep bulky generated directories out of version control.
