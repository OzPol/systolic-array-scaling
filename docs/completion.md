# Completion and submission checklist

The implementation, all 144 simulation cases, and all three Vivado runs are complete. The refreshed analysis and IEEE report cover the full planned study. No additional FPGA experiment is required for this scope.

## Completed evidence

- [x] Merge Thomas's baseline in PR #1, Oz's follow-up in PR #2, and Thomas's larger-grid Vivado results in PR #3, retaining original commits and authorship.
- [x] Verify all 18 grid/matrix/budget configurations and eight full-width cases per configuration.
- [x] Check vector hashes, independent clock counts, PE/stager behavior, and synthesis-mode datapath agreement.
- [x] Retain original simulation evidence, routed reports, and console logs.
- [x] Confirm identical Vivado version, part, 10 ns constraint, INSTR=false, and implementation flow for P=2/4/8.
- [x] Check every hardware CSV value against the actual reports, including setup/hold timing and unconstrained-path scope.
- [x] Regenerate latency, utilization, cycle accounting, FPGA resources, and throughput-versus-DSP figures.
- [x] Update the manuscript's hardware tables, abstract, findings, and conclusions; compile and visually review the IEEE PDF.
- [x] Update the README, document navigation, mathematical definitions, and video narration with the completed evidence.

## Remaining submission tasks

| Task | Completion evidence |
|---|---|
| Team review of the refreshed report | Review the [PDF](../deliverables/report/main.pdf), author list, and claims before submission |
| Record the five-minute video | Use the [storyboard and narration](../deliverables/video/outline.md), latest plots, and measured hardware table; review legibility, audio, and duration |
| Upload the group deliverables | One video and one final report per group, following Canvas instructions |
| Complete peer Q&A | Participate in the assigned November 19–20 discussion |

A final team review and a completed recording cannot be inferred from repository files. The checked-in narration is a script, not a recorded video.

## Reproduce the completed analysis

After activating the Python environment, from the repository root:

```bash
make check
python -m analysis.report --simulation results/verification/ghdl_sim_results.csv
```

The first command makes a fresh 144-case GHDL sweep and temporary analysis/replay. The second reproduces the reviewed figures from the committed independent GHDL evidence and all three measured Vivado rows. Both validate every configuration. See [report build instructions](../deliverables/report/README.md) to compile the PDF.

The existing Vivado runs were produced before PR #2's analysis follow-up. Its only RTL change is a reset/clear mask on an activity signal unused with INSTR=false. The datapath, controller, stager, clock constraint, part, tool version, and implementation flow match. The imported FPGA evidence remains valid for this comparison; it is not relabeled as a new run on the final commit. Exact source hashes and a clean-worktree run manifest were not recorded by the original flow.

For an intentional future RTL or constraint change, use a fresh output directory and rerun all three comparable implementations. The README retains the optional Vivado commands. Preserve earlier reviewed evidence.

## Course dates and requirements

Source: the repository's [course guidelines PDF](eel5764_project_guidelines_fall_2026.pdf).

| Deliverable | Due | Requirement |
|---|---|---|
| Recorded video | November 17, 2026, 11:59 PM | Five-minute architecture/findings presentation |
| Peer Q&A | November 19–20, 2026 | Asynchronous discussion participation |
| Final written report | December 1, 2026, 11:59 PM | IEEE double-column conference-style paper |

The guideline specifies one submission per group. It does not require every member to narrate the video. Check Canvas for newer instructor instructions before submitting.

## Optional extensions

BRAM-friendly output storage, overlapping boundary steps, larger workloads, alternate dataflows, physical-board runs, measured DRAM supply, power, and CPU comparisons are future work. They are not required to finish the current study and would need separate implementation and comparable measurements.
