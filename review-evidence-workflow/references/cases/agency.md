# Case 2 — Agency: review-level evidence synthesis

## Status and provenance

This is an implemented **pilot** case, inspected on 2026-09-25. It is not a completed
cross-review synthesis or a completed independent-review validation. Source artifacts:

- Project `Agency`, `outputs/full_text_screening_workflow_v1/README.md`.
- `outputs/full_text_screening_workflow_v2/rubric.json` and
  `PILOT_EXTRACTION_CODEBOOK_v2.md`.
- `outputs/full_text_screening_workflow_v2/coding/MR00192.json`.
- `outputs/meta_review_protocol/Meta_Review_Protocol_v5.md`.
- `outputs/coauthor_coding_packages_2026-09-25/` package instructions.

Provenance paths are relative to the original project, not runtime dependencies.
The case does not distribute PDFs, coauthor identities, or private reviewer returns.

## Project adapter

- Unit: included review, not an independently re-analysed primary study.
- Scope: all AI-supported educational learning, with GenAI separately coded.
- Eligibility: F1–F6 and at least one of A/B/C: explicit agency/control;
  enacted regulation/autonomy; or a conditional agency-related construct with
  an explicit analytical connection to learner direction/control.
- Appraisal: 11 item-level JBI judgments, after inclusion; no numerical total or
  automatic exclusion based on appraisal.
- Three layers: source extraction, descriptive coding, cross-review synthesis.
- Extraction: review landscape, search strategy, construct definitions,
  review-level propositions, actor locus, allocation movement, AI role, agency
  implications, linked enabling/constraining conditions, limitations and gaps.
- Later synthesis: review families, underlying-study identity/overlap, convergence
  and discordance; do not fill these from one review alone.

## Observed example: MR00192

The pilot record identifies *AI support in self-regulated learning: A decade of
technological evolution and meta-analysis* (DOI `10.1111/bjet.70058`). Its provisional
screening evidence includes this source excerpt (line-break hyphenation normalized) at PDF page 6, under
“Study characteristics and intervention coding”:

> relevant variables—such as goal setting, strategy planning, self-efficacy,
> metacognitive monitoring, time management and self-evaluation—were aligned
> with the appropriate SRL phases.

The example shows why a field needs a page and context, and why a regulation pathway
requires substantive process evidence. This single passage alone does not establish
all eligibility criteria, causal effects, or a final human inclusion decision.

The v2 codebook separates exact source wording from coder interpretation, and
actor locus from allocation movement and agency implication. For example, task
delegation to AI does not by itself determine whether agency is expanded or eroded.
That is a coding distinction, not a new empirical conclusion supplied by this skill.

## Observed vs planned

The documented pilot screened 10 reports and provisionally coded 6 included reviews.
Those pilot counts are a snapshot. The codebook's freeze rule calls for joint
verification of at least 10 included reviews; do not confuse reports screened with
reviews included, or infer that the freeze/human verification has occurred.

The formal protocol plans independent human screening and appraisal. The current
coauthor calibration packages show AI-generated proposals and Correct/Revise
controls. Those packages implement assisted verification; their existence does not
prove that the independent portions of the protocol have been completed.

## What transfers

Page-linked evidence, correctable field proposals, versioned codebooks, offline
reviewer packages, separate reviewer returns, and source-to-claim tracing transfer.
The explicit separation of source wording, coding, and synthesis is useful beyond
meta-reviews. Overlap mapping is specifically relevant when evidence is reused
across reviews/reports; it is not automatically required for every review design.

## What must not transfer

Do not copy the agency pathways, 14 learning functions, JBI choice, pilot size,
freeze threshold, or review-level inference rules into a primary-study review.
Choose those from the new project's question and design.
