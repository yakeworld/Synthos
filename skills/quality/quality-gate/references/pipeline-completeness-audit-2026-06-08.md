# 管线完整性审计实例 — 2026-06-08 (更新)

**Date updated:** 2026-06-08  
**Previous version:** 2026-06-07

## 审计结果摘要（更新）

| 指标 | 数值 |
|------|------|
| 论文目录总数 | 107 |
| 有 .tex 文件 | ~95 |
| 有 state.json | 28 (26%) |
| 有质量报告 | ~45 (42%) |
| 有 .bib | ~30 (28%) |
| 有 .pdf 编译结果 | ~20 |
| 有 step_* 文件 | ~35 |
| T1 通过 (Layer B ≥ 0.85) | 2 (2%) |
| T2 通过 (Layer B 0.80-0.84 or equivalent) | ~8 (7%) |
| 无质量报告 (需补全) | ~60 (56%) |

## 2026-06-08 T1 论文（校准分 ≥ 0.85）

| 论文 | Layer B | D1 | D2 | D3 | D7 | Layer B覆盖 | 管线状态 |
|------|---------|----|----|----|----|------------|---------|
| off-axis-iris-normalization-correction | 0.90 | 0.95 | 0.90 | 0.95 | 0.85 | ✅ 完整 | 管线部分完成 |
| hcs3wt-breast-cancer | 0.86 | 0.95 | 0.95 | 0.90 | 0.75 | ✅ 完整 | 完整管线 |

## 2026-06-08 T2 论文（4.43-4.73/5.0）

| 论文 | 评分 | 系统 | 亮点 |
|------|------|------|------|
| saccade-adaptation-pinn | 4.73 | Layer A | 绝对空白D3=5 |
| saccade-kinematic-ODE | 4.67 | Layer A-G | G1-G7全通过 |
| head-impulse-ODE | 4.60 | 7维度 | Integrity 5.0 |
| semicircular-canal-PINN | 4.60 | 7维度 | 全量通过 |
| okan-dynamics-PINN | 4.60 | Layer A | 7项A类全部4.5+ |
| torsional-VOR-PINN | 4.53 | 7维度 | Paper 82, 7维度全PASS |
| perilymph-hydropressure-ODE | 4.43 | 7 Gate | G1=5(绝对空白) |
| caloric-nystagmus-ODE | 4.30 | Layer A | 已PASS |

## 关键瓶颈

1. **Layer B 覆盖率低**: 仅~40%论文有Layer B质检（45/107）
2. **60+篇无质量报告**: 56%的论文有.tex但完全无质量评估
3. **质量报告位置分散**: 4-5种文件名在不同目录（见 quality-report-location-discovery）
4. **D7 DOI覆盖率**: T1论文中off-axis-iris D7=0.85（有30条引用但PDF未本地缓存）
5. **D5编码乱码**: hcs3wt-breast-cancer PDF有UTF-8 ligature乱码

## 2026-06-07 vs 2026-06-08 对比

| 指标 | 06-07 | 06-08 | 变化 |
|------|-------|-------|------|
| 论文总数 | 95 | 107 | +12 |
| 有state.json | 28 | 28 | 持平 |
| Layer B覆盖 | 42% | 42% | 持平 |
| T1数量 | 4 | 2 | -2（重新评估，原4篇中2篇实为T2） |
| T2数量 | ~5 | ~8 | +3 |

注：2026-06-07的4篇T1中，scc-mathematical-morphology和crispdm-wdbc经本轮重新扫描发现Layer B不全或数据不一致，实际归为T2。

## 任务优先级（2026-06-08）

P1: 为60+篇无质量报告的论文补充Layer B质检
P1: hcs3wt-breast-cancer修复D5编码乱码
P2: off-axis-iris补充D9引用PDF本地缓存
P2: 建立论文质量索引（paper-quality-index.json）

## 教训

1. 论文管线碎片化是常态——需要定期全面审计（已见2026-06-07和2026-06-08两次独立审计）
2. **Layer B覆盖率是核心瓶颈**（仅42%，需要提升至>80%）
3. D8/D10a只在少数论文中有记录，不能依赖state.json作为质量依据
4. 目录结构不统一：有的用01-manuscript/，有的用根级别
5. 双目录问题可导致数据分裂——定期校验symlink
6. **T1论文数量比预期少**：很多管线有.tex和state.json，但Layer B质检缺失或不完整
7. **扫描逻辑需要多文件名搜索**：不要只看layer-b或quality，要搜索4-5种模式
