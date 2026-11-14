# IEEE report source

`main.tex` is a draft manuscript in IEEE conference format, based on measured simulation data and the existing P=2 FPGA report. It explicitly marks the missing P=4/P=8 FPGA evidence. It has not been compiled in this workspace, where a TeX installation is unavailable.

After collecting final FPGA results:

1. Run `python -m analysis.report` from the repository root.
2. Replace the pending FPGA table rows using actual post-route reports.
3. Update the hardware discussion, abstract, and conclusion if the measured outcome changes them.
4. Compile with a TeX distribution containing `IEEEtran`, `amsmath`, `booktabs`, `graphicx`, and `hyperref`:

```bash
cd deliverables/report
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

5. Inspect every page, references, equations, tables, plot labels, and remaining draft/pending text. The source alone is not a completed final PDF.

Upload the source and generated plot PNGs to an IEEE conference project in a LaTeX editor if you prefer that workflow. Keep the relative figure paths consistent with your project's root.
