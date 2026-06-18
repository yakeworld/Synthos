# Paper Pipeline Scan Procedure

**Session:** 2026-06-07 | **Purpose:** Diagnostic of full paper pipeline state across 95论文目录

## Scanning Approach

The paper pipeline at `outputs/papers/` contains 95 paper directories. Each paper follows the convention:
```
outputs/papers/<paper-name>/
  01-manuscript/      # .md sections
  07-quality/         # quality reports
  03-code/            # scripts and data
  06-references/      # bib, pdfs
```

## Key Metrics to Extract

1. **校准分 (Calibration Score)** — Look in quality reports for lines containing "校准分" with values 0.5-1.0
2. **T1/T2/T3 labels** — T1 ≥0.85, T2 ≥0.80, T3 <0.80
3. **D8 (参考文献数量)** — Count of references, target ≥30
4. **D10a (引用一致性)** — Must be 100%
5. **Layer B质检** — Gemini-based quality check on top of Layer A

## Patterns Found (2026-06-07)

### T1 Papers (4):
- **pima-crispdm**: 校准分=0.94, D8=40, D10a=100% — all D dimensions ≥0.95
- **scc-mathematical-morphology**: 校准分=0.92, D8=100, D10a=100%
- **crispdm-wdbc**: 校准分=0.86 (optimized from 0.78→0.86), D8=31, D10a=100%
- **vor-bppv-diagnosis**: 校准分=0.85 (v7 revision), has Layer B

### T2 Critical (差0.01-0.05 to T1):
- **membranous-scc-reconstruction**: 校准分=0.81 — bottleneck: D3/D2/D6

### Papers with D8 but no Calibration Score:
19 papers have D8≥30 but quality reports use different formats (qc-d8-refs.md, auto-generated) that don't contain explicit calibration scores. These still need manual review.

## Common Quality Report Formats

1. **Layer A/B table** — `| 维度 | Layer A | Layer B | 校准分 |` format (most structured)
2. **D8 check only** — `qc-d8-refs.md` — just reference count and D10a
3. **Step-by-step** — `step_quality_check.md` — per-section checks
4. **Auto-generated** — status messages without explicit scores

## Key Insight

Many papers have quality files but the quality check format varies. A universal scanner that reads `*quality*`, `*qc*`, `*qualcheck*` files will find quality data across all papers, but extracting calibration scores requires format-aware parsing (regex for "校准分" with decimal 0.XX values).
