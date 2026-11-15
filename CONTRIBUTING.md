# Contributing

Create a branch from the current project branch and submit focused changes through a pull request. Preserve existing measurement archives and commit authorship.

Before changing RTL, retain the configuration, source revision, and current verification evidence. Run `make check` for the open-source workflow. RTL or clock-constraint changes also require comparable FPGA measurements before updating implementation claims.

Use `python scripts/experiment.py --measure` for a full measurement run, and `python scripts/experiment.py` to analyze the selected archived data. Every execution gets a unique output directory. Keep generated reports tied to one selected dataset.

Commit compact reviewed text evidence and generated results. Keep compiler work directories and routed checkpoints outside Git. The complete archive can be distributed as a reviewed release asset.

Documentation describes interfaces, methods, and measured results. Development history belongs in the chronological commit table in `docs/review.md`.
