---
name: kaggle-leakage-audit
description: 1. 不平衡度越高 → 泄漏杀伤越大
signature: 'kaggle-leakage-audit -> research: synthetic skill for kaggle leakage audit'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. 不平衡度越高 → 泄漏杀伤越大
    signature: 'kaggle-leakage-audit -> research: synthetic skill for kaggle leakage
      audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

## IO_CONTRACT

- **input**: Kaggle 数据集（标签不平衡度）+ 基线/泄漏变体模型配置（全局 SMOTE/impute/scale vs 折内预处理）
- **input**: 评估指标需求 — F1 对比、模型复杂度梯度（RF/XGB）
- **output**: 泄漏杀伤对比表 — 基线 vs ImputeLeak/SMOTELeak/SevereLeak 各变体的 F1 差异
- **output**: 泄漏规律总结 — 不平衡度/模型复杂度与泄漏杀伤的关系结论（全局 SMOTE 为主要杀伤源）

|
| Helix | 所有预处理在 CV 折内部 | 基线（正确） |
| ImputeLeak | 全局 impute + scale i>- 分割 | 几乎无影响 |
| SMOTELeak | 全局 SMOTE → 分割 | 🔴 主要杀伤来源 |
| SevereLeak | SMOTE + impute + scale 全局 | 🔴 与纯 SMOTE 一致 |

## 规律总结

1. 不平衡度越高 → 泄漏杀伤越大
2. 模型越复杂（RF/XGB）→ 受害越深
3. 只有全局 SMOTE 造成实质性泄漏；全局标准化几乎无害
4. 平衡/多类数据集不受影响
5. 极度不平衡(0.17%)时所有模型 F1≈0，SMOTE 也无法挽救

## 参考

- `ref/educational-standard.md` — 完整教学规范（04-standards/）
- `ref/run_audit_v2.py` — Python 审计脚本（02-benchmarks/）

## 验证清单 · VERIFICATION

- [ ] 所有预处理（Impute/Scale/SMOTE）严格在 CV 折内部执行，无任何步骤跨越数据分割边界
- [ ] 已对比基线与泄漏变体（ImputeLeak / SMOTELeak / SevereLeak）的 F1 差异，并输出泄漏杀伤对比表
- [ ] 数据集类别不平衡度已记录，且审计结论标注了全局 SMOTE 为主要杀伤来源
- [ ] 高复杂度模型（RF/XGB）的泄漏偏差已单独标注，与低复杂度模型结果区分
- [ ] 极度不平衡（正样本 <1%）场景下，F1≈0 已用其他指标（precision/recall/AUC）补充评估，未仅凭 F1 下结论
- [ ] 平衡/多类数据集已确认不受此类泄漏影响，跳过了不平衡泄漏深度审计

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 类别不平衡数据集（记录正负比）+ 基线配置（所有预处理在 CV 折内）+ 三个泄漏变体（ImputeLeak / SMOTELeak / SevereLeak：全局 impute/scale/SMOTE 先于分割），RF 与 XGB 各一轮
- **Golden Output**: 泄漏杀伤对比表（基线 vs 各变体 F1 差异）+ 规律总结（全局 SMOTE 为主要杀伤来源；不平衡度越高/模型越复杂杀伤越大；全局标准化几乎无害），RF/XGB 偏差单独标注
- **Golden Error**: 预处理跨越分割边界未被识别（如全局 SMOTE 先于分割却报告基线 F1）、正样本 <1% 时仅凭 F1≈0 下结论而未补 precision/recall/AUC、或把全局 impute/scale 误标为主要泄漏源

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Kaggle Leakage Audit---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[KAGG-001]** 数据集存在类别不平衡 → 优先审计全局 SMOTE 操作，因其是主要泄漏源
- **[KAGG-002]** 预处理步骤（Impute/Scale）位于数据分割之前 → 检查是否引入全局信息泄漏，但通常影响较小
- **[KAGG-003]** 使用高复杂度模型（如 XGB/RF） → 预期泄漏导致的性能偏差更显著，需重点监控
- **[KAGG-004]** 数据极度不平衡（如正样本 <1%） → 即使存在泄漏，模型 F1 可能仍接近 0，需结合其他指标评估
- **[KAGG-005]** 数据集类别平衡或多类分布均匀 → 可跳过针对不平衡泄漏的深度审计，因不受此类泄漏影响
- **[KAGG-006]** 需要验证预处理安全性 → 确保所有预处理（Impute/Scale/SMOTE）严格在 CV 折内部执行
- **[KAGG-007]** 审计结论输出 → 必须基于基线与泄漏变体（ImputeLeak/SMOTELeak/SevereLeak）的 F1 对比数据