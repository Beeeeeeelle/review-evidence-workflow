# Review Evidence Workflow

**A reusable agent skill for human-led literature review: full-text retrieval and checks, flexible coding rounds, personalized reviewer UI, and traceable decisions.**

Humans develop the codebook and make scientific decisions. AI applies the current rules,
organizes source evidence and helps people verify it. The helper scripts handle packaging,
version checks, returned files and change tracking.

[中文使用说明](docs/README.zh-CN.md) · [Step-by-step guide and sample prompts](review-evidence-workflow/references/getting-started.md) · [Workflow and human/AI roles](review-evidence-workflow/references/rounds.md) · [Validation](docs/VALIDATION.md)

## When to use it

- You have a study list, protocol/codebook and some PDFs, and want repeatable full-text screening, appraisal or extraction.
- Your team is developing a codebook on a chosen pilot sample, then wants AI to apply it to later batches for human verification.
- Different reviewers need different records, fields, instructions or review modes.
- Reviewers receive separate packages and return JSON files; you need to compare them without losing source/version provenance.

This is an offline review workbench, not a hosted multiuser service. It does not decide
scientific eligibility, write/approve a human codebook autonomously, or prove AI accuracy
or time savings.

## Two modes, chosen by round or reviewer

| Mode | Reviewer sees | Reviewer does | Coordinator receives |
|---|---|---|---|
| Assisted verification | AI proposal, rationale, page-linked evidence, original PDF | Correct / Revise / Unclear, with reasons | Source-bound verification responses |
| Independent review | Human codebook definitions, original PDF, blank form; AI/peer feedback omitted from package data | Enter value, rationale and evidence; save or defer | Independent entries for comparison/adjudication |

A team may start with 10 papers, 5 papers or another sample to develop its codebook.
It may then use AI coding plus human verification, add an independent check, or return
to calibration. No fixed sample size, number of rounds or universal quality threshold
is imposed. Independent packages support independent conduct; they cannot prove it or
remove prior exposure to suggestions.

## Install in Codex

Download or clone this repository. Copy the `review-evidence-workflow` folder to your
Codex skills directory (`~/.codex/skills/` in the environment used for this release).
If that name already exists, preserve it before replacing it. Start a new session so
Codex discovers the installed skill, then invoke `$review-evidence-workflow`.

The skill uses relative internal paths; it does not require this author's projects.
For another agent host, follow that host's skill installation conventions. Cross-host
runtime support has not been verified in this release.

**Requirements:** Python 3.9+; Poppler for PDF checks/text/page images (`brew install
poppler` on macOS, or `sudo apt-get install poppler-utils` on Debian/Ubuntu). The Python
helpers use only the standard library. Reviewers need only a current browser, not Python
or an AI account. With verified sources, packages can use the browser PDF viewer without
rendering; rendered pages give a more consistent offline experience.

**PDF retrieval:** If `literature-pdf-retrieval` is installed, the agent composes that
skill for finding and validating full texts. It is optional: this package includes a
local PDF handoff validator and a documented search/browser fallback. No paid API key,
institutional account or inaccessible private skill is required to run the examples.

## Try six runnable packages

From the repository root:

```bash
python3 examples/make_examples.py --out /tmp/review-workflow-demo --render-pages
```

Use a new output directory for each run. Open, for example:

- `/tmp/review-workflow-demo/primary-study-assisted/OPEN_ME.html`
- `/tmp/review-workflow-demo/primary-study-independent/OPEN_ME.html`
- `/tmp/review-workflow-demo/review-level-independent/OPEN_ME.html`
- `/tmp/review-workflow-demo/field-report-assisted/OPEN_ME.html`

The generator creates three projects, each in both modes. All PDFs, coding values and
codebook providers are **explicitly fictional**. You can change a field, save progress,
export a JSON and import it to resume. The examples are not research findings or actual
human reviewer judgments.

For actual projects, give the agent your materials and a request such as:

> Use $review-evidence-workflow. Our team developed this codebook on a pilot sample.
> Apply v2 to the remaining PDFs and make separate source-linked verification packages
> for reviewers A and B. Preserve uncertainty and return a coverage report.

Or:

> Use $review-evidence-workflow to prepare blank independent packages for our calibration
> sample. Do not include AI suggestions or other reviewers' feedback. Help us compare
> returned files before we revise the codebook.

[More prompts and reviewer instructions](review-evidence-workflow/references/getting-started.md).

## From input to review output

| Step | AI/software assistance | Human responsibility | Output |
|---|---|---|---|
| 1. Scope and codebook | Map supplied rules to fields; expose ambiguities | Develop criteria/codebook; choose current sample/mode | Round configuration |
| 2. Full texts | Locate legal copies; record attempts; check DOI/title/pages/hash | Supply access if needed; resolve ambiguous identity/completeness | Accepted manifest + remaining queue |
| 3. Coding | Apply current human-led rules with source evidence, or prepare blank forms | Calibrate meanings and decide rule revisions | Proposals or blank assignment |
| 4. Reviewer package | Select records/fields; build offline UI and source navigation | Read full sources, verify or independently code | Reviewer JSON |
| 5. Comparison | Validate versions/coverage; align differences and evidence | Resolve disagreement; authorize release | Decision record and ledger |
| 6. Change | Detect replaced hashes; invalidate registered dependencies | Decide/review revised coding and conclusions | New round and recomputed outputs |

The exact command sequence, inputs and next-person instructions are in
[SKILL.md](review-evidence-workflow/SKILL.md), [contracts](review-evidence-workflow/references/contracts.md),
[PDF handoff](review-evidence-workflow/references/pdf-handoff.md) and
[round settings](review-evidence-workflow/references/rounds.md).

## Cases and distinction from related tools

[TALL](review-evidence-workflow/references/cases/tall.md) supplies a retrospective
primary-study implementation case. [Agency](review-evidence-workflow/references/cases/agency.md)
supplies a review-level pilot adaptation. They motivate reusable design; they are not
two completed, equivalent validation experiments. The archaeology example tests technical
transfer to a third unit and vocabulary, not scientific generalizability.

Literature search, evidence ledgers, annotation UIs and human approval gates already
exist. This skill connects them through configurable rounds, source-bound field judgments,
content-separated reviewer packages, offline JSON returns and downstream invalidation.
See [related work and positioning](docs/RELATED_WORK.md). No priority or superiority claim
is made.

## Validate or contribute

```bash
python3 -m unittest discover -s tests -v
node --check review-evidence-workflow/assets/app.js
```

Tests cover version rejection, incomplete coverage, independent data omission, human
release requirements, source replacement, draft handling and cross-domain examples.
GitHub Actions runs the same portable checks; a configured workflow is not a claim that
cloud CI has already run. [Validation report](docs/VALIDATION.md) distinguishes local
checks, browser observations and untested claims.

Keep tests and examples synthetic. Do not commit real reviewer returns, institutional
credentials or third-party full texts. Report the command, expected/actual result and
an anonymized minimal fixture when filing a bug. Suggested improvements should preserve
human authority, configurable research rules and source/version provenance.

MIT license applies to this code, documentation and synthetic fixtures. It grants no
rights to PDFs a user retrieves or adds to their own project.
