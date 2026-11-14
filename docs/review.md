# Contribution and technical review

## Baseline attribution

Thomas Martin's branch was merged **before** Oz's follow-up work, through [PR #1](https://github.com/OzPol/systolic-array-scaling/pull/1), merge `86bbfb9`. The original commits retain their hashes and author. Follow-up commits are on `oz-finish-systolic-study`, reviewed separately in PR #2.

| Commit | Author | Substantive contribution |
|---|---|---|
| `2269d2c` | Thomas Martin | Documentation links, generated-file exclusions, tool/board records, project PDFs |
| `3459a9f` | Thomas Martin | Shared VHDL package; PE; generated array; budget stager; tiled controller/result storage/readout; Python reference/vector generation; self-checking testbench; simulator and Vivado scripts; 144 recorded passing cases; P=2 post-route reports |
| `d771fc7` | Thomas Martin | Explanatory RTL/testbench comments, with the recorded Claude co-author retained |
| Earlier main-branch commits | Ozlem Polat | Project definition, architectural specification, experiment plan, 18-row configuration matrix, proposal/project documentation |

**Assessment:** Thomas's contribution is substantial. It provides most of the executable baseline implementation and original measurement pipeline, not a cosmetic addition or isolated helper. His November 10 message accurately describes the branch contents and the remaining P=4/P=8 Vivado work. The second November commit is primarily explanatory comments; the first contains the substantive implementation.

Commit/file size is not a useful workload percentage: most added lines are vectors, logs, and generated reports. This review assesses delivered behavior and evidence, not hours, effort, or who typed each line. Recorded AI assistance does not change which team member delivered and validated the branch. No commits attributed to Keith appear in the reviewed history; that does not establish whether he contributed outside GitHub.

## Verified behavior

- Same PE design produces P=2/4/8 grids and computes complete N=8/16 outputs with full inner-dimension tiling.
- Signed 16-bit operands and 36-bit accumulators preserve the 16-term extremes.
- Input staging supports the 4/8/16 budget sweep, bypasses when a step fits, and holds partial values across stalls.
- Every original full-matrix case passed independently in GHDL: 18 configurations × 8 cases = 144.
- Output words are checked against the Python reference at full width; N³ useful MACs and counter formulas are checked.
- Additional observations check transaction clocks independently of the DUT counters.
- Directed regressions cover PE reset/clear/hold/valid behavior, sparse/full/empty staging steps, partial-step reset, and INSTR=false/true datapath agreement.
- The existing P=2 Vivado report parses to 7,260 LUTs, 9,437 FFs, four DSPs, zero BRAM, and +3.955 ns internal WNS.

## Findings and disposition

| Finding | Consequence | Follow-up |
|---|---|---|
| `run_one.sh` piped simulator output through `grep ... || true` | A failing simulator could appear successful to the caller | Replaced with a checked Python runner, required completion markers and exact case coverage |
| Original manifest hashes were computed over CRLF bytes; Git stored LF vectors | Cross-platform checksum mismatch despite identical matrix values | Canonical LF generation and attributes; historical hashes explicitly labelled |
| PE `fire` ignored reset/clear priority | MAC event could be asserted when accumulation was suppressed | Masked `fire`; regression failed before the fix and passes afterward |
| Counters were compared mainly with formulas | Counter and schedule errors needed an additional independent observation | Added interface-clock observations |
| Old summarizer accepted incomplete configuration sets and rewrote summaries | Partial runs could produce misleading reviewed tables | Routed summarization through strict completeness/integrity validation; preserved original evidence |
| README/setup/architecture still described implementation as planned | Users could not reproduce the existing code reliably | Updated interfaces, clock conventions, setup, commands, troubleshooting, CI, and completion gates |
| Only P=2 has a routed FPGA result | Hardware scaling and throughput/DSP comparisons remain incomplete | Sequential runner and report collector are ready; P=4/P=8 remain pending |
| External input/output delays are absent in the original OOC timing report | Positive WNS covers constrained internal timing, not board I/O timing | Report timing scope explicitly; do not claim verified system MHz or physical throughput |
| P=2 result RAM maps to registers | N=16 result store accounts for 9,216 bits and much of the FF cost | Retain measured mapping; memory redesign is optional future work |

No matrix-result defect was found in the 144-case baseline sweep. The reset/clear finding concerns the useful-MAC instrumentation contract, and the top-level original schedule does not assert grid enable during those clear cycles; its published sweep counts are not invalidated by that fix.

## Interpretation limits

The data show smaller-than-ideal scaling and budget-induced stalls. They do **not** show that an 8×8 grid stops outperforming a 4×4 grid within these workloads. At B=4, P=8 still takes half the compute clocks of P=4 for both N values. Report the measured result instead of forcing a stronger bandwidth-knee conclusion.

The analysis module uses independent predictions to validate measured counters. It does not generate missing measurements. Hardware cost and timing comparisons must remain incomplete until actual P=4/P=8 reports are available.
