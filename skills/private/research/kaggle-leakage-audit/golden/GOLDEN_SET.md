---
name: kaggle-leakage-audit
description: GOLDEN_SET.md
---

# 金测集: kaggle-leakage-audit

> 单一真理来源。所有改进必须通过 golden 测试。
> 语义依据：SKILL.md「Golden 集合 · GOLDEN SET」「Genes (KAGG-001..KAGG-007)」「验证清单 · VERIFICATION」「规律总结」「IO_CONTRACT」。
> 口径：基线（所有预处理在 CV 折内）vs 泄漏变体（ImputeLeak / SMOTELeak / SevereLeak：全局预处理先于分割），RF 与 XGB 各一轮。

## 测试用例
| ID | 类型 | 描述 | 关键检查（gene 映射） |
|----|------|------|----------------------|
| case_001 | 正常路径 | 类别不平衡数据集（记录正负比）+ 基线（折内预处理）+ 三个泄漏变体，RF 与 XGB 各一轮 | KAGG-001（全局 SMOTE 主要泄漏源）、KAGG-003（高复杂度模型受害更深）、KAGG-006（预处理严格在折内）、KAGG-007（结论基于 F1 对比表） |
| case_002 | 错误路径 | 正样本 <1% 的极度不平衡数据集，仅凭 F1≈0 下结论；且全局 SMOTE 先于分割却报告为「基线 F1」 | KAGG-004（须补 precision/recall/AUC）、预处理跨分割边界未识别（漏检全局 SMOTE 泄漏） |
| case_003 | 正常路径（边界） | 平衡/多类分布均匀数据集 → 跳过不平衡泄漏深度审计 | KAGG-005（平衡/多类不受此类泄漏影响） |

## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过（一票否决）
- 泄漏杀伤对比表必须含 基线 vs ImputeLeak/SMOTELeak/SevereLeak 的 F1 差异，且标注全局 SMOTE 为主要杀伤源
- RF/XGB 偏差必须单独标注，与低复杂度模型结果区分
- 正样本 <1% 场景禁止仅凭 F1≈0 下结论，须补 precision/recall/AUC
- 错误路径必须检出跨分割边界泄漏（不得把全局 SMOTE 先于分割报告为基线）

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（折内预处理、SMOTE 主泄漏源判定、F1 对比表、跨分割泄漏检出） |
| high | 0.7 | 重要但不致命（不平衡度记录、高复杂度模型单独标注） |
| medium | 0.4 | 有价值但不是核心（平衡集跳过深度审计、结论规律总结） |
