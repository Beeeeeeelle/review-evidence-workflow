# Project configuration and data contracts

## Configuration

`init` copies `assets/review-config.template.json`. Set `status` to `ready` only once
`unit_of_analysis` and `research.decision_rule` are substantive. Configure stages, fields,
answer options, reviewer IDs, minimum coverage, quote word limit and action labels.
`required: true` requires that the field appear in each record. `not_assessed` marks a
present but unfinished field; it is available for independent human coding but is omitted from assisted verification until a proposal exists.
Omit inapplicable optional fields or explicitly code NA with rationale.

Fields use `source_extraction` for what a source reports and `descriptive_coding` for
review-team classification. `synthesis` is rejected in the single-source UI. UI groups
only organize fields; one human action applies to exactly one atomic field.

`derived_rules` defaults to empty. The supported operation `all_equal` has `id`,
`fields`, `required_value`, `failure_values`, `success`, `failure`, `unresolved`.
It is for explicitly authorized project logic. TALL's historical rule, for example:

```json
{"id":"tall_gate","operation":"all_equal","fields":["Q2","Q4"],"required_value":"Yes","failure_values":["No"],"success":"PASS","failure":"FAIL","unresolved":"REVIEW"}
```

This is not a universal MMAT rule. Agency has no automatic JBI exclusion rule.

## Bundle

`bundle.json` uses schema version `1.0` and matches config `project_id`,
`protocol_version`, `codebook_version`. It additionally has `assignment_id`, `records`
and optional `outputs`. A minimal record is:

```json
{
  "record_id":"R001","title":"Source title","doi":"10.example/source",
  "source":{"path":"sources/R001.pdf","sha256":"64 lowercase hex characters","page_count":12,"identity_status":"matched"},
  "items":[{
    "field_id":"design","status":"proposed","value":"Systematic review",
    "rationale":"Methods states the design.","missingness":null,
    "evidence":[{"pdf_page":3,"printed_page":"102","section":"Methods","quote":"The exact short source passage."}],
    "depends_on":[]
  }]
}
```

IDs use letters, digits, underscores, hyphens or dots (first character alphanumeric).
Source paths are relative PDFs confined to the project directory. Hashes are SHA-256
of PDF bytes. PDF pages are one-based physical pages, not printed pagination.
A dossier hash/page count does not by itself establish bibliographic identity.

NR means not reported after checking locations: value `NR`, missingness `NR`,
`checked_locations: [{"pdf_page":3,"section":"Methods"}]`, and a rationale explaining
what was searched. NA means not applicable with reason. Unclear means ambiguous with
source evidence. Unassessed uses status `not_assessed`, null value, no evidence; it is
not a completed review. Ordinary proposed values require evidence and obey configured
options. A quote limit limits display length, not required reading depth or distribution rights.

Dependencies are canonical `record_id/field_id` strings. Cycles and unknown keys are
rejected. Outputs use `{"id":"table1","depends_on":["R001/design"]}`. Changed inputs
invalidate transitive dependent fields and registered outputs. Rebuild affected fields
in a new assignment; the helper flags outputs, it does not regenerate a manuscript.

## Reviewer return and version binding

Exports carry the `binding(config,bundle)` keys plus `reviewer_id`, `exported_at`,
`responses`, optional `draft_responses`, events and an explicitly limited activity estimate.
An assisted response is `{key, action, comment, reviewed_at}`; actions are `accept`, `revise`, `unclear`. Both non-accept actions require a nonempty explanation. Drafts do not count
as processed. `compare` accepts one latest file per assigned reviewer.

Bindings include project/assignment/protocol/codebook IDs, canonical-JSON SHA-256 of
config and bundle, verification mode, and PDF byte hashes. Canonical JSON means UTF-8,
sorted object keys, compact separators, unescaped Unicode. These detect accidental
mixing/version drift; they are not cryptographic signatures or reviewer authentication.
The browser also rejects another reviewer's return and namespaces local storage by
these bindings. Copying a package to another computer requires exporting/importing JSON;
local browser storage alone is not a durable handover.

## Human decision record

Create `decisions.json` only from an actual authorized human instruction. Use the
binding keys from comparison, `comparison_sha256` from the helper's `digest(comparison)`,
`human_authorized: true`, `authorized_by`, `authorized_at` and `decisions` array.
This records an assertion of authorization; it does not verify a person's identity.

Each explicit decision has `key`, `disposition` (`adopt`, `retain`, `select_review`, `unresolved`) and
`rationale`. An adopted correction additionally supplies `value`, `evidence`,
`missingness` and, for NR, `checked_locations` in the same item schema. For example:

```json
{"key":"R001/design","disposition":"retain","rationale":"The adjudicator checked the full Methods and retained the stated design."}
```

Required reviewer coverage must be complete before adopt/retain. Fields accepted by
all required reviewers can be authorized together by the actual human release instruction;
unresolved challenges are never silently accepted. `finalize` validates the embedded
reviewer returns and reconstructs the comparison states before using decisions.
It retains corrected evidence, human reasons, response history and source fingerprints.
Completeness covers fields, not automatic semantic validation of downstream outputs.
Do not invent release authorization or synthesize reviewer signatures for a live review.

## Version 1.1 round and independent contracts

The project schema remains 1.0; package schema is 1.1. `codebook_governance` requires
origin `human_led` or `human_developed`, nonempty provided_by and source. A developing
codebook is allowed if its current rules are usable for the assigned calibration task.
See rounds.md for reviewer profiles. Legacy V1 configs need this metadata added in a
new project version; do not retrofit old returns to a newly hashed config.

Package bindings add package_schema_version, review_mode and assignment_sha256; source
fingerprints are scoped to assigned records. Package data is a whitelist projection.
Independent items contain only field_id and awaiting_human status; field definitions
and original PDFs remain. An independent response includes action submit/defer,
committed:true, key, comment, reviewed_at; submit additionally requires value,
missingness, rationale, evidence and/or checked_locations under the field contract.
Drafts belong in draft_responses and cannot count toward coverage.

The comparison state concordant_independent_values compares exact JSON values and
missingness codes, not evidence quality or statistical agreement. It never auto-releases.
A human decision can use `select_review` plus reviewer_id and rationale to choose an
actual submitted independent response; `adopt` records a separately adjudicated value.
`retain` applies to proposals actually exposed in assisted review. Required coverage
still applies. An actual global human authorization record is required for finalization.

Source replacement requires a new source manifest and recoding. Codebook version changes
through new-round reset all proposals. Corrected upstream proposals invalidate registered
dependents transitively. A blank independent round jointly supplies its initial values;
there is no previous AI value to invalidate, but later corrections still require a new
round and re-verification of affected fields. Completeness is about the configured bundle,
not all records in the original search universe.
