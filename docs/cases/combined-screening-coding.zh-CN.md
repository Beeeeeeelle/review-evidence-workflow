# 在同一轮里完成全文筛选与编码

有时不必先把所有报告筛完，再从头回到纳入报告做编码。一个人独立处理一篇报告时，可以使用更直接的单次流程：

1. 先选择全文 eligibility；
2. 选择 **Include**，立即开启质量检查与 coding；
3. 选择 **Exclude**，只填写一个主要排除理由，后续阶段显示为不适用。

选择分支后，界面会立即变化；但 eligibility 本身只有在理由与原文证据保存后才算完成。纳入报告不会再出现或要求 exclusion reason；排除报告也不会被算进质量检查和 coding 的分母。进度与导出只计算当前适用的字段。

这个模式来自一个 AI／GenAI literacy measurement review 的 coauthor 校准任务。可以复用的是交互逻辑，不是该项目的纳入标准、质量 gate 或 codebook。

## 重要边界

内置条件分支用于每个字段只要求一位 reviewer 的独立工作。如果两个人要对同一篇报告做独立全文筛选，应先裁决 eligibility，再把团队最终保留的报告送入 coding 轮次；否则两个人可能进入不同分支，却被误算为完整覆盖。

[详细分支规则与配置方法](../../review-evidence-workflow/references/cases/combined-screening-coding.md) · [数据约定](../../review-evidence-workflow/references/contracts.md) · [对比 TALL](tall.zh-CN.md) · [对比 Agency](agency.zh-CN.md)
