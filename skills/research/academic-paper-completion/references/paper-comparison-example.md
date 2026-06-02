# Paper Comparison / Gap Analysis — Worked Example

## Source Session

SynthOS paper comparison analysis (2026-05-18). Target: "SynthOS: A Cognitive Operating System with Philosophy-Driven Self-Evolution for Autonomous AI Research" — a self-evolving AI research agent system.

## Domain

Autonomous AI Research Agents / Scientific Discovery Automation

## Top Competitors (identified via multi-source search)

| # | Paper | Venue/Year | Team | Retrieval Source |
|:--|:------|:----------:|:----:|:----------------:|
| 1 | The AI Scientist (Lu et al.) | arXiv 2024 | Sakana AI | arXiv 2408.06292 |
| 2 | Agent Laboratory (Schmidgall et al.) | arXiv 2025 | AMD + JHU + ETH | arXiv 2501.04227 (84pp) |
| 3 | OpenScholar (Asai et al.) | arXiv 2025 | Allen AI + UW | arXiv 2411.14199 |
| 4 | MLGym (Nathani et al.) | arXiv 2025 | Meta FAIR | arXiv 2502.14499 (35pp) |
| 5 | STORM (Shao et al.) | ACL 2024 | Stanford | arXiv 2402.14207 |

## Known Data Fallback Patterns

| Symptom | Cause | Recovery |
|:--------|:------|:---------|
| arXiv API returns "Rate exceeded" | Rate limit (~1 req/3s) | Wait 5s, retry. Switch to direct arxiv.org/abs/ID |
| arXiv API returns empty/non-XML | Rate limited | Try `https://` not `http://`. Fall back to `curl -sL https://arxiv.org/abs/ARXIVID` |
| pdftotext "Couldn't find trailer dictionary" | Corrupt PDF (incomplete download) | Fall back to arXiv HTML for abstract extraction |
| S2 API 403 Forbidden | API key expired/disallowed | Fall back to local PDF or arXiv HTML |

## Dimension Comparison Matrix Template

| Dimension | Your Paper | Competitor A | Competitor B | Competitor C |
|:----------|:---------:|:-----------:|:-----------:|:-----------:|
| Autonomy level | | | | |
| Architecture style | | | | |
| Self-evolution | | | | |
| Quality assurance | | | | |
| Evaluation rigor | | | | |
| Citation verification | | | | |
| Publication venue | | | | |

## Gap Prioritization

| Priority | Gap | Current → Target | Evidence |
|:--------:|:----|:---------------------|:---------|
| **P0** | Critical | Missing feature/evidence common across all top competitors | 3/3 top papers have X |
| **P1** | Notable | Missing feature in 2+ competitors | 2/3 have Y |
| **P2** | Enhancement | Nice-to-have improvement | Industry standard practice |

## Get the analysis done before final submission

This is a one-shot positioning check, not an iterative tuning loop. Run it once per paper to identify the target's biggest gaps vs current SOTA, then address the P0 items before delivery.
