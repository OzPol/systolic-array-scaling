# Project artifacts

The completed simulation comparison covers eighteen grid/matrix/budget configurations and 144 passing cases. The hardware comparison covers the three N=16 PE-grid implementations. The paper and presentation use the original saved measurement files.

| Artifact | Location |
|---|---|
| Simulation and independent verification | `results/summary_sim.csv`, `results/verification/` |
| FPGA reports and logs | `results/vivado/`, `results/logs/` |
| Generated tables and plots | `results/analysis/` |
| Recorded activity replay | `results/visualization/` |
| IEEE report and editable source | `deliverables/report/` |
| Five-minute presentation and speaking outline | `deliverables/presentation/` |
| Original video outline | `deliverables/video/outline.md` |

## Commands

- `make analysis`: analyze saved evidence in a new timestamped directory.
- `make study`: run the full configured experiment with automatic folder naming.
- `make publish`: rebuild the published analysis, paper, and slides from the saved study.
- `make check`: run open-source verification and generate fresh verification artifacts.

The original measurement CSVs, FPGA reports, console logs, replay, and video outline remain unchanged. The configuration tests cover every combination, and the analysis generates the values inserted into the paper.

The presentation provides nine slides and a timed five-minute speaking outline. Record the slides with the narration and check the resulting duration, audio, and chart legibility.

## Optional extensions

BRAM-oriented output storage, overlapping boundary steps or readout, larger workloads, alternate dataflows, physical-board runs, measured DRAM supply, power, and CPU comparisons are separate extensions requiring their own implementation and comparable measurements.
