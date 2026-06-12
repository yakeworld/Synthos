# Companion/Sister Paper Strategy

> 2026-05-25 | Derived from writing two complementary papers on breast cancer ML + three-way decision

## Concept

Sometimes a single research finding is best expressed as **two complementary papers** rather than one:

| Paper A (Critique) | Paper B (Methodology) |
|:-------------------|:----------------------|
| Reveals the problem's magnitude | Proposes and formalizes the fix |
| "The emperor has no clothes" framing | Technical depth: theorems, proofs, validation |
| Shorter, punchier (4-6 pages) | Longer, structured (5-8 pages) |
| Targets Perspective/Review sections | Targets regular research sections |

The two papers share the same core data and experiments, but serve different audiences and journals.

## When to Use

- Problem is large enough to warrant separate documentation from the solution
- Limited experimental data but strong theoretical framing
- One paper's format doesn't fit both critique and methodology
- User suggests a second angle (e.g., "can't we write about the three-class concept too?")

## Data Sharing Between Papers

```
┌──────────────────────────────────────────────┐
│  Shared Experiments                           │
│  ├── Honest benchmarks                       │
│  ├── Leakage quantification                  │
│  └── 3WD vs binary comparison                │
│                                              │
│  ┌────────────────┬──────────────────────────┐
│  │ Paper A        │ Paper B                  │
│  │ (Critique)     │ (Methodology)            │
│  │                │                          │
│  │ Tables 1-3:    │ Tables 1-3:               │
│  │ bench + leak   │ bench + leak + 3WD       │
│  │ + lit audit    │ results                  │
│  │                │                          │
│  │ No theorems    │ Theorems 1-2 + Algo 1    │
│  │ No algorithm   │                          │
│  │                │                          │
│  │ Target:        │ Target: KBS, Inf. Sci.   │
│  │ IEEE Access    │                          │
└──┴────────────────┴──────────────────────────┘
```

## Writing Order

Write both papers in parallel by section, not sequentially:

1. Run all experiments once (shared)
2. Write Results tables for both (different organization)
3. Write Paper B's Framework first (theorems need most thought)
4. Write Paper A's Introduction (needs most rhetorical power)
5. Write Methods for both
6. Write Discussion for both
7. Write Abstracts last

## Citation Cross-Referencing

Each paper cites the other as companion work:

```latex
% In Paper A (review):
% ... a formal framework that structurally solves this problem 
% is presented in our companion work~\cite{Yang2026beyond}.
```

```latex
% In Paper B (methodology):  
% The empirical motivation for this framework is detailed 
% in our companion audit~\cite{Yang2026emperor}.
```

## Dual Quality Check

| Step | Action |
|:-----|:-------|
| 1 | Paper A → Layer A → fix → Layer B → fix |
| 2 | Paper B → Layer A → fix → Layer B → fix |
| 3 | Cross-check: Claims consistent between both papers? |
| 4 | Generate combined quality summary table |
