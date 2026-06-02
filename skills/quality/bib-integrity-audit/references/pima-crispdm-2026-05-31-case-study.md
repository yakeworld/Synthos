# pima-crispdm 引用审计实战（2026-05-31）

## 初始状态

| 指标 | 值 |
|:-----|:----|
| 总引用 | 49条 |
| 有效PDF | 17篇（35%） |
| 假DOI | ~15条（33%） |
| 僵尸引用 | 5条 |

## 修复过程

### 阶段1: 批量下载（17→34→33→43→41篇）

| 方法 | 成功 | 说明 |
|:-----|:----:|:------|
| article9_pima副本 | 9篇（3篇错误PDF后删除） | 原项目已有PDF |
| OA直连 | 3篇 | PLOS ONE, SpringerOpen |
| arXiv直链 | 3篇 | XGBoost, SHAP, Lohani |
| meddata平台 | 3篇 | Dietterich, Kaufman, 部分其他 |
| SS/OpenAlex替换+OA下载 | 8篇 | 用OA论文替换假条目 |
| 用户手动meddata云盘 | 1篇 | Ali2025 (IEEE) |

### 阶段2: 假DOI检测与修复

**检测方法**：逐条Crossref API验证 → 33%为假DOI

| 来源 | 修复数量 | 典型 |
|:-----|:--------:|:-----|
| PDF元数据提取 | 2 | Kalagotla2021, Dey2023 |
| SS搜索 | 3 | Ali2025, Gr2024, Tong2024 |
| OpenAlex搜索 | 7 | Cabral2025, Chinnababu2024等 |

### 阶段3: 引用挖掘（从已有PDF找OA替代）

SS引用图谱 `/references` 端点。从4篇核心PDF（Saeed2023/Talari2024等）的 `citedPaper` 字段挖出18条OA候选。

### 最终状态

| 指标 | 值 |
|:-----|:----|
| Bib条目 | 41条 |
| 有效PDF | 41篇 |
| D9覆盖率 | **100%** |
| D8 | 41 ✅ ≥30 |
| D10a | 100% ✅ 0孤儿0僵尸 |

## 关键教训

1. **假DOI比例极高**（33%）— 凡引必验
2. **OpenAlex比SS覆盖更广** — 搜不到时切换
3. **SS引用图谱是OA候选金矿** — `references?fields=openAccessPdf`
4. **meddata不支持IEEE/BMJ/Lancet/Hindawi** — 这些需要手动或替换
5. **用SS引用挖掘替代付费墙** — 效率极高（4篇挖出18条OA候选）
6. **保持bibkey不变只改DOI** — 正文不需要修改
7. **删除前验证Cite Chain** — 避免删空 `\cite{}` 组
