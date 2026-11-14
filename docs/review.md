# Contribution and technical review

## Baseline attribution

Thomas Martin's branch was merged **before** Oz's follow-up work, through [PR #1](https://github.com/OzPol/systolic-array-scaling/pull/1), merge `86bbfb9`. The original commits retain their hashes and author. Follow-up commits were merged separately in [PR #2](https://github.com/OzPol/systolic-array-scaling/pull/2). Thomas's remaining P=4/P=8 evidence was retained in [PR #3](https://github.com/OzPol/systolic-array-scaling/pull/3).

| Commit | Author | Substantive contribution |
|---|---|---|
| `2269d2c` | Thomas Martin | Documentation links, generated-file exclusions, tool/board records, project PDFs |
| `3459a9f` | Thomas Martin | Shared VHDL package; PE; generated array; budget stager; tiled controller/result storage/readout; Python reference/vector generation; self-checking testbench; simulator and Vivado scripts; 144 recorded passing cases; P=2 post-route reports |
| `d771fc7` | Thomas Martin | Explanatory RTL/testbench comments, with the recorded Claude co-author retained |
| `fcf8247`, `87b297d` | Thomas Martin | Completed P=4/N=16 and P=8/N=16 synthesis and post-route utilization/timing reports and logs |
| Earlier main-branch commits | Ozlem Polat | Project definition, architectural specification, experiment plan, 18-row configuration matrix, proposal/project documentation |

**Assessment:** Thomas's contribution is substantial. It provides most of the executable baseline implementation and original measurement pipeline, not a cosmetic addition or isolated helper. His November 10 message accurately describes the branch contents and the remaining P=4/P=8 Vivado work. The second November commit is primarily explanatory comments; the first contains the substantive implementation.

Most added lines are vectors, logs, and reports, so line counts would overstate the implementation size. The functional contribution is substantial. Keith has no commits in the reviewed history; any work outside GitHub would need to be assessed separately.

## Verified behavior

- Same PE design produces P=2/4/8 grids and computes complete N=8/16 outputs with full inner-dimension tiling.
- Signed 16-bit operands and 36-bit accumulators preserve the 16-term extremes.
- Input staging supports the 4/8/16 budget sweep, bypasses when a step fits, and holds partial values across stalls.
- Every original full-matrix case passed independently in GHDL: 18 configurations × 8 cases = 144.
- Output words are checked against the Python reference at full width; N³ useful MACs and counter formulas are checked.
- Additional observations check transaction clocks independently of the DUT counters.
- Directed regressions cover PE reset/clear/hold/valid behavior, sparse/full/empty staging steps, partial-step reset, and INSTR=false/true datapath agreement.
- All three Vivado result rows match direct parsing of their synthesis and routed reports. P=2/4/8 use 4/16/64 DSPs, zero BRAM, and have +3.955/+3.786/+2.176 ns internal WNS.

## Findings and disposition

| Finding | Consequence | Follow-up |
|---|---|---|
| `run_one.sh` piped simulator output through `grep ... || true` | A failing simulator could appear successful to the caller | Replaced with a checked Python runner, required completion markers and exact case coverage |
| Original manifest hashes were computed over CRLF bytes; Git stored LF vectors | Cross-platform checksum mismatch despite identical matrix values | Canonical LF generation and attributes; historical hashes explicitly labelled |
| PE `fire` ignored reset/clear priority | MAC event could be asserted when accumulation was suppressed | Masked `fire`; regression failed before the fix and passes afterward |
| Counters were compared mainly with formulas | Counter and schedule errors needed an additional independent observation | Added interface-clock observations |
| Old summarizer accepted incomplete configuration sets and rewrote summaries | Partial runs could produce misleading reviewed tables | Routed summarization through strict completeness/integrity validation; preserved original evidence |
| README/setup/architecture still described implementation as planned | Users could not reproduce the existing code reliably | Updated interfaces, clock conventions, setup, commands, troubleshooting, CI, and completion gates |
| Initial evidence covered only P=2 | Hardware cost comparison required the larger grids | Resolved: Thomas's P=4/P=8 runs are merged, reports match the CSV, and all three meet the same constrained internal target |
| External input/output delays are absent in the original OOC timing report | Positive WNS covers constrained internal timing, not board I/O timing | Keep internal timing and board-level timing separate |
| P=2 result RAM maps to registers | N=16 result store accounts for 9,216 bits and much of the FF cost | Retain measured mapping; memory redesign is optional future work |

No matrix-result defect was found in the 144-case baseline sweep. The reset/clear finding concerns the useful-MAC instrumentation contract, and the top-level original schedule does not assert grid enable during those clear cycles; its published sweep counts are not invalidated by that fix.

## Interpretation limits

The data show smaller-than-ideal scaling and budget-induced stalls. They do **not** show that an 8×8 grid stops outperforming a 4×4 grid within these workloads. At B=4, P=8 still takes half the compute clocks of P=4 for both N values. This is the scaling result to explain in the report.

The analysis module uses independent predictions to validate measured counters. The completed FPGA comparison uses 4/16/64 DSPs and +3.955/+3.786/+2.176 ns internal WNS. At N=16/B=16, useful throughput per DSP is 0.842/0.696/0.516 MACs per clock. The latest analysis pairs each simulated workload with its measured hardware count. The raw reports and Thomas's original commits are unchanged.
