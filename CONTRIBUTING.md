# Contributing

## Branch and commit boundaries

- Thomas's baseline is merged in PR #1, retaining `3459a9f` and `d771fc7` unchanged.
- Follow-up work belongs on a new branch from current `main` and its own PR. The original `oz-finish-systolic-study` work was merged in PR #2; Thomas's later Vivado evidence was merged in PR #3. Do not add follow-up commits to Thomas's branch or rewrite his authorship.
- Use one commit per feature, bug fix with its regression, new test group, or significant documentation change. Keep reviewed measurement updates in a separate commit where practical.
- Keep each commit reviewable. Describe the behavior and validation in its message. Do not squash unrelated changes if their independent history matters to the team.

## Before a PR

```bash
source .venv/bin/activate
make check
git diff --check
git status --short
```

CI runs the same checks. Add a regression when fixing a functional defect. Use full-width signed references and retain N³ useful MACs; correctness is required before interpreting performance.

## Measurement integrity

- Compare the same full matrix, input vectors, budget, numeric widths, and measurement boundary across P values.
- Keep model predictions distinct from simulator counters. Missing, failed, duplicated, and partial results must fail validation.
- Retain source commit, dirty state, tool version, source/vector hashes, and CSV hash with reviewed simulation results.
- Collect DSP count, BRAM mapping, and timing from the post-route reports.
- Use identical part, clock, synthesis boundary, and implementation settings across FPGA configurations. Record any source/settings change; rerun all sizes if it can change their comparison.
- The OOC timing result covers the constrained internal paths. Board timing and memory measurements are separate experiments.

`build/` and `results/raw/` are ignored. Commit reviewed compact CSV/JSON/text reports and figures deliberately. Do not commit license data, installation paths containing credentials, checkpoints, or bulky generated project trees.

## Updating figures and reports

```bash
python scripts/collect_vivado.py
python -m analysis.report
```

Use `--simulation` for a new full per-case sweep. Review the generated report, missing hardware status, and plot labels before committing. Use the complete sweep when updating the reviewed summary.
