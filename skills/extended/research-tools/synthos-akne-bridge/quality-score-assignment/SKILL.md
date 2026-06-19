---
name: quality-score-assignment
related_skills: ["knowledge-extraction"]
description: Quick-scorer for assigning quality_score to stuck-at-complete-steps papers. Covers D7 reference audit, D3 data source check, D4 structural completeness, D5 compilation check, and auto threshold assignment.
version: 1.0.0
author: Hermes Agent
license: MIT
category: research
---

## IO_CONTRACT

- **input**: `paper: str, rubric: dict` — 用户请求描述、上下文信息
- **output**: `scores: dict — 评分`

> 对应原则：P2（机械原子暴露输入输出规范）


# Quality Score Assignment — Stuck-at-Complete-Steps Papers

> Papers with all steps completed in `steps_completed` but no `quality_score` in `state.json` must get a quality score assigned during advancement. Never leave `quality_score` as null/None.

## Trigger

Paper satisfies `current_step in steps_completed` AND `len(steps_completed) >= 8`.

## 5-Step Quick Scorer

| Step | Check | Method | Typical Score |
|------|-------|--------|---------------|
| **D7 References** | Count `\cite{}` vs `\bibitem{}` or `references.bib` entries | 0 cite in text → 0.50; zombie bibitems → 0.50-0.70; clean BibTeX 100% D10a → 0.80-0.85 |
| **D3 Results** | Data source: synthetic vs clinical? Code exists? | Synthetic only → 0.55-0.60; real clinical with code → 0.70-0.80 |
| **D4 Completeness** | IMRaD present? Missing sections? | IMRaD missing → ≤0.60; complete → ≥0.70 |
| **D5 Clarity** | Compiled PDF valid? 0 errors? | Valid PDF, 0 errors → 0.70; errors → ≤0.60 |
| **D1/D2/D6** | Quick scan of abstract + methods + conclusion | Manual estimate based on content quality |

## Formula

```
quality_score = round(avg(D1, D2, D3, D4, D5, D6, D7) * 100)
```

## Auto Threshold Assignment

| avg | Threshold | Gate Status |
|-----|-----------|-------------|
| ≥ 0.80 | T2 (Nature子刊/NeurIPS) | T2_PASS |
| ≥ 0.75 | T3 (SCI 1-2区) | T3_PASS |
| ≥ 0.70 | T4 (SCI 3-4区/中文核心) | T4_PASS |
| < 0.70 | T4 border | T4_BORDERLINE_FAIL |

## Key Pattern: `thebibliography` with 0 `\cite{}`

When LLM generates a paper, it often creates `\begin{thebibliography}...\bibitem{...}...\end{thebibliography}` with a "Reference Verification" section but **never adds `\cite{key}` commands in the actual text body**. Detection: `grep -c '\\cite{' paper.tex` → 0 while `grep -c '\\bibitem{' paper.tex` → 15+.

Fix: For each `\bibitem{key}`, add a `\cite{key}` in the text body wherever that reference is relevant.