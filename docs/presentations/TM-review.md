# TM presentation versions and technical review

## Scope and canonical files

Three presentation attachments were received for this review. Two existing repository copies were also identified and checked by Git blob hash. The attachments contain three different binary packages but **two distinct presentations**.

| Source | Slides | Speaker notes | Classification and retained version |
|---|---:|---:|---|
| `Systolic_Array_Premium_Group_2.pptx` | 31 | Main slides 1–10 | Full presentation: retain as [TM-04](TM-04-systolic-array-scaling-full-31-slides.pptx) |
| `Group2_Systolic_Array_Premium_Math_Video_Only.pptx` | 11 | All 11 slides | Same visible slides and notes as the next file; use the later saved copy in TM-05 |
| `Systolic_Array_Premium_Group_2_Math_Video_Only.pptx` | 11 | All 11 slides | Canonical recording presentation: [TM-05](TM-05-systolic-array-scaling-math-recording-11-slides.pptx) |
| Repository copy: `docs/Group2_Systolic_Array_Premium.pptx` | 11 | All 11 slides | Byte-identical to the second attachment; [existing copy](../Group2_Systolic_Array_Premium.pptx) |
| Historical repository copy: `docs/Systolic_Array_Premium_Group_2.pptx` at `8b8d7fb` | 31 | Main slides 1–10 | Byte-identical to the first attachment; [historical copy](https://github.com/OzPol/systolic-array-scaling/blob/8b8d7fb4fab549548667bfde6986b1b83437f35c/docs/Systolic_Array_Premium_Group_2.pptx) |

This is a review of the three received attachments and the two matching repository copies. If two additional attachments are intended, they still need to be added to this comparison. The catalog numbers continue the repository's existing editions 01–03.

The TM-05 copy retains all speaker notes. An [unchanged text export of those notes](TM-05-speaker-notes.md) makes the narration readable without opening PowerPoint. The deck files are preserved as provided; the recommendations below are review findings rather than silent edits to Thomas's slides.

## Evolution and duplicate check

1. **Full presentation:** ten main slides followed by an appendix divider and twenty reference slides, for 31 slides total. All ten main slides have narration; the appendix has none.
2. **Math recording presentation:** retains the ten main-slide topics, inserts a matrix-multiplication explanation as slide 3, revises the introductory PE-grid diagram, and omits the 21-slide appendix. The other nine shared main slides retain their substantive text. All ten corresponding original notes remain the same, with one new note for the math slide.
3. **Later save of the recording presentation:** retains exactly the same ordered slide text and speaker notes. All eleven slide renders compare pixel for pixel under the same rendering process. Neither package contains animation or transition blocks. Differences are in packaging and document properties, including a later modification timestamp and a smaller package size.

The two 11-slide attachments are 434,724 and 91,459 bytes respectively. The smaller, later-saved copy is retained as TM-05. Both already contain the same notes, so this pair does not contain an additional narration-only revision.

## Technical verdict

The latest received recording presentation and its notes agree with the implemented study on the important facts: output-stationary dataflow; grids 2×2, 4×4, and 8×8; full matrix orders 8 and 16; input budgets 4, 8, and 16; eighteen configurations and 144 passing cases; and the distinction between compute latency and serial-readout-inclusive latency.

The worked matrix example is correct: $1\times5+2\times7=19$. The full-demand boundary rule is consistent with the RTL: up to $2P$ new combined A/B words per enabled step, with the grid held while an incomplete step is staged. The slide correctly notes that not every step requires the peak word count.

The headline numerical claims also match the saved measurements:

| Claim | Checked value |
|---|---|
| N=16, P=8 compute clocks at B=4,8,16 | 304, 184, 124 |
| Reduction from B=4 to B=16 | 59.21%, correctly rounded to 59% |
| N=16, B=16 compute speedup versus 2×2 | 1216/124 = 9.806×, correctly shown as 9.81× |
| Complete-product speedup | (1216+256)/(124+256) = 3.874×, correctly shown as 3.87× |
| DSP counts | 4, 16, 64 in the original N=16 implementation reports |

The complete result tables in full-deck slides 24–28 were checked against the selected analysis: **162 displayed numerical entries match**, including all eighteen configuration rows, their throughput and speedups, and all nine timing-qualified rate rows. The FPGA resource table matches the original routed reports.

The narration is coherent and follows the slide sequence. It contains approximately 554 words, leaving reasonable room for pauses in a five-minute recording. Actual delivery still determines the final duration.

## Substantive corrections and clarifications

### 1. The cover overstates the observed result

**Location:** slide 1 in both distinct presentations.

“When more hardware stops paying off” can suggest a measured point at which additional hardware stops improving performance. The study instead finds the 8×8 grid fastest in every tested configuration, with sub-proportional gains and lower useful work per DSP.

Suggested title: **“Why More Hardware Delivers Diminishing Returns.”** This preserves the presentation's message while matching the actual finding.

### 2. The input limit belongs to the RTL stager

**Location:** TM-05 slide 7 speaker notes; corresponding full-deck slide 6.

The note says that the testbench enforces the input budgets. The testbench selects and drives the budget, while `rtl/input_stager.vhd` actually limits accepted boundary words and determines whether the grid can advance. That distinction matters because the stager is part of the synthesized design and its cost.

Suggested replacement: **“The testbench drives the selected input budget and checks the result. The RTL input stager enforces that budget and holds the grid until each boundary step is ready.”**

Sources: [input stager](../../rtl/input_stager.vhd) and [top-level integration](../../rtl/systolic_top.vhd).

### 3. The appendix accounting bar needs an explicit interpretation

**Location:** full-deck slide 29, “Where 440 clocks go.”

The counts are correct: 64 useful-equivalent, 56 fill/drain capacity cost, four capture, sixty stalls, and 256 readout clocks sum to 440. However, the “event trace” heading and continuous segmented bar can be read as five consecutive physical phases.

The first two terms are capacity-normalized accounting. Useful MACs occur during the physical fill/drain interval; stalls and captures are distributed among tiles. Only the final readout is a separate 256-clock tail after the 184-clock compute interval.

Suggested caption: **“Capacity-normalized clock accounting. Useful MACs overlap fill/drain; the colored segments are not a chronological event trace.”**

## One useful explanatory addition

Slide 10's efficiency message is supported if “efficient” means useful throughput per DSP. Name that metric explicitly: at N=16/B=16, the 2×2 grid achieves 0.842 MAC/clock/DSP versus 0.516 for 8×8. This is an arithmetic-resource efficiency comparison. The experiment does not measure energy efficiency.

## Editability note

The matrix equation on slide 3 of the recording presentation is a PNG image. The equation and example are mathematically correct, but this one object does not meet the requested native-equation editing requirement. It is retained in these archived originals. A future edited recording copy should convert it to Office Math or editable mathematical text.

## Evidence

- [Architecture and clock definitions](../architecture.md)
- [Selected simulation summary](../../results/summary_sim.csv)
- [Generated metrics](../../results/analysis/metrics.csv)
- [Original FPGA reports](../../results/vivado/)
- [P=8/N=16/B=8 trace](../../results/verification/traces/p8_n16_b8.csv)
- [Final report](../../deliverables/report/final-report.pdf)
- [Source filenames and hashes](versions.json)
