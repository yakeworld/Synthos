# GOLDEN_SET.md — research-output-evaluation

> 对应原则：P0（凡数必源）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

金标准自设（`self_defined`）。设计目标：验证给定一个含 .tex / PDF / quality_score 状态与逐篇质量门状态、质量分、T 等级、D10a 覆盖率、僵尸引用数的论文目录，技能能否产出多维交叉验证评估报告，且所有数字可追溯、缺失项单独统计、僵尸引用不折叠、低质量产出有明确处置分类。

## 测试用例表 (cases/)

| Case | 类型 | 输入摘要 | 通过标准 |
|------|------|----------|----------|
| case_001 | 正常路径 — 全量目录多维评估 | 12 篇论文目录（含 .tex 9 篇、PDF 8 篇、quality_score 11 篇），含质量门状态、质量分、T 等级、D10a 覆盖率、僵尸引用数 | ① 质量门分布可复算 PASS 3 / CONDITIONAL 5 / FAIL 4，与输入一致（RESE-004）；② 缺失项单独统计（无 .tex = 3，无 PDF = 4，无 quality_score = 1）且不混入主分布；③ 复合阈值「T1+T2 且 D10a≥95%」过滤出核心资产清单，数量与占比精确匹配 expected；④ 僵尸引用总数 47 逐一归属到论文、未折叠进质量分均值；⑤ 每篇 FAIL 论文带处置标签（need_major_revision 或 archive），无模糊地带（RESE-003） |
| case_002 | 错误路径 — 数字无源（违反 RESE-004） | 目录中 3 篇论文缺 quality_score 但报告声称质量分均值 55.3，且 2 篇 D10a 值为 null | 技能必须：① 拒绝输出无源均值（或将无源论文显式排除并说明分母），触发 RESE-004 数据诚实门；② null D10a 论文不得计入 D10a≥95% 比例，分母单独注明；③ 错误信息含上下文（哪篇缺什么）与恢复建议（补 quality_score / 补 D10a 审计）（RESE-006）；④ 不得编造缺失值 |

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，采用语义等价判定：

- `gate_distribution` / `missing_stats` / `core_assets` / `zombie_citations` 等字段必须与输入独立重算结果精确一致（数必重算）
- case_002 中 `rejections` 字段必须列出被拒/被排除的数字及其原因；`inferred` 与 `factual` 必须分离标注（VERIFICATION #8）

## 通过标准

- pass_threshold: 1.00（2 个 case 全部通过）
- 理由：本技能为 P0 数据诚实门，任一数字不可追溯即失败，不设容忍度（对应 RESE-004 / 凡数必源）
- 权重：RESE-004（数字可追溯）与 RESE-003（处置分类无模糊）为 critical；其余为 normal

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始自设金标准，2 个 case（正常 + 无源错误路径） | Synthos Agent |
