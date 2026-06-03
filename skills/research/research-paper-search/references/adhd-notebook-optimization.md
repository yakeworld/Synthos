# ADHD Notebook Optimization — Session Playbook (2026-05-08)

## Purpose
Systematic optimization of a Google NotebookLM notebook dedicated to ADHD research with focus on:头戴式三维眼动追踪 (head-worn 3D eye tracking), ADHD multimodal screening, and subtyping.

## Workflow

### Phase 1: Audit Current Sources
1. `notebooklm source list` — get full inventory with types
2. Categorize each source by relevance to the core research question
3. Identify sources that are:
   - Directly relevant (keep)
   - Tangentially relevant (keep if few alternatives)
   - Irrelevant (delete)
   - Duplicates (keep the most recent/comprehensive)

### Phase 2: Search for Gaps
Search PubMed for missing categories:
- Head-worn/eyeglass eye tracking accuracy validation
- ADHD subtype classification via eye movement biomarkers
- Vestibular function / VOR function in ADHD
- Multimodal detection (eye tracking + EEG + physiological)
- VR / ecological assessment of ADHD
- Deep learning / ML classification from eye movement data
- Digital biomarkers / mobile sensing for ADHD

**Query tips:**
- PubMed queries must be specific enough to return ADHD papers (not autism or other conditions)
- Use terms like "systematic review", "meta-analysis", "clinical validation" for high-value papers
- If PubMed returns 0 results, try different query phrasing or fall back to Crossref/OpenAlex

### Phase 3: Download and Save
Save as Markdown files (lighter than PDF for NotebookLM source):
```python
fname = f'{year}_{query[:20].replace(" ", "_")}.md'
# Include: title, PMID, DOI, authors, year, journal, abstract, pubmed URL
```

### Phase 4: Add to Notebook
```bash
notebooklm source add /path/to/new_paper.md
```
Note: May need to add in batches; some requests can timeout. If one fails, retry individually.

### Phase 5: Clean Up
Delete irrelevant sources:
```bash
echo "y" | notebooklm source delete "short-uuid-prefix"
```
The `echo "y" |` pipe is required because the CLI prompts for confirmation.

### Phase 6: Save Conversation
```bash
notebooklm history --save
```

## Sources to Remove (Not ADHD-Specific)
- SMOTE oversampling algorithm papers (pure ML, not domain)
- Neural network basics papers (not specific to eye tracking)
- European consensus guidelines (covered by Faraone2021)
- Bibliometric analysis papers (limited value for grant writing)
- Duplicate assessment tools (e.g., SNAP4 when Faraone2021 already covers ADHD diagnosis)

## Key Literature Found (2020-2026)
- Oculomotor deficits ADHD meta-analysis (2021, PMID:34655657) — P0
- Transdiagnostic eye-tracking biomarkers (2025) — P0
- Head-worn eye tracker slippage accuracy (2020) — P0
- Stochastic vestibular stimulation ADHD (2023) — P0
- Vestibular function in neurodevelopmental disorders (2025) — P0
- Serious gaming + eye-tracking screening (2025) — P1
- Portable eye-tracking neurology (2026) — P1
- Computer tech ADHD diagnosis trends (2022) — P1
- VR technology measuring attention in ADHD (2022) — P1
- AI eye-tracking screening ADHD symptoms CNN (2023) — P1
- Portable eye tracking ML ADHD screening (2024) — P1
