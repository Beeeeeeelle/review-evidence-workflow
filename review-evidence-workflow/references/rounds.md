# Flexible rounds and personalized packages

A round is a traceable assignment, not a prescribed research phase. People determine
which materials develop the codebook and when its current rules are usable. AI may
organize examples/ambiguities or suggest wording when asked; human decisions establish
and revise the meanings, criteria and interpretation rules.

| Possible round | Human work | AI/software work | Deliverable / next step |
|---|---|---|---|
| Human calibration (e.g. 10 chosen papers) | Develop/test rules, code, discuss ambiguities | Find/check PDFs; blank forms; compare returns | Revised human-led codebook; choose next sample |
| AI application | Supply usable codebook and scope | Evidence-grounded coding proposals on selected remaining papers | Personalized assisted packages |
| Human verification | Read sources; accept, revise, defer | Page navigation, saving, return validation | Challenges/coverage for adjudication |
| Optional independent check | Code without supplied AI/peer suggestions | Omit suggestions from each package, compare returned values | Independent responses; no automatic finality |
| Adjudication | Resolve disagreements, authorize values/release | Assemble evidence, preserve reasons, apply declared rules | Authorized or unresolved ledger |
| Revision/repeat | Change codebook/source/scope when warranted | New round; invalidate stale coding and outputs | Recode and reverify affected work |

The order can repeat or branch. Ten papers is an example, not a minimum or freeze rule.
`codebook_governance.development_status` is descriptive (developing, calibrating, in_use,
revising); the software does not infer scientific readiness from that label.

## Example configuration fragment

```json
{
  "codebook_governance": {
    "origin": "human_led",
    "provided_by": "Review team",
    "source": "Human codebook v2, Methods definitions",
    "development_status": "in_use"
  },
  "review_round": {"id":"batch-2","purpose":"Apply calibrated rules and verify"},
  "verification": {
    "mode":"assisted_verification",
    "reviewers":["reviewer-a","reviewer-b"],
    "min_reviewers":1,
    "reviewer_profiles": {
      "reviewer-a": {
        "mode":"independent_review",
        "record_ids":["R001"], "field_ids":["design"],
        "ui":{"title":"Methods worksheet","instructions":"Read the full Methods and enter your own answer.","expand_all_groups":true}
      },
      "reviewer-b": {
        "record_ids":["R001","R002"],
        "ui":{"instructions":"Verify each proposal against the complete source.","stage_labels":{"extraction":"Methods and measures"},"collapsed_groups":["Background"]}
      }
    }
  }
}
```

Absent profile selections mean all records/fields; absent profile mode uses the round's
default. Profiles never confer access to another reviewer's feedback. `field_ids` sets
field order, `record_ids` sets record order. Field `min_reviewers` can override the global
minimum; impossible coverage is rejected. Mixing modes is supported operationally but
is labelled for adjudication, not independent reliability estimation.

Personalizable UI settings: title, instructions, stage/action labels, field definitions/
options/groups, collapsed groups and group expansion. Structural field definitions and
scientific options remain the shared human codebook; do not personalize their meaning
and then treat responses as interchangeable. Styling can be edited in assets/styles.css
before a new build. There is no settings editor or central reviewer account service.

`new-round` changes assignment ID and preserves prior files. Optional `--record-ids`
selects a subset; include cross-record dependencies or revise them explicitly. A new
`--codebook-version` clears old proposals. It does not write or approve new definitions:
update the human-provided source and rules, then recode and build. Changing only mode
preserves coordinator-side proposals, but an independent package still omits them.

Independent review is protected through package content separation. Do not send the
coordinator's full project/bundle to an independent reviewer. Use clean original PDFs;
AI-annotated PDFs can reveal hints even if data.js is clean. Prior exposure, external
communication and reviewer identity are research/coordination concerns, not enforced
by an offline browser. Do not describe this as double-blind peer review.
