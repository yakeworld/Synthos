# Critical Review / Perspective Paper Workflow

> 2026-05-25 | Derived from writing "The Emperor's New Accuracy" (breast cancer ML data leakage audit)

## When to Use This Workflow

Use this workflow when:

- Experimental data is insufficient for a standard experimental paper
- The thesis is a critique / re-examination of existing literature (not a new method)
- You need to combine empirical benchmarks with theoretical analysis
- The user requests "review" or "theoretical analysis" instead of experiment

## Key Differences from Standard Pipeline

| Aspect | Standard Experimental | Critical Review / Perspective |
|:-------|:---------------------|:------------------------------|
| Thesis | "We propose a new method" | "Existing literature has systematic flaw X" |
| Data source | Primary experiments | Self-run benchmarks on public datasets + lit audit |
| P-1 stage | Gap → Hypothesis → Method | Gap → Evidence of problem → Quantified inflation |
| CARS Move3 | Our new method fills the gap | **Our audit reveals the problem's magnitude** |
| Writing order | Results→Methods→... (experimental) | **Results(benchmarks)→Methods→Discussion→Intro** |
| Claims | "Our method achieves X%" | "Honest baseline is Y%, published claims exceed this by Z%" |
| Typical pages | 8-12 | 4-6 (focused argument) |
| Target journal | T2-T1 | T2-T3 (Perspective/Review section) |

## P-1: Problem Definition for a Critical Review

The thesis is not "we built something" but "we found something wrong with the literature."

### Template Thesis Statement

```
Published accuracy claims on Dataset X cluster around A%, 
but honest (leakage-free) baselines show only B%. 
The gap (A-B) = C% is attributable to untreated data leakage, 
not genuine diagnostic superiority. This systematic inflation 
distorts the evidence base for clinical translation.
```

### Evidence Chain Required

1. **Honest baseline** — metric achievable under strict no-leakage conditions (Pipeline-isolated CV)
2. **Published claims** — representative sample from literature, with full citations
3. **Leakage mechanism** — demonstrable cause (global SMOTE, multi-classifier shopping, fold cherry-picking)
4. **Structural solution** — how a different architecture mitigates the problem

## P2: Writing Strategy

### When OpenML/External Benchmarks Are Unavailable

OpenML API may return 0 tasks or 412/404 errors. **Do not stall.** Run your own benchmarks:

```python
# Minimal honest benchmark pattern
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, RepeatedStratifiedKFold

rkf = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)
pipe = Pipeline([('scaler', StandardScaler()), ('clf', RandomForestClassifier())])
acc = cross_val_score(pipe, X, y, cv=rkf, scoring='accuracy')
print(f"Honest baseline: {acc.mean():.4f} ± {acc.std():.4f}")
```

Benchmark six standard classifiers (LogReg, SVM, RF, GBM, KNN, DT) for completeness. Report the full range, not just the best.

### Leakage Simulation (Quantifiable Evidence)

Simulate and quantify each common leakage pattern:

| Pattern | Code | Expectation |
|:--------|:-----|:------------|
| Global SMOTE | `SMOTE().fit_resample(X, y)` before CV | +0.5-1.0% inflation |
| Global scaling | `StandardScaler().fit_transform(X)` before CV | Minimal (+0-0.2%) |
| Global feature selection | `SelectKBest().fit_transform(X, y)` before CV | Negative or small positive |
| Multi-classifier shopping | Bootstrap: sample N from N(0.94,0.02), take max | +1-2% for N=30 |

### Writing Order (Reverse of Standard)

For critical reviews, write **Results first** (the punchline is the data), then Methods, Discussion, Intro, Abstract:

```
Results (benchmarks + leakage quantification + lit audit table)
  → Methods (protocol + datasets + search strategy)
  → Discussion (why it matters + solutions + limitations)
  → Introduction (CARS: expand from puzzle → hypothesis → contribution)
  → Abstract (last)
```

This order ensures the argument is grounded in data from the start.

### Literature Audit Table Format

```latex
\begin{table}[h]
\centering
\caption{Representative published accuracy claims vs. honest benchmarks.}
\label{tab:literature}
\small
\begin{tabular}{lcccc}
\toprule
\textbf{Reference} & \textbf{Year} & \textbf{Dataset} & \textbf{Claimed} & \textbf{Concern} \\
\midrule
Author et al. \cite{key} & 2020 & WBC Orig. & 99.4\% & Global SMOTE likely \\
... & & & & \\
\bottomrule
\end{tabular}
\end{table}
```

Always flag papers as "honest boundary", "suspected leakage", or "misleading" explicitly.

## P4: Quality Gate Nuances for Critical Reviews

### Known Pitfall: PDF Encoding Artifacts in Gemini Layer B

When compiling with LaTeX and uploading PDF to NotebookLM for Layer B evaluation, Gemini's PDF text extraction may introduce encoding artifacts:

- `\u0010`, `\u0011`, `\u0016` control characters
- Words broken across lines: "in\nated" → "inflated"
- Ligature corruption: "fi" → "\\fb01"
- Missing ligature symbols: "›", "–" replaced by hex codes

**These are NOT errors in your .tex file** — they are PDF extraction artifacts. The Gemini evaluator will penalize D4/D5/D7 for these even though your source is clean.

**Mitigation**:
1. In the `ask` prompt, pre-warn: "The PDF may have encoding artifacts from LaTeX compilation that are not actual text errors. Please focus on content and structure."
2. If Layer B D4/D5/D7 are suspiciously low (0.05+ below Layer A), check whether artifacts caused the discrepancy
3. Re-upload as plain markdown `.md` instead of PDF when possible (`notebooklm source add paper.md`)
4. Use calibration score = min(Layer A, Layer B) but flag artifact-affected dimensions for human arbitration

### Reference Metadata Completeness

For critical reviews, every citation MUST have complete metadata (journal, volume, pages, year). The D7 score is especially sensitive because:
- Reviewers will check whether your references are real papers
- Incomplete metadata signals "LLM-generated citations"
- One missing DOI or volume number can trigger a full audit

Checklist before submission:
```
grep -c '\\bibitem' paper.tex         # Total references
grep -c '\\\\textit{' paper.tex       # Journal names (every entry needs one)
grep '\\\\bibitem' paper.tex | wc -l  # Match total
```

## Pitfalls

1. **🚩 Over-claiming "systematic review"** — If your lit audit is representative (not PRISMA-guided), say so explicitly in Limitations. Do NOT call it a "systematic review" in the title.
2. **🚩 Starting with Introduction** — For critical reviews, write Results first or you'll write the wrong Introduction.
3. **🔴 D5 Clarity suffers from PDF encoding** — See known pitfall above. Always check the PDF text output before submission.
4. **🟡 The "this is obvious" objection** — The thesis "data leakage is bad" may seem obvious to ML experts. Frame it as: "We quantify the cost of ignoring leakage" rather than "We discovered leakage exists."
5. **🟡 Narrative reframe** — If D6 (novelty) scores low, reframe from "we found X problem" to "we provide the first executable protocol for X problem detection." See `sci-paper-quality-review` references/narrative-reframe-demo-*.md.
