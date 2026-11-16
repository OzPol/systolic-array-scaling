# Five-minute presentation narration

## 1. Systolic Array Scaling Under Input Bandwidth Limits

0:00–0:20

We evaluate how three systolic PE grids respond to input bandwidth limits. The same VHDL dataflow computes complete order-eight and order-sixteen matrix products. The comparison measures compute clocks, useful utilization, complete-product latency, and FPGA resources. Our reference is the two-by-two RTL grid.

## 2. Presentation Outline

0:20–0:30

The presentation follows the original structure: scaling model, implemented architecture, input staging, hardware cost, tile overhead, and conclusions. The added evidence separates computation from serial result delivery.

## 3. Theoretical Framework & Mathematical Predictions

0:30–0:55

Peak capacity grows with P squared, while the largest boundary step requires two P input words. A restricted budget forces partial steps to wait while the grid holds its state. Actual step demand varies during fill and drain, so the exact cycle model also counts that variation and tile capture.

## 4. The VHDL array is a concrete evaluation platform

0:55–1:20

The output-stationary array uses signed sixteen-bit operands and thirty-six-bit accumulators. Skewed inputs align matching operands at each PE. A complete boundary step enables the entire grid. Each output tile streams the full inner dimension, captures all tile results in one clock, and clears the accumulators before the next tile.

## 5. Experimental scope and verification

1:20–1:45

The simulation sweep covers all eighteen parameter combinations, with eight numerical cases each. QuestaSim and independent GHDL sweeps pass all one hundred forty-four cases. Python checks every output and compares observed counters with the analytical schedule. Recorded MAC events check that stalls preserve state and do not perform extra work.

## 6. Finding I: Input staging limits scaling

1:45–2:10

For an order-sixteen product with an eight-word budget, compute clocks are twelve sixteen, three sixty-eight, and one eighty-four. Moving from four-by-four to eight-by-eight doubles performance with four times the PEs. Raising the wide array budget to sixteen removes sixty stalls and reduces its compute time to one twenty-four.

## 7. Measured latency across both workloads

2:10–2:30

These charts show the full budget sweep for both matrix workloads. Larger grids are faster at every measured budget. The gains remain below proportional PE scaling. The order-sixteen product also takes substantially more clocks than order eight. The panels use different vertical ranges so both complete workloads remain visible.

## 8. Useful PE utilization

2:30–2:50

Useful utilization divides the required MAC count by the candidate grid capacity and its measured compute clocks. On eight-by-eight at full supply, utilization is thirty-four point eight percent for the smaller workload and fifty-one point six percent for the larger one. Removing input stalls does not remove fill, drain, or capture overhead.

## 9. Finding II: FPGA resources and timing

2:50–3:20

The saved order-sixteen FPGA implementations use four, sixteen, and sixty-four DSPs. Their LUT counts are seven thousand two sixty, eleven thousand four eighty-eight, and eight thousand one sixty-six. All meet the internal ten-nanosecond setup and hold requirements. The smallest grid produces the most useful work per DSP, while the largest minimizes latency.

## 10. Finding III: Tile overhead on small matrices

3:20–3:45

The measured schedule includes one capture clock per tile. For the large workload on eight-by-eight, sixty-four useful-equivalent clocks, fifty-six fill-and-drain clocks, and four capture clocks sum to one twenty-four. For the small workload, eight plus fourteen plus one gives twenty-three. This capacity accounting explains finite-workload utilization.

## 11. Serial readout and complete-product latency

3:45–4:10

Serial readout adds one clock for every output element. The wide grid needs eighty-seven total clocks for order eight and three eighty for order sixteen. For the latter, a nine-point-eight-one compute speedup becomes three-point-eight-seven for the complete product. The throughput table uses only the timing-qualified order-sixteen implementations.

## 12. Compute speedup and scaling efficiency

4:10–4:30

The dashed reference shows the increase in PE count. Measured compute speedup stays below it, and readout-inclusive speedup is lower again. At full supply, the wide grid reaches forty-seven point eight percent scaling efficiency on order eight and sixty-one point three percent on order sixteen. This isolates the difference between more arithmetic capacity and useful completion rate.

## 13. Evaluation Summary & Conclusions

4:30–4:55

Both hypotheses are supported: limiting input supply reduces the gain from the wider array, and short products spend more capacity on structural overhead. The largest grid is fastest throughout this sweep. The smallest maximizes useful work per DSP. All measured FPGA builds meet internal timing. Serial readout substantially limits the complete-product speedup.
