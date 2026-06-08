# 管线完整性审计实例 — 2026-06-07

## 背景

Sythos 论文管线发现双目录问题：`~/Synthos` 是独立目录（GitHub clone），`/media/yakeworld/sda2/Synthos` 是主仓库。合并数据、重建 symlink 后进行全面审计。

## 审计结果摘要

| 指标 | 数值 |
|------|------|
| 论文目录总数 | 95 |
| 有完整管线 (tex+bib+state+quality) | 6 (6%) |
| 有管线痕迹 (pipeline) | 23 (24%) |
| 部分完成 (partial) | 55 (58%) |
| 空白/未完成 (empty) | 11 (12%) |
| 有 Layer B 质检 | 40 (42%) |
| 有校准分报告 | 5 (5%) |
| D8≥30 已验证 | 5 |
| D10a=100% 已验证 | 5 |

## T1 论文 (校准分 ≥ 0.85) — 4 篇

| 论文 | 校准分 | D8 | D10a | DOI% | Layer B | 管线状态 |
|------|--------|----|----|----|---------|---------|
| pima-crispdm | 0.94 | 33 | 100% | 97% | ✅ | 完整 |
| scc-mathematical-morphology | 0.92 | 34 (v4) | 100% | 100% | ❌ | 管线 |
| crispdm-wdbc | 0.86 | 31 | 100% | 84% | ❌ | 完整 |
| vor-bppv-diagnosis | 0.85 | N/A | N/A | N/A | ✅ | 部分 |

## 问题论文

### 完整管线但有引用问题：
- **3wd-framework**: references.bib 为空，30篇引用全部孤儿
- **hcs3wt-breast-cancer**: 4孤儿 + 11僵尸
- **off-axis-iris-normalization-correction**: DOI 仅 57% (17/30)

### T1 论文缺 Layer B：
- scc-mathematical-morphology (T1, 需送 NotebookLM)
- crispdm-wdbc (T1, 需送 NotebookLM)

## 任务编排

84 个单任务 → 合并为 11 个任务（减少 87%）：
- P1: 6 个紧急修复 (repair + layer_b + doi_fix)
- P2: 3 个批量任务 (COMPLETE-PAPERS/PIPELINE-PAPERS/PARTIAL-PAPERS)

## 教训

1. 论文管线碎片化是常态——需要定期全面审计
2. Layer B 覆盖率是核心瓶颈（仅 42%）
3. D8/D10a 只在少量论文中有记录
4. 目录结构不统一：有的用 01-manuscript/，有的用根级别
5. 双目录问题可导致数据分裂——定期校验 symlink
