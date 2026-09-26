# 从一份文献清单开始，认识两个 skill

**[▶ 中文入门视频 · 5:04](two-skills-introduction.zh-CN.mp4)** · [直接下载](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/download/v1.2.0/two-skills-introduction.zh-CN.mp4) · [English · 4:57](README.md)

[![从文献清单，到有据可查的审阅](poster.zh-CN.jpg)](two-skills-introduction.zh-CN.mp4)

如果你第一次看到这两个 skill，先看这支视频。它从“我有一份文献清单和一些 PDF，接下来怎么办”开始，带你走到个人审阅包、回传和团队裁决。12 个章节、27 个讲解步骤，把人和 AI 的分工放在具体场景里。

想看按钮怎样操作？接着看 **[真实 Pilot 工作台导览（中英双版）](../demo/README.zh-CN.md)**。两支视频分别回答“整套方法怎样用”和“进入工作台后怎样做”。

## 跟着视频走一轮

| 观众的问题 | 这一段带你认识什么 |
|---|---|
| 两个 skill 各做什么？ | PDF Retrieval 准备全文；Review Evidence Workflow 组织审阅，可以连用或单独开始 |
| 我要先准备什么？ | 研究问题、文献清单、已有 PDF、当前规则；初稿也可以 |
| PDF 不好找怎么办？ | 补元数据、记录失败、结合实际访问条件换路径 |
| 什么时候需要我？ | 明确的登录、验证、保存与交回操作；AI 接着核对 |
| 下载完就能编码吗？ | 文章身份、版本和完整性需要证据；保留未解决项 |
| Codebook 谁来做？ | 人发展规则，用自己选定的样本和轮次校准 |
| 一定要看 AI 建议吗？ | 每轮选择辅助核验或独立空白表单 |
| 怎么对照证据？ | 真实 Pilot 的页码跳转、引文定位和修订说明 |
| 能按审阅者分工吗？ | 个人文献、字段、说明和模式；配置由 agent 准备 |
| 回传后谁决定？ | AI 整理差异，人对照证据裁决；资料改变时检查受影响工作 |
| 能搬到我的研究里吗？ | TALL 与 Agency 展示不同研究单位下的适配，规则由新项目重新定义 |
| 我现在怎么开始？ | 安装入口、模拟包和可以照着修改的提问 |

## 看完可以直接这样问

> 用 $literature-pdf-retrieval。帮我找这份清单里缺的全文，保留 ID 和原件。需要我登录或下载时，给我具体入口和操作。

> 用 $review-evidence-workflow。这是全文、codebook 初稿和本轮样本。请准备审阅包，说明缺口和需要人决定的地方。

[安装 PDF skill](https://github.com/Beeeeeeelle/literature-pdf-retrieval/blob/main/README.zh-CN.md) · [安装 review skill](../../README.zh-CN.md#怎样开始) · [试用模拟包](../TRY_DEMOS.md)

## 播放、字幕和制作说明

同一个本地播放器可以切换**总览／操作**和**中文／English**，并按章节跳转。在仓库根目录运行：

```bash
python3 docs/demo/serve.py --port 8940
```

打开 [播放器](http://127.0.0.1:8940/?video=intro&lang=zh-CN)。GitHub 上可直接播放／下载上面的 MP4，无需启动本地服务。

视频使用合成配音，字幕已嵌入画面。流程图是解释性示意；R017 是交接模板；独立表单使用模拟资料。实际 Pilot 截图、两个案例的适配展示与 Belle 概念插画分别标注。这是剪辑导览，不是连续录屏，也不是一场新完成的研究审阅。

[中文全文](TRANSCRIPT.zh-CN.md) · [SRT 字幕](two-skills-introduction.zh-CN.srt) · [章节](chapters.zh-CN.json) · [素材与制作记录](PROVENANCE.md) · [可复用制作脚本](tools/render_overview.py)
