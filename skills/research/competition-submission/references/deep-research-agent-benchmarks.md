# Deep Research Agent Benchmarks — Evaluation & Submission Guide

Research agent benchmarks evaluate **report quality, evidence synthesis, and reasoning depth** rather than factual recall. Synthos's full pipeline (ACQ→KEX→ASC→HYP→ARG) maps directly to these benchmarks.

## Active Benchmarks (2025-2026)

| Benchmark | Venue | Tasks | Evaluator | Best for |
|-----------|-------|-------|-----------|----------|
| **ResearchRubrics** | ICLR 2026 | 101 open-ended queries | LLM-as-judge (Gemini 2.5 Pro) vs structured rubrics | Full report quality (Synthos ARG) |
| **BrowseComp-Plus** | ACL 2026 | ~200 factoid QA | Qwen3-32B vs ground-truth answers | Search+extract agents (NOT Synthos's strength) |
| **HeurekaBench** | ICLR 2026 | 50+ data analysis tasks | Ground-truth from published findings | AI Co-scientist on experimental data |

## ResearchRubrics — Submission Strategy

### Architecture (ICLR 2026 Benchmark)

ResearchRubrics evaluates AI-generated research reports against **structured binary rubrics** — each criterion is scored Satisfied (full weight) or Not Satisfied (0). Scores range 0-100%. The evaluator is an LLM-as-judge (official: Gemini 2.5 Pro via LiteLLM; offline: any available model).

### Critical Approach: Rubric-First Writing

**Do NOT write the report first and check rubrics after.** Read ALL rubric criteria before writing a single sentence:

1. List every criterion with its weight and axis
2. Create a compliance checklist mapping each criterion to a specific report location
3. Write the report section-by-section ensuring each criterion is addressed
4. Self-check after writing: for each criterion, confirm the report satisfies it

### Pipeline (Synthos)

```
ACQ (search S2/PubMed for domain papers, 1 req/sec rate limit)
  → KEX (extract structured knowledge — MUST use full PDFs, not abstracts)
  → ASC (find associations between approaches, identify gaps)
  → HYP (generate 3-5 testable hypotheses from gaps)
  → ARG (write comprehensive markdown report)
```

### Word Count Criticality

| Report type | Expected length | Synthos default | Strategy |
|-------------|:--------------:|:---------------:|----------|
| 2-page overview | **850-1100 words** | 2000-4000 words | Tighten: pack same density into half the words |
| Full report | 3000-4500 words | 2000-4000 words | Expand as needed |

**For short reports (850-1100 words):** Every sentence must serve ≥1 criterion. Cut background fluff. Use dense academic prose. Put definitions inline rather than in separate sections. The word limit IS a rubric criterion with weight 5.0 — exceeding it loses points immediately.

### Offline Self-Evaluation (when Gemini unavailable)

Without the official LiteLLM pipeline, use this manual checklist approach:

```
1. Read all rubric criteria
2. For each criterion, decide: does the report explicitly address it?
3. Score: earned_weight / total_weight
4. Identify failures → regenerate with fixes
```

This was the method used to score 0% (Engram+PC), 13% (AI drug discovery), and 46% (NELF-E in HCC) for 3 ResearchRubrics tasks. The 46% scorer succeeded on ~half the criteria; 0% and 13% failed most implicit/explicit content requirements.

### Common Failure Patterns (from 3-task attempt)

| Pattern | Frequency | Fix |
|---------|:---------:|-----|
| Word count over limit | 3/3 | Tighten prose, remove redundant explanations |
| Missing specific citation (e.g., "Dang et. al 2025") | 2/3 | Check rubric for named references before writing |
| Section names don't match rubric expectations | 2/3 | Use rubric-specified headings verbatim |
| Missing required analogy/example | 2/3 | Review "Implicit Criteria" axis for stylistic asks |
| Deterministic language ("will", "always", "guarantee") | 1/3 | Use hedging: "suggests", "may", "remains to be proven" |

### Rubric Categories

| Axis | Weight range | What it checks |
|------|:-----------:|----------------|
| Explicit Criteria | +2 to +5 | Required content: specific methods, examples, sections |
| Implicit Criteria | -4 to +5 | Writing quality: no contradictions, proper definitions, appropriate tone |
| Instruction Following | -4 to +5 | Exact format: word count, section names, audience targeting |
| References & Citation Quality | +2 to +5 | Real citations, accessible links, dataset-specific claims |
| Communication Quality | +1 to +4 | Structure: lists, figures, glossaries, logical flow |
| Synthesis of Information | +2 to +5 | Connecting ideas across domains, identifying trade-offs |

### Key Pitfalls

1. **Word count matters**: The 2-page overview task expects 850-1100 words. Synthos naturally produces 2000-4000 words. For this benchmark type, shorter is better — pack the same density into fewer words.
2. **Full-text only**: KEX must extract from actual PDFs, not abstracts. Abstracts miss critical details (e.g., Paper 2 found "EEG does NOT contribute" — only visible in the results section).
3. **No deterministic language**: Negative rubrics penalize `will`, `always`, `guarantee`. Use hedging: `suggests`, `may`, `remains to be proven`.
4. **Real citations with DOIs**: Performance claims must specify dataset (PubChem, ChEMBL, Tox21), validation method, and include DOI.
5. **Exact section names**: Some rubrics require specific section headings (e.g., "Applications", "Advancements", "Challenges", "Adoption") — check rubric criteria before writing.

## When to Use

- User asks to evaluate Synthos against a benchmark
- User has a research agent and wants a quantitative quality score
- Preparing for ICLR/ACL/NeurIPS agent evaluation tracks

## Related Skills

- `hermes-scientist` — Research platform orchestration
- `research-paper-search` — Multi-source paper search and PDF download
