# CARS Restructure Case Study: Synthos Paper

> Generated from Session 2026-05-21 — Synthos paper optimization
> Technique: CARS Introduction Restructuring

## Problem

The original Synthos paper's Introduction had a single paragraph containing **12 citations** covering:
- Background (research agent ecosystem, benchmarks)
- Three critical gaps (epistemological, self-improvement, philosophical)
- Related work (Claude Code, DeepResearchAgent, AI-Research-SKILLs, GEPA)
- Foundational LLM advances (Transformers, GPT-3, CoT, etc.)

This created a "citation wall" that made the argument hard to follow.

## Restructured Output (3 subsections)

### Subsection 1: Move 1 — The Rise of AI Research Agents
- 2 sentences on the ecosystem + benchmarks
- 1 sentence identifying the shared limitation
- **Before**: ~6 citations in one run-on sentence
- **After**: Clean topic sentence + 5 citations for ecosystem breadth

### Subsection 2: Move 2a — Three Critical Gaps
Each gap gets its own bold-labeled paragraph:
- **Epistemological rigor is weakly enforced** → 4 citations
- **Self-improvement remains ad-hoc** → 3 citations  
- **Philosophical principles remain aspirational** → 6 foundational citations

### Subsection 3: Move 2b→3 — Related Work and Positioning
- One paragraph with **12 systems** (Claude Code, DeepResearchAgent, AI-Research-SKILLs, GEPA, STORM, OpenScholar, nature-skills, ARS, PaperOrchestra, AutoR, KILO-KIT), each with 1 line analysis
- Comparison table (Table 1)
- Transition sentence: "However, no existing system simultaneously achieves..."
- Three numbered contributions

## Key Metrics

| Metric | Before | After |
|--------|--------|-------|
| Introduction length | 2 paragraphs, 32 lines | 3 subsections, 54 lines |
| Citations in first segment | 12 (single paragraph) | 4-6 per subsection |
| Systems compared | 4 | 12 |
| Subsection count | 0 | 3 |
| CARS Moves tracked | Implicit | Labeled (Move1/Move2a/Move2b→3) |

## When to Apply

- A single paragraph contains ≥8 citations
- The paragraph mixes background, gap, and related work without structure
- Reviewer feedback mentions "literature review lacks focus"

## Pitfalls

- Don't split for splitting's sake: each subsection needs a real topic sentence
- Move2b (Gap) and Move3 (Contributions) can share a subsection when the gap is the direct motivation
- Keep citation density ≤4 per paragraph even after splitting
