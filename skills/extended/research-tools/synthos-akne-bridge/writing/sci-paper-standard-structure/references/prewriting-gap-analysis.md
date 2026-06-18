# Pre-Writing Gap Analysis — From Research Assets to SCI Paper Plan

> Use this BEFORE writing a paper. It answers: "What experiments/data do I need to collect before I can write the paper I want?"

## Trigger

User asks any of:
- "我能基于现在的X写一篇什么论文？"
- "需要补充什么实验和数据？"
- "当前资产能发什么水平的论文？"
- "想写一篇关于XXX的SCI，看看缺什么"
- Any question about research feasibility, experiment planning, or paper type selection

## Workflow

### Phase 1: Current Asset Audit

Audit the user's existing work across 5 categories:

| Asset Type | What to check | Examples |
|:-----------|:--------------|:---------|
| **Published papers** | Search PubMed/Google Scholar for the user's prior work | BPPV仿真13篇, 眼动追踪R2资产 |
| **Simulation platforms** | Code, models, simulation environments | BPPV虚拟仿真平台, PINN代码 |
| **Clinical data access** | Patient databases, equipment availability, historical records | vHIT records, iTrace data, 眼动仪原型 |
| **Algorithm/code** | Algorithm implementations, math derivations, analysis scripts | VOR-Kappa四元数代码, 闭式解析解 |
| **Literature base** | NotebookLM notebooks, PDFs, R2 reviews | iTrace-Kappa R2, VOR解码 R2 |

### Phase 2: IMRaD Gap Mapping

Map current assets to the 5 IMRaD sections. For each section, assess:

| Section | Critical Data Need | Assessment |
|:--------|:-------------------|:-----------|
| **Introduction** | Literature knowledge + Gap identification | 🟢 Usually well-covered by R2 |
| **Methods** | Algorithm detail, experiment protocol | 🟡 May need formalization |
| **Results** | **Quantitative data (≥2 tables)** | 🔴 Most common gap — needs experiments |
| **Discussion** | Comparison baseline | 🟡 Can be prepared |
| **Conclusion** | Contribution summary | 🟢 Can be drafted |

### Phase 3: Results Gap — Experiment Planning

The most common bottleneck is the Results section. For each potential experiment:

| Dimension | Questions |
|:----------|:----------|
| **Simulation experiments** | Can we generate synthetic data with known ground truth? What metrics (RMSE, R², ICC)? |
| **Clinical/real data** | Do we have ethics approval? Patient access? Equipment ready? Sample size? |
| **Comparison/baseline** | What is the gold standard? (e.g., iTrace for Kappa, vHIT for VOR) |
| **Reproducibility** | How many subjects/trials? Test-retest? Intra/inter-rater reliability? |

### Phase 4: Feasibility Assessment

For each identified experiment, assess:

| Factor | 🟢 Easy (days) | 🟡 Moderate (weeks) | 🔴 Hard (months) |
|:-------|:--------------|:-------------------|:-----------------|
| **Effort** | Existing code/data, just run analysis | Need minor modifications | Need new data collection |
| **Ethics** | Retrospective data | Chart review, expedited IRB | Prospective study, full IRB |
| **Equipment** | Equipment ready & calibrated | Minor setup needed | Need new hardware |
| **Skills** | Known technique | Need literature learning | Need new method development |

### Phase 5: Paper Path Recommendation

Based on the gaps and feasibility, recommend the right paper type:

| Paper Type | When to Choose | Data Need | Journal Level |
|:-----------|:---------------|:----------|:--------------|
| **Pure simulation** | Strong simulation platform, no clinical data | Simulated data with ground truth | Q2-Q3 |
| **Methodology + pilot** | Algorithm novel + small clinical sample (n≥15) | Simulation + pilot data | Q1-Q2 |
| **Clinical validation** | Access to clinical data + gold standard comparator | n≥30 paired measurements | Q1 |
| **Algorithm-only** | Novel math derivation, no experimental data feasible | Derivation + 1-2 demo cases | Q2-Q3 |

### Phase 6: Minimal Viable Experiment Plan

Output a concrete, ordered plan:

```
Milestone 1⃣ [This week, pure computation]:
  - What: [experiment description]
  - Method: [how to do it]
  - Output: [specific table/figure]

Milestone 2⃣ [1-2 weeks]:
  - ...

Milestone 3⃣ [2-4 weeks]:
  - ...
```

## Example: VOR-Kappa 3D Angle Paper

This session's real-world output for a novel algorithm (VOR-based 3D Kappa angle calibration):

| Phase | Result |
|:------|:-------|
| **Asset audit** | ✅ Existing: VOR-Kappa四元数闭式解代码, iTrace数据, 13篇BPPV论文, 眼动仪原型 |
| **IMRaD gap** | Methods: ✅ 完整推导; Results: ❌ 无实验数据 |
| **Experiment plan** | ① 仿真验证(1周,纯计算) ② 与iTrace回顾数据对比(1周) ③ 临床验证n=30(2-4周) |
| **Paper path** | 方法学论文 + 临床预实验 → Q2期刊 |

## Pitfalls

| Pitfall | Symptom | Fix |
|:--------|:--------|:-----|
| **Overestimating asset readiness** | "我们可以写一篇Q1论文"但没有原始实验数据 | Use the IMRaD gap mapping — if Results column has zero entries, you need experiments first |
| **Assuming existing data fits new paper** | Published paper A + Paper B ≠ new paper C | Check: are the same subjects? Same methods? Same research question? |
| **Forgetting clinical feasibility** | Proposing a study that needs 6 months of IRB approval | Always ask: retrospective vs. prospective? Equipment ready? Patient access? |
| **One experiment is not a Results section** | Only 1 table planned | SCI papers need ≥2 tables minimum. Plan at least 2 complementary experiments |
