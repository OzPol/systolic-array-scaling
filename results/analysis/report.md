# Measured scaling analysis

Simulation input: `results/verification/ghdl_sim_results.csv`. Every configuration is checked for eight passing cases,
exact N^3 useful MACs, data-independent counters, complete readout, and agreement with a separate cycle model.
The cycle model cross-checks the recorded simulation counts.

## Findings

- At N=16, B=16, compute cycles are 1216 / 368 / 124 for P=2/4/8. The 8×8 achieves 9.806× speedup with 16× as many PEs: 61.3% scaling efficiency.
- At N=16, P=8, lowering B from 16 to 8 adds 60 stalls (124 → 184 cycles); lowering it to 4 adds 180 stalls (124 → 304 cycles). B=4 costs 2.452× the fully supplied compute latency.
- At B=4, P=8 is still 2× faster than P=4 for both matrix sizes. The input limit reduces the benefit of scaling; these measurements do not establish a point where a larger array stops helping.
- At full supply, N=16/P=8 has 64 useful-equivalent cycles, 56 fill/drain cycles, and 4 capture cycles. Thus 51.6% PE utilization is explained by the finite workload and per-tile schedule even without budget stalls.
- For N=8/P=8/B=16, compute takes 23 clocks but serial readout adds 64. Compute speedup and end-to-end speedup answer different questions; readout is identical across P for a given N.

## Cycle accounting

For each tile, the grid advances N+2P−2 times and uses one capture clock.
For boundary step t, w(t)=2·count{i: 0≤t−i<N, 0≤i<P} words are needed.
Stalls are sum(max(0, ceil(w(t)/B)−1)) over all steps and tiles.
Compute = useful-equivalent + fill/drain + capture + stalls; total = compute + N² readout.

“Useful-equivalent” is N³/P², the capacity-normalized MAC work. This is an accounting decomposition,
not a claim that useful MACs happen exclusively in a separate block of clocks. Useful MACs overlap fill/drain.

| N | P | B | compute_cycles | stall_cycles | useful_equivalent_cycles | fill_drain_cycles | capture_cycles | pe_utilization | speedup_vs_2x2 |
|---|---|---|---|---|---|---|---|---|---|
| 8 | 2 | 4 | 176 | 0 | 128 | 32 | 16 | 0.7273 | 1.0000 |
| 8 | 2 | 8 | 176 | 0 | 128 | 32 | 16 | 0.7273 | 1.0000 |
| 8 | 2 | 16 | 176 | 0 | 128 | 32 | 16 | 0.7273 | 1.0000 |
| 8 | 4 | 4 | 88 | 28 | 32 | 24 | 4 | 0.3636 | 2.0000 |
| 8 | 4 | 8 | 60 | 0 | 32 | 24 | 4 | 0.5333 | 2.9333 |
| 8 | 4 | 16 | 60 | 0 | 32 | 24 | 4 | 0.5333 | 2.9333 |
| 8 | 8 | 4 | 44 | 21 | 8 | 14 | 1 | 0.1818 | 4.0000 |
| 8 | 8 | 8 | 30 | 7 | 8 | 14 | 1 | 0.2667 | 5.8667 |
| 8 | 8 | 16 | 23 | 0 | 8 | 14 | 1 | 0.3478 | 7.6522 |
| 16 | 2 | 4 | 1216 | 0 | 1024 | 128 | 64 | 0.8421 | 1.0000 |
| 16 | 2 | 8 | 1216 | 0 | 1024 | 128 | 64 | 0.8421 | 1.0000 |
| 16 | 2 | 16 | 1216 | 0 | 1024 | 128 | 64 | 0.8421 | 1.0000 |
| 16 | 4 | 4 | 608 | 240 | 256 | 96 | 16 | 0.4211 | 2.0000 |
| 16 | 4 | 8 | 368 | 0 | 256 | 96 | 16 | 0.6957 | 3.3043 |
| 16 | 4 | 16 | 368 | 0 | 256 | 96 | 16 | 0.6957 | 3.3043 |
| 16 | 8 | 4 | 304 | 180 | 64 | 56 | 4 | 0.2105 | 4.0000 |
| 16 | 8 | 8 | 184 | 60 | 64 | 56 | 4 | 0.3478 | 6.6087 |
| 16 | 8 | 16 | 124 | 0 | 64 | 56 | 4 | 0.5161 | 9.8065 |

