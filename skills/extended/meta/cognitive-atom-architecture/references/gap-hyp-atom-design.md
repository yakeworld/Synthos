# GAP + HYP Atom Design Pattern

> Applying the cognitive-atom methodology to research gap discovery and hypothesis generation — two new atoms (9-atom architecture, v4.3)

## Motivation

The original 7-atom architecture covered the "how" of research (search → code → write → absorb → route → evaluate → encode) but missed the "what": identifying what to research and formulating testable hypotheses.

## Constitutional Extension

New principles added to CONSTITUTION.md:

| Principle | Core Idea |
|-----------|-----------|
| P4 假说可证伪性 | Every hypothesis must have an observable prediction AND a falsification condition |
| P5 空白可追溯性 | Every gap must be localized to specific literature contradictions or methodology gaps |

## Atom Design

### GAP — Gap Discovery

**Function**: Detect research gaps from a literature corpus

**Gap types** (4-class taxonomy):
1. `contradiction` — Paper A says X, Paper B says not-X
2. `methodology_gap` — No existing method can measure the key variable
3. `unanswered_question` — Explicit "future work" or implicit from limitations
4. `outdated_conclusion` — Early findings contradicted by newer evidence

**Key schema fields**:
```yaml
gap_record:
  type: enum[contradiction, methodology_gap, unanswered_question, outdated_conclusion]
  priority: enum[P0, P1, P2, P3]
  source_refs: [doi, claim, lines]  # ≥2 refs
  falsification_condition: string    # "If X were true, this gap would not exist"
```

**Contradiction map**: Graph of which papers contradict which, with edge types (conclusion/method/assumption/temporal) and strength (strong/moderate/weak).

### HYP — Hypothesis Generation

**Function**: Transform gaps into formalized, falsifiable hypotheses

**Required fields** (enforced by schema):
- `prediction`: Observable, measurable outcome ("Pearson r ≥ 0.5, p < 0.01")
- `falsification`: Condition that would disprove ("If r < 0.2, hypothesis is false")
- `supporting_evidence`: ≥2 literature refs
- `competing_hypotheses`: At least 1 alternative explanation
- `suggested_design`: Population, sample size estimate, key measurements

**Competing hypothesis types** (to counter confirmation bias):
- Confounding variable (Z causes both X and Y)
- Reverse causality (Y → X, not X → Y)
- Moderation effect (only significant in subgroup)
- Measurement artifact (spurious correlation from instrument)

**NSFC question tree**: For grant-eligible hypotheses, generate a hierarchical question tree (top-level question → sub-questions → specific hypotheses)

## Workflow Integration

```
ACQ → GAP → HYP → ASC (paper writing)
         ↓       ↓
    Gap Library  Hypothesis Library
    (NotionLM)   (NotionLM)
```

## Constitution Compliance

| Principle | GAP | HYP |
|-----------|-----|-----|
| P0 (traceability) | Every gap has ≥2 source refs | Every hypothesis has ≥2 supporting refs |
| P1 (reproducibility) | Same corpus → same gaps | Same gap → same hypotheses |
| P4 (falsifiability) | Gap has falsification condition | Hypothesis has prediction + falsification |
| P5 (gap traceability) | Gap has type + priority + source | Hypothesis links to source gap |

## Comparison with Existing Atoms

| Dimension | COD (Coding) | ASC (Argumentation) | HYP (Hypothesis) |
|-----------|-------------|---------------------|------------------|
| Input | Cognitive need | Hypothesis + evidence | Research gap |
| Output | Executable code | Structured argument | Formalized hypothesis |
| Core constraint | Code must run | Evidence must support | Must be falsifiable |
| Competition | N/A | N/A | Required (≥1 competing hypothesis) |
