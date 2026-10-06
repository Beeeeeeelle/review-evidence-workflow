# Case 3 — Combined full-text screening and coding

## Status and provenance

This case was distilled on 2026-10-06 from a coauthor calibration workbench for an
AI/GenAI literacy measurement review. It documents a reusable interaction pattern,
not completed screening results, reviewer agreement, or a validation study. No source
PDFs, reviewer answers, or project-private records are included here.

The scientific criteria in that project remain project-specific. The transferable part
is the routing: make one full-text eligibility decision, then show only the work that
logically follows from that decision.

## When to use this pattern

Use it when one independently working reviewer should handle a report in a single pass:

1. decide full-text eligibility;
2. if included, continue to quality appraisal and coding;
3. if excluded, record one primary exclusion reason and stop that record.

This avoids asking an included report for an exclusion reason or asking an excluded
report for appraisal and extraction. It also keeps quality judgments conceptually
separate: weak quality does not silently reverse an eligibility decision unless the
protocol explicitly says it should.

## Routing contract

| Eligibility state | Screening stage | Quality/coding stages | Progress and export |
|---|---|---|---|
| No route chosen | Show the eligibility field | Locked | Count only the currently applicable screening field |
| Include | Hide the exclusion-reason field | Open immediately | Count/export eligibility plus applicable downstream fields |
| Exclude | Show exactly one primary exclusion-reason field | Not applicable | Count/export eligibility plus exclusion reason only |

Route selection and answer completion are separate states. Selecting Include may open
later stages immediately so the reviewer can work naturally, but the eligibility answer
does not count as complete until its required rationale and source evidence are saved.
Inactive branch responses are retained only in browser-local state in case the reviewer
switches back; they are omitted from export and listed as `not_applicable_fields` in a
finalized ledger.

## Configuration recipe

Put `applies_when` on a whole stage when all fields share the route, and on an individual
field for a branch-specific field in an otherwise shared stage. The controller must be
an unconditional required field with configured options.

```json
{
  "verification": {
    "mode": "independent_review",
    "reviewers": ["reviewer-a"],
    "min_reviewers": 1
  },
  "ui": {
    "stages": [
      {"id": "screening", "label": "Full-text eligibility"},
      {
        "id": "quality",
        "label": "Quality check",
        "applies_when": {"field_id": "eligibility", "values": ["Include"]}
      },
      {
        "id": "coding",
        "label": "Coding",
        "applies_when": {"field_id": "eligibility", "values": ["Include"]}
      }
    ]
  },
  "fields": [
    {
      "id": "eligibility",
      "label": "Full-text eligibility",
      "definition": "Apply the project's full-text inclusion and exclusion rules.",
      "stage": "screening",
      "layer": "descriptive_coding",
      "options": ["Include", "Exclude"],
      "required": true,
      "allow_missingness": false
    },
    {
      "id": "exclusion_reason",
      "label": "Primary exclusion reason",
      "definition": "Select one reason only when the report is excluded.",
      "stage": "screening",
      "layer": "descriptive_coding",
      "options": ["Wrong population", "Wrong construct", "No usable evidence"],
      "required": false,
      "allow_missingness": false,
      "applies_when": {"field_id": "eligibility", "values": ["Exclude"]}
    }
  ]
}
```

An inclusion tier can use several values, for example `values: ["Include - primary",
"Include - boundary"]`. Do not hard-code those labels in the app; keep them in the
project configuration and codebook.

## Review design boundary

The built-in conditional route is intentionally limited to independent packages with
one required reviewer per field. If two reviewers independently screen the same report,
their eligibility decisions may put them on different downstream branches. Resolve that
eligibility disagreement first, then open a coding round for reports retained by the
team. Do not count one reviewer's inclusion-branch coding as dual-reviewed merely because
another reviewer excluded the report.

This restriction does not prohibit several reviewers from working on disjoint records;
it prohibits treating divergent routes on the same record as complete multi-reviewer
coverage. Assisted-verification proposals are also excluded from this routing mode:
when eligibility itself may be revised, a proposal value is not a safe branch controller.

## What transfers

Conditional stage/field visibility, immediate route updates, branch-specific progress,
inactive-response filtering, explicit `not_applicable_fields`, and the separation between
route selection and evidentiary completion transfer to other reviews.

## What must not transfer

Do not copy the AI-literacy construct boundary, measurement contribution types, quality
gate, exclusion labels, or number of downstream coding fields. Do not assume that all
reviews should combine screening and coding. Use separate rounds when eligibility needs
dual independent review, when the codebook is still changing materially, or when a team
wants to blind coders to earlier screening judgments.
