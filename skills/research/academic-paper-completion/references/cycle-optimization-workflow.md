# SCI Paper Cycle Optimization Workflow

A systematic approach to iteratively optimize academic papers until they meet high-quality SCI standards. Designed for researchers preparing manuscripts for SCI journal submission.

## When to Use

- User has an existing draft paper that needs quality improvement for SCI submission
- User wants to systematically enhance paper quality through iterative cycles
- Paper has experimental results but needs better presentation, analysis, or writing quality
- User needs to prepare a manuscript for a specific target journal

## Workflow Design

### Iteration Cycle

```
[Assess Current Quality] → [Identify Missing Elements] → [Execute Parallel Tasks] → [Reassess] → [Continue or Stop]
     ↑                                                                                              |
     └──────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Optimization Dimensions (Scored 1-10 Each)

| Dimension | What to Check | High-Quality Standard |
|-----------|--------------|----------------------|
| Innovation | Novelty statement, SOTA comparison | Clear Gap identified, 3+ SOTA compared |
| Methodology | Reproducibility, rigor | Pipeline encapsulation, leakage-free, ablation studies |
| Experimental Completeness | Dataset count, comparison methods | 2+ datasets, 5+ comparison methods |
| Results Presentation | Chart quality and quantity | 6+ high-quality charts, 300 DPI+ |
| Writing Quality | Logic flow, academic language | Fluent, professional, consistent terminology |
| Clinical Significance | Application scenario, limitations | Clear clinical value, limitations discussed |
| Literature Citation | Quantity, quality, recency | 30+ citations, 50%+ from last 5 years |
| Structure Compliance | Word count, chapters, format | Matches target journal guidelines |

### Typical Iteration Progression

| Iteration | Score | Major Work |
|-----------|-------|------------|
| Iteration 0 (Baseline) | ~65/100 | Initial assessment, identifying gaps |
| Iteration 1 (Core) | ~74/100 | Filling missing charts, SOTA comparison, language polish |
| Iteration 2 (Enhancement) | ~85/100 | Clinical significance deepening, limitations, abstract |
| Iteration 3 (Final Polish) | ~90+ | Consistency check, reference format, final scoring |

### Key Principle

**Stop condition**: When score reaches 90/100, or when improvement between iterations drops below 5 points.

## Debugging Experience

### Common Bug: BorderlineSMOTE Fails on Single-Class Training Data

When using BorderlineSMOTE in cross-validation, some folds may end up with only one class due to small sample size or random splitting. This causes a crash:

```
ValueError: The target 'y' needs to have more than 1 class. Got 1 class instead
```

**Fix**: Add a class count check before calling SMOTE:

```python
n_classes = len(np.unique(y_train))
do_smote = use_smote and n_classes >= 2
if do_smote:
    # Apply BorderlineSMOTE
    ...
else:
    # Skip SMOTE, use original data
    ...
```

### Common Bug: Dictionary Key Mismatch (mean_overall_accuracy vs mean_accuracy)

When computing statistics across CV folds, dictionary keys may not match between:
- The function that computes results (`run_cv_experiment`)
- The code that prints/uses results (`main()`, `print_markdown_table()`)

**Fix**: Ensure consistent key naming. If `run_cv_experiment` returns `mean_accuracy`, then all consumers must use `mean_accuracy`, NOT `mean_overall_accuracy`.

## Application Example

See the HCS-3WT breast cancer diagnosis paper case study:
- Started at ~65/100 (baseline draft)
- Through Iteration 1: Added Abstract, improved Introduction to funnel structure, added 6 new sections, 28+ high-quality references
- Through Iteration 2: 12 high-quality charts generated (300 DPI PNG + PDF vector)
- Final score: 92.5/100 (74/80)
- Result: Paper ready for submission to Artificial Intelligence in Medicine (Q1, IF ~7.0)
