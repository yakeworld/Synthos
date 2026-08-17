# GOLDEN_SET.md — openml-benchmark

> 对应原则：P0（凡数必源，数必重算）+ P2（稳定下沉）
> golden_set_origin: self_defined

## 设计依据

金标准自设（`self_defined`）。设计目标：验证给定 OpenML 任务的原始 run 列表（含字符串型 evaluation value、无效 run、Weka 特有方法）与 Helix 本方法指标，技能能否产出干净的基准对比表：float 转换、无效 run 过滤、独立重算均值、排名定位、框架差异标注与正确归因排序。

## 测试用例表 (cases/)

| Case | 类型 | 输入摘要 | 通过标准 |
|------|------|----------|----------|
| case_001 | 正常路径 — PIDD 基准对比 | PIDD 任务 55 个原始 run（含 3 个 accuracy/f1=0 无效 run、47 个 evaluation value 为字符串）+ Helix CatBoost F1=0.7759 / GBC F1=0.7629 | ① 无效 run（f1=0）被过滤，有效样本 = 52；② 字符串 value 全部 float() 转换后复算：均值 accuracy 0.6745 / f1 0.6982（容差 ±0.001，数必重算）；③ 对比表含 WEKA RF F1=0.7648、最佳 0.8026（AttributeSelectedClassifier）；④ Helix 排名位置基于有效样本正确计算；⑤ 归因排序：模型实现差异 > 不做 SMOTE/标准化 > 特征选择不可移植（OPEN-004），未归因于预处理；⑥ Weka 特有方法标注 not_portable_to_sklearn |
| case_002 | 错误路径 — str 未转换 + 无效 run 混入（OPEN-002） | 10 个 run，evaluation value 全为字符串，其中 2 个 f1="0.0" | 技能必须：① 未做 float() 的字符串不得参与均值/排序（若直接拼接或按字典序排序即失败）；② f1=0 的 2 个 run 过滤出均值，有效 n=8；③ 复算均值与 expected 一致（容差 ±0.001）；④ 报告注明过滤数与原始 n（n=10 → 有效 n=8），不得静默丢弃 |

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，采用语义等价判定：

- `mean_accuracy` / `mean_f1` 必须可由 expected 中给出的有效 run 列表独立重算（数必重算，不可袭旧）
- `rank` 必须基于「有效样本中 f1 严格大于本方法 f1 的 run 数 + 1」计算
- `attribution_order` 首项必须是模型实现差异（OPEN-004）
- `rejections` 必须列出被过滤的 run id 及原因

## 通过标准

- pass_threshold: 1.00（2 个 case 全部通过）
- 理由：均值/排名错误直接污染论文基准声明，属 P0 数据诚实问题，不设容忍度（±0.001 为浮点重算容差，非判定容忍）
- 权重：OPEN-002（float 转换 + 无效过滤）与均值复算为 critical；排名与归因为 normal

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始自设金标准，2 个 case（PIDD 正常 + str/无效 run 错误路径） | Synthos Agent |
