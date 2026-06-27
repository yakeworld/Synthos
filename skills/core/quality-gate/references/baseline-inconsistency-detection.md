# Baseline Inconsistency Detection

> 检测论文中"delta值使用的基线与报告基线不一致"问题。

## 模式描述

论文声称一个变化量（如F1膨胀率、准确率提升），但实际计算使用的基线与文中声明的基线不同。

## 典型示例（crispdm-heart 2026-06-25）

```
Abstract: "ensemble achieves F1=0.8206. However... F1 inflates to 0.9004 — a +14.17% increase"
实际: 0.8206 → 0.9004 = +9.72% (不是+14.17%)
+14.17% 来自: GBC 0.7886 → 0.9004
```

论文在摘要中用ensemble(0.8206)作为baseline，但膨胀率计算用了GBC(0.7886)作为baseline。

## 检测方法

```bash
# 1. 找到所有delta/膨胀/变化百分比声明
grep -n '%\|increase\|decrease\|delta\|delta\|Δ\|变化\|膨胀' paper.tex

# 2. 提取每个delta值声称的baseline和delta值
# 3. 从JSON中验证: (delta_end - baseline) / baseline * 100 = 声称的delta%

# 关键: 不仅检查数字本身正确，还要检查baseline是否一致
```

## 检查清单

| 位置 | baseline声明 | delta值 | 从JSON验证 | 是否一致 |
|------|-------------|---------|-----------|----------|
| Abstract | | | | |
| Intro | | | | |
| Table描述 | | | | |
| Discussion | | | | |
| Conclusion | | | | |
| Figure caption | | | | |
| Figure内容 | | | | |

**原则**: 同一个delta值必须在论文所有出现位置使用**相同baseline**。如果某处用ensemble而另一处用GBC，都是不一致。

## 修复策略

1. **确定正确baseline**: 哪个值最符合论文逻辑？
2. **统一全文**: 将所有位置改为一致baseline
3. **修正数字**: 用正确baseline重新计算delta%
4. **移除不可验证声明**: p-value等无法从代码验证的统计声称需移除

## 关联陷阱

- 与 `references/numeric-cross-location-consistency.md` 配合使用
- 常与 `references/stale-quality-report-trap.md` 同时出现（旧质量报告可能未检测到此问题）
