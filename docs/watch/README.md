<p align="right"><strong>English</strong> · <a href="README.zh-CN.md">中文</a></p>

# From papers to judgments

Watch the introduction and the real workbench tour directly on this page. Both films are available in English and Chinese. The approved original films remain in [Introduction](../intro/README.md) and [Workbench](../demo/README.md).

Play both films directly below—no download or local setup needed. Use the language link at the top for the Chinese edition.

## Meet the two skills · 4:57

https://github.com/user-attachments/assets/015182cb-25d4-4a7c-bcbd-29c9b64eb867

[Read the transcript](../intro/TRANSCRIPT.en.md)

## Inside the real workbench · 3:40

https://github.com/user-attachments/assets/1bc47e8e-7276-4822-9731-5e6af63e3d78

[Read the transcript](../demo/TRANSCRIPT.en.md)

<details>
<summary>Download a copy for offline viewing</summary>

| Film | English | 中文 |
|---|---|---|
| Meet the two skills | [Download · 4:57](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/download/v1.2.0/two-skills-introduction.belle.en.mp4) | [下载 · 5:04](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/download/v1.2.0/two-skills-introduction.belle.zh-CN.mp4) |
| Inside the real workbench | [Download · 3:40](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/download/v1.2.0/pilot-guided-walkthrough.belle.en.mp4) | [下载 · 3:36](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/download/v1.2.0/pilot-guided-walkthrough.belle.zh-CN.mp4) |

</details>

## Optional: the local chapter player

For a combined player with clickable chapters and language switching that retains the corresponding chapter, start it from the repository root:

```sh
python3 docs/watch/serve.py --port 8942
```

Open [the English introduction](http://127.0.0.1:8942/?video=intro&lang=en) or [the English workbench tour](http://127.0.0.1:8942/?video=pilot&lang=en). The original player remains available through the **Original edition** link. Native playback controls support seeking, volume and fullscreen; optional WebVTT captions are included. Chapter navigation and language switching need JavaScript, while the default video can play without it.

The edition preserves the original narration, chapter order and timing. It changes composition, type hierarchy, annotation placement and editorial camera movement. The workbench screenshots are authentic; circles, numbered markers, arrows and crops are editorial overlays. Yellow quotation matches come from the functioning PDF reader. Demonstration feedback is separate from research judgments. This is a guided film made from captures, not a continuous screen recording. Narration is synthetic.

TALL and Agency images are real-source adaptations, as described in [image provenance](../images/PROVENANCE.md). The independent form uses fictional data. R017 is an illustrative retrieval handoff. Belle illustrations are reused from the [existing story](../story/README.md).

The original material remains the starting point for the redesign. See [design decisions and QA](DESIGN.md). To reproduce a film, run `tools/render_belle.py` with its approved narration cache (`timeline.json` and `narration.wav`), using `--kind intro|pilot`, `--lang en|zh-CN`, `--build PATH`, and `--out PATH`. Pillow and ffmpeg are required. Font paths can be set with `BELLE_FONT_EN`, `BELLE_FONT_ZH` and `BELLE_MONO`; the default fonts are macOS Helvetica Neue, Hiragino Sans GB and Menlo. The earlier render tools produce the narration caches. Existing screenshots and codebook content are not regenerated.
