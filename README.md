<p align="right"><strong>English</strong> · <a href="README.zh-CN.md">中文</a></p>

# Review Evidence Workflow

**Turn your team's codebook and PDFs into personalized review packages—with source evidence, human decisions and a traceable return path.**

A reusable agent skill for full-text screening, appraisal and extraction. Humans develop the rules; AI prepares evidence and proposals; reviewers verify or code independently in a browser. Send each person a package, receive their JSON, then resolve differences with the evidence in view.

**[Follow the illustrated story](docs/story/README.md) · [Try the runnable demos](#try-it) · [Explore the two cases](#two-cases-one-reusable-workflow) · [See the workflow](#how-humans-stay-in-the-loop) · [Read the guide](review-evidence-workflow/references/getting-started.md)**

![The assisted review workbench: assigned records on the left, a correctable proposal in the center, and its source PDF on the right.](docs/images/workbench-assisted.jpg)

*Actual v1.1 workbench, using a clearly fictional review and PDF. Reviewers can inspect the source, choose Correct / Revise / Unclear, save progress and export their own return.*

## Follow Belle through a review

A team begins with scattered papers and developing rules. Follow Belle through six scenes to see how the skill prepares the work, where people judge, and what happens when something changes.

| 01 · Start with a question | 02 · People develop the rules |
|---|---|
| [![01 · Start with a question](assets/review-evidence-story-belle黑色彗星/01-the-question.png)](docs/story/README.md) | [![02 · People develop the rules](assets/review-evidence-story-belle黑色彗星/02-people-write-the-rules.png)](docs/story/README.md) |

| 03 · Check the full text | 04 · Choose how to review |
|---|---|
| [![03 · Check the full text](assets/review-evidence-story-belle黑色彗星/03-find-the-right-source.png)](docs/story/README.md) | [![04 · Choose how to review](assets/review-evidence-story-belle黑色彗星/04-two-ways-to-review.png)](docs/story/README.md) |

| 05 · Return and resolve | 06 · Revisit and reuse |
|---|---|
| [![05 · Return and resolve](assets/review-evidence-story-belle黑色彗星/05-return-and-resolve.png)](docs/story/README.md) | [![06 · Revisit and reuse](assets/review-evidence-story-belle黑色彗星/06-a-traceable-next-round.png)](docs/story/README.md) |

**[Read the illustrated story →](docs/story/README.md)** Each scene has a short explanation and a link to the real workflow. These are conceptual illustrations; the workbench above is the actual application.

## Is this for your review?

Use it when your team has a study list and developing or established criteria, and needs to:

- Find and check full texts, keeping missing or uncertain sources visible.
- Develop a codebook on a chosen sample, then apply it to further batches for human verification.
- Give different reviewers different records, fields, instructions or review modes.
- Compare returned judgments without losing their source, codebook version or unresolved questions.

You provide the research question, human-led rules and available materials. The agent guides the current step and prepares **source manifests, reviewer packages, comparison reports and a decision ledger**. Reviewers need a browser; they do not need Python or an AI account. Coordination runs through local files rather than a hosted multiuser service.

## Two cases, one reusable workflow

The cases show why the skill exists and what changes when the research unit changes. Click either image for its walkthrough.

| TALL · primary studies | Agency · reviews of research |
|---|---|
| [![TALL case illustration with a source-linked study-design field.](docs/images/tall-workbench.jpg)](docs/cases/tall.md) | [![Agency case illustration distinguishing measurement reporting from descriptive coding.](docs/images/agency-workbench.jpg)](docs/cases/agency.md) |
| **What happens after a human changes a judgment?** A retained appraisal revision changes a project gate while screening remains Include. The case motivates explicit versions and review of affected work. | **What did the source say, and what did we infer?** A review's reported measurement types are kept separate from team coding and later cross-review synthesis. |
| Historical implementation in technology-assisted L2 learning. | Pilot adaptation for AI-supported education and learner agency. |
| [Read the TALL case →](docs/cases/tall.md) | [Read the Agency case →](docs/cases/agency.md) |

*Case images render real source material in the reusable v1.1 workbench. The public source pane uses attributed excerpts. These are illustrative adaptations, not historical reviewer-session screenshots. [Image provenance](docs/images/PROVENANCE.md).*

| What differs | TALL | Agency |
|---|---|---|
| Unit being coded | Original empirical study | Review report |
| Appraisal rule | Project-specific MMAT Q2/Q4 gate | 11 JBI items; no automatic numerical exclusion |
| Main reasoning boundary | Eligibility, appraisal and extraction membership | Source wording, descriptive coding and synthesis |
| Evidence status | Retrospective implementation case | Implemented pilot; synthesis still to follow |

**What transfers:** PDF checks, source-linked fields, configurable UI, separate reviewer returns, human adjudication and version tracking. **What you define again:** eligibility, codebook, appraisal rules, unit of analysis and review coverage. These are two motivating cases, not two equivalent completed validation experiments.

## How humans stay in the loop

![Workflow: humans develop the codebook; AI and software prepare full texts; each round branches to assisted verification or independent coding; separate returns are checked before human adjudication. Rule or PDF changes start another version.](docs/images/workflow-en.svg)

| Stage | AI and software help with | People are responsible for |
|---|---|---|
| Scope and calibration | Map supplied rules to fields; expose missing definitions | Develop and revise the codebook; choose sample and round |
| Full texts | Locate lawful copies; check identity, completeness and file versions | Provide access when needed; resolve ambiguous sources |
| Review | Prepare grounded proposals or blank forms; personalize assignments | Read sources; verify or independently code; explain uncertainty |
| Returns and decisions | Check versions/coverage; align differences; retain a decision record | Resolve disagreements and authorize the current result |
| Revisions | Flag registered dependencies after changes; prepare affected work | Decide what needs recoding, rechecking or a revised conclusion |

Start with ten papers, five, or another useful sample. Continue with AI coding plus human verification, add an independent round, or revisit calibration. **The sample size, number of rounds and appraisal threshold are project choices.** AI does not invent human approvals or make final scientific decisions. Registered dependencies can be flagged; undeclared relationships still need human review.

## Two review modes—and your own UI settings

| | Assisted verification | Independent review |
|---|---|---|
| Visible material | AI proposal, reason, evidence and original PDF | Human codebook, original PDF and blank form |
| Reviewer action | Correct / Revise / Unclear, with reasons | Enter value, rationale and source locations; save or defer |
| Package contents | Assigned proposals | AI suggestions and peer feedback omitted from the data |
| Useful when | Applying calibrated rules to another batch | People should code before seeing suggestions |

<details>
<summary><strong>See the independent mode</strong> — the same workbench with blank answers</summary>

![Independent review workbench with a blank answer and rationale form beside the fictional source PDF.](docs/images/workbench-independent.jpg)

*The same synthetic example, assigned to a different reviewer. Independent packages support independent conduct; software cannot remove prior exposure to suggestions or prove reviewer independence.*

</details>

The agent can configure **records, fields, order, stages, groups, labels, instructions, mode and coverage requirements** per round or reviewer. Settings are supplied through configuration files; there is no visual settings editor in v1.1. Reviewers receive their own package and return files to the coordinator. [Modes, settings and round transitions](review-evidence-workflow/references/rounds.md).

## Try it

**Just look around:** [download the synthetic examples from v1.1.0](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/tag/v1.1.0), unzip, and open a package's `OPEN_ME.html`. The release includes three fictional projects in both modes. If your browser restricts local files, follow the [local-server instructions](docs/TRY_DEMOS.md).

**Install the skill:** clone or download this repository, then copy its `review-evidence-workflow` folder to your Codex skills directory (`~/.codex/skills/` in the environment used for this release). Preserve any existing folder with that name. Start a new session and invoke `$review-evidence-workflow`.

```bash
git clone https://github.com/Beeeeeeelle/review-evidence-workflow.git
cd review-evidence-workflow
python3 examples/make_examples.py --out /tmp/review-workflow-demo --render-pages
```

Use a new output directory. Try `primary-study-assisted/OPEN_ME.html` or `review-level-independent/OPEN_ME.html` inside it: save an answer, export JSON and import it again.

**Coordinator requirements:** Python 3.9+ and Poppler for PDF checks/text/page rendering (`brew install poppler` or `sudo apt-get install poppler-utils`). Python helpers use the standard library. A verified-source package can use the browser PDF viewer without rendering. Cross-host agent runtime support has not been verified.

**PDF retrieval is part of the workflow.** The agent can compose the optional `literature-pdf-retrieval` skill, or use the included search/browser fallback and local validator. No private skill, paid API key or institutional account is required for the examples. Access to a particular paper depends on its availability and your authorized access. [PDF handoff and unresolved-source queue](review-evidence-workflow/references/pdf-handoff.md).

## What can I ask the agent?

**Develop rules with people**

> Use $review-evidence-workflow. Our team is developing a codebook on this pilot sample. Make separate blank packages with our current definitions. Omit AI suggestions and other reviewers' feedback; compare our returns before we revise the rules.

**Apply rules and verify**

> Our team has calibrated codebook v2. Apply it to the remaining PDFs. Assign methods and measures to reviewer A, other fields to reviewer B, and prepare source-linked verification packages. Keep uncertain cases visible.

**Resume after feedback**

> These are the returned JSON files. Check versions and coverage, show disagreements with their source evidence, and list what needs our decision before producing the authorized ledger.

[More sample prompts, reviewer instructions and troubleshooting](review-evidence-workflow/references/getting-started.md).

## What has been checked?

**40 distinct automated tests**, local Python 3.9/3.12 checks, a fresh-context workflow trial, browser interactions, and six synthetic packages across three domains. The [release-commit CI run](https://github.com/Beeeeeeelle/review-evidence-workflow/actions/runs/36187005213) also passed on Ubuntu/Python 3.11. [Validation record and limits](docs/VALIDATION.md).

These checks establish specific software behaviors, including mismatched-return rejection, independent-package omission, source replacement handling and unresolved-state preservation. They do not establish AI accuracy, universal scientific validity or measured time savings. The intended benefit is less manual preparation and easier verification; that efficiency claim still needs a comparative study.

## Explore or contribute

- [Skill instructions](review-evidence-workflow/SKILL.md) · [Data contracts](review-evidence-workflow/references/contracts.md) · [Human workflow](review-evidence-workflow/references/human-workflow.md)
- [Related tools and positioning](docs/RELATED_WORK.md): what already exists, what this workflow connects, and what remains to evaluate.
- [Diagram sources and screenshot provenance](docs/images/PROVENANCE.md)

```bash
python3 -m unittest discover -s tests -v
node --check review-evidence-workflow/assets/app.js
```

Keep contributed tests and examples synthetic. Include a minimal anonymized fixture and expected/actual result in bug reports. MIT covers the code, documentation and synthetic fixtures; third-party source excerpts retain their original rights. The license grants no rights to PDFs added to a project.

---

**AI in learning. Humans in charge.**
