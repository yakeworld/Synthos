# Literature Gap Analysis — Grant Proposal Enhancement

> Methodology for detecting weak/skewed references in Chinese grant proposals and replacing them with high-quality citations.
> Validated on: 温州市科技项目 (PD误吸风险预测模型, 2026-05-13)

## When to Use

During a grant proposal review when:
- The reference list has obvious weak entries (case reports, tangential animal studies, irrelevant methods papers)
- Key epidemiological statistics lack citations (e.g., "发生率50%~80%" with no [ref])
- The proposal claims "已有研究表明..." but doesn't name the actual study
- You see 5+ year old citations for fast-moving fields (ML/nutrition/PD treatments)

## Workflow

### Phase 1: Reference Audit — 4-Type Classification

Read every reference in the proposal and classify:

| Type | Signal | Action |
|------|--------|--------|
| **Direct** | Title exactly matches topic, same population/disease | Keep, verify DOI |
| **Tangential** | Related field but different population (e.g., stroke→PD) | Replace with disease-specific |
| **Weak** | Case report (n=1), conference abstract, animal study | Replace with systematic review/RCT |
| **Irrelevant** | No connection to the proposal (e.g., OSA→PD aspiration) | Delete |

**Rule of thumb**: If >30% of references are Tangential/Weak/Irrelevant, the proposal will be flagged for poor literature preparation.

### Phase 2: Gap Detection — Missing Citation Points

Scan the proposal body for data claims that need citation support:

1. **Prevalence/incidence numbers**: "发生率50%~80%" → needs source
2. **Risk ratios**: "RR=3.30", "死亡率增加2~3倍" → needs source
3. **AUC claims**: "AUC 0.75-0.85", "AUC 0.950" → needs the actual study cited
4. **Odds ratios**: "OR=6.407" → needs original paper
5. **Vague claims**: "已有预测模型..." → name and cite the model
6. **Guideline mentions**: "ESPEN与ASPEN指南均强调..." → cite the specific guideline

### Phase 3: Literature Search — Target Replacement

Search in parallel using S2 API (for speed) + PubMed (for depth):

**Search strategy pattern** (for PD aspiration example):

| Topic | S2 query | PubMed MeSH query |
|-------|----------|-------------------|
| Disease prevalence | "Parkinson's disease dysphagia prevalence" | ("Parkinson disease"[MeSH]) AND (dysphagia OR deglutition disorders) AND epidemiology |
| Prediction model | "Parkinson's disease aspiration prediction model" | ("Parkinson disease"[MeSH]) AND (aspiration pneumonia OR respiratory aspiration) AND (risk assessment OR nomogram) |
| Nutritional factors | "malnutrition Parkinson aspiration pneumonia" | ("Parkinson disease"[MeSH]) AND (nutritional status OR malnutrition OR albumin) AND (pneumonia OR aspiration) |
| Nursing pathway | "nursing aspiration risk stratification elderly" | (dysphagia OR aspiration) AND (nursing assessment OR clinical pathway) AND elderly |

**Quality filters**: 
- Year ≥ 2020 (prefer 2023-2026 for fast-moving fields)
- Systematic reviews / Meta-analyses first (highest evidence level)
- Disease-specific > general elderly > other disease
- Chinese population data preferred for Chinese grants

### Phase 4: Replacement Table — Build and Justify

Construct a replacement table with 4 columns:

| Original [N] | Problem | Replacement | Justification |
|-------------|---------|-------------|---------------|
| [5] Hsu 2026 | 口腔锻炼Meta，非PD | → Nienstedt 2019 PD误吸预测 | 直接PD人群，预测因素 |
| [14] Miranda 2024 | 小鼠睡眠实验 | → Chua 2024 PD吸入性肺炎Meta | 系统综述最高证据级别 |

Also build a "missing data" table for claims that need new citations:

| Data in proposal | Recommended citation | DOI | Reason |
|-----------------|---------------------|-----|--------|
| AUC 0.950 PD误吸模型 | Nienstedt 2019 | 10.1111/nmo.13524 | PD特异性的预测因素研究 |

### Phase 5: Innovation Enhancement

After replacing weak literature, check if the proposal's innovation claims are substantiated:
- If the proposal claims novelty in "三维框架" but the literature search finds 5 existing multi-factor models → the innovation needs sharpening
- If literature search finds NO existing model combining all 3 dimensions → the innovation claim is validated
- If there's a specific gap (e.g., "营养调节效应" never studied in PD aspiration) → cite that gap explicitly

### Phase 6: NotebookLM Integration

To preserve the analysis:

1. Create a NotebookLM project: `notebooklm create "项目名+评估"`
2. Upload original proposal + evaluation report + literature supplement
3. Rename sources with numbered prefixes: `01_原始标书`, `02_评估报告`, `03_文献增强包`
4. (Optional) `notebooklm ask` to verify the sources are indexed correctly

## Concrete Example: PD误吸风险预测项目 (2026-05-13)

| Metric | Before | After |
|--------|--------|-------|
| Total references | 22 | 22 (6 replaced) |
| Direct references | ~12 (55%) | ~18 (82%) |
| Tangential/Weak | ~8 (36%) | ~2 (9%) |
| Data points without citation | 7 | 0 (recommended) |
| Innovation points | scattered across 5000 chars | reorganized into 3 core points |

## Pitfalls

- **PubMed search needs explicit MeSH**: A plain text search "Parkinson's disease dysphagia" returns many false positives (Alzheimer's, stroke). Use MeSH headings like `"Parkinson disease"[MeSH]` for precision.
- **S2 API rate limits**: 1 req/sec max with the user's key. Add `time.sleep(1.2)` between calls or rotate keys.
- **Chinese language PubMed limitations**: Chinese journals are poorly indexed in PubMed. Use CNKI/万方 for Chinese literature if available, or search OpenAlex with `institutions.country_code:CN`.
- **Cochrane reviews are gold**: If a Cochrane review exists for the intervention, cite it preferentially — it's the highest evidence level.
- **Don't cite without reading**: If a paper's abstract says exactly what the proposal needs, note "abstract confirms" but flag for full-text reading before final submission.

## References

- PubMed E-utilities: https://eutils.ncbi.nlm.nih.gov/
- Semantic Scholar API: https://api.semanticscholar.org/
- OpenAlex: https://api.openalex.org/ (free, no key, good for Chinese institution filtering)
