# Project artifacts

The completed simulation comparison covers eighteen grid/matrix/budget configurations and 144 passing cases. The hardware comparison covers the three N=16 PE-grid implementations. The paper and presentation use the original saved measurement files.

| Artifact | Location |
|---|---|
| Simulation and independent verification | `results/summary_sim.csv`, `results/verification/` |
| FPGA reports and logs | `results/vivado/`, `results/logs/` |
| Generated tables and plots | `results/analysis/` |
| Recorded activity replay | `results/visualization/` |
| Final report and editable source | `deliverables/report/final-report.pdf`, `final-report.tex` |
| Three editable presentation editions and technical Markdown deck | `docs/presentations/` |
| Five-minute speaking outline | `deliverables/presentation/narration.md` |
| Original video outline | `deliverables/video/outline.md` |

## Commands

- `make analysis`: analyze saved evidence in a new timestamped directory.
- `make study`: run the full configured experiment with automatic folder naming.
- `make publish`: rebuild the published analysis and final report, then package the reviewed native slides.
- `make check`: run open-source verification and generate fresh verification artifacts.

The original measurement CSVs, FPGA reports, console logs, replay, and video outline remain unchanged. The configuration tests cover every combination, and the analysis generates the values inserted into the paper.

The current presentation provides thirteen main slides and nineteen supporting slides. The timed narration covers the main sequence in approximately five minutes. Earlier 19-slide and 32-slide editions remain available alongside the latest edition. The Markdown deck provides a longer technical explanation for study and discussion.

## Optional extensions

BRAM-oriented output storage, overlapping boundary steps or readout, larger workloads, alternate dataflows, physical-board runs, measured DRAM supply, power, and CPU comparisons are separate extensions requiring their own implementation and comparable measurements.
