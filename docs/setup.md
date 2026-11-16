# Development setup

## Analyze archived evidence

Python 3.12+ is required for the pinned plotting packages. Python 3.10 can run the standard-library simulation and Vivado wrappers, but it cannot install the complete pinned analysis environment.

On Ubuntu with Python 3.12 already installed:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/experiment.py
```

On Ubuntu 22.04, a managed interpreter avoids replacing the system Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
"$HOME/.local/bin/uv" venv --python 3.12 --seed .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`PYTHON=python3.12 bash scripts/bootstrap.sh` is also available. The bootstrap script accepts `--install-system` for Ubuntu/Debian GHDL, make, git, and venv packages. On Ubuntu 22.04 that package installation does not itself upgrade Python to 3.12.

## Simulation

Record the active tools and source revision before measuring a new run:

```bash
python --version
ghdl --version
git rev-parse HEAD
git status --short
```

```bash
sudo apt-get update
sudo apt-get install -y ghdl make git
python scripts/test_rtl.py --sim ghdl
python scripts/sim.py --sim ghdl --sweep
```

The simulator allocates a unique timestamped run directory when no output path is supplied. `make study` keeps simulation, traces, all six configured FPGA builds, and analysis under one automatically generated run ID.

The committed independent verification used GHDL 5.0.1. Its 144 passing cases agree with the simulation-summary counters. The original licensed sweep used QuestaSim 2026.2. The evidence records actual tool versions rather than assuming that an installed package matches another platform's package version.

For Questa, configure `vlib`, `vcom`, and `vsim` using the provided licensed installation. Verify them with `vlib -version`, `vcom -version`, and `vsim -version`. Then use `python scripts/sim.py --sim questa --sweep`. License-server configuration belongs in the local environment.

Compilation follows `sys_pkg`, `pe`, `systolic_array`, `input_stager`, `systolic_top`, then the testbenches. The runner uses VHDL-2008, checks tool exit status and completion markers, and requires every expected case. Custom GHDL installations can set `GHDL` to the executable path.

## FPGA implementation

The published FPGA reports used Vivado 2025.2.1, SW Build 6403652, on Windows, targeting `xck26-sfvc784-2LV-c`. For new measurements in Ubuntu, install Vivado ML Standard with **Kria SOMs and Starter Kits** support. The Vivado installer includes Vitis HLS as part of the selected design-tool bundle.

The tools and repository can occupy different directories. Activate the installed tools before starting a build:

```bash
source "$HOME/AMDDesignTools/2025.2.1/Vivado/settings64.sh"
vivado -version
python scripts/vivado/run.py
```

The default sweep includes every grid and matrix size from `docs/configurations.csv`, executing one build at a time. Narrow a debugging run with `--p 4 --n 8`, or select several matrix sizes with `--n 8 16`. `--output-root` selects a shared destination. The wrapper preserves completed runs and rejects an occupied incomplete/mismatched destination.

If the installer requests OS libraries, run its own `Vivado/scripts/installLibs.sh` with sudo. If Vivado reports a missing `en_US.UTF-8` locale:

```bash
sudo locale-gen en_US.UTF-8
```

The batch flow retains a routed checkpoint, utilization/timing reports, DRC and methodology reports, and console output. `run.json` records source identity, parameters, completion, wall duration, and the launched command for new runs. Checkpoints remain outside ordinary Git history.

Inspect each completed build's evidence:

| File | Check |
|---|---|
| `console.txt` | Synthesis, optimization, placement, and routing completed |
| `util_impl.rpt` | Post-route LUT, FF, DSP, and BRAM counts |
| `timing_impl.rpt` | Setup and hold slack, total negative slack, constrained paths |
| `check_timing_impl.rpt` | Internal endpoint coverage and external I/O-delay scope |
| `drc_impl.rpt`, `methodology_impl.rpt` | Design-rule and methodology findings |
| `run.json` | Parameters, source identity, duration, and completion state |

The original saved FPGA runs predate the diagnostic-file and run-manifest additions. Their retained utilization, timing, and console reports are the original evidence.

## Report and presentation

Use Tectonic or a complete pdfLaTeX distribution containing IEEEtran, Beamer, TikZ, booktabs, and the standard Times/Helvetica fonts. On Ubuntu, the relevant packages are `texlive-publishers`, `texlive-latex-extra`, `texlive-pictures`, and `texlive-fonts-recommended`. Then:

```bash
python scripts/experiment.py --publish
```

Analysis from an existing run does not require GHDL or Vivado. Complete new measurements require both. All rates at 100 MHz are conditional calculations from cycle counts and successful internal timing, rather than board measurements.

## Troubleshooting

| Symptom | Action |
|---|---|
| Python 3.10 selected for plotting | Create the Python 3.12 environment above |
| `ghdl` missing | Install GHDL or run the bootstrap with `--install-system` |
| Virtual-environment creation fails | Install the venv package for the selected Python interpreter |
| Plotting-package import fails | Activate `.venv` and install `requirements.txt` |
| Vector-checksum mismatch | Inspect vector changes before intentionally regenerating the fixed inputs |
| Simulator compilation or assertion failure | Read the logs in `build/<sim>/` or `build/ghdl_units/` |
| Missing or duplicate configurations | Supply a complete measured sweep; the analysis rejects partial coverage |
| `libXtst.so.6` missing | Install `libxtst6`, then relaunch the installer |
| Locale initialization error | Generate `en_US.UTF-8` |
| Vivado unavailable | Source the installation's actual `settings64.sh` |
| Existing output directory | Use the automatically allocated destination or a matching `--resume` |
| Incomplete evidence | Read that configuration's `console.txt`; partial runs cannot replace the reviewed analysis |
| Timing disagreement | Inspect both setup and hold slack, and the unconstrained-path checks |
