# Five-minute speaking outline

Use `slides.pdf` for the current data values. The allocation below totals five minutes; rehearse the actual recording against that limit.

| Slide | Time | Speaking points |
|---|---|---|
| 1. Research question | 0:00–0:20 | Does increasing a systolic grid deliver proportional improvement when operand supply is limited? Compare complete products and implementation cost. |
| 2. Architecture | 0:20–1:00 | Explain output-stationary accumulation, staggered inputs, and global holds. Each output tile streams the full inner dimension. Store every tile, then serialize the complete result. |
| 3. Verification | 1:00–1:35 | Describe the complete configuration sweep and full-width software reference. The original sweep and independent GHDL verification agree. All three order-16 implementations meet internal timing; external I/O delays remain outside the experiment. |
| 4. Compute latency | 1:35–2:10 | Read the full-supply order-16 latency values from the slide. Larger grids reduce latency for both workloads. Restricted input supply penalizes the wider grids more strongly. |
| 5. Cycle accounting | 2:10–2:45 | Separate supply stalls from fill/drain and capture overhead. Useful-equivalent work is capacity accounting: useful MACs also occur during fill/drain. Full supply does not eliminate finite-workload overhead. |
| 6. Serial readout | 2:45–3:20 | Compare compute clocks with total clocks. The result interface emits one word per clock, so output delivery erodes the compute gain. Explain that clock-based GMAC/s is conditional on internal timing and excludes external transfers. |
| 7. Scaling | 3:20–3:50 | Speedup uses the matching 2×2 RTL configuration as reference. Gray lines show PE-count scaling. Both input supply and serial readout widen the gap from proportional scaling. No CPU-relative speedup is claimed. |
| 8. FPGA cost | 3:50–4:30 | DSP counts follow PE count. Matrix size also changes result storage and selection logic. Read each resource value from its matching implementation. The largest grid minimizes clocks; the smallest provides the highest useful throughput per DSP in this sweep. |
| 9. Findings | 4:30–5:00 | State the measured trade-off. The reported FPGA results cover the three order-16 builds. LUT use peaks at the 4×4 grid, while DSP count follows PE count. Board integration, physical memory supply, and power measurements are future extensions. |

The nine-slide deck is the current technical presentation. The earlier video outline remains unchanged in `deliverables/video/outline.md`.
