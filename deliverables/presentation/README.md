# Presentations and narration

The [presentation index](../../docs/presentations/README.md) preserves all three editable PowerPoint editions: the 19-slide edition, the expanded 32-slide edition, and the 32-slide edition with consistent black text and yellow accents. The latest edition is the recommended presentation. Charts and tables are native objects, and display equations use Office Math.

[narration.md](narration.md) covers the thirteen-slide main sequence in approximately five minutes. The remaining nineteen slides provide supporting analyses and detailed reference tables.

The [technical Markdown deck](../../docs/presentations/systolic-array-scaling-technical.md) develops the dataflow, arithmetic, cycle model, verification, performance metrics, and FPGA interpretation in more detail. It works as an Obsidian note with slide separators and editable mathematical notation.

`make publish` rebuilds the final report and analysis, then packages the reviewed PowerPoint and PDF preview under `build/documents/`. It preserves the native charts and equations. Edit the PowerPoint deliberately when changing the selected study, then refresh its PDF preview.

The earlier Beamer outline and its narration remain in [archive/](archive/). The original video storyboard remains in [video/outline.md](../video/outline.md).

The [TM editions and substantive review](../../docs/presentations/TM-review.md) continue the version catalog with a 31-slide reference deck and an 11-slide recording deck. The latter retains all [speaker notes](../../docs/presentations/TM-05-speaker-notes.md).
