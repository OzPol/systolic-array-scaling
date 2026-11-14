# IEEE report source

[The report PDF](main.pdf) and [editable LaTeX source](main.tex) cover all 18 simulation configurations and all three measured post-route FPGA implementations. The report separates constrained internal timing from board I/O timing and compares useful throughput per measured DSP.

To reproduce the figures and PDF:

1. Activate the project's Python environment and run `python -m analysis.report --simulation results/verification/ghdl_sim_results.csv` from the repository root.
2. Use the committed Vivado reports under `results/vivado/` and `results/summary_vivado.csv`; no new Vivado run is needed.
3. Compile with a TeX distribution containing `IEEEtran`, `amsmath`, `amssymb`, `booktabs`, `graphicx`, and `hyperref`:

```bash
cd deliverables/report
mkdir -p ../../build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../build main.tex
cp ../../build/main.pdf main.pdf
```

4. Inspect every rendered page, equation, table, and plot label before submission. The [course guidelines](../../docs/eel5764_project_guidelines_fall_2026.pdf) specify an IEEE double-column paper.

Upload the source and generated plot PNGs to an IEEE conference project in a LaTeX editor if you prefer that workflow. Keep the relative figure paths consistent with your project's root.
