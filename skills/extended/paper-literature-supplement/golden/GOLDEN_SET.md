# GOLDEN_SET.md — paper-literature-supplement

> 对应原则：P0 证据可溯性（凡数必源）、P1 原子可复现性、六大铁律①凡文必配30引 / ②凡引必核
> golden_set_origin: self_defined
> 单一真理来源：所有功能改进必须通过本 golden 测试（见 SKILL.md「Golden 集合 · GOLDEN SET」小节）

## 设计依据

本技能为管道技能（ACQ 检索 → EXT 引用提取 → 下载 → quality-gate 质检），金标准自设。
设计目标验证：**给定一个引用不足的论文目录，管道能否补齐至 30+ 篇引用、每篇 PDF 过 `%PDF-` 魔数验证、无 PDF 引用被删除且保留 ≥20 篇、quality-gate D8≥80% 且 D10a≥90% 无 undefined citation**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 引用解析路径 | 2/2 | `.bbl` 文件 / paper.tex 内联 `\bibitem` |
| 正常路径 | 2 case | 标准补齐 + 错误处理（Crossref 误匹配人工核对） |
| 错误路径 | 1 case | paper_dir 不存在 / 无引用可解析 → 拒绝执行并给出恢复指引 |
| 质检门 | 3 项 | D8 ≥80%、D10a ≥90%、无 undefined citation |

## 测试用例表 (cases/)

| case | 类型 | 输入摘要 | 期望结论 |
|------|------|----------|----------|
| case_001 | 正常 | `paper_dir=outputs/papers/pima-crispdm`（.bbl 解析 22 篇），2 个 topic_queries | 补齐至 32 篇；29 篇 PDF 过 `%PDF-`；3 篇无 PDF 引用已删；D8=0.94, D10a=0.97，无 undefined citation |
| case_002 | 正常(错误处理) | `paper_dir=outputs/papers/bppv-nystagmus`（内联 `\bibitem`，15 篇），Crossref 自动匹配 3 篇标题不符 | 3 篇 DOI 人工核对标题+年份后修正；补齐至 30 篇；quality-gate 全过 |
| case_003 | 错误路径 | `paper_dir=outputs/papers/not-exist`（目录不存在） | 管道拒绝执行；错误信息含上下文与恢复指引；不产生部分结果 |

## 通过标准

- **引用数**：补齐后引用 ≥30 篇；删除无 PDF 引用后保留 ≥20 篇（宁缺毋滥）。
- **PDF 验证**：保留的每篇引用对应 PDF 必须过 `%PDF-` 魔数（`head -c 5` 以 `%PDF-` 开头）。
- **DOI 核对**：Crossref 自动匹配的 DOI 必须人工核对标题+年份；不匹配则修正或删除。
- **质检门**：quality-gate 结论 D8（引用完整性）≥80%、D10a（bib-tex 匹配）≥90%、无 undefined citation。
- **检索方式**：检索必须经聚类（每方向 1 次 × 5 聚类），不逐篇 80 次检索。
- **错误路径**：输入非法时不启动管道，错误信息含上下文与恢复建议。

## pass_threshold: 0.80

3 个 case 中至少 2.4 → 权重加权分 ≥ 0.80 且全部 critical 检查通过。
critical 检查：case_001 的 D8/D10a 门、case_003 的拒绝执行。

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-30 | 初始自设金标准，3 个 case（正常 2 + 错误 1） | Synthos Agent |
