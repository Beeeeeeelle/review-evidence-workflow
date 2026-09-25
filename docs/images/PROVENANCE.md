# Visuals: provenance and reproduction

Created on 2026-09-25 for the repository's English/Chinese landing pages and case walkthroughs. Screenshots were captured from the running v1.1 workbench in the Codex in-app browser at its existing 1280 × 720 viewport. They are actual browser captures, not generated UI mockups.

## Screenshots

| File | Material | Interpretation |
|---|---|---|
| `workbench-assisted.jpg` | `examples/make_examples.py` → review-level assisted package | Unmodified application with explicitly fictional data and a synthetic one-page PDF |
| `workbench-independent.jpg` | Same example → review-level independent package | Blank independent form; no reviewer answers have been entered |
| `tall-workbench.jpg` | TALL I031, DOI [10.14742/ajet.10402](https://doi.org/10.14742/ajet.10402); PDF page 4, printed page 20 | Real-source two-field adaptation in the current workbench; assignment reporting and descriptive interpretation |
| `agency-workbench.jpg` | Agency MR00192, DOI [10.1111/bjet.70058](https://doi.org/10.1111/bjet.70058); PDF page 6 | Real-source two-field adaptation; measurement reporting and descriptive interpretation |

For the two case captures, documentation-only preview copies bring the two fields into one stage, tighten spacing, and replace the full-PDF pane with an attributed short excerpt. The pane, instructions and captions explicitly identify this as a public illustration. Line-break hyphenation in excerpts is normalized. These views do not reproduce the historic review interface or a historic reviewer session, and are not distributed as valid review assignments. No real human response, private reviewer identity, institutional access watermark or full-text PDF is published here.

The normal application displays the full locally supplied PDF (or its rendered pages), as shown in the synthetic screenshot. The case illustrations show how real material maps to the reusable interface; the downloadable synthetic packages are the runnable examples.

To reproduce the synthetic captures, generate the examples, serve the output locally, open the two review-level packages in an empty browser state, and capture the browser without entering responses. See [Try the demos](../TRY_DEMOS.md). Real-case captures require access to the cited sources and the documented adapter values; those PDFs are not bundled.

## Diagrams

| Files | Purpose and evidence boundary |
|---|---|
| `workflow-en.svg`, `workflow-zh.svg` | The released skill's intended division of work, optional review branches, return path and revision loop. Not a measured speed/accuracy result. |
| `tall-change-en.svg`, `tall-change-zh.svg` | First two boxes summarize the retained I031 adjudication note of 2026-07-20. Third box states the reusable skill's response; not an assertion of complete historical downstream tracing. |
| `agency-layers-en.svg`, `agency-layers-zh.svg` | Source-reporting example and the project's separation of coding from synthesis. Does not claim completed cross-review synthesis. |

The SVGs have white backgrounds, accessible titles and editable text. Orange denotes human judgment, blue denotes AI-assisted preparation, and gray denotes source/software context. Arrows describe sequence or dependence, not measured causal effects. Dashed connections mark a revisiting or further-work relationship.

Regenerate all six with Python's standard library:

```bash
python3 docs/images/draw_diagrams.py
```

[Generator source](draw_diagrams.py) · [TALL provenance](../../review-evidence-workflow/references/cases/tall.md) · [Agency provenance](../../review-evidence-workflow/references/cases/agency.md) · [Validation](../VALIDATION.md)

Third-party source excerpts retain their original rights; the repository's MIT license does not grant rights to the cited articles. The surrounding UI, diagrams and synthetic fixtures are part of this repository.
