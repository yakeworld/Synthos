# Absorption Record: PaperSpine V2

## Source
- **GitHub**: https://github.com/WUBING2023/PaperSpine
- **Author**: WUBING2023
- **Version**: V2
- **License**: MIT

## 5-Dimension Score

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Architectural Alignment | 4.0 | Claude Code skill suite (flat folders + slash commands) vs Synthos (hierarchical + DAG). Different paradigm but same goal. |
| Philosophical Alignment | 4.5 | "Motivation-driven writing" aligns with Synthos's "hypothesis-first" principle. Strong evidence ethics. |
| Gap Fill | 5.0 | Synthos paper-workflow lacks: Writing Rationale Matrix, scene-specific adaptation, artifact audit trail, dual rewrite/build modes |
| Code Quality | 4.5 | Well-structured, clear README, artifact checker scripts, multi-platform install |
| Actionability | 5.0 | Directly absorbable concepts: Writing Rationale Matrix, motivation confirmation gate, scene profiles, artifact inventory |

**Overall Score: 4.6/5.0 (P0)**

## Key Capabilities Absorbed

| # | Capability | Synthos Integration | Priority |
|:-:|:-----------|:--------------------|:--------:|
| 1 | **Writing Rationale Matrix** | Pre-writing artifact explaining each section's motivation, evidence, and SOTA reference | P0 |
| 2 | **Motivation-First Gate** | User must confirm core thesis/motivation before any writing begins | P0 |
| 3 | **Scene-Specific Profiles** | journal ≠ conference ≠ competition ≠ report — different prompt sets per scene | P1 |
| 4 | **Artifact Checklist** | 15+ artifacts produced per run, not just final manuscript | P1 |
| 5 | **Dual Rewrite/Build Mode** | Explicit rewrite mode for improving existing drafts | P2 |

## Detailed Analysis

### PaperSpine V2 Key Innovations

| Feature | PaperSpine V2 | Synthos paper-workflow (current) |
|:--------|:--------------|:---------------------------------|
| **Core philosophy** | Motivation-driven (why) | Hypothesis-driven (what) |
| **Pre-writing artifact** | `writing_rationale_matrix.md` — row-by-row plan | None (write directly) |
| **Scene detection** | journal/conference/report/competition (4 profiles) | IMRaD only (1 profile) |
| **Research tiers** | flash (3 ex) / pro (6 ex) | Fixed depth |
| **Evidence bank** | `evidence_bank.md` + `claim_register.md` | Embedded in hypothesis |
| **Audit trail** | 15+ artifacts in `paper_rewriting_output/` | Final paper only |
| **Ethical constraint** | "Never fabricate data..." — explicit in every SKILL.md | Constitution-based (P0) |
| **Dual mode** | Rewrite existing + Build from materials | Build from scratch only |

### What Synthos Should NOT Absorb

| Feature | Reason to Skip |
|:--------|:---------------|
| Flat skill structure (6+ separate SKILL.md files) | Synthos uses hierarchical DAG atoms — more modular and testable |
| Scene-specific SKILL.md per target | Better: scene-specific prompt templates within a single paper-workflow skill |
| Claude Code plugin metadata | Synthos runs on Hermes Agent, not Claude Code |
| Separate dist/ for Codex vs Claude | One source, one deployment target (Hermes) |

### Integration Plan

**P0 (immediate):**
1. Add "Motivation Confirmation" gate to paper-workflow — before NotebookLM Q&A, force user to confirm the core thesis
2. Define `writing_rationale_matrix.md` format — pre-writing artifact

**P1 (next cycle):**
3. Add scene detection (journal/conference/competition/report) — different prompt templates per scene
4. Add artifact inventory — `outputs/{paper_id}/` directory with structured sub-artifacts

**P2 (future):**
5. Add explicit "rewrite existing" mode — separate from "build from scratch" path

## References
- WUBING2023. *PaperSpine V2*. GitHub: https://github.com/WUBING2023/PaperSpine
