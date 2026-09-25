# Guide a new user from their current materials

Begin by stating the next artifact you will make and the inputs already available.
Ask the next necessary scientific question only; choose routine technical settings.
Provide a usable deliverable at each stage rather than requiring the whole project to
be complete before helping. A typical first exchange:

User: “I have 80 papers and want to speed up full-text review.”
Agent: “I can organize the full texts and prepare reviewer packages. I will first check
the list and PDFs. Do you already have the criteria/codebook your team wants to use?”

If the criteria are provided, read them instead of asking again. If they are still being
developed, offer a blank calibration round; people can develop rules on any chosen sample.
Explain that the agent can help structure examples and apply rules, while the team owns
codebook changes. Do not silently invent research criteria to get a demo working.

## Example requests (copy and adapt)

**Starting with a list / missing PDFs**
> Use $review-evidence-workflow. Here is my CSV and PDF folder. Find missing full texts,
> check that each PDF matches its record, and give me an accepted manifest and remaining queue.

**Human-led calibration**
> 先用我选的这 10 篇发展 codebook。按我的初稿做两份独立空白包，不显示 AI 建议；
> reviewer 各自导出给我。把不清楚的定义留给我们讨论，不要自行定稿。

**AI applies the resulting codebook**
> 用我们修订后的 codebook v2 处理剩余文献，逐字段给出原文、PDF 页码和理由，
> 做成让人 verify 的 UI。无法判断的保留 Unclear，不要替人确认。

**Personalized assignments**
> Reviewer A 只审方法与测量，B 负责其余字段。给 A 独立空白包、B 带 AI 建议的包；
> 按我的覆盖要求检查分配是否完整，每个人只收到自己的材料。

**Continue from returned files**
> These are the returned reviewer JSON files and their project directory. Check versions,
> compare disagreements and missing responses, and prepare an adjudication worksheet.
> Preserve unresolved fields until I decide them.

**Revise rules or replace a wrong source**
> R012 was the wrong PDF. Check this replacement, preserve the original audit trail,
> identify affected coding and outputs, and prepare a fresh round for re-verification.

**Adapt to another review**
> I am reviewing archaeological field reports. Reuse the workbench and return workflow,
> but use my units, categories and rules. Do not import TALL or Agency eligibility thresholds.

## What the agent hands over

1. Source stage: manifest, accepted copies, audit/attempt history, unresolved reasons.
2. Configuration stage: human codebook mapping, mode, assignments and coverage summary.
3. Package stage: a separate folder/ZIP per reviewer; open OPEN_ME.html after extraction.
4. Return stage: one latest JSON per reviewer and matching project, plus validation result.
5. Resolution stage: comparison and human decision record, then authorized/unresolved ledger.

## Instructions to give reviewers

- Extract the entire package; keep its files together. Open OPEN_ME.html in a current browser.
- Read the codebook definitions and full source. Use the search, stage tabs and page controls.
- In assisted mode, choose Correct, Revise or Unclear; explain a correction/uncertainty.
- In independent mode, enter your answer, rationale and source evidence, then Save my answer.
  NR requires checked locations; NA requires a reason. A draft does not count as submitted.
- Export JSON periodically and when finished. Send the exported file back through the
  channel agreed with your coordinator. Import your own file to resume on another device.
- Export before clearing browser storage. No server receives your answers automatically.

## Common problems and next actions

| Situation | Next action |
|---|---|
| Codebook still developing | Human calibration round with current draft/version |
| Missing full text | Continue available sources and preserve an actionable retrieval queue |
| PDF does not load in embedded viewer | Open source PDF separately, or coordinator rebuilds with --render-pages |
| No reviewable fields in assisted build | Prepare evidence-grounded proposals; or choose independent coding |
| Return rejected after configuration change | Use original matching project to read it; create a new round for revised work |
| Duplicate/ambiguous PDF identity | Resolve the record or document actual human identity confirmation |
| Reviewers disagree | Compare sources and reasons; await actual human adjudication |
| Only an abstract is available | Label source limitation; do not represent full-text review as complete |

## When to use something else

This skill is for evidence workflows, not manuscript peer review, unrestricted web
research, autonomous eligibility decisions or automatic codebook authorship. It does
not provide a hosted multiuser app, identity verification, OCR, arbitrary synthesis,
interrater statistics, or measured efficiency benefits. Use a separate appropriately
validated analysis for those tasks.

## Reader controls and source quotation location

Drag the divider to adjust PDF width; arrow keys adjust a focused divider, Shift
uses a larger step, Home/End move to limits, and double-click resets. Rendered-page
packages support 100–200% zoom and independent horizontal/vertical scrolling.

Install optional `pdfplumber` in the coordinator build environment, then rebuild with
`--render-pages` for source glyph coordinates. Reviewers do not install Python. The
coordinate index is generated from the same source copied to the package and carries
its SHA-256. A changed PDF requires a new package/round under the source contract.

An evidence button opens its physical PDF page and highlights a unique normalized
quotation. Missing text, short quotes, paraphrases and duplicate matches produce an
explicit manual-check message. This is not OCR or semantic matching. With native PDF
embedding, use the browser's PDF controls; custom highlights require rendered pages.
