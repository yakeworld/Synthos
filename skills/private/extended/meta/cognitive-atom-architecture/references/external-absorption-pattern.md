# External Absorption Pattern — How to Absorb Open-Source Projects

> From session 2026-05-11: AutoResearchClaw (12k⭐) absorption into Synthos

## Pattern Overview

When absorbing an external open-source project into a Synthos-style cognitive atom system:

```
1. DISCOVER   → GitHub search / web_search / Hermes skills_list
2. EVALUATE   → Star count, activity recency, license, architecture match
3. ANALYZE    → Identify what's absorbable vs. not (architecture constraints)
4. PROPOSE    → Prioritize (P0/P1/P2), estimate cost, write proposal
5. IMPLEMENT  → Create reference docs + update skills → NO direct code copy
6. VERIFY     → Test each absorption works (API calls, output formats)
7. RECORD     → Update evolution-state.json skill_tree + last_absorption
```

## Key Constraint: No Direct Code Copy

The absorbing system may use a different execution model (Python vs pure SKILL.md). Never copy code. Instead:

| External project has | Synthos equivalent |
|---------------------|-------------------|
| Python function | SKILL.md instruction for Agent to execute |
| Python API client | curl commands in SKILL.md |
| Python data model | JSON schema in references/ |
| Python class | Reference document describing the concept |
| Python test | BENCHMARK test scenario in BENCHMARKS.md |

## What to Look For

High-value absorption targets:
- **Verification systems** (citation verification, hallucination detection)
- **Output format converters** (LaTeX, BibTeX, Overleaf integration)
- **Knowledge base schemas** (structured storage, cross-run retrieval)
- **Evolution/learning mechanisms** (lesson extraction, cross-run improvement)
- **Search source integrations** (novelty checkers, new API endpoints)

## What NOT to Absorb

- Python orchestration code → violates zero-Python principle
- Docker/container environments → different platform scope
- Graphics/chart generation → different output pipeline
- Experiment execution engines → different tool purpose
- Code that would modify core atom logic → violates P2 stability

## Integration Maturity Levels

| Level | Status | Meaning |
|-------|--------|---------|
| ❓ Proposed | Not started | Analysis done, waiting for approval |
| 🔄 In Progress | Being implemented | Reference docs being created |
| ✅ Integrated | Done | Skill updated, tested, evolution-state recorded |
| ⏳ Deferred | Parked | Worth doing but lower priority |

## Example: AutoResearchClaw Absorption

| Absorption | Type | Status | Effort |
|-----------|------|--------|--------|
| Citation Verification (L1-L4) | Reference doc + skill update | ✅ Integrated | ~30min |
| LaTeX Output (.tex + .bib) | New skill creation | ✅ Integrated | ~30min |
| Lesson Learning (lessons.jsonl) | Evolution engine update | ✅ Integrated v2.1 | ~45min |
| Structured Knowledge Base (6KB) | Output format enhancement | ⏳ Deferred | ~30min |
