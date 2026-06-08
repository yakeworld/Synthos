# Layer B Audit Template

Use this template when writing Layer B audit reports for the paper pipeline.

## Structure

```markdown
# Layer B Quality Audit Report — <paper-name>

**Date**: YYYY-MM-DD
**Notebook**: <notebook-id>
**Conversation**: <conversation-id>

## Overall Quality Score: X.XX / 1.0

**Verdict**: T1 通过 (≥0.85) / T2 临界 (0.75-0.84) / 不通过 (<0.75)

---

## 1) Originality/Importance of Scientific Contribution
[Assessment]

## 2) Methodological Rigor
[Assessment]

## 3) Credibility/Reproducibility of Results
[Assessment with specific metrics/datasets]

## 4) Literature Reference Quality
[Reference structure analysis — D8, D10a, D9, orphans/zombies]

## 5) Writing/Logical Structure
[IMRaD analysis, flow, clarity]

## 6) Top 3-5 Improvement Suggestions
| Priority | Suggestion |
|:--------:|:-----------|

## 7) Scoring Summary
| Dimension | Score (implied) | Notes |
|:---------|:----------------|:------|

## Quality Gate Assessment
| Gate | Threshold | Result |
|:----:|:---------:|:------:|
| Quality Score | ≥0.85 | ✅ / ❌ |
| Layer B Status | Completed | ✅ Complete |
```

## Key Rules

1. **Always use pure English prompts** — Chinese triggers security scan
2. **Always create fresh notebook** — never clean old one (source delete is unreliable)
3. **Prefer text upload over PDF** — PDF source add returns error more often than not
4. **Report must reference actual metrics** from paper (datasets, EER, GAR, d')
5. **Cross-check with Layer A** — correct any previous audit errors in the report
