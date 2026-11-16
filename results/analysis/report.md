# Measured scaling analysis

Simulation input: `results/summary_sim.csv`. The analysis validates 18 configurations and 144 passing cases against the cycle model. Hardware values are read from the saved implementation reports.

## Findings

- N=8, B=16: compute latency 176 / 60 / 23 clocks; total latency 240 / 124 / 87 clocks for P=2/4/8.
- N=16, B=16: compute latency 1216 / 368 / 124 clocks; total latency 1472 / 624 / 380 clocks for P=2/4/8.
- N=16/P=8: reducing B=16 to B=4 adds 180 budget stalls and changes compute latency from 124 to 304 clocks.
- The N=16/P=8/B=16 compute speedup is 9.806, with 61.3% scaling efficiency and 51.6% useful PE utilization.
- The largest grid has the lowest compute latency in every measured case.
- The smallest grid has the highest useful throughput per measured DSP for the measured hardware workloads.
- 3/3 implementations meet the constrained internal 10 ns clock target.

## Latency, utilization, and scaling

The [configuration comparison](comparison_table.md) places grid sizes in columns for both workloads at full input supply. The complete budget sweep follows below.

| N | P | B | compute_cycles | total_cycles | stall_cycles | macs_per_cycle | pe_utilization | speedup_vs_2x2 | end_to_end_speedup_vs_2x2 | scaling_efficiency |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 2 | 4 | 176 | 240 | 0 | 2.9091 | 0.7273 | 1.0000 | 1.0000 | 1.0000 |
| 8 | 2 | 8 | 176 | 240 | 0 | 2.9091 | 0.7273 | 1.0000 | 1.0000 | 1.0000 |
| 8 | 2 | 16 | 176 | 240 | 0 | 2.9091 | 0.7273 | 1.0000 | 1.0000 | 1.0000 |
| 8 | 4 | 4 | 88 | 152 | 28 | 5.8182 | 0.3636 | 2.0000 | 1.5789 | 0.5000 |
| 8 | 4 | 8 | 60 | 124 | 0 | 8.5333 | 0.5333 | 2.9333 | 1.9355 | 0.7333 |
| 8 | 4 | 16 | 60 | 124 | 0 | 8.5333 | 0.5333 | 2.9333 | 1.9355 | 0.7333 |
| 8 | 8 | 4 | 44 | 108 | 21 | 11.6364 | 0.1818 | 4.0000 | 2.2222 | 0.2500 |
| 8 | 8 | 8 | 30 | 94 | 7 | 17.0667 | 0.2667 | 5.8667 | 2.5532 | 0.3667 |
| 8 | 8 | 16 | 23 | 87 | 0 | 22.2609 | 0.3478 | 7.6522 | 2.7586 | 0.4783 |
| 16 | 2 | 4 | 1216 | 1472 | 0 | 3.3684 | 0.8421 | 1.0000 | 1.0000 | 1.0000 |
| 16 | 2 | 8 | 1216 | 1472 | 0 | 3.3684 | 0.8421 | 1.0000 | 1.0000 | 1.0000 |
| 16 | 2 | 16 | 1216 | 1472 | 0 | 3.3684 | 0.8421 | 1.0000 | 1.0000 | 1.0000 |
| 16 | 4 | 4 | 608 | 864 | 240 | 6.7368 | 0.4211 | 2.0000 | 1.7037 | 0.5000 |
| 16 | 4 | 8 | 368 | 624 | 0 | 11.1304 | 0.6957 | 3.3043 | 2.3590 | 0.8261 |
| 16 | 4 | 16 | 368 | 624 | 0 | 11.1304 | 0.6957 | 3.3043 | 2.3590 | 0.8261 |
| 16 | 8 | 4 | 304 | 560 | 180 | 13.4737 | 0.2105 | 4.0000 | 2.6286 | 0.2500 |
| 16 | 8 | 8 | 184 | 440 | 60 | 22.2609 | 0.3478 | 6.6087 | 3.3455 | 0.4130 |
| 16 | 8 | 16 | 124 | 380 | 0 | 33.0323 | 0.5161 | 9.8065 | 3.8737 | 0.6129 |

