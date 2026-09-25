# Human governance, UI and evaluation

| Work | Human responsibility | AI assistance | Deterministic software |
|---|---|---|---|
| Protocol | Choose question, unit, criteria, appraisal and stopping policy | Draft alternatives, expose ambiguous criteria | Version and validate configuration |
| Source | Resolve wrong/ambiguous identity | Retrieve, organize, propose identity match | Hash, extract pages, check manifest |
| Coding | Interpret constructs and evidence, challenge proposals | Draft atomic values, quotes, locations and reasons | Schema, options, page bounds, missingness checks |
| Verification | Inspect full context; accept, revise or defer | Prepare navigable evidence and summarize challenges | UI, autosave, exports, coverage checks |
| Adjudication | Resolve disagreement and authorize release | Assemble positions and consequences | Reconcile returns, preserve reasons, apply declared rules |
| Synthesis | Decide inferential warrant and conclusions | Draft supported summaries | Flag registered dependencies, regenerate specified artifacts |

Human-in-the-loop here means authority at protocol definition, field judgment and
release. A generic final approval button is insufficient if a person cannot see the
source, explain disagreement, preserve uncertainty or prevent a dependent conclusion.
AI must not complete the person's review actions. The helper never makes a live LLM
call: the invoking agent prepares proposals with whatever authorized tools/model the
project uses, and records those settings when available.

## Reusable UI and settings

Three panes: record navigation; stage/group/field coding; complete PDF with page controls.
Page evidence links, printed-page labels, layer badges, configurable stage labels,
search/status filters, optional collapsed groups, image zoom, source PDF opening,
local autosave and reviewer-specific JSON import/export all belong to the skill.
Rendered images make all pages usable offline without relying on PDF-plugin behavior.
Without Poppler rendering the browser's own PDF viewer is used; its zoom is separate.

Research rules, codebook fields and evidence requirements are separate from assignment
settings (IDs, reviewer coverage, versions) and presentation settings (stages, labels,
collapse). The first two influence valid return bindings; even a presentation change
currently changes the config hash, so generate a new package instead of migrating
accepted states implicitly. Version 1.1 also supplies independent blank forms with AI/peer data omitted at build time. Mode, record/field selection and instructions can vary by reviewer and round.

Processed = a valid response, including a reasoned challenge. Accepted = reviewer accepts
the displayed proposal. Resolved = authorized adjudication/release. They are different
states. A reviewer who challenges everything has processed the assignment but has not
approved its evidence. Unclear/defer remains visible for human resolution.

## What may accelerate work

Candidate mechanisms: pre-organized full texts, page-linked evidence, consistent coding
forms, fewer transcription steps, targeted disagreement reconciliation and fewer stale
outputs after corrections. These relocate human effort toward judgment. Whether total
work falls depends on preparation, source reading, adjudication and rework; report these
components separately before making efficiency claims.

The UI exports `activity_seconds_estimate`, summing visible-page interaction intervals
capped at 60 seconds each. It excludes much off-screen PDF reading, breaks, calibration,
AI preparation, adjudication and cross-device work. It can include inactivity below the
cap. It is neither a time-and-motion study nor comparative time savings.

For a prospective evaluation predefine comparable tasks, baseline, assignment/crossover
procedure, expertise and source complexity; log preparation, verification, adjudication,
rework and total elapsed time separately. Assess seeded or independently adjudicated
errors with a declared denominator, unsupported source claims, unresolved fields,
downstream corrections and usability. Measure anchoring with genuinely independent
conditions if needed. Do not derive AI accuracy from the number of Correct clicks.

## Case status and novelty boundary

TALL is a retrospective completed-project implementation trace; Agency is a pilot
adaptation at another unit of analysis. They demonstrate design transfer, not equivalent
completed validation datasets. Version 1 adds generic configuration,
strict return binding and dependency checking; do not retrospectively attribute these
to the original cases. Literature-review skills, audit ledgers, human gates and annotation
UIs already exist. The defensible contribution to investigate is their operational
combination across evidence level, interface action and downstream consequence.


Version 1.1 adds flexible human-led calibration rounds, independent blank packages,
personalized assignments and an executable PDF identity-to-review handoff. These are
new software capabilities. They do not establish that historical TALL or Agency data
were collected independently, nor establish a speed/accuracy gain. The coordinator's
send-separate-packages/receive-separate-JSON practice supports independent review when
packages and actual conduct preserve the intended separation.
