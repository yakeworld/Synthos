# Comparative Gap Analysis for Paper Improvement

> Systematically benchmark your paper against top competitors to identify and prioritize improvements.

## Workflow (7 Steps)

```
Step 1: Identify 3-5 target competitors
Step 2: Extract metadata (authors, citations, venue, abstract, page count, key features)
Step 3: Build 10+ dimension comparison matrix
Step 4: Identify gaps, grade by P0/P1/P2 priority
Step 5: Generate prioritized improvement plan
Step 6: Execute improvements (one priority at a time)
Step 7: Verify with pdflatex x2 + bibtex compilation
```

## Step 1: Competitor Selection Criteria

Pick papers that:
1. Address the **same problem domain** (e.g., autonomous research agents)
2. Are **high quality** (NeurIPS/ACL/Q1 SCI, or high-citation arXiv)
3. Use **different architectural approaches** (monolithic vs pipeline vs atomic vs retrieval-augmented)
4. Are **recent** (2023-2025 for AI/ML papers)

**Example selection** (for autonomous research agent paper):
- AI Scientist (Sakana AI, ~100+ citations) — end-to-end, fully automatic
- Agent Laboratory (AMD/JHU/ETH, 84pp) — human-in-the-loop, multi-LLM eval
- OpenScholar (Allen AI) — retrieval-augmented literature synthesis
- MLGym (Meta FAIR, 35pp) — standardized Gym benchmark
- STORM (Stanford, ACL 2024) — grounded long-form writing

## Step 2: Metadata Extraction

For each competitor, extract into a structured record:

```json
{
  "key": "AIScientist2024",
  "title": "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery",
  "authors": "Lu, Chris; Lu, Cong; Lange, Robert Tjarko; Foerster, Jakob; Clune, Jeff; Ha, David",
  "year": 2024,
  "venue": "arXiv preprint",
  "citation_count": "~100+",
  "pages": 15,
  "pdf_size_mb": 7.0,
  "has_code": true,
  "approach": "Monolithic Python pipeline",
  "key_strength": "First end-to-end automated research with real experiments",
  "key_weakness": "Fixed architecture, no self-evolution, Python-dependent",
  "abstract_snippet": "Presents the first comprehensive framework for fully automatic scientific discovery..."
}
```

**Tool commands for extraction:**
```bash
# From existing PDF
pdftotext -raw papers/Key2024.pdf - | head -80

# From arXiv page (if PDF corrupted)
curl -sL "https://arxiv.org/abs/XXXX.XXXXX" | python3 -c "
import sys, re; html = sys.stdin.read()
extract metadata...
"

# PDF metadata
pdfinfo papers/Key2024.pdf | grep Pages
```

## Step 3: Comparison Matrix (10+ Dimensions)

Group dimensions into two clusters:

### Cluster A: Core Capabilities (checkmark-based)

| Dimension | Definition | ✓ | △ | ✗ |
|-----------|-----------|:-:|:-:|:-:|
| Formal boundaries | Components have proven non-overlapping interfaces | ✓ | partial | ✗ |
| Architecture-level evolution | System evolves its own architecture, not just params | ✓ | optimizes within fixed arch | ✗ |
| Runtime independence | Zero Python/framework dependency | ✓ | minimal deps | ✗ |
| Process-level quality gates | Checks procedure execution, not just output | ✓ | output checks only | ✗ |
| Auditable absorption | External knowledge integrated with verification chain | ✓ | manual only | ✗ |
| Citation verification | Every cite → PDF file → search candidate | ✓ | partial | ✗ |

### Cluster B: Meta Metrics (quantitative/qualitative)

| Dimension | Scale | Example values |
|-----------|-------|---------------|
| Publication quality | preprint / conf / journal (+ citations) | "ACL 2024 (25 cites)" |
| Team scale | Solo / small (2-5) / medium (5-15) / large (15+) | "Sakana AI (6 authors)" |
| Code availability | none / partial / full | "github.com/..." |
| Page count | integer | 7-84 pages |
| Human evaluation | none / internal / peer review | "Anonymous peer review" |

