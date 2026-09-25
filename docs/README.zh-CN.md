[← 中文项目首页与案例](../README.zh-CN.md) · [English demo guide](TRY_DEMOS.md)

# 用这个 skill 带领一项 review

这个 skill 把“找全文 → 核对 PDF → 按人制定的 codebook 编码 → 人审阅 → 汇总回传 → 裁决与版本更新”连成可复用流程。你不需要先学 JSON；把现有材料交给 agent，它负责配置与打包。

**codebook 由人主导制定、发展和修改。** 例如先用 10 篇校准，再让 AI 按当前版本处理剩余文献、人来 verify。10 篇只是示例；轮次、样本、审阅方式和任务分配都可选。

## 第一次怎么用

1. 按仓库 README 安装 `review-evidence-workflow` 文件夹，并准备文献清单、已有 codebook、PDF 和任务范围。有缺失也可以开始。
2. 告诉 agent 当前要完成哪一步。例如：“先核对全文并列缺失清单”；或“按我们的 codebook v2 做 reviewer 的审阅包”。
3. Agent 读取已有规则，只询问当前缺少的科学判断；先交付可完成的材料。
4. 你把每人的独立文件夹/ZIP 发给对应 reviewer。他们打开 `OPEN_ME.html`、审阅并导出 JSON，再发还给你。没有自动上传服务。
5. 把回传和对应 project 交给 agent。它核对版本、列出分歧和未完成项；人裁决后才形成最终 ledger。

## 可以直接这样问

> 用 $review-evidence-workflow。我们想先用这 10 篇发展 codebook。按我的初稿做两份独立空白包，不放 AI 建议和他人反馈；我们看完后再讨论规则。

> 我们已经校准了 codebook v2。请给其余文献准备 AI 编码、短原文、页码和理由，做成让人 verify 的 UI。不要替我们点确认。

> 给 A 分配方法和测量，给 B 分配其他字段；按照我规定的覆盖要求检查分配。两人的说明、顺序和分组可以不同。

> 我给 reviewer 发包，他们导出发还。这些是返回文件；先检查版本和覆盖，再把需要我决定的分歧逐条列出来。

> 这篇 PDF 找错了。核对新文件，保留旧版本记录，列出受影响的编码和输出，准备新一轮复核。

[完整示例提问与排错](../review-evidence-workflow/references/getting-started.md)。

## 两种模式怎么选

| 需求 | 设置 | 人的工作 |
|---|---|---|
| 看 AI 提案后核验 | assisted_verification | 对照原文选 Correct / Revise / Unclear，写理由 |
| 自己先编码，不看建议 | independent_review | 空白录入答案、理由和原文位置，保存或延后 |

独立模式在生成文件时移除 AI 答案、理由、证据提示和他人反馈。它仍提供人制定的字段定义和原始 PDF。请发生成的个人 package，不要把 coordinator 的完整 bundle 发给独立 reviewer。

可以按轮次或 reviewer 选择模式。混合模式回传可比较，但不能当作独立一致性指标。软件无法保证 reviewer 没看过别处的建议，也不能把这种模式称作隐藏论文作者身份的双盲评审。

## UI 与设置包含什么

文献搜索与状态筛选、字段/阶段/分组、原文与 PDF 页码、整份全文翻页、每人自己的保存/导入/导出、独立录入或提案核验。可配置文献、字段、字段顺序、标题、说明、阶段与按钮标签、分组展开方式、审阅覆盖要求。

这些设置通过配置文件由 agent 调整；当前没有可视化设置编辑器、登录账号或多人云端数据库。

## 跑一遍示例

在仓库根目录运行：

```bash
python3 examples/make_examples.py --out /tmp/review-workflow-demo --render-pages
```

它生成 primary-study、review-level、field-report 三种项目、每种两种模式，共六个包。打开任一 `OPEN_ME.html`，试着保存、导出和重新导入。示例资料均为模拟，不是 TALL/Agency 的真实文献或 reviewer 结果。

TALL 和 Agency 的案例说明保留它们的研究差异；示例演示如何迁移 UI、字段结构和回传流程。验证结果见 [VALIDATION.md](VALIDATION.md)。目前能证明哪些技术路径跑通，就只报告哪些；不会把脚本通过写成“所有 review 都适用”或“已经证明提速”。


## 运行示例与本地预览

可以先从 [v1.2.0 release](https://github.com/Beeeeeeelle/review-evidence-workflow/releases/tag/v1.2.0) 下载 `review-workflow-synthetic-examples-v1.2.0.zip` 并解压，无需 AI 账号。也可以用上面的命令生成六份包；生成时需 Python 3.9+ 和 Poppler。

先打开 `review-level-assisted/OPEN_ME.html`：看原文，选 Correct 或填写修订，再点 Export review 导出。将导出的 JSON 导入同一个包，可以恢复进度。再打开 `review-level-independent/OPEN_ME.html`，比较空白表单。这里录入的都是测试响应，请勿混入真实研究。

若浏览器限制本地文件，可以运行：

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory /tmp/review-workflow-demo
```

在命令运行期间，打开 [AI 辅助包](http://127.0.0.1:8000/review-level-assisted/OPEN_ME.html) 或 [独立包](http://127.0.0.1:8000/review-level-independent/OPEN_ME.html)。如果使用下载的 ZIP，把命令末尾替换成实际解压后包含这些包的目录。完成后用 Ctrl+C 停止。这个本地服务只用于预览文件，不收集或上传答案。

本次浏览器验证使用本地 HTTP 服务；直接双击文件和所有浏览器／设备组合尚未全面验证。保存和回传步骤见 [英文示例指南](TRY_DEMOS.md)。

**AI in learning. Humans in charge.**