Compute latency includes budget stalls, grid fill/drain, and tile capture. Total latency also includes N² serial-readout clocks. Both speedups use the 2×2 grid at the same matrix size and input budget. Scaling efficiency divides compute speedup by P²/4.

## Implementation cost and timing

| N | P | impl_luts | impl_ffs | impl_dsps | impl_bram_tiles | impl_wns_ns | impl_whs_ns | impl_timing_met |
|---|---|---|---|---|---|---|---|---|
| 16 | 2 | 7260 | 9437 | 4 | 0 | 3.955 | 0.092 | yes |
| 16 | 4 | 11488 | 9505 | 16 | 0 | 3.786 | 0.062 | yes |
| 16 | 8 | 8166 | 10211 | 64 | 0 | 2.176 | 0.057 | yes |

The hardware comparison covers matrix order(s) 16 and all three PE grids. The runtime input budget does not require separate synthesis builds. Matrix size is a synthesis generic, so each P/N pair has its own implementation.

These are out-of-context internal timing results. The reports do not constrain external input/output delays. They do not establish board interface timing or measured board throughput. The result store holds N² signed 36-bit values, corresponding to 2304 bits at N=8 and 9216 bits at N=16. Resource mapping is measured separately for each implementation.

## Throughput at the constrained clock

| N | P | B | modeled_compute_gmac_s_100mhz | modeled_total_gmac_s_100mhz | modeled_compute_gops_100mhz | modeled_products_s_100mhz | macs_per_cycle_per_dsp |
|---|---|---|---|---|---|---|---|
| 16 | 2 | 4 | 0.3368 | 0.2783 | 0.6737 | 67934.7826 | 0.8421 |
| 16 | 2 | 8 | 0.3368 | 0.2783 | 0.6737 | 67934.7826 | 0.8421 |
| 16 | 2 | 16 | 0.3368 | 0.2783 | 0.6737 | 67934.7826 | 0.8421 |
| 16 | 4 | 4 | 0.6737 | 0.4741 | 1.3474 | 115740.7407 | 0.4211 |
| 16 | 4 | 8 | 1.1130 | 0.6564 | 2.2261 | 160256.4103 | 0.6957 |
| 16 | 4 | 16 | 1.1130 | 0.6564 | 2.2261 | 160256.4103 | 0.6957 |
| 16 | 8 | 4 | 1.3474 | 0.7314 | 2.6947 | 178571.4286 | 0.2105 |
| 16 | 8 | 8 | 2.2261 | 0.9309 | 4.4522 | 227272.7273 | 0.3478 |
| 16 | 8 | 16 | 3.3032 | 1.0779 | 6.6065 | 263157.8947 | 0.5161 |

Rates use the common 100 MHz target only when the corresponding implementation meets internal setup and hold timing. One MAC is one multiply plus one addition: GOP/s is twice GMAC/s. Compute rates exclude readout; total rates include serial readout but exclude external transfers and software overhead. These are conditional model-derived rates, not measured board rates.

## Cycle accounting

Each tile advances N+2P−2 times and uses one capture clock. Compute = N³/P² useful-equivalent work + fill/drain + capture + budget stalls. Total = compute + N². Useful MACs overlap fill/drain; the decomposition is capacity accounting rather than a partition of physical execution phases.

## Figures

| Figure | Interpretation |
|---|---|
| `latency.png` | Matrix-specific compute latency across grids and budgets |
| `latency_combined.png` | Both workloads on a shared clock axis |
| `speedup.png` | Compute and readout-inclusive speedup against the matching 2×2 grid |
| `speedup_full_supply.png` | Full-supply comparison for a compact presentation view |
| `utilization.png` | Useful MAC events divided by available PE clocks |
| `cycle_breakdown.png` | Finite-workload overhead and input-budget stalls |
| `fpga_resources.png` | Measured FPGA resource configurations |
| `throughput_vs_dsp.png` | Implemented workloads paired with measured DSP counts |

The [trace views](../visualization/README.md) explain operand wavefronts, grid holds, and tile boundaries using recorded events from all configurations. The report interprets these alongside the cycle and resource measurements.
