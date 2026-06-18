# SynthOS Writing Pipeline Execution Protocol

> Captured: 2026-05-18 | Source: 3 consecutive writing pipeline tests + 6+ user corrections
> Governing principle: Pipeline is only valid when EVERY atom loads its SKILL.md and executes real (not simulated) operations.

## Core Rules

### Rule 1: No Simulation — All Data Must Be Real
- Every search must use real API calls (S2 1req/s, PubMed, Crossref, OpenAlex, arXiv, bioRxiv)
- Every PDF download must attempt real download (use `curl -sL` to follow redirects)
- If a paper doesn't exist or can't be downloaded: report it honestly, don't simulate
- 0 results is a valid output — not a failure

### Rule 2: Every Atom Loads Its SKILL.md Before Execution
The pipeline fails silently when atoms are skipped. For each atom in the chain:
```
1. Read the atom's SKILL.md (skill_view or cat) → understand its protocol
2. Execute per that protocol (not ad-hoc)
3. Save output to <run_dir>/<atom-name>_output.json
4. Update pipeline_trace.json
```
**Chain**: ROUTE → ACQ → EXT → ASC → HYP → ARG → VER → latex-output

### Rule 3: ROUTE — First Step, Every Time
Load task-router SKILL.md → analyze query keywords → determine mode:
- `simple_chain`: linear execution, one pass
- `exploratory_loop`: inner-loop only (HYP→VER→ASC iteration)
- `research_twoloop`: inner + outer loop (ACQ→EXT bootstrap, then inner loop, outer review every 5 iterations)

Write `pipeline_trace.json` to run directory with: run_id, mode, atom_chain, status.

### Rule 4: ACQ — Multi-Keyword Search Protocol
Per knowledge-acquisition v1.5.0:
- **At least 3 keyword variants**: core → synonyms → methodology (→ → Chinese → broad)
- **Default limit: 100** per source (S2: `limit=100`, PubMed: `retmax=100`, Crossref: `rows=100`)
- **Rate limits**: S2 1req/sec (sleep 1s between calls), PubMed 3req/sec
- **Fallback chain**: S2 → PubMed → Crossref → OpenAlex → arXiv → bioRxiv → local_absorption_db
- **Cache**: check `outputs/search-cache/` first (24h TTL)

### Rule 5: ACQ — PDF Download + Naming
- Use `curl -sL` (with `-L` to follow 301 redirects — arXiv uses 301→302→200)
- **PDF filename = `{BibTeX_key}.pdf`** where key = `{first_author_surname}{year}` (e.g., `Chen2025.pdf`)
- Save to `{run_dir}/{bibkey}.pdf`
- If download fails: mark `pdf_status = "unavailable"`, still include the paper in results

### Rule 6: ACQ — BibTeX .bib Saving
Every paper (downloaded or not) gets a `.bib` file:
```
refs/{bibkey}.bib
```
Format:
```bibtex
@article{Chen2025,
  author    = {Chen, X. and Wang, S. and others},
  title     = {Full paper title},
  journal   = {Journal Name},
  year      = {2025},
  volume    = {15},
  pages     = {1337595},
  doi       = {10.xxx/...},
  abstract  = {Abstract text from API}
}
```
**All fields from real API data** — never fabricate metadata.

### Rule 7: Quality Threshold (≥40 References)
- After PDF download, check reference count (via Crossref `reference` field or PDF parsing)
- Papers with ≥40 references: mark as high-quality in `field_summary`
- Papers with <40 references: include but note the count
- If PDF can't be downloaded: still include the paper, mark `pdf_status = "unavailable"`

### Rule 8: EXT → ASC → HYP → ARG — Sequential, Each Loads Its Skill
Each atom depends on the previous output. Execute in strict order:
1. **EXT**: Load knowledge-extraction SKILL.md → read raw_papers → extract key_findings/methodology/domain/limitations/themes → write `knowledge-extraction_output.json`
2. **ASC**: Load association-discovery SKILL.md → read EXT output → identify associations and research_gaps → write `association-discovery_output.json`
3. **HYP**: Load hypothesis-generation SKILL.md → read ASC output → generate falsifiable hypotheses (each with prediction + testability + falsification) → write `hypothesis-generation_output.json`
4. **ARG**: Load argument-expression SKILL.md → read HYP output → write paper sections with citations → write `argument-expression_output.json`

### Rule 9: VER — Multi-Persona Debate + 6D Scoring
Load viewpoint-verification v1.3+ SKILL.md → read ARG output → verify each claim:
- Multi-persona debate (absorbed from ARS anti-sycophancy protocol)
- 6-dimensional epistemic scoring: evidence_relevance, falsifiability, scope_calibration, argument_coherence, exploration_completeness, methodological_rigor
- Each claim gets: verdict (supported/refuted/inconclusive), confidence score, evidence trace, gaps, contradictions
- Overall assessment with critical gaps list

### Rule 10: latex-output — Export Protocol
Load latex-output SKILL.md → read ARG output → generate:
- `paper.tex` — full LaTeX document with sections, citations, bibliography
- `references.bib` — BibTeX entries
- `build.sh` — compile script (pdflatex + bibtex + pdflatex + pdflatex)

### Rule 11: Pipeline Trace (pipeline_trace.json)
Every pipeline run writes a trace file:
```json
{
  "run_id": "20260518_064558",
  "query": "write a paper about SynthOS...",
  "mode": "research_twoloop",
  "status": "completed | running | error",
  "routing": {"complexity": "research", "atom_chain": [...], "mode": "research_twoloop"},
  "atoms_executed": [...],
  "output_dir": "outputs/runs/20260518_064558",
  "started_at": "...",
  "completed_at": "..."
}
```

## Common Pitfalls

| # | Pitfall | Avoidance |
|---|---------|-----------|
| 1 | **Simulating ACQ output instead of real search** | Always hit real APIs. 0 papers > fake papers. |
| 2 | **Skipping atom SKILL.md loading** | Load EVERY atom's SKILL.md before executing it. |
| 3 | **Forgetting -L flag for PDF download** | arXiv returns 301 redirect — use `curl -sL`. |
| 4 | **Using limit=5/10 instead of 100** | Default `max_results=100` per ACQ v1.5.0. |
| 5 | **No sleep between S2 calls** | S2 is 1req/sec — `sleep 1` between every curl call. |
| 6 | **No BibTeX key for PDF naming** | PDF must be `{AuthorYear}.pdf`, never generic names. |
| 7 | **No .bib file for abstracts** | Every paper gets a `.bib` file in `refs/` directory. |
| 8 | **Not checking reference count** | ≥40 references = high quality. Check via Crossref `reference` field. |
| 9 | **Not updating pipeline_trace.json** | Each atom update the trace after execution. |
