# Measurement evidence

The published study uses `results/summary_sim.csv`, the three N=16 implementations in `results/summary_vivado.csv` and `results/vivado/`, and the original console logs in `results/logs/`. These measurement files are retained unchanged.

The analysis compares every hardware-summary field with the saved synthesis and routed reports. It checks setup/hold timing and internal endpoint coverage. The original OOC reports leave external I/O delays unspecified, so timing-qualified rates apply to the constrained internal design.

The independent GHDL archive contains 144 passing cases and source/vector SHA-256 records. Every simulation configuration is compared with the complete-product cycle model and the original summary. The eighteen CSV activity traces reproduce the bytes identified by the existing replay's SHA-256 manifest; the existing replay and activity figures remain unchanged.

`results/selected.json` identifies the published input paths. Generated tables, plots, and LaTeX values are derived from those inputs. `make analysis` writes a separate timestamped analysis directory. `make publish` rebuilds the published analysis, paper, and slides from the same saved study.

New measurements from `make study` receive a fresh timestamped directory and retain source hashes, actual build start/end times, tool versions, reports, and checkpoints. They remain separate from the published measurement files. Keep compact numerical and text evidence in Git; distribute full checkpoint archives separately when needed.
