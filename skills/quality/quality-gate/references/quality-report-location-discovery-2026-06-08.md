# Quality Report Location Discovery — 2026-06-08

**Date discovered:** 2026-06-08  
**Class of tasks:** 论文质量报告扫描与审计

## 问题

论文质量报告存储在4-5种不同文件名、不同目录下，格式各异（Layer A 5分制、Layer B 0-1.0、Layer C-G等）。程序化扫描极易遗漏。

## 质量报告文件模式

| 文件名模式 | 典型位置 | 评分系统 | 示例 |
|:-----------|:---------|:---------|:-----|
| `step_quality_check.md` | 论文根目录 或 `01-manuscript/` | Layer A/B/C-G (1-5.0) | saccade-kinematic-ODE |
| `layer-b-report.md` | `07-quality/` 或根目录 | Layer B (0-1.0) | off-axis-iris |
| `qc-layer-b.md` | 论文根目录 | Layer B (0-1.0) | hcs3wt-breast-cancer |
| `layer-b-qc-v2.md` / `layer-b-qc-v3.1.md` | `07-quality/` | Layer B v2/v3 | hcs3wt-breast-cancer |
| `quality-report.md` | 论文根目录 或 `07-quality/` | 混合 (整体PASS/FAIL) | 多数论文 |
| `dimension*.md` | 论文根目录 | 单维度评分 | 少数论文 |

## 扫描策略

**不要只找单一文件名。** 按以下优先级搜索：

```
for each paper_dir:
    1. search for: *layer-b* (case-insensitive) → 最精确
    2. search for: *qc* → quality check
    3. search for: *quality* → quality report
    4. search for: *report* → may contain scores
    5. search for: *dimension* → may contain scores
```

然后对每个找到的文件，提取:
- `Overall` / `Overall Score` / `PASSED` / `FAIL` / `Score` 关键词
- 评分数字（正则: `\d+\.\d+` 或 `\d+/\d+`）
- 维度分数 (D1-D7, A-G, Layer A-G)

## 陷阱

- **不要假设目录结构统一**: 同一篇论文可能同时有根目录和`01-manuscript/`版本
- **不要只看`layer-b`**: 有些论文只有`step_quality_check.md`，有些只有`quality-report.md`
- **不要跳过文件**: 质量报告可能在小文件(<500字节)中，但包含关键评分
- **不同评分系统**: Layer A用1-5.0，Layer B用0-1.0，不要混为一谈
- **os.walk递归**: 论文目录本身可能是`01-manuscript/`的子目录，需要去重

## 2026-06-08 实战记录

扫描107篇论文，发现:
- 2篇T1: off-axis-iris (Layer B 0.90), hcs3wt-breast-cancer (avg 0.86)
- 8篇T2 (4.43-4.73/5.0)
- 60+篇有.tex但无质量报告
- 关键瓶颈: Layer B覆盖率仅~40%

## 后续建议

1. 统一质量报告位置: 强制写入`07-quality/quality-report-latest.md`
2. 在每篇论文中维护`latest-quality-snapshot.json` 包含: 最佳score, 最佳Layer, verdict
3. 建立论文质量索引: 定期扫描所有论文，生成`paper-quality-index.json`
4. Layer B 优先: 论文管线中Layer B是最关键的质量指标
