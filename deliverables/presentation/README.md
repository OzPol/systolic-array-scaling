# Technical presentation

[slides.pdf](slides.pdf) is a nine-slide presentation of the selected experiment. [slides.tex](slides.tex) is the editable Beamer source. Charts use the same generated measurements as the IEEE report; the summary table is editable LaTeX.

The presentation covers architecture, verification, compute latency, stalls, serial readout, speedup, FPGA cost, and limitations. [narration.md](narration.md) provides a short speaking outline; use the slide figures for current numerical values.

Build the slides and report with `python scripts/build_documents.py`, or refresh the complete selected evidence and documents with `python scripts/experiment.py --publish` from the repository root. See [setup](../../docs/setup.md) for dependencies.

The earlier `deliverables/video/outline.md` remains available unchanged.
