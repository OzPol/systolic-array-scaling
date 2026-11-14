# Development setup and troubleshooting

The [README](../README.md) contains the complete first-run path. Use Linux/WSL2 with Python 3.12 and GHDL for the open-source checks. All commands below run at the repository root with the virtual environment active.

## Tool records

| Tool | Evidence and scope |
|---|---|
| Python | Clean Python 3.12 environment installed from `requirements.txt` and passed the open-source workflow |
| GHDL | Independent rerun: GHDL 5.0.1, Debian mcode/GNAT 14.2.0; CI installs the Ubuntu 24.04 package and records its actual version |
| Questa | Original Thomas run: Questa Sim-64 2026.2 win64 May 18 2026; `vcom -2008` / `vsim -c` |
| Vivado | All three Thomas runs: 2025.2.1, SW Build 6403652, Windows; Vivado is unnecessary to regenerate the committed analysis |
| Vivado part | `xck26-sfvc784-2LV-c` (KV260 SOM target) |
| Flow | Out-of-context synth, opt, place, route; one thread; default directives; no board programming |
| Arithmetic and RTL | VHDL-2008; signed 16-bit input, 36-bit exact result; N≤16 |
| Clock | 10 ns, `constraints/clk_10ns.xdc` |
| Dependencies | Pinned Python plotting dependency set in `requirements.txt`; simulation and CSV validation use stdlib |

Record local versions before reporting new evidence:

```bash
python --version
ghdl --version
git rev-parse HEAD
git status --short
```

For repeatable measurements, run from a clean checkout. The simulator records the commit and file hashes with each run.

## Open-source setup details

`bash scripts/bootstrap.sh --install-system` uses apt with sudo on Ubuntu/Debian, then creates `.venv` and installs `requirements.txt`. Sudo is only needed for system tools. The script does not install licensed software.

For later terminal sessions:

```bash
cd ~/systolic-array-scaling
source .venv/bin/activate
make check
```

If GHDL has a custom location, set `GHDL` to its executable path before running the Python scripts. Standard package installations do not require `GHDL_PREFIX` or `LD_LIBRARY_PATH` overrides.

`make check` requires GHDL by default. `make check SIM=questa` uses the licensed simulator but retains the same vector/test/analysis workflow.

## Questa

Install the course-supported Questa version and configure its licensing as directed by the course. Where the course license requires GatorLink VPN and `SALT_LICENSE_SERVER`, use the actual server value provided by the course; no server address or credentials are stored here.

Confirm the executables are available:

```bash
vlib -version
vcom -version
vsim -version
```

Then run the README's Questa commands. Compile order is `sys_pkg`, `pe`, `systolic_array`, `input_stager`, `systolic_top`, then testbenches. The runner uses VHDL-2008, stops on tool failures, checks a PASS marker, and validates all expected case rows. It no longer hides errors through a shell `|| true` pipeline.

If your simulator presents an interactive finish prompt, configure batch execution to finish/exit rather than wait. Keep the completion marker and CSV checks enabled; a tool returning zero alone is insufficient evidence.

## Vivado

Install Vivado with support for the K26 device and the required license. Keep installation/licensing configuration outside the repository. On Linux, source the `settings64.sh` belonging to your actual installation. On Windows, use a terminal with Vivado's `bin` on PATH. Python can drive the same batch Tcl flow on either platform.

Check the installation:

```bash
vivado -version
```

Use `python scripts/vivado/run.py --help` for configuration and destination options. A single run may be launched directly through Tcl:

```bash
vivado -mode batch -nojournal -nolog -source scripts/vivado/synth.tcl -tclargs 4 16
```

The Python wrapper is preferred because it retains console logs, records hashes, and requires a completion marker plus all four core utilization/timing reports. It also retains routed checkpoints for later inspection; checkpoints stay in ignored raw directories.

For a future run through the current wrapper, inspect (the original committed runs predate the extra diagnostic files and run manifest):

1. `console.txt`: synthesis, optimization, placement, and routing completed without errors.
2. `util_impl.rpt`: post-route LUTs, FFs, DSPs, BRAM.
3. `timing_impl.rpt`: WNS/TNS, hold checks, and unconstrained paths.
4. `check_timing_impl.rpt`, `drc_impl.rpt`, `methodology_impl.rpt`: remaining violations and warnings.
5. `run.json`: source hash/commit, correct P/N/part, and `completed=true`.

The P=2/4/8 post-route reports give +3.955/+3.786/+2.176 ns WNS for the constrained internal paths. The current OOC setup leaves external input/output delays unspecified; board I/O timing would be a separate implementation step.

## Troubleshooting

| Symptom | Action |
|---|---|
| `ghdl` not found | Run bootstrap with `--install-system`; verify `command -v ghdl` |
| `venv` creation fails on Ubuntu | Install `python3-venv`; use Python 3.12 |
| `matplotlib` import fails | Activate `.venv`; run `python -m pip install -r requirements.txt` |
| Vector/manifest mismatch | Inspect `git diff -- tb/vectors`; regenerate only if intentional; rerun `--check` |
| Simulator compile/assertion failure | Read `build/<sim>/compile.txt` or per-configuration log; do not use partial CSV as a complete sweep |
| `missing configurations` in analysis | Run the full sweep or provide the reviewed 18-row summary; a smoke run is intentionally rejected |
| Vivado missing from PATH | Use its configured terminal or source its actual settings script |
| Vivado reports an existing directory | Use a fresh `--output-root`, or `--resume` for a completed run with identical hashes |
| Vivado memory pressure | Run P values sequentially; the provided wrapper already does this |
| CSV/report does not change after a Vivado run | Run `scripts/collect_vivado.py` for the correct source directory, then regenerate analysis |
| GitHub cannot find a required check | Let CI complete once, then select `VHDL and analysis` in the main-branch ruleset |

The Linux/GHDL workflow and report parsers have been tested. Docker and macOS are alternative setups; Questa and Vivado run in the licensed team environment.
