# Architecture

## Purpose and scope

This document describes the implemented output-stationary VHDL matrix multiplier. The same design generates square PE grids of size $P=2,4,8$ and computes complete $N\times N$ products for $N=8,16$. All configurations use signed 16-bit input words. The RTL includes input staging, a tiled computation controller, and serial result readout. The KV260 is a Vivado synthesis target; no physical board or external DRAM controller is in scope.

## Dataflow

For output tile $(r_0,c_0)$, PE $(r,c)$ accumulates $C[r_0+r,c_0+c]$ for $0\le r,c<P$. Values from $A$ enter at the left and move right; values from $B$ enter at the top and move down. Matching operands must carry the same inner index $k$ when they meet:

$$
C[r_0+r,c_0+c]=\sum_{k=0}^{N-1}A[r_0+r,k]B[k,c_0+c].
$$

One conventional skew schedule introduces $A[r_0+r,k]$ and $B[k,c_0+c]$ on boundary step $t=k+r$ and $t=k+c$, respectively. Internal register movement then brings both operands to PE $(r,c)$ for the same MAC. Valid signals accompany operands so fill and drain cycles do not create spurious MACs. Operands presented during RUN are consumed at the rising edge when the stager is complete. Registered links move one PE per enabled rising edge; all grid registers hold on an incomplete step.

## Numeric representation

| Item | Implemented definition |
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

The tile controller, result store, serial readout, and optional instrumentation are implemented together in `rtl/systolic_top.vhd`; the other modules have matching RTL files. Shared widths and array types live in `rtl/sys_pkg.vhd`.

## Tiling

The controller visits tiles in row-major order. Each tile streams the **full inner dimension $N$** and completes $P^2N$ useful MACs before its outputs are stored. There is no cross-tile partial-sum reuse. The number of output tiles is $(N/P)^2$: 16/4/1 tiles for $N=8$, and 64/16/4 tiles for $N=16$, at $P=2/4/8$ respectively. All sizes are divisible by each chosen $P$, so edge padding is unnecessary.

The next tile must not clear PE state until the preceding tile's last MAC has completed and its results have been captured. Serial readout occurs after the complete product is available; tile capture and transition remain part of compute latency.

## Input budget and stalls

The experiment selects a budget $B\in\{4,8,16\}$ **combined $A/B$ words per clock**. A full boundary step can request at most $2P$ words, although fill and drain steps can request fewer. The stager accumulates that step's valid words; the grid advances exactly once when the step is complete. While staging is incomplete, every PE's accumulator, forwarded data, and valid state hold. During a drain step with no new boundary words, the grid advances normally.

The implemented interface uses a runtime budget setting in synthesizable staging logic, with the same maximum-width input interface for all three budget settings. The testbench supplies operands and also checks that the RTL enforces $B$ and holds state correctly. This allows Vivado to compare **three grid implementations** while the simulation varies $B$ on each implementation. The input budget is a modeled interface limit, not a measured KV260 memory rate.

At full supply ($B\ge 2P$), a complete incoming step should advance without an artificial extra staging cycle. If an implementation requires an additional clock even at full supply, that latency must be documented and included consistently; it must not be silently attributed to input bandwidth.

## Synthesis boundary

Vivado will synthesize the grid, controller, staging logic, result storage, and serial output path at the same 10 ns constraint and exact KV260 target part. The testbench and software reference model are excluded. The top is `systolic_top`, with `P`, `N`, and `INSTR` generics; the recorded part is `xck26-sfvc784-2LV-c`. `INSTR=false` removes measurement counters for synthesis. See `setup.md` for provenance and timing scope. Resource and timing reports must name the synthesis stage used; timing slack after implementation is reported where feasible.

## Verification gates

1. Verify one PE's signed MAC, valid forwarding, clear, and stall hold.
2. Verify a 2×2 output tile with known values and no stalls.
3. Verify complete 8×8 and 16×16 products through tiling.
4. Verify budget staging, stalls, signed extremes, and fixed-seed random inputs.
5. Repeat the same correctness checks at $P=4$ and $P=8$ before collecting performance data.

The proposal does not include an alternate dataflow, processor interface, DRAM controller, CPU baseline, power measurement, or physical FPGA run.


## Implemented controller and clock convention

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> RUN: start
    RUN --> RUN: incomplete boundary step
    RUN --> CAPTURE: last enabled step
    CAPTURE --> RUN: more tiles
    CAPTURE --> READOUT: last tile stored
    READOUT --> DONE: last serial word
    DONE --> RUN: start
```

`T_STEPS = N + 2P - 2`. RUN includes zero-input drain steps, which advance without budget stalls. CAPTURE copies the preceding tile's completed accumulators and clears the grid at the same rising edge. Every tile, including the last, uses one capture clock. READOUT transfers N² row-major words, one per rising edge, with `out_valid=1`; there is no output-ready/backpressure input. A consumer must accept every word during that interval. `done` remains high until a new start or reset.

The input interface publishes `tile_row`, `tile_col`, `step_t`, `a_need`, and `b_need`. The producer supplies the requested boundary values and holds the logical step's values while staging proceeds. `stage_got` exposes accepted words only when instrumentation is enabled; synthesis-mode producers must not depend on that debug signal. Runtime budget is assumed positive and stable for the intended experiment; the supported sweep values are 4, 8, and 16.

Simulation exposes `cnt_compute`, `cnt_total`, `cnt_stall`, `cnt_adv`, `cnt_cap`, and per-PE `mac_fire`. Reset and clear suppress useful MAC events. The testbench observes result events and elapsed transaction clocks independently, compares counters with those observations and the separate formula, and counts only actual useful MAC fires.

## Result storage and synthesis evidence

Each capture writes P² output elements into the N²-element store. This multiwrite structure mapped to registers in the existing P=2 Vivado run, with 9,216 storage bits at N=16. Changing it to BRAM would change the design and capture schedule; it is not a prerequisite for the proposed study. The measured zero-BRAM outcome must be retained honestly.

The P=2 reports constrain internal paths at 10 ns but leave external input/output delays unspecified. The synthesis-mode equivalence regression compares requests, values, and readout/completion timing against the instrumented design. It is RTL regression evidence, not a routed-netlist equivalence proof.
