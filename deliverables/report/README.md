# IEEE report

[main.pdf](main.pdf) and its editable [LaTeX source](main.tex) describe all 18 simulation configurations and the three N=16 post-route FPGA implementations. The main text covers architecture, verification, cycle accounting, scaling, throughput, resources, related work, and timing scope. The appendix contains both complete activity atlases.

The source inserts generated tables and numeric values from `results/analysis/`. Grid-to-grid comparisons and speedup plots use the matching 2×2 RTL configuration as their reference. ASIC energy, CPU speedup, pruning, and application accuracy from related work are not measurements of this project.

From the repository root, refresh the selected analysis and both PDFs together:

```bash
python scripts/experiment.py --publish
```

This needs the pinned Python environment and Tectonic or a complete pdfLaTeX distribution with IEEEtran, Beamer, TikZ, booktabs, and standard Times/Helvetica fonts. GHDL and Vivado are unnecessary when analyzing the archived evidence. The workflow builds in a temporary location before replacing current generated views.

To compile only the documents against existing generated results:

```bash
python scripts/build_documents.py
```

That writes `build/documents/report.pdf` and `build/documents/presentation.pdf`. Direct compilation of `main.tex` also works from this directory with a complete LaTeX installation. Inspect rendered pages before distributing a changed report.
