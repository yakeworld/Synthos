# Full-Claim L0.5 Verification Protocol

> **Key lesson from Pima CRISP-DM 2026-06-01**: Don't just verify "key" claims — extract ALL numerical claims systematically. LLMs routinely fabricate ensemble/ablation values even when source data exists for baseline models.

## The Trap

Previous L0.5 protocols said "verify key numerical claims." In practice, this means the agent picks 2-3 values that look important, checks them, and declares PASS. Meanwhile, 5 out of 18 claims in the paper have no source file whatsoever — including the paper's central ensemble F1 value.

## Systematic Protocol

### Step 1: Full Extraction

```bash
# Extract ALL precise numerical values from paper
grep -oP '\d+\.\d{2,}' 01-manuscript/paper.tex | sort -u
# This catches F1 scores, accuracy, Lambda, p-values, etc.
# Filter for meaningful values (ignore figure/table labels)
```

Key: Extract every number with 2+ decimal places. No pre-filtering.

### Step 2: Source Inventory

```bash
# List all experimental output files
find . -name "*.json" -path "*/experiments/*"
find . -name "*.csv" -path "*/experiments/*"
# Map what experiments were actually run vs what the paper claims
```

### Step 3: Cross-Reference Each Value

For each numerical claim in the paper, trace to source:
- **Has source file** → Compare values (diff < 0.02 passes)
- **No source file** → Flag as UNVERIFIABLE
- **Source file exists but values differ** → Document discrepancy

Example comparison table:
```
Claim in paper | Source file | Paper value | Source value | Verdict
Ensemble F1    | (none)      | 0.7541      | —            | ❌ NO SOURCE
Ablation LDA   | benchmark   | 0.6759      | 0.6647       | ❌ MISMATCH
PIDD Helix F1  | cross_dataset| 0.664       | 0.664        | ✅ OK
```

### Step 4: Write Missing Experiments

When claims lack source code, write and run proper experiments:

1. **Ensemble/voting experiments**: The most commonly fabricated values. Write actual `VotingClassifier` code, run proper CV, save JSON output.
2. **Ablation experiments**: Write explicit `run_ablation.py` with controlled scenarios. Use the SAME classifier as the paper baseline.
3. **Individual model benchmarks**: Already have source? Still verify the specific model version matches.

### Step 5: Update Paper with Real Values

Replace ALL fabricated values with experimental output. This includes:
- Abstract (most commonly contains stale old values)
- Introduction (research contributions list)
- Results (tables + text)
- Discussion (inflation percentages, Lambda)
- Conclusion (summary numbers)
- Clinical implications (Recall interpretation)

Common missed locations (check ALL of these):
- `\begin{abstract}` ... `\end{abstract}`
- `\item \textbf{...}:` (research contribution list items)
- Table environments (`\begin{tabular}`)
- Discussion/Conclusion paragraphs embedded in other sections

### Step 6: Retain All Traces

```
paper_dir/03-code/experiments/
  run_ensemble.py       # Voting experiment code
  ensemble_results.json # Real output (JSON)
  run_ablation.py       # Ablation experiment code  
  ablation_results.json # Real output (JSON)
  run_helix_benchmark.py  # Multi-model benchmark
  helix_benchmark_results.json
```

Each JSON contains: experiment name, date, protocol, full result values, fold-level detail.

## Common Fabrication Patterns

| Pattern | Detection | Fix |
|:--------|:----------|:-----|
| **Ensemble F1 > any component model** | Check: ensemble F1 > max(component F1)? If yes, suspicious | Run actual VotingClassifier |
| **Ablation Λ values > 0.01** | LDA-based Λ is typically ~0.002; higher values suggest ensemble model was used not LDA | Check which classifier ablation used |
| **"Gradient Boosting achieves highest F1"** | On PIDD, GBC=0.6379, LDA=0.6647, LinearSVC=0.6678 — GBC is NOT top | Check actual benchmark |
| **No medium-leakage effect** | Medium leakage (global impute+scale, SMOTE inside CV) may have ZERO effect on LDA — document this honestly | Don't fabricate a non-existent effect |
| **Λ formula deviation** | Paper claims Λ=0.090 but formula gives Λ=0.002. The formula in paper defines Λ = (F1_L - F1_H) * (Recall_H - Recall_L) / max(F1_H, Recall_H). Check actual computation. | Recompute from raw data |

## Pima 2026-06-01 Reference Numbers

### Actual Experimental Results (PIDD, 5x2 CV, Helix isolation)

| Model | F1 | Recall | Precision | Accuracy | AUC |
|:------|:--:|:------:|:---------:|:--------:|:---:|
| LinearSVC | 0.6678 | 0.7142 | — | — | — |
| LogisticRegression | 0.6667 | 0.7172 | — | — | 0.8233 |
| LDA (isolated) | 0.6647 | 0.7104 | 0.6264 | 0.7500 | 0.8234 |
| LDA (severe leak) | 0.7290 | 0.6888 | 0.7762 | 0.7444 | 0.8442 |
| Ensemble GBC+LDA+LR | **0.6699** | **0.7142** | **0.6328** | **0.7542** | **0.8291** |

**Key insight**: Ensemble F1 (0.6699) ≈ individual model F1 (0.6647-0.6678). The ensemble doesn't magically boost F1 — it stabilizes variance. The paper's claimed 0.7541 was fabricated.

### Fabrication Magnitude

| Claim | Fabricated | Actual | Error |
|:------|:----------:|:-----:|:-----:|
| Ensemble F1 | 0.7541 | 0.6699 | **+0.0842** |
| Ensemble Recall | 0.7500 | 0.7142 | +0.0358 |
| Ablation LDA F1 | 0.6759 | 0.6647 | +0.0112 |
| Severe Leak F1 | 0.7338 | 0.7290 | +0.0048 |
| Lambda | 0.090 | 0.002 | +0.088 |
