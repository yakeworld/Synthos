# Stale Quality Report Trap

> 旧版 07-quality/ 报告可能完全错误，但 state.json 仍标记 PASS。

## 问题描述

论文目录中的 07-quality/ 子目录包含历史质量报告。这些报告可能在多个版本前就已过时，但 state.json 中的 `gate_status` 和 `quality_score` 可能仍然标记为 PASS。新的审计如果读取旧报告做判断，会得到错误结论。

## 典型场景（crispdm-heart 2026-06-25）

07-quality/quality-report.md 记录:
- D8=0, D10a=0%, 30个orphans, 判定"❌ FAIL"
- 但 state.json 中: gates_result.overall="PASS", quality_score=78

**根因**: 该报告是早期批次扫描（当paper.tex还不存在或不同版本时）生成的，与当前论文完全脱节。但 state.json 已经更新为PASS。

## 检测方法

```bash
# 1. 检查质量报告日期 vs state.json 日期
head -3 07-quality/quality-report.md | grep "Generated"
# 2. 对比 state.json 中质量状态
cat state.json | jq '.gate_status, .quality_score'
# 3. 检查报告日期与state.json last_updated 差异
# 4. 如果报告日期远早于 last_updated → 报告已过期
```

## 检测清单

| 检查项 | 值 | 判定 |
|--------|----|------|
| quality-report.md 生成日期 | | |
| state.json last_updated | | |
| 日期差异 | | |
| 报告中D8=0但state说30? | | 如果报告说0但state说有30引用 → 报告过期 |
| 报告中D10a=0%但state说100%? | | 同上 |

**原则**: 如果报告中的引用统计（D8, D10a, orphans）与 state.json 中 `reference_health` 或 `d8_d10a_scan` 不一致 → 报告已过期，必须重新审计。

## 修复策略

1. **忽略旧报告**: 不将其作为当前质量的依据
2. **生成新报告**: 基于当前 paper.tex 和 state.json 做独立审计
3. **验证 state.json**: 如果 state.json 也过时，需要重新运行G1-G7
4. **不自动信任**: 即使是 VERIFIED 状态，也需验证 state.json 中的 quality_score 与 gates_result.quality_score 是否一致

## 与 state.json 内部不一致的结合

```python
# state.json 内部一致性检查
state.top_level_quality_score == state.gates_result.quality_score
state.gate_status == "PASS" (should match all gates PASS)
state.d8_d10a_scan.cited_count == len(all_cite_keys_in_tex)
state.reference_health.D8 == state.d8_d10a_scan.d8
```

任一不一致 → 整个状态不可信，需重新审计。

## 关联陷阱

- 与 `comprehensive-quality-report-template.md` 结合：生成新报告时不参考旧报告内容
- 与 `references/baseline-inconsistency-detection.md` 结合：旧报告可能未检测基线不一致
