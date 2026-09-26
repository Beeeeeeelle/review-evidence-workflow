# 怎样把操作截图讲成一个能跟得上的过程

这次修改解决的是一个观看问题：观众面对完整工作台时，不知道解说在指哪里。导览按“指出位置 → 展示操作结果 → 解释为什么要看它”来组织。

## 从观众的问题开始

开头先问“这条编码，原文真的支持吗？”，随后展示页码和原句的关系。观众先看到这个工作台能解决什么问题，再认识文献列表、编码区和 PDF 区。

每个章节只解决一个主要问题。比如：“需要改时在哪里写？”“已核验为什么还有修改意见？”“原文太窄怎么读？”章节标题也用这些问题的语言。

## 一次只引导一个主要视线

| 讲解目的 | 画面处理 |
|---|---|
| 找到小按钮 | 橙色圈线、短标签、局部镜头放大 |
| 连接证据与原文 | 青色箭头；保留两侧空间关系 |
| 看清操作结果 | 切到真实操作后的画面，突出改变的区域 |
| 展示拖动方向 | 分隔线标注与方向提示，再展示实际变宽后的状态 |
| 读懂说明框 | 先指按钮，再突出展开的输入区 |
| 分清进度与结论 | 先看已核验列表，再指向仍存在的修订数量 |

圈线不是装饰。每一条标注都应回答“此刻该看哪里”，并避开要读的文字。解说开始前留约半秒，让观众先找到位置。同一章节里的镜头尽量延续，避免每句话都重新推拉。

## 把书面说明改成操作语言

“审阅者可通过修订功能记录核验差异”改成“需要改，就点旁边的 Revise。把哪里不对、建议怎么改，写在这里。”

按钮保留页面上的英文，解释用自然中文。字幕跟解说一致。重复的来源说明放在播放器说明区，演示反馈标识保持可见。

## 保留真实性

原始截图存放在 `frames/`。后期只做镜头裁切、圈线、箭头、指示动画和字幕。黄色引文高亮必须来自真实阅读器；不能用后期画黄块冒充定位功能。拖动、缩放、滚动使用真实前后状态，不能把编辑动画当作连续录屏。

界面演示只使用隔离反馈；展示按钮作用不能变成代替研究者做正式核验。具体研究的 codebook、排除阈值和构念路径也不能被包装成所有 review 的通用规则。

## 复用制作文件

- [storyboard.json](storyboard.json)：每个讲解步骤的原始截图、口播、标注文字、坐标与镜头范围。
- [tools/render_guided_video.py](tools/render_guided_video.py)：生成配音、预览帧和导览视频。
- [chapters.json](chapters.json)：播放器章节时间。
- [pilot-guided.zh-CN.srt](pilot-guided.zh-CN.srt)：逐段字幕。

需要 Python、Pillow、edge-tts，以及 `ffmpeg` / `ffprobe`。`GUIDE_FONT` 可指定支持中文的字体文件；默认使用 macOS 的 Hiragino Sans GB。在线配音会把公开口播发送到微软语音服务。

```bash
python3 -m pip install Pillow edge-tts
python3 docs/demo/tools/render_guided_video.py voice
python3 docs/demo/tools/render_guided_video.py preview
python3 docs/demo/tools/render_guided_video.py proof
python3 docs/demo/tools/render_guided_video.py render
```

生成结果保存在 `docs/demo/tools/.build/zh-CN/`。先检查预览和短片，再渲染完整视频。更换项目时，要重新截图、标记坐标、校准讲解时间；不要直接套用本案例的界面坐标和研究判断。

英文版使用 `storyboard.en.json`，在相同命令后加 `--lang en`。字幕按英文词组换行，标题和标注按实际宽度排版；配音与章节时间独立生成，不能沿用中文字幕的时间轴。用 `tools/export_media.py` 从完成的渲染中导出 MP4、SRT、VTT、章节与解说全文。

两支全流程入门视频的 [制作与素材说明](../intro/PROVENANCE.md) 另列：它们把解释性流程图、Belle 插画与真实界面连接起来，帮助观众先认识两项 skill 的分工。
