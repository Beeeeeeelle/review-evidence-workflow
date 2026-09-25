# Validation record — v1.1.0 baseline and v1.2.0 reader

Validation date: 2026-09-25. This report concerns reusable software behavior and guided
workflow execution. It does not establish scientific validity, reviewer independence,
AI accuracy, generalizability to all reviews or measured time savings.

## Rounds performed

| Pass | Inputs and method | Observed result |
|---|---|---|
| 1. Structure and contracts | skill-creator frontmatter check; Belle 23-item manual audit; original 20 backend tests | Format accepted; critical governance/version/source checks passed |
| 2. New behavior and transfer | 40 distinct automated tests, including independent forms, personalized scope, draft rejection, codebook revision, PDF identity/queues/replacement; three synthetic domains × two modes | All 40 passed on Python 3.9 and 3.12 locally; six packages generated |
| 3. Independent forward test | Fresh-context evaluator received only repository, realistic archaeological-review request and synthetic examples; 17 workflow commands + 5 source/dependency commands | CLI/payload path completed; two small issues found and fixed before release |
| 4. Browser and case checks | CUA interaction with synthetic independent/assisted packages; local TALL/Agency two-field adapters and real PDFs | Save/draft/defer/export/restore/reject incompatible return observed; source handoff accepted each case PDF; full-page packages generated |

Forward testing did not assume access to the author's private PDF retrieval skill. It
successfully created a human-calibration round from local synthetic PDFs, compared two
separate returns, left disagreement unresolved, enforced TEST-only human release records,
opened a revised-codebook round, rejected old returns, prepared new proposals and compared
assisted responses. A missing source stayed queued while an accepted one proceeded.
A replaced source flagged its affected fields. Required-Poppler failures were clear;
verified-source builds without page rendering worked with Poppler absent from PATH.

## Observed fixes

1. The cold-start evaluator found that `validate` reported zero “reviewable fields” for
   a valid blank independent round. The summary now reports `total_fields`,
   `proposed_fields`, `assigned_fields`, and each reviewer's mode/assigned count.
2. README linked to a validation report that was still being prepared. This report now
   resolves that link and records the limits of the evidence.
3. During browser hardening, the independent form was extended to preserve and edit
   multiple source locations instead of displaying only the first location.
4. Selecting revised human evidence invalidates registered dependents even when the code value stays the same; a dedicated regression test covers this.
5. Independent navigation text now describes saved answers rather than accepting proposals.

The independent evaluator rechecked both fixes: the blank round reports 2 total, 0 proposed and 2 assigned fields; all 22 audited local Markdown links resolve.

## Browser observations

Environment: Codex in-app browser on macOS, local HTTP test server, rendered PDF pages.
Only clearly synthetic responses were entered; no real reviewer decisions were invented.

- Blank independent fields displayed codebook definitions and original PDF, without
  AI values/rationales/quotes or peer responses in package data.
- Saving one answer moved progress to 1/2; editing it returned it to draft and progress
  to 0/2. Re-saving restored the submitted count.
- A reasoned deferral produced 2/2 processed, 1 submitted and 1 needing resolution;
  “processed” was not treated as finalized.
- Browser export created a real JSON file. Backend return validation accepted it.
- Import into an empty browser storage origin restored both responses and the pending issue.
- Importing the independent return into the assisted reviewer package was rejected on
  mode binding, preserving the existing progress.
- Adding another source location, saving and exporting retained both quotations.
- Agency page-linked evidence navigated to PDF page 6 of 30; the rendered image loaded.
  Switching source-reporting/team-coding stages preserved the distinction.

The fresh evaluator's direct `file://` navigation was blocked by the browser automation
security policy. No bypass was attempted. Direct double-click opening, all browsers,
mobile layouts, assistive-technology usability and cross-device handover have **not**
been comprehensively verified. The design is static/offline-capable; the browser evidence
above comes from the explicitly served local HTTP packages.

## Cases versus reusable examples

The two real-source adapters exercise one TALL primary-study PDF (15 pages) and one
Agency review PDF (30 pages), two fields each. They do not rerun either full research
project. Real PDFs and reviewer returns are excluded from the public repository.
Public fixtures are fictional, reproducibly generated and clearly marked synthetic.
The third archaeology fixture changes unit, vocabulary and rules to check technical
portability beyond the two motivating cases.

## Six-dimensional design check

| Dimension | Concrete contract |
|---|---|
| Scenario | Reusable full-text evidence review from available inputs to requested stage |
| Procedure | Human-led codebook → source handoff → mode-specific package → separate returns → adjudication/versioning |
| Data | Config, source manifest, bundle, reviewer JSON, comparison, decisions, ledger |
| Tools | Python standard library, Poppler, invoking agent's authorized search/browser tools |
| Quality | Source/version/coverage checks; no invented human responses or silent release |
| Assumption | Evidence organization can support faster verification; actual efficiency requires evaluation |