## Step 4: Gap Identification & Priority Grading

### P0 — Fatal (reviewers notice immediately)
- No independent experimental data / no reproducibility
- No ablation studies / control groups
- Self-reported metrics without verification
- Citation fabrication detected

### P1 — Important (significant quality gap)
- Paper too short relative to competitors (7 vs 15-84 pages)
- Citation metadata sparse (placeholder authors, missing abstracts)
- Comparison table has too few dimensions (4 vs 10+)
- No figures/diagrams
- No quantified limitations

### P2 — Nice to have (polish)
- Missing code availability section
- Missing future work directions
- Single-column vs double-column layout
- No acknowledgments
- Bibliography missing venues

### Fixed vs Deferred

| Status | Meaning | Example |
|--------|---------|---------|
| ✅ Executable | Can fix with available tools (write/edit/compile) | Enrich .bib, add figures, expand sections |
| 🟡 Needs resource | Requires compute budget or API access | Run MLGym benchmarks |
| 🔴 Needs human | Requires human judgment | Independent peer review |

## Step 5: Improvement Plan Template

```
## Improvement Plan

### P0 (must fix)
- [ ] Need independent benchmark — → mention in Future Work, add to quantified Limitations
- [ ] Need ablation study — → mention as limitation with estimated β value

### P1 (important)
- [ ] Expand paper from 7→15pp — → add: architecture figure, evolution trajectory, pipeline figure, systematic taxonomy table, quantified limitations
- [ ] Enrich bibliography — → fix placeholder authors, add abstract+venue for all entries

### P2 (polish)
- [ ] Add code availability section
- [ ] Switch to double-column layout
```

## Step 6: Execute Improvements

### Rule: One priority level at a time

```
P0 first → compile verify → P1 → compile verify → P2 → compile verify
```

### Common Improvements Catalog

| Improvement | How-To | Typical Impact |
|-------------|--------|---------------|
| Add architecture figure | TikZ/SVG 3-layer diagram with teal accent | +2-3 pages |
| Add evolution trajectory | pgfplots xy-plot with score over cycles | +1 page |
| Add pipeline flow figure | TikZ horizontal G1-G7 diamond pipeline | +1 page |
| Expand Related Work | Systematic taxonomy with comparison table | +1-2 pages |
| Add more results tables | Per-atom PROBE, version trajectory, SCI scores | +1-2 pages |
| Quantify limitations | Add Δ/β/α estimates for each limitation | +0.5 page |
| Enrich bibliography | Fetch real metadata from arXiv/Crossref APIs | Embedded |
| Switch to twocolumn | `\documentclass[11pt,twocolumn]{article}` | Density doubles |

### Compilation Check (always required after each batch)

```bash
cd latex/
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
pdfinfo paper.pdf | grep Pages
grep -c "\\bibitem" paper.bbl  # Count citations resolved
```

## Real Example: SynthOS Paper Expansion (2026-05-18)

| Before (7pp) | After (11pp) | Delta |
|:------------:|:------------:|:-----:|
| 0 figures, 1 table | 3 figures, 4 tables | +3 figs, +3 tables |
| 34 citations, placeholder authors | 34 citations, full metadata | enriched |
| 3-paragraph Related Work | 5-category taxonomy + 10-dimension table | systematic |
| 4 qualitative limitations | 4 quantified limitations (Δ, β, α) | quantifiable |
| Single-column | Double-column | denser |
| 15KB .tex, 159KB PDF | 29KB .tex, 384KB PDF | 2x larger |

## Common Pitfalls

1. **PDF corruption**: AI Scientist (7MB xref error), SciAgents (6MB xref error) — always fall back to arXiv page
2. **API rate limits**: arXiv API redirects http→https; Semantic Scholar 1 req/sec; use fallback chains
3. **Placeholder citations**: G5 gate catches cite-without-PDF — don't skip this check
4. **Overclaiming without evidence**: P0 gap — self-reported scores need external calibration
5. **Bibliography not compiling**: `\b` in LaTeX via f-strings = backspace — run `cat -A paper.tex | grep '^H'`
