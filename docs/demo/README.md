# A walk through the real Pilot workbench

**[Watch/download the guided Chinese walkthrough](pilot-guided-walkthrough.zh-CN.mp4)** · [Direct download](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/download/v1.2.0/pilot-guided-walkthrough.zh-CN.mp4) · [中文完整指南](README.zh-CN.md)

These are captures of Belle's actual **Pilot full-text coding** interface, using real project proposals and corresponding source PDFs. The revised 3:36 walkthrough has 16 chapters and 35 guided beats, conversational Chinese narration, neural synthetic speech and captions. Orange circles and labels identify controls; teal arrows connect citations to source text; editorial close-ups make small controls legible. Yellow quotation highlights come from the functioning reader.

![Guidance connects a page citation to its actual source quotation](guided-preview-evidence.jpg)

![A close-up calls attention to the Revise control](guided-preview-revise.jpg)

This is an edited walkthrough of authentic browser states, **not a continuous screen recording**. Circles, arrows, pointer cues and camera crops are editorial guidance, not application features or recorded cursor telemetry. Original captures remain in `frames/`. Demo Correct/Revise responses are stored separately and are not human research decisions.

To use the chapter player locally, run `python3 docs/demo/serve.py --port 8940` from the repository root, then open <http://127.0.0.1:8940/>.

The walkthrough covers all five report filters; excluded reports with decisive evidence; included reports with Screening, Foundational conditions and Construct pathways; Review profile; Concepts; Review-level synthesis; Correct and Revise; physical PDF pages 3 and 18; pane resizing; zoom; independent scrolling; and page navigation.

Use this workflow when a literature review needs full-text preparation, codebook calibration, rule-based coding, source verification or coordinated reviewer returns. Start with the materials you have. Humans develop the codebook and decide; AI prepares source-linked proposals and packages. A completed verification can still contain a revision requiring adjudication. Review-level synthesis represents claims made by that review, not a new analysis of its primary studies or a completed synthesis across reviews.

The resizable reader and quotation highlights are shared with the **v1.2.0 portable template**. Build with `--render-pages`; install optional `pdfplumber` in the coordinator's build environment to obtain glyph coordinates. Reviewers need only their browser. The pilot's specific eligibility rules, filters and concept pathways are project-specific, while portable stages and fields follow the team's own codebook.

Highlighting uses unique normalized text matches on the specified physical page, never semantic guesses. Scans, unavailable coordinates, paraphrases, discontinuous or duplicate matches require manual location. A highlighted quotation is a navigation aid, not a validated scientific judgment.

[Capture provenance](PROVENANCE.md) · [Chapters and narration](chapters.json) · [Concept story](../story/README.md)

[中文解说全文 / narration transcript](TRANSCRIPT.zh-CN.md)
