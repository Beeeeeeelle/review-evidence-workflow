[← Project](../README.md) · [中文步骤](README.zh-CN.md#运行示例与本地预览)

# Try a review package

**No AI account is needed to try the reviewer interface.** Download `review-workflow-synthetic-examples-v1.2.0.zip` from the [release](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/tag/v1.2.0) and unzip it. The six packages contain fictional sources, not TALL/Agency research data.

Alternatively, from the repository root with Python 3.9+ and Poppler:

```bash
python3 examples/make_examples.py --out /tmp/review-workflow-demo --render-pages
```

The generator requires a fresh output directory and creates three projects, each in assisted and independent modes. Poppler (`brew install poppler` / `sudo apt-get install poppler-utils`) provides the PDF tools.

## Open and return one record

1. Open `review-level-assisted/OPEN_ME.html` in the generated or unzipped examples. Read the proposal and the fictional PDF beside it.
2. Choose Correct, or Revise/Unclear and explain your reasoning. These are test responses, not research judgments.
3. Select Export review. The downloaded JSON is the file a reviewer would send back to the coordinator.
4. Import that file into the **same package** to restore it. A different assignment or version can reject it.
5. Open `review-level-independent/OPEN_ME.html` to see the alternative: a blank answer, rationale and evidence form, without AI proposals.

Browser state may preserve earlier test answers. For a clean view, use a fresh browser profile. Keep test returns out of real research projects.

## If local-file access is restricted

Serve the folder locally. With the generated examples above:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory /tmp/review-workflow-demo
```

Open [the assisted package](http://127.0.0.1:8000/review-level-assisted/OPEN_ME.html) or [the independent package](http://127.0.0.1:8000/review-level-independent/OPEN_ME.html) while that command is running. If you downloaded the ZIP, replace `/tmp/review-workflow-demo` with the actual extracted directory containing those package folders. Stop the server with Ctrl+C when finished. This loopback server serves files for preview; it does not collect reviewer submissions or upload answers.

The release's observed browser tests used an explicitly served local HTTP package. Direct file opening and all browser/device combinations have not been comprehensively verified. [Validation details](VALIDATION.md).

## Move from a demo to your review

Use the [installation instructions](../README.md#try-it), then give the agent your study list, current human-led codebook and available PDFs. Ask it to complete a specific stage and prepare the next person's instructions. Do not replace only a title in a fictional example and treat it as a validated real assignment; the source identities, field rules, versions and scope must be configured for your project.

[Step-by-step prompts](../review-evidence-workflow/references/getting-started.md) · [Round settings](../review-evidence-workflow/references/rounds.md)
