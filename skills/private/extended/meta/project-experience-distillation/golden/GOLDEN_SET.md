# Golden 集合 · project-experience-distillation

> 单一真理来源。所有改进必须通过 golden 测试。

## 测试用例表

| Case ID | 名称 | 类型 | 输入要点 | 预期行为 |
|---------|------|------|----------|----------|
| case_001 | 正常提炼：ODE 正反馈耦合 | normal | P141 视网膜剪切 ODE 调优实践，含正反馈耦合发现 | 提炼至约束类型级别，扩展 ode-simulation-tuning |
| case_002 | 正常提炼：批量 DOI 修复 | normal | batch_fix_all.py 修复 88 篇论文 DOI | 提炼聚类检索模式，扩展 paper-literature-supplement |
| case_003 | 错误路径：只记录不反思 | error | 仅含操作步骤，未回答"为什么有效" | 拒绝产出，报"只记录不反思"并要求补充反思 |

## 通过标准

### case_001（ODE 正反馈耦合）
1. `reusable_patterns` 中无项目名（P141/P140）、路径、日期
2. 已上升到约束类型级别（"耦合必须加性且基线锚定"，非 "alpha 改小"）
3. 回答了"为什么有效"（PROJ-001）
4. `skill_update` 为扩展 ode-simulation-tuning 的 diff（PROJ-004 优先扩展不新建）
5. 模式可跨项目复用

### case_002（批量 DOI 修复）
1. `reusable_patterns` 中无具体项目名/日期
2. 提炼出约束类型级别模式（"聚类检索替代逐篇检索"）
3. `skill_update` 为扩展 paper-literature-supplement（非新建 skill）
4. 含量化对比（40min→2.5min 的约束是"批量维度聚合"）

### case_003（只记录不反思）
1. 不产出 `reusable_patterns`（为空或 null）
2. 错误引用 PROJ-001（只记录不反思）
3. 错误信息包含：具体缺失（未回答"为什么有效"）
4. 错误信息包含：恢复建议（补充反思问题后再提炼）

## 文件清单

- `cases/case_001.json` — ODE 调优实践输入
- `cases/case_002.json` — 批量 DOI 修复实践输入
- `cases/case_003.json` — 无反思输入
- `expected/case_001.json` — ODE 提炼预期输出
- `expected/case_002.json` — DOI 修复提炼预期输出
- `expected/case_003.json` — 无反思预期错误
