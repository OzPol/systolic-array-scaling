# Five-minute project video outline

The course guideline requires a five-minute recorded architecture/findings presentation. The storyboard below allocates the five minutes across architecture, verification, and results. The provided guideline does not require every team member to narrate. Divide speaking and recording duties within the team as appropriate.

| Time | Visual | Main point |
|---|---|---|
| 0:00–0:30 | Title and research question | Does adding PEs deliver proportional speedup under limited operand supply? |
| 0:30–1:15 | PE dataflow and tiled-controller diagram | Output-stationary MACs, staggered operands, full-inner-dimension tiling |
| 1:15–2:00 | Configuration/verification table | 18 configurations; 144 passing cases; full-width reference; modeled budget |
| 2:00–3:15 | `results/analysis/latency.png` | 1216/368/124 at N=16/B=16; input restriction raises P=8 to 304 |
| 3:15–4:10 | `cycle_breakdown.png` and utilization | Separate budget stalls from finite-workload overhead; useful work overlaps fill/drain |
| 4:10–4:45 | Actual FPGA table and DSP plot | Report only measured designs; explain internal timing scope and result storage |
| 4:45–5:00 | Conclusion and limitations | Larger grids help, with sublinear scaling |

## Narration draft

We built a small matrix-multiplication accelerator and asked a computer architecture question: if we add more arithmetic units, how much performance do we gain when the input interface can deliver only a limited number of operands per clock? We compare grid size, useful performance, and FPGA implementation cost while holding the complete workload constant.

The implementation is an output-stationary systolic array in VHDL. Each processing element receives one A value from the left and one B value from above. It multiplies matching valid operands, accumulates a 36-bit result, and forwards the operands to neighboring elements. A single processing-element design generates 2-by-2, 4-by-4, and 8-by-8 grids. Boundary operands are staggered so the same inner-product index arrives together.

When a matrix is larger than the grid, the controller divides the output into tiles. Each tile still streams the full inner dimension. We store its completed results, clear the grid, and continue to the next tile. After the complete product is available, results are read serially. Compute latency includes tile transitions and stalls; serial readout is reported separately.

We vary three grid sizes, two full matrix orders, and three combined input budgets: four, eight, and sixteen words per clock. That gives eighteen architectural configurations. This budget is an RTL interface model, not measured physical DRAM bandwidth. A step waits until all its required boundary operands have been staged. During that wait, the entire grid holds its state.

Correctness comes first. Each configuration passes eight directed or fixed-seed cases, including zero, identity, mixed signs, and signed extremes. Every output is compared with an independent Python reference at full width. We also require the exact cube of the matrix order in useful MACs and check measured clock counts against independent observations and formulas. The original Questa sweep and independent GHDL rerun both pass all 144 cases. Additional directed tests cover the processing element, staging, and synthesis-mode instrumentation setting.

For order-sixteen matrices at full supply, compute latency falls from 1216 clocks for the 2-by-2 to 368 for the 4-by-4 and 124 for the 8-by-8. The largest grid is about 9.8 times faster than the baseline, using sixteen times as many processing elements. The improvement is substantial, but less than ideal scaling.

The input limit has a measurable cost. On the 8-by-8 grid, an eight-word budget adds sixty stalls, raising latency to 184 clocks. A four-word budget adds 180 stalls, raising it to 304. The useful work and enabled-step schedule are unchanged; the extra clocks come from waiting for boundary operands.

Input supply is not the only source of lost utilization. At full supply, the order-sixteen product on the 8-by-8 has sixty-four useful-equivalent clocks, fifty-six fill-and-drain clocks, and four capture clocks. This is capacity-normalized accounting, not a claim that no useful MACs occur during filling and draining. Serial readout also matters: for the smallest fully supplied product, it adds sixty-four clocks to twenty-three compute clocks.

All three FPGA implementations meet the constrained internal ten-nanosecond target. The 2-by-2, 4-by-4, and 8-by-8 use four, sixteen, and sixty-four DSPs, with positive setup slack of 3.955, 3.786, and 2.176 nanoseconds. All use zero block RAM; the complete result matrix is stored in registers. At full supply, useful throughput per DSP falls from 0.842 to 0.696 to 0.516 MACs per clock. The 8-by-8 gives the shortest compute latency, while the 2-by-2 uses its arithmetic resources most efficiently for these workloads. LUT use is not monotonic, so we report the measured implementation counts directly. Timing covers constrained internal paths; board I/O delays are not specified.

Our conclusion is that adding processing elements helps in every tested configuration, but input supply and finite-workload overhead reduce scaling efficiency. The larger arrays remain faster throughout this sweep. All three measured hardware configurations are included in the resource and throughput comparison.

## Before recording

- Use the completed P=2/P=4/P=8 FPGA table and the refreshed throughput-per-DSP figures.
- Use the latest figures from the analysis module.
- Rehearse and trim to five minutes; the draft timing is an allocation, not a measured recording duration.
- Show the architecture and findings. Reading terminal output alone does not communicate the architectural result.
- Review the recording for legible charts and intelligible audio, then follow the single-submission Canvas instructions.
