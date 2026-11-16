# Analysis in Visual Studio Code

From the repository root in Ubuntu, open the existing checkout:

```bash
code .
```

Use the VS Code WSL extension and select `.venv/bin/python` as the Python interpreter. The pinned plotting environment requires Python 3.12+; complete the one-time [setup](setup.md) first.

Choose **Terminal → Run Task → Analyze selected experiment**, or run:

```bash
make analysis
```

The printed timestamped directory contains `metrics.csv`, `hardware_metrics.csv`, the comparison table, and PNG/SVG plots. Its adjacent `visualization` folder contains the offline replay and trace figures. Edit `analysis/plots.py` and rerun the command to create another separate analysis. The published measurements stay intact.

Use `make unit` for the Python integrity checks. `make study` runs the full simulation/FPGA experiment with automatic output naming; it requires GHDL and Vivado. Existing-data analysis requires neither hardware tool.
