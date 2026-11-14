# Completion checklist and remaining steps

The project can be brought to a verified simulation-and-analysis state here. The full proposed study still needs actual P=4/P=8 Vivado evidence from a licensed machine. The recorded course presentation and Canvas submissions require the team.

## Completed in the separate follow-up branch

- [x] Merge Thomas's existing branch separately and preserve attribution.
- [x] Review implementation, commit history, original logs, and report numbers.
- [x] Rerun all 144 full-matrix cases independently in GHDL.
- [x] Fix simulator error propagation and vector checksum reproducibility.
- [x] Add direct PE/stager tests and INSTR=false datapath regression.
- [x] Check interface-clock counts independently of DUT counters.
- [x] Add strict analysis, cycle decomposition, and PNG/SVG plots.
- [x] Prepare sequential Vivado execution, report collection, and provenance.
- [x] Document WSL/Linux setup, pinned packages, commands, and troubleshooting.
- [x] Add PR-triggered CI and downloadable measurement/log/plot artifacts.
- [x] Provide a report source draft and five-minute video outline.

## Remaining, in execution order

| Step | Action | Completion evidence | Suggested commit boundary |
|---|---|---|---|
| 1 | On a Vivado machine, fetch this branch and check `git status` | Correct branch/commit; clean source | No new commit needed |
| 2 | Confirm the Vivado version, K26 support, and license | `vivado -version`; successful device initialization | Record changed tool settings only if necessary |
| 3 | Run P=4/N=16 using the wrapper | Completed `run.json`, full console, synth/route utilization and timing reports | `Record 4x4 Vivado implementation results` |
| 4 | Review warnings, WNS/TNS/hold/unconstrained paths and collect P=4 reports | Actual measured LUT/FF/DSP/BRAM plus scoped timing conclusion | Same P=4 evidence commit |
| 5 | Run P=8/N=16, sequentially | Same completion evidence | `Record 8x8 Vivado implementation results` |
| 6 | Review/collect P=8 and regenerate analysis | All three measured FPGA configurations in `summary_vivado.csv` | Same P=8 evidence commit, or separate plot update |
| 7 | If the source/tool/settings differ materially, rerun P=2/4/8 from one clean revision | Comparable source hashes and flow settings | One evidence commit per configuration |
| 8 | Review final hardware scaling and throughput/DSP conclusions | No missing hardware rows; claims match reports | `Finalize hardware scaling analysis` |
| 9 | Compile and review the IEEE report source, replace explicit pending hardware entries, update conclusions | Rendered double-column PDF with final real measurements | `Finalize project report` |
| 10 | Update the presentation with the measured figures and record the five-minute video | Playable recording near the required duration | `Finalize presentation and video notes` (keep bulky video outside git) |
| 11 | Review and merge PR #2 after CI succeeds | Main contains the follow-up commits separately from PR #1 | Merge with history retained |
| 12 | Submit one video and final report per group; complete peer Q&A | Canvas submission confirmations | No repository commit needed |

## Concrete Vivado commands

From a configured tool shell at the repository root:

```bash
git fetch origin
git switch oz-finish-systolic-study
git pull --ff-only
git status --short
vivado -version
```

Run/collect P=4 first:

```bash
python scripts/vivado/run.py --p 4 --n 16
python scripts/collect_vivado.py
python -m analysis.report
```

Inspect the actual reports before staging the evidence:

```bash
git status --short
git add results/vivado/p4_n16 results/summary_vivado.csv results/analysis
git diff --cached --stat
git commit -m "Record 4x4 Vivado implementation results"
```

Then P=8:

```bash
python scripts/vivado/run.py --p 8 --n 16
python scripts/collect_vivado.py
python -m analysis.report
```

```bash
git add results/vivado/p8_n16 results/summary_vivado.csv results/analysis
git diff --cached --stat
git commit -m "Record 8x8 Vivado implementation results"
```

If a raw output folder already exists, use `--resume` only for an unchanged completed run, or choose a fresh `--output-root`. Do not delete prior evidence merely to make a rerun fit the default path.

For a comparable clean-current-source rerun of all sizes:

```bash
python scripts/vivado/run.py --p 2 4 8 --n 16 --output-root results/raw/current_rtl
python scripts/collect_vivado.py --source results/raw/current_rtl
python -m analysis.report
```

Re-run `make check` after any RTL or measurement-boundary change. Timing failure is a valid finding; do not alter the target solely to make an individual design appear successful without rerunning comparable configurations.

## Course dates and requirements

Source: the repository's [course guidelines PDF](eel5764_project_guidelines_fall_2026.pdf).

| Deliverable | Due | Requirement |
|---|---|---|
| Recorded video | November 17, 2026, 11:59 PM | Five-minute architecture/findings presentation |
| Peer Q&A | November 19–20, 2026 | Asynchronous discussion participation |
| Final written report | December 1, 2026, 11:59 PM | IEEE double-column conference-style paper |

The guideline specifies one submission per group. The supplied video requirement does not say every member must narrate; the team may divide presentation duties, while checking Canvas for any newer instructor instructions. The recording itself and final Canvas confirmations are not completed by repository changes.

## Optional work after the committed scope

BRAM-friendly output storage, buffered/overlapped boundary steps, larger workloads, alternate dataflows, a physical-board run, measured DRAM supply, and CPU comparisons are extensions. None is needed to finish the current proposed study. Implementing an extension changes what is measured and should have its own feature/tests/experiment commits.
