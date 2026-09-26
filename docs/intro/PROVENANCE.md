# Introductory video: sources and reproduction

Created 2026-09-25. English and Chinese editions each contain 12 chapters and 27 beats.

- The story follows a general review task, not a claimed observation of one completed new project.
- Existing Belle concept illustrations are reused from `assets/review-evidence-story-belle黑色彗星/01-the-question.png` and `02-people-write-the-rules.png`. They are conceptual artwork, not research evidence.
- Pilot source-page, highlight, Revise and export views use the existing [authentic captures](../demo/PROVENANCE.md). No new research response was entered for these videos.
- The independent form comes from the [fictional portable example](../images/PROVENANCE.md). Its source and form remain fictional, explicitly labelled on screen.
- TALL and Agency screenshots are the previously documented [real-source adaptations](../images/PROVENANCE.md), not historic reviewer sessions. Their project status and scientific decisions are not changed by the narration.
- The access handoff R017, workflow arrows, task assignment panels and example prompts are explanatory illustrations. They are not reconstructed download logs, a fabricated chat session or a visual settings editor.
- Orange outlines, arrows and camera movements are editorial guidance. Yellow quotation highlights in Pilot captures come from the functioning reader. Captured source text is not rewritten or newly highlighted in post-production.
- Voice generation sends only the public narration to Microsoft's speech service via `edge-tts`: `zh-CN-XiaoxiaoNeural` for Chinese, `en-US-JennyNeural` for English. No source PDFs, private records or reviewer returns are sent. The language versions are independently timed, including captions and chapter starts.
- Complete papers and private review bundles are not included. Article material retains its original rights. Repository licensing does not relicense those excerpts.

## Reproduce

Use Python with Pillow and edge-tts, plus local ffmpeg/ffprobe. A suitable system font is needed; `GUIDE_FONT` overrides the default macOS font. Chinese output requires a Chinese-capable font.

```bash
python3 docs/intro/tools/render_overview.py preview --lang en
python3 docs/intro/tools/render_overview.py voice --lang en
python3 docs/intro/tools/render_overview.py proof --lang en
python3 docs/intro/tools/render_overview.py render --lang en
python3 docs/demo/tools/export_media.py \
  --build docs/intro/tools/.build/en --destination docs/intro \
  --stem two-skills-introduction --lang en --source overview.mp4
```

Replace `en` with `zh-CN` for the Chinese edition. Inspect previews and proof clips before the full render. `--out-dir` can keep temporary media outside the repository. The renderer uses the [shared guided-video helpers](../demo/tools/render_guided_video.py); narration, labels, asset paths and diagram data live in the adjacent storyboard JSON files.
