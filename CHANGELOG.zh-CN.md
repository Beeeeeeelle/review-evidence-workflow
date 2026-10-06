# 更新记录

这里记录 Review Evidence Workflow 对使用者可见的变化。版本号描述可复用的 skill 与协调端工具；发布新版本不等于任何 review 的科学结论已被验证。

## 1.3.1 — 2026-10-06

### 许可与引用

- 从本版本起，软件代码、脚本、浏览器 UI、测试、自动化与机器可读配置使用 Apache License 2.0。
- 从本版本起，原创文档、skill 指令、workflow 材料、图表、插图与原创媒体使用 CC BY 4.0。
- 新增 Apache `NOTICE` 和机器可读的 `CITATION.cff`，并提供项目建议引用。
- 明确第三方摘录、后续加入的 PDF 与私有 review 数据不在仓库许可范围内。v1.3.0 及更早版本保留原 MIT 条款。

## 1.3.0 — 2026-10-06

### 新增

- stage 和单个字段可使用条件规则 `applies_when`。
- 新增单次独立操作流：每篇全文先判断 eligibility，然后进入质量检查／coding，或只填写一个主要排除理由。
- 新增 `allow_missingness: false`，让分支问题只能使用 codebook 明确定义的选项。
- 进度、导出、回传验证、comparison 和 finalization 都按当前适用分支计算。
- 最终 ledger 新增 `not_applicable_fields`；依赖非活动分支的输出标记为 `not_applicable`。
- 新增“全文筛选与 coding 合并”中英文案例说明。

### 边界与保护

- 条件分支限于 independent review；每个字段只要求一位 reviewer，每篇进入分支的报告只分配给一位 reviewer。多位 reviewer 可以处理不同报告。
- 如果两人要独立筛选同一篇报告，必须先裁决 eligibility，再开启后续 coding 轮次；不同分支不会被误算为审阅覆盖。
- 选择分支后界面会立即更新，但控制字段仍需填写配置中要求的理由和原文证据，才算完成。

### 验证

- 47 项自动测试通过；因测试环境未安装可选 pdfplumber，1 项集成测试跳过。
- 在新构建的 10 篇报告包中实测了未选择、Include 和 Exclude 三种浏览器状态。这些检查验证软件行为，不验证 eligibility 或 coding 的科学准确性。

## 1.2.0 / 1.2.1 — 2026-09-25

- 新增可复用 evidence reader、可拖动 PDF／coding 分隔、页面缩放，以及精确原文引文高亮；未匹配和多处匹配会明确提示。
- 新增真实界面操作演示、双语文档和可下载模拟包。v1.2.1 tag 与 v1.2.0 指向同一份发布代码。

## 1.1.0 — 2026-09-25

- 新增独立空白 reviewer package、个性化任务、校准轮次、PDF 身份交接、版本绑定回传、comparison 和人工授权 finalization。

[英文更新记录](CHANGELOG.md)
