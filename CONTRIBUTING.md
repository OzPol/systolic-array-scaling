# Contributing

Create a branch from `main` and submit focused changes through a pull request. Preserve existing measurement archives and commit authorship. Keep unrelated features, measurement updates, and documentation changes in separate reviewable commits.

Before changing RTL, retain the configuration, source revision, and current verification evidence. Run `make check` for the open-source workflow. RTL or clock-constraint changes also require comparable FPGA measurements before updating implementation claims.

Compare identical complete workloads, vectors, input budgets, numerical widths, device parts, clock constraints, and implementation settings. Keep analytical predictions separate from observed counters. Retain the source revision, tool version, source/vector hashes, and CSV hash with each measurement archive. Missing, failed, duplicate, or partial measurements must fail validation.

Use `python scripts/experiment.py --measure` for a full measurement run, and `python scripts/experiment.py` to analyze the selected archived data. Every execution gets a unique output directory. Keep generated reports tied to one selected dataset.

Commit compact reviewed text evidence and generated results. Keep compiler work directories and routed checkpoints outside Git. The complete archive can be distributed as a reviewed release asset.

Documentation describes interfaces, methods, and measured results. Development history belongs in the chronological commit table in `docs/review.md`.