## FPGA evidence

| P | N | impl_luts | impl_ffs | impl_dsps | impl_bram_tiles | impl_wns_ns | impl_timing_met |
|---|---|---|---|---|---|---|---|
| 2 | 16 | 7260 | 9437 | 4 | 0 | 3.955 | yes |
| 4 | 16 | 11488 | 9505 | 16 | 0 | 3.786 | yes |
| 8 | 16 | 8166 | 10211 | 64 | 0 | 2.176 | yes |

Missing N=16 hardware configurations: none.
All three N=16 grid implementations have measured post-route evidence.
Thomas Martin produced the three Vivado 2025.2.1 runs using the same part, 10 ns clock,
INSTR=false setting, and out-of-context synth/opt/place/route flow. His reports and console logs are retained unchanged.
The evidence predates the analysis follow-up: the only RTL change is a reset/clear mask on an activity signal
that is unused with INSTR=false. The datapath, controller, stager, and clock constraint are unchanged.
The out-of-context reports leave external input/output delays unspecified (71/63 ports at P=2,
135/67 at P=4, and 263/74 at P=8). No unconstrained internal endpoints are reported.
The reported slack covers the constrained internal paths; board I/O timing is a separate implementation step.
The registered result store uses 9216 bits for N=16 and dominates FF use; zero BRAM is a measured mapping outcome.
The study compares RTL cycle behavior and FPGA implementation cost.

## Throughput per measured DSP

| P | B | compute_cycles | impl_dsps | macs_per_cycle | macs_per_cycle_per_dsp |
|---|---|---|---|---|---|
| 2 | 4 | 1216 | 4 | 3.3684 | 0.8421 |
| 2 | 8 | 1216 | 4 | 3.3684 | 0.8421 |
| 2 | 16 | 1216 | 4 | 3.3684 | 0.8421 |
| 4 | 4 | 608 | 16 | 6.7368 | 0.4211 |
| 4 | 8 | 368 | 16 | 11.1304 | 0.6957 |
| 4 | 16 | 368 | 16 | 11.1304 | 0.6957 |
| 8 | 4 | 304 | 64 | 13.4737 | 0.2105 |
| 8 | 8 | 184 | 64 | 22.2609 | 0.3478 |
| 8 | 16 | 124 | 64 | 33.0323 | 0.5161 |

These ratios pair simulated complete-product throughput with actual post-route DSP counts.
They exclude serial readout, external data transfer, and software overhead. They are not board measurements.
At N=16/B=16, the measured four-, sixteen-, and sixty-four-DSP designs deliver 3.368, 11.130,
and 33.032 useful MACs per compute clock: 0.842, 0.696, and 0.516 MACs per clock per DSP.
The largest array is fastest, while the smallest has the highest useful throughput per DSP for these workloads.
LUT usage is not monotonic: the 4x4 uses 11,488 LUTs and the 8x8 uses 8,166. Retain this measured result;
resource mapping and control/storage logic cannot be inferred from PE count alone.

## Figures

- `latency.png` / `.svg`: compute latency by grid, workload, and input budget.
- `utilization.png` / `.svg`: useful PE utilization with the same comparisons.
- `cycle_breakdown.png` / `.svg`: useful-equivalent work, fill/drain, capture, and budget stalls.
- `throughput_vs_dsp.png` / `.svg`: throughput paired with the collected FPGA DSP counts.
- `fpga_resources.png` / `.svg`: post-route LUTs, FFs, DSPs, and BRAM for all measured grids.
- `hardware_metrics.csv`: simulated throughput and useful throughput per measured DSP for each N=16 grid/budget pair.
- [8×8 matrix activity atlas](../visualization/activity_matrix08.png): all nine grid/budget combinations.
- [16×16 matrix activity atlas](../visualization/activity_matrix16.png): all nine grid/budget combinations.

Each atlas has PE grids 2×2, 4×4, and 8×8 down the rows and budgets 4, 8, and 16 across the columns. Color shows useful MACs per PE per clock in four-clock bins. Together they cover all 18 configurations.
