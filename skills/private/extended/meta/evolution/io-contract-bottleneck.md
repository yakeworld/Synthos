# IO_CONTRACT Bottleneck Analysis

## Summary

As of cycle 71 (2026-06-12), only 6/109 SKILL.md files (5.50%) contain an `IO_CONTRACT`
section in their body text. This is the single largest drag on the benchmark dimension
(0.34 weight × 0.0550 = 0.0187 contribution to a 0.488 benchmark).

## Current State

| Metric | Value |
|--------|-------|
| Total SKILL.md | 109 |
| With IO_CONTRACT | 6 (5.50%) |
| Missing IO_CONTRACT | 103 (94.50%) |
| Formula contribution | 0.0550 × 0.34 = 0.0187 |
| Max possible contribution | 1.0 × 0.34 = 0.34 |
| Gap to max | 0.3213 (94.5% of this dimension) |

## Skills With IO_CONTRACT

1. `evolution/SKILL.md` — self-evolution engine (cycle: int → report: dict)
2. `knowledge-acquisition/SKILL.md` — multi-source paper search
3. `pubmed/SKILL.md` — deep PubMed/MEDLINE search via NCBI E-utilities
4. `research-ideation/SKILL.md` — research ideation framework
5. `task-router/SKILL.md` — system entry router
6. `research-paper-search/SKILL.md` — added cycle 71

## Why IO_CONTRACT Is Hard

1. **New concept**: IO_CONTRACT was introduced in ~cycle 65-67 as a standardization
   measure. Most skills predate this requirement.
2. **Body-level change**: Unlike `version` or `signature` (which go in YAML frontmatter),
   IO_CONTRACT must appear in the body text as a markdown section. This requires
   understanding the skill's actual input/output semantics.
3. **Manual effort**: Each addition takes ~2-5 minutes of reading the skill to extract
   meaningful I/O types.

## Marginal Impact Analysis

Adding 1 IO_CONTRACT changes the benchmark formula by:
- io_contract_pct increases from N/109 to (N+1)/109
- Formula delta: (1/109) × 0.34 ≈ 0.0031 per addition
- Overall score delta (6 dimensions): 0.0031 / 6 ≈ 0.0005

To reach 50% coverage (55/109), requires **49 additional additions** = ~49 cycles
at current pace (1-2 per cycle).

## Priority Strategy

Add IO_CONTRACT to highest-impact skills first:

| Priority | Skill | Reason |
|----------|-------|--------|
| P0 | research-paper-search | Entry point for all research — highest indirect impact |
| P0 | pubmed | Most frequently used research sub-skill |
| P1 | openalex | Multi-disciplinary search, high frequency |
| P1 | arxiv | Preprint access, high frequency |
| P1 | knowledge-extraction | Used by paper-pipeline |
| P2 | research-ideation | Already has one, verify/update |
| P2 | knowledge-base-audit | Audit workflow |
| P2 | scc-bppv-kinematics | Domain-specific research |

## Format Reference

See evolution/SKILL.md for the canonical format.

## Verdict

IO_CONTRACT is structurally required for benchmark improvement, but the ROI is low
per-edit (~0.0005 overall). Accept 5-10% coverage as realistic until a bulk-edit
strategy is devised. The effort is still worth doing because:
1. It improves documentation quality (forces I/O clarity)
2. It's a "correctness" signal, not just a score
3. Cumulative effect: 10 additions = ~0.005 overall improvement