## Belle 23-item manual audit

The local `belle-skill-design` checklist was used as a design review, not a scientific
validation instrument. The skill is a workflow tool; dialogue/audit-genre extensions do
not apply. A fresh-context forward test was nevertheless performed because reuse matters.

| # | Check | Evidence / result |
|---|---|---|
| 1 | Name | Lowercase hyphenated name — pass |
| 2 | Description | Concrete capability and input/use conditions — pass |
| 3 | Frontmatter | name and description only — pass |
| 4 | Trigger coverage | Retrieval, calibration, UI and returned files — pass |
| 5 | Directory identity | Folder equals skill name — pass |
| 6 | UI metadata | agents/openai.yaml names the same workflow — pass |
| 7 | Prerequisites | Inputs, current stage, dependencies — pass |
| 8 | Steps | Seven stages each with a completion marker — pass |
| 9 | Output | Versioned project/package/return/ledger contracts — pass |
| 10 | Boundaries | Missing rules/sources, out-of-scope synthesis, unavailable tools — pass |
| 11 | Terms | Independent coding versus assisted verification versus release — pass |
| 12 | Completion states | DONE / DONE_WITH_CONCERNS / BLOCKED — pass |
| 13 | Quality gates | Critical and standard checks — pass |
| 14 | Examples | Good/bad calibration and content-separation examples — pass |
| 15 | Evidence grounding | PDF identity, page/source checks and semantic limits — pass |
| 16 | Suppressions | No universal sample/threshold/dual-review rule — pass |
| 17 | Entrypoint length | Under 500 lines — pass |
| 18 | Assets | Actual UI/config templates used by builder — pass |
| 19 | References | Relevant conditional guidance — pass |
| 20 | Scripts | Parameterized helpers exercised by tests and forward run — pass |
| 21 | Portability | Relative skill paths, no author's private project prerequisite — pass |
| 22 | Discoverability | All references routed from SKILL.md — pass |
| 23 | Execution | Python helpers/arguments work in observed environments — pass |

## Reproduce the technical checks

From a clean repository directory with Python 3.9+ and Poppler:

```bash
python3 -m unittest discover -s tests -v
node --check review-evidence-workflow/assets/app.js
python3 examples/make_examples.py --out /tmp/review-demo-new --render-pages
```

Use a new demo output directory each time. The generator refuses overwrite. For an
independent agent re-run, provide a fresh context with only the repository and this prompt:

> Our human team is reviewing archaeological field reports and has a developing codebook.
> Prepare separate blank calibration packages, compare returned JSONs, and show how to
> move to AI-assisted verification under revised rules. Use only the repository's
> synthetic sources, write to a new temporary directory, mark any simulated human
> responses TEST, and report blockers without assuming the desired answer.

Keep a record of actual commands, exit codes, artifacts and observed failures. Do not
replace behavioral trials with repeated runs of the same format validator.

## Limits that remain

Live online retrieval, institutional-login routes, OCR/scanned PDFs, complex multi-page
tables, a large multi-reviewer cohort, all target browsers and real efficiency/error-rate
outcomes were not evaluated in these release checks. Manual identity/authorization
records assert human actions; they do not authenticate them. Registered dependencies
can be invalidated; undeclared dependencies require review. The [first GitHub Actions run](https://github.com/Beeeeeeelle/review-evidence-workflow/actions/runs/36186782098) passed on Ubuntu/Python 3.11 for commit `21466df`. This adds a Linux execution check; it does not expand the scientific or browser claims above.

## v1.2.0 reader and real UI demonstration (2026-09-25)

42 automated tests passed on Python 3.12 with the optional pdfplumber indexer,
including source-hash binding, glyph coordinates and both portable modes. Node
checks cover exact normalized matching, line breaks, hyphenation, ligatures, missing
text, short quotes and repeated matches. No semantic similarity is used.

Browser verification: actual Pilot MR00047 exclusion; isolated Correct/Revise
responses; all five filters; MR00265's four stages, conditions/pathways; real PDF p.18
and MR00574 p.3 unique highlights; 512→612 px divider drag; 150% zoom; independent
PDF scroll; next/previous page clearing highlights. Shared portable reader also
verified on a newly built synthetic review with keyboard width 512→532 px and a
1,000 px viewport retaining the PDF while hiding the desktop divider. An updated
coauthor package rendered its own page image and quote overlay without a PDF server.

These are functional checks, not accuracy, agreement, or time-saving estimates.
The public video uses real browser captures and synthetic Chinese narration; it
contains demonstration responses, not human coauthor returns.
