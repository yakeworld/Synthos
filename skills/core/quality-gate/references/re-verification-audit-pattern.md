# Re-Verification Audit Pattern

> **Context**: 对之前已审计的论文执行新一轮审计时，必须验证之前修复是否仍然有效（无残留、未回退），而非直接接受上次的审计结果。
> **Last updated**: 2026-06-26
> **Case**: crispdm-heart — 2026-06-25审计后P0修复已应用，2026-06-26重验证确保无残留

## Design Pattern

### 为什么需要重验证

Paper 经过多轮修复后，state.json 和 07-quality/ 目录中的旧报告可能已经过期（stale_quality_report_trap）。如果直接使用旧报告结论，会产生：
1. **假阳性通过** — 旧报告标记 PASS，但实际仍有残留问题
2. **误判状态** — 认为修复已到位，实际未验证
3. **跳过修复** — 认为无需修复，但问题又回来了

### 重验证流程

```
Step 1: 读取旧报告 (07-quality/report-*.md) 和 fix-log.md
Step 2: 逐项检查旧修复是否仍然有效
  - grep 全文确认无残留 (p<0.01, +14.17%, 错误baseline等)
  - 重新运行 D8/D10a 扫描
  - 重新核对所有数值与 JSON 的一致性
  - 确认编译状态 (PDF 存在且非空)
Step 3: 如果旧修复仍然有效 → 报告为 VERIFIED
        如果有残留 → 报告为 STALE_RESIDUE，执行修复
Step 4: 更新 fix-log.md 添加重验证记录
Step 5: 更新 state.json notes 添加审计记录
Step 6: 更新 AUDIT_QUEUE.md 状态
```

### 关键检查命令

```bash
# 检查残留
grep -iP 'p<0|p-value|p =' paper.tex       # 统计显著性残留
grep '+14.17' paper.tex                     # 旧数值残留
grep 'ensemble.*baseline' paper.tex         # 错误基线残留

# D8/D10a 重新扫描
python3 scripts/d8d10a-scan.py <paper_dir>

# PDF 验证
file paper.pdf && ls -la paper.pdf

# Inline bib 检测
grep -c 'thebibliography' paper.tex

# .bbl 残留检测
ls -la *.bbl                               # 应为空或 0 bytes
```

## Stale Residue Detection

| 残留类型 | 检查方法 | 典型残留 |
|---------|---------|---------|
| p-value 残留 | `grep -i 'p<0\|p-value' paper.tex` | abstract 中 p<0.01 已删但 results 中还在 |
| 旧数值残留 | `grep '+14.17' paper.tex` | 部分位置已修但遗漏 |
| 基线不一致 | 检查 abstract + results + conclusion | abstract 用 ensemble, results 用 GBC |
| 统计检验残留 | `grep -i 'wilcoxon\|t.test' paper.tex` | 声称做了但代码没做 |

## BLOCKED vs IN_PROGRESS Decision Rule

| 条件 | 队列状态 |
|------|---------|
| 所有 P0 修复完成且验证通过 | 可移至 VERIFIED 或处理 P1 |
| P0 数值修复完成但 P0 代码/统计检验未完成 | [BLOCKED: P0] |
| P0 有残留修复问题 | [BLOCKED: P0_RESIDUE] |
| 仅 P1/P2 问题 | [IN_PROGRESS] 或处理完后标记完成 |
| 审计正在执行中 | [IN_PROGRESS] (仅用于正在进行的审计) |

## Real Case: crispdm-heart (2026-06-26)

### Context
- 2026-06-25 审计发现 P0 问题（摘要基线不一致 + p<0.01 + 14.17→14.18）
- P0 修复已应用，修复报告在 07-quality/
- 2026-06-26 重验证（新审计周期）

### Verification Results
- ✅ abstract F1 baseline: GBC=0.7886 正确 (ensemble baseline 完全清除)
- ✅ p<0.01: 全文 0 残留
- ✅ +14.18%: 7 处全部正确
- ✅ D8/D10a: 30/30, 100%, 0 orphans, 0 zombies
- ✅ 编译: 4 pages, 199108 bytes
- ✅ 数值与 JSON: 15/15 精确匹配

### Decision
- P0 数值修复 VERIFIED → 通过
- P0 统计检验 (Wilcoxon) 需要代码修改 → [BLOCKED: P0]
- P1/P2 可继续处理 → 后续迭代解决

### Key Learning
- 重验证不是"跳过"，而是必须执行
- 旧报告的 PASS 结论可能过期 (stale_quality_report_trap)
- state.json 中的 quality_audit_2026-06-25 记录只是"声称修复"，不是验证结果

## Pitfalls

1. **不要信任旧报告的 PASS** — stale_quality_report_trap：07-quality/ 中的旧报告可能完全过时但 state.json 仍标记 PASS
2. **不要信任 state.json 中的修复记录** — 它记录的是"声称已修复"，不是"已验证修复"
3. **grep 必须覆盖全文** — 包括 abstract, results, discussion, conclusion, figure captions, tikz 节点
4. **重验证 ≠ 从头审计** — 重点检查旧修复是否仍然有效，不是重新评估论文质量
