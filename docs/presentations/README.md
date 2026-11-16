# Systolic Array Scaling presentations

| Edition | Slides | Use |
|---|---:|---|
| [01 — Illustrated edition](01-systolic-array-scaling-19-slides.pptx) | 19 | Completed illustrated deck before the additional analysis appendix |
| [02 — Expanded edition](02-systolic-array-scaling-expanded-32-slides.pptx) | 32 | Adds cycle accounting, resource comparisons, all-budget speedup, spatial activity, and shared-clock progress |
| [03 — Readable edition](03-systolic-array-scaling-readable-32-slides.pptx) | 32 | Recommended: consistent black text on light surfaces, yellow accents, and the original blue background |
| [03 — PDF preview](03-systolic-array-scaling-readable-32-slides.pdf) | 32 | Preview of the readable edition |
| [Technical Markdown deck](systolic-array-scaling-technical.md) | Extended | Educational explanation with equations, worked examples, diagrams, complete results, and discussion prompts |

All three PowerPoint editions preserve the original eight illustrated slides and the original study's measurements. Text, charts, tables, and display equations remain editable. The decorative background and logo are image assets. The nineteen-slide edition retains its original material, with the inherited formula images converted to Office Math.

The expanded editions contain a thirteen-slide main sequence and nineteen supporting slides. Use the [five-minute narration](../../deliverables/presentation/narration.md) for the main sequence. The full appendix supports a longer presentation or questions.

## Reading the Markdown deck

Open the repository as an Obsidian vault, enable the **Slides** core plugin, open the Markdown deck, and select **Start presentation** from the command palette. Blank lines surrounding `---` separate slides. The note remains readable in normal Markdown editors, including VS Code. See the [official Obsidian Slides instructions](https://help.obsidian.md/plugins/slides).

The Markdown edition uses text, equations, Markdown tables, and Mermaid source. It contains no rasterized equations or slide screenshots. It complements the [final report](../../deliverables/report/final-report.pdf) and [architecture specification](../architecture.md).

## Versioning and publication

The numbered PowerPoint files preserve the requested editions. Git records subsequent revisions to each file. The latest PDF is a preview of the curated PowerPoint, while report numbers and tables come from the saved measurements.

`make publish` rebuilds the final report and selected analysis, then copies the latest reviewed PowerPoint and PDF into `build/documents/`. It preserves these numbered native decks and the archived Beamer outline.
