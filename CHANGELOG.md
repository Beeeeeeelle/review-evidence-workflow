# Changelog

This file records user-visible changes to Review Evidence Workflow. Version numbers
describe the reusable skill and coordinator tooling; a new version does not imply that
any review's scientific findings have been validated.

## 1.3.0 — 2026-10-06

### Added

- Conditional `applies_when` rules for stages and individual fields.
- A one-pass independent workflow that routes each full-text report from eligibility to
  either downstream quality/coding or one primary exclusion reason.
- `allow_missingness: false` for route questions that must use explicit codebook options.
- Branch-aware progress, export, returned-file validation, comparison and finalization.
- `not_applicable_fields` in final ledgers and `not_applicable` status for outputs that
  depend on an inactive branch.
- English and Chinese case guides for combined full-text screening and coding.

### Guardrails

- Conditional routing is limited to independent review with one required reviewer per
  field and one reviewer assigned to each routed record. Multiple reviewers may work on
  disjoint records.
- When two people independently screen the same report, eligibility must be adjudicated
  before a downstream coding round; divergent routes are not treated as review coverage.
- Choosing a route updates the interface immediately, but the controller answer still
  needs its configured rationale and source evidence before it counts as complete.

### Validation

- 47 automated tests passed; one optional pdfplumber integration test was skipped because
  that dependency was not installed in the test environment.
- Browser checks covered pending, Include and Exclude states on a newly built ten-report
  package. These checks establish software behavior, not eligibility or coding accuracy.

## 1.2.0 / 1.2.1 — 2026-09-25

- Added the reusable evidence reader, resizable PDF/coding panes, page zoom and exact
  source-quotation highlighting with explicit no-match and ambiguity fallbacks.
- Added real-interface walkthroughs, bilingual documentation and downloadable synthetic
  examples. The v1.2.1 tag points to the same release code as v1.2.0.

## 1.1.0 — 2026-09-25

- Added independent blank reviewer packages, personalized assignments, calibration
  rounds, PDF identity handoff, version-bound returns, comparison and human-authorized
  finalization.

[Chinese changelog](CHANGELOG.zh-CN.md)
