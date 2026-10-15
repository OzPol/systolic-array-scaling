# Architecture

## Purpose and scope

This document describes the planned output-stationary VHDL matrix multiplier. The same design generates square PE grids of size $P=2,4,8$ and computes complete $N\times N$ products for $N=8,16$. All configurations use signed 16-bit input words. The RTL includes input staging, a tiled computation controller, and serial result readout. The KV260 is a Vivado synthesis target; no physical board or external DRAM controller is in scope.

## Dataflow

For output tile $(r_0,c_0)$, PE $(r,c)$ accumulates $C[r_0+r,c_0+c]$ for $0\le r,c<P$. Values from $A$ enter at the left and move right; values from $B$ enter at the top and move down. Matching operands must carry the same inner index $k$ when they meet:

$$
C[r_0+r,c_0+c]=\sum_{k=0}^{N-1}A[r_0+r,k]B[k,c_0+c].
$$

One conventional skew schedule introduces $A[r_0+r,k]$ and $B[k,c_0+c]$ on boundary step $t=k+r$ and $t=k+c$, respectively. Internal register movement then brings both operands to PE $(r,c)$ for the same MAC. Valid signals accompany operands so fill and drain cycles do not create spurious MACs. The exact clock-edge convention will be fixed alongside the first PE testbench and used consistently in the counters.

## Numeric representation

| Item | Planned definition |
|---|---|
| Inputs | Signed 16-bit two's-complement $A$ and $B$ |
| Product | Signed 32-bit result before extension |
| PE accumulator and stored output | Signed 36-bit value |
| Maximum inner dimension | 16 terms per output |

Thirty-six signed bits preserve the exact sum for every 16-term dot product of signed 16-bit operands, including $(-32768)\times(-32768)$ repeated 16 times. The testbench compares full-width results without truncation.

## Logical modules

| Module | Responsibility |
|---|---|
| `pe` | Register and forward valid $A/B$ values; perform one useful signed MAC when a matching pair is valid; clear the accumulator at a tile boundary; hold all state on a grid stall. |
| `systolic_array` | Generate a $P\times P$ grid from the same PE; distribute boundary operands and propagate valid/stall control. |
| `input_stager` | Collect all valid words for the next boundary step subject to the selected budget; deliver one complete step to the grid without dropping or duplicating words. |
| `tile_controller` | Enumerate output tiles and inner indices, clear at the correct boundary, wait for in-flight work to finish, and store each completed tile at its global output coordinates. |
| Result storage/readout | Retain the complete $N\times N$ output and expose its elements serially after computation. Readout time is counted separately. |

These are logical responsibilities. RTL files may be combined or split after the first working 2Ã—2 implementation; the behavior and measurement definitions remain the same.

## Tiling

The controller visits tiles in row-major order. Each tile streams the **full inner dimension $N$** and completes $P^2N$ useful MACs before its outputs are stored. There is no cross-tile partial-sum reuse. The number of output tiles is $(N/P)^2$: 16/4/1 tiles for $N=8$, and 64/16/4 tiles for $N=16$, at $P=2/4/8$ respectively. All sizes are divisible by each chosen $P$, so edge padding is unnecessary.

The next tile must not clear PE state until the preceding tile's last MAC has completed and its results have been captured. Serial readout occurs after the complete product is available; tile capture and transition remain part of compute latency.

## Input budget and stalls

The experiment selects a budget $B\in\{4,8,16\}$ **combined $A/B$ words per clock**. A full boundary step can request at most $2P$ words, although fill and drain steps can request fewer. The stager accumulates that step's valid words; the grid advances exactly once when the step is complete. While staging is incomplete, every PE's accumulator, forwarded data, and valid state hold. During a drain step with no new boundary words, the grid advances normally.

The working design choice is a runtime budget setting in synthesizable staging logic, with the same maximum-width input interface for all three budget settings. The testbench supplies operands and also checks that the RTL enforces $B$ and holds state correctly. This lets Vivado compare **three grid implementations** while the simulation varies $B$ on each implementation. The input budget is a modeled interface limit, not a measured KV260 memory rate.

At full supply ($B\ge 2P$), a complete incoming step should advance without an artificial extra staging cycle. If an implementation requires an additional clock even at full supply, that latency must be documented and included consistently; it must not be silently attributed to input bandwidth.

## Synthesis boundary

Vivado will synthesize the grid, controller, staging logic, result storage, and serial output path at the same 10 ns constraint and exact KV260 target part. The testbench and software reference model are excluded. The precise top-level port map and part number will be recorded in `setup.md` once the tool environment is checked. Resource and timing reports must name the synthesis stage used; timing slack after implementation is reported where feasible.

## Verification gates

1. Verify one PE's signed MAC, valid forwarding, clear, and stall hold.
2. Verify a 2Ã—2 output tile with known values and no stalls.
3. Verify complete 8Ã—8 and 16Ã—16 products through tiling.
4. Verify budget staging, stalls, signed extremes, and fixed-seed random inputs.
5. Repeat the same correctness checks at $P=4$ and $P=8$ before collecting performance data.

The proposal does not include an alternate dataflow, processor interface, DRAM controller, CPU baseline, power measurement, or physical FPGA run.
