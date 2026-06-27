# Numeric Cross-Location Consistency

> 关键数值在论文中的所有出现位置必须一致。

## 问题描述

论文中同一个数值（如F1分数、膨胀率百分比、p-value）出现在多个位置：摘要、引言、正文表格、表格描述、讨论、结论、图注、图内容。这些位置的值必须完全一致。

## 常见不一致模式

1. **数值精度差异**: 0.8206 vs 0.82060 vs 0.821
2. **基线不一致**: 同一个delta值用不同baseline计算
3. **引用不同来源**: abstract说ensemble F1但delta用GBC
4. **格式差异**: 0.82 vs 0.820 vs 82.0%
5. **p-value删除**: 一处有p<0.01另一处没有

## 检测方法（crispdm-heart 实战，2026-06-25）

核心F1膨胀率 +14.17% 在以下7个位置均需一致：

```bash
# 搜索核心数字的所有出现
grep -n '14.17' paper.tex          # 膨胀率
grep -n '0.9004' paper.tex         # 泄露后F1
grep -n '0.7886' paper.tex         # 基线F1 (GBC)
grep -n '0.8206' paper.tex         # baseline F1 (ensemble)
grep -n 'p<0.01\|p < 0.01\|p<0.1' paper.tex  # 统计显著性
grep -n 'F1' paper.tex             # 所有F1声明
```

**检查要求**:
1. 同一数字在所有位置格式一致（如0.7886不应有时出现0.789）
2. delta值在所有位置使用相同baseline
3. 所有p-value声明在所有位置一致
4. 图、表、正文、摘要的数值互相兼容

## 检查清单模板

| 数值 | 位置 | 值 | 来源(代码/表格) | 是否一致 |
|------|------|----|----------------|----------|
| F1膨胀率 | Abstract | +14.17% | 需验证 | |
| F1膨胀率 | Results | +14.17% | 需验证 | |
| F1膨胀率 | Discussion | +14.17% | 需验证 | |
| F1膨胀率 | Conclusion | +14.17% | 需验证 | |
| F1膨胀率 | Figure 1 caption | +14.17% | 需验证 | |
| F1膨胀率 | Figure 1 node | +14.17% | 需验证 | |
| F1膨胀率 | Limitations | +14.17% | 需验证 | |

## 修复优先级

1. **P0**: 不同位置数值不同（如一个位置0.82另一位置0.821）
2. **P0**: delta值基线不一致（最常见）
3. **P1**: 格式不一致（0.82 vs 0.820）
4. **P2**: 某位置遗漏该数值

## 关联技能

- `references/baseline-inconsistency-detection.md` — 基线不一致专项
- `references/stale-quality-report-trap.md` — 旧报告可能未检测
- `references/inline-bibliography-audit.md` — inline bib论文需额外注意
