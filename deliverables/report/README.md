# Final report

[final-report.pdf](final-report.pdf) and its editable [LaTeX source](final-report.tex) describe all eighteen simulation configurations and the three N=16 post-route FPGA implementations. The report covers architecture, verification, cycle accounting, scaling, throughput, resources, related work, and timing scope. Its appendix contains both complete activity atlases.

Tables and numerical macros come from `results/analysis/`. Comparisons use the matching 2×2 RTL configuration. The selected measurements are the original saved simulation and Vivado evidence. Report revisions remain in Git history under the same descriptive filename.

From the repository root:

```bash
make publish
```

This validates the archived study, regenerates its analysis, compiles the final report in a staging directory, and packages the reviewed native presentation. A failed document build leaves the current published analysis and report intact.

To compile against existing generated results:

```bash
python scripts/build_documents.py
```

Outputs are `build/documents/final-report.pdf`, `presentation.pptx`, and `presentation.pdf`. The source can also be compiled directly from this directory. Compilation requires Tectonic or a complete pdfLaTeX installation with IEEEtran, TikZ, booktabs, and the report's font packages.
