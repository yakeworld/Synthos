---
name: systematic-review
description: "Systematic review and meta-analysis workflow assistant. Covers PRISMA flow, search strategy design, study selection, quality assessment, data extraction, and synthesis support."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Systematic-Review, Meta-Analysis, PRISMA, Evidence-Synthesis, Literature-Review, Quality-Assessment]
    related_skills: [pubmed, openalex, arxiv, biorxiv, ocr-and-documents, llm-wiki, research-paper-writing]
---

# Systematic Review — PRISMA Workflow Assistant

Systematic reviews follow a rigorous, reproducible methodology. The PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) framework is the gold standard.

## Quick Reference

| Phase | Action | Command |
|-------|--------|---------|
| Search Strategy | Design PICO search | Define PICO, construct query |
| Search Execution | Run searches | PubMed, OpenAlex, Cochrane |
| Screening | Deduplicate + Screen | Remove duplicates, title/abstract, full text |
| Quality Assessment | Risk of bias | ROB-2, ROBINS-I, Newcastle-Ottawa |
| Data Extraction | Extract data | Standardized extraction form |
| Synthesis | Meta-analysis | Statistical synthesis or narrative |

## PRISMA 2020 Checklist

The PRISMA 2020 statement has 27 items across 4 sections:

### Section 1: Title
1. Identify as systematic review in title

### Section 2: Abstract
2. Structured summary (background, methods, results, discussion, funding)

### Section 3: Introduction
3. Background and rationale
4. Objectives (include PICO)

### Section 4: Methods
5. Eligibility criteria (study characteristics, report characteristics)
6. Information sources (dates, databases, registries, contact)
7. Search strategy (full strategy for at least one database)
8. Selection process (screening and inclusion)
9. Data collection process (how many, process)
10. Data items (study level, outcome level)
11. Risk of bias in individual studies (method, number of reviewers)
12. Effect measures (effect measures for each outcome)
13. Synthesis methods (methods of synthesis, meta-analysis, risk of bias impact)
14. Reporting bias assessment (methods)
15. Certainty assessment (methods)
16. Analysis methods (grouping, subgroup, sensitivity)

### Section 5: Results
17. Selection (flow diagram, numbers at each stage)
18. Study characteristics (table of study characteristics)
19. Risk of bias in studies (results at study level)
20. Results of individual studies (forest plots for each outcome)
21. Results of meta-analyses (forest plots)
22. Reporting bias (assessment results)
23. Certainty of evidence (assessment results)
24. Discussion — key results
25. Discussion — limitations (of evidence, processes)
26. Discussion — interpretation

### Section 6: Other Information
27. Funding

## PRISMA Flow Diagram Process

```
Records identified from:     Records screened
Databases                    n = N reports
n = N reports                |
                              | Excluded:
                              n = N reports
                              |
                              Records screened (titles/abstracts)
                              n = N reports
                              |
                              | Excluded:
                              n = N reports
                              |
                              Reports sought for retrieval
                              n = N reports
                              |
                              | Reports not retrieved
                              n = N reports
                              |
                              Reports assessed for eligibility
                              n = N reports
                              |
                              | Excluded (with reasons):
                              n = N reports
                              |
                              Studies included in review
                              n = N studies
                              |
                              Studies included in meta-analysis
                              n = N studies (if applicable)
```

## PICO Framework

Before designing any search, define your PICO:

- **P**opulation: Who is the study about? (age, condition, setting)
- **I**ntervention: What exposure/intervention/treatment?
- **C**omparison: What is the comparison group?
- **O**utcome: What are the measured outcomes?

Example:
```
P: Adults with vestibular disorders (age 18+)
I: Virtual reality-based rehabilitation therapy
C: Conventional vestibular rehabilitation therapy
O: Balance function, fall frequency, quality of life
```

## Search Strategy Construction

### Step 1: Build Concept Blocks

For each PICO element, list all relevant terms:

```
Population:
  - "vestibular diseases"[MeSH]
  - OR "balance disorders"[All Fields]
  - OR "vertigo"[All Fields]
  - OR "vestibular disorder"[All Fields]

Intervention:
  - "virtual reality"[MeSH]
  - OR "virtual reality therapy"[All Fields]
  - OR "VR rehabilitation"[All Fields]
  - OR "immersive therapy"[All Fields]

Comparison:
  - "conventional rehabilitation"[All Fields]
  - OR "standard vestibular therapy"[All Fields]
  - OR "non-VR therapy"[All Fields]

Outcome:
  - "postural balance"[MeSH]
  - OR "balance function"[All Fields]
  - OR "fall frequency"[All Fields]
  - OR "quality of life"[MeSH]
```

### Step 2: Combine with AND

```
(Concept 1) AND (Concept 2) AND (Concept 3) AND (Concept 4)
```

### Step 3: Add Filters

```
[AND study design filter] — e.g., randomized controlled trial[pt], clinical trial[pt]
[AND date filter] — e.g., last 10 years
[AND language filter] — e.g., english[Language]
```

### Step 4: Test and Refine

```bash
# Test the search
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+FULL+QUERY&retmax=100&retmode=json"

# Count results
# Aim for 100-5000 papers (too many = refine, too few = expand)
```

## Database-Specific Searches

### PubMed

```bash
# Full systematic review search in PubMed
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Vestibular+Diseases%22%5BMeSH%5D+OR+%22balance+disorders%22%5BAll+Fields%5D+OR+%22vertigo%22%5BAll+Fields%5D+AND+%22virtual+reality%22%5BMeSH%5D+OR+%22virtual+reality+therapy%22%5BAll+Fields%5D+OR+%22VR+rehabilitation%22%5BAll+Fields%5D+AND+%22postural+balance%22%5BMeSH%5D+OR+%22balance+function%22%5BAll+Fields%5D+AND+%22randomized+controlled+trial%22%5BPublication+Type%5D+OR+%22clinical+trial%22%5BPublication+Type%5D&retmax=500&retmode=json"
```

### OpenAlex

```bash
# OpenAlex search (less structured but broader)
curl -s "https://api.openalex.org/works?search=vestibular+disorder+virtual+reality+rehabilitation+balance+function&filter=from_publication_date:2014-01-01,to_publication_date:2026-12-31&sort=relevance:desc&per_page=100&select=title,abstract_inverted_index,cited_by_count,publication_year,concepts,open_access"
```

### Cochrane Library

```bash
# Cochrane Library search
curl -s "https://cochranelibrary.com/cdsr/search?query=vestibular+disorder+virtual+reality&type=topic"
```

### Cochrane Central Register (CENTRAL)

```bash
# CENTRAL is Cochrane's controlled vocabulary database
# Use PubMed's Clinical Queries with Cochrane filter
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorder+virtual+reality+AND+%22cochrane+database+of+systematic+reviews%22%5BSource%5D&retmax=50&retmode=json"
```

### Embase (via PubMed Ovid interface)

```bash
# Note: Embase requires subscription. Use PubMed as a proxy for Embase-like content.
# Embase has better pharmacology and European coverage.
```

## Deduplication

After collecting papers from multiple sources, deduplicate:

```bash
# Deduplicate by DOI, PMID, or title similarity
# Use the llm-wiki or a custom script to identify duplicates

# Common deduplication method:
# 1. Collect all PMIDs/DOIs from all databases
# 2. Remove exact duplicates
# 3. For remaining, compare titles with fuzzy matching
# 4. Keep the version with the best metadata (PMID > DOI > title-only)
```

## Quality Assessment Tools

### Randomized Controlled Trials (RCTs)

**Cochrane Risk of Bias Tool (ROB-2)**

| Domain | Question |
|--------|----------|
| Randomization | Was the randomization process appropriate? |
| Deviations | Are there deviations from intended interventions? |
| Missing data | Are missing outcome data adequately addressed? |
| Outcome measurement | Was the outcome assessment blinded? |
| Selective reporting | Are all expected outcomes reported? |

### Non-Randomized Studies

**ROBINS-I** (Risk Of Bias In Non-randomized Studies - of Interventions)

| Domain | Question |
|--------|----------|
| Confounding | Were confounding factors addressed? |
| Selection | Was selection of participants biased? |
| Classification of intervention | Was intervention classification adequate? |
| Deviations | Are there deviations from intended interventions? |
| Missing data | Are missing data adequately addressed? |
| Measurement | Was outcome assessment blinded? |
| Selective reporting | Selective reporting of outcomes? |

### Observational Studies

**Newcastle-Ottawa Scale (NOS)**

| Category | Criteria |
|----------|----------|
| Selection (max 4) | Representativeness, selection of non-exposed, ascertainment of exposure, demonstration that outcome of interest was not present at start |
| Comparability (max 2) | Control for confounding factors |
| Outcome (max 3) | Assessment method, follow-up length, adequacy of follow-up |

### All Study Types

**Cochrane Critical Appraisal Tools:**

| Study Type | Tool |
|------------|------|
| RCT | Cochrane ROB-2 |
| Non-randomized | ROBINS-I |
| Diagnostic accuracy | QUADAS-2 |
| Qualitative | CASP |
| Prevalence | JBI |
| Economic evaluation | CHEERS |

## Data Extraction Form

Standardized data extraction template:

```
Study ID:
  - First author
  - Year
  - Country
  - Journal

Study Design:
  - Type (RCT, cohort, case-control, cross-sectional)
  - Blinding (yes/no, who was blinded)
  - Randomization method

Population:
  - Sample size
  - Inclusion criteria
  - Exclusion criteria
  - Demographics (age, sex, ethnicity)
  - Diagnosis criteria
  - Disease severity/stage

Intervention:
  - Description
  - Dose/duration/frequency
  - Comparator
  - Setting (hospital, clinic, home)

Outcomes:
  - Primary outcome (measure, instrument, timepoint)
  - Secondary outcomes (measure, instrument, timepoint)
  - Effect size (mean, SD, OR, RR, HR)
  - Statistical significance

Quality Indicators:
  - Risk of bias assessment
  - Follow-up rate
  - Intention-to-treat analysis
  - Protocol registration
```

## Methodological Flaw Analysis for Inflated Metrics

When reviewing papers that claim exceptionally high performance on well-studied benchmarks (e.g., medical ML datasets), standard PRISMA quality tools (ROB-2, NOS) are insufficient. A specialized **methodological flaw analysis** is needed:

### Technique: Metric Claim Extraction + Pipeline Audit

For each paper in the corpus:

1. **Extract claimed metrics** from abstract using regex:
   ```
   accuracy/acc\s*(?:of|:|=|is|was|achieved|reached|obtained)?\s*(\d{2,3}\.?\d*)\s*%?
   F1[- ]?(?:score|measure)?\s*(?:of|:|=|is|was)\s*(\d?\.\d+)
   AUC\s*(?:of|:|=|is|was)\s*(\d?\.\d+)
   ```

2. **Classify preprocessing pipeline** by scanning abstract for keywords:
   | Flaw | Keyword Indicator | Severity |
   |------|------------------|----------|
   | Global SMOTE before split | "SMOTE" + NOT "within-fold" / "training fold" | 🔴 High |
   | No cross-validation | NOT "cross-validation" / "k-fold" / "10-fold" | 🔴 High |
   | No train-test split | NOT "train" + "test" / "validation" | 🟡 Medium |
   | No imbalance handling | NOT "SMOTE" / "ADASYN" / "oversampling" / "imbalance" | 🟡 Medium |
   | No zero-value correction | NOT "zero" / "missing" / "imputation" / "biologically implausible" | 🟡 Medium |

3. **Calculate inflation evidence** — compare claimed metrics against the upper bound achievable under strict methodological protocols (e.g., F1 ~0.75 for PIDD with 10-fold CV + within-fold SMOTE).

### When to Use

Use this methodology when:
- The review targets ML/DL papers on small-to-medium clinical benchmarks (n < 5,000, features < 50)
- The research question involves reproducibility, credibility, or data leakage
- The corpus includes papers claiming accuracy > 90% on datasets with known quality issues (missing values, imbalance)

### Citation Analysis for Data Leakage Claims

For papers flagged as potentially inflated:
- Cross-reference with retraction databases (e.g., PLOS ONE Expressions of Concern for global SMOTE cases like Talari et al. 2024)
- Check if the authors' later papers acknowledge or address the flaw
- Document whether the flaw is explicitly mentioned, obfuscated, or absent from the methods section

### Extension: Full-Text Methodology Verification Protocol

Abstract-level detection (above) is a useful triage step. For papers flagged as high-inflation, **full-text verification** is needed — downloading the PDF, locating the methods section, and identifying the exact paragraph-level evidence of methodological violations.

#### Step 1: Download target PDFs

For each flagged paper, obtain the PDF using priority order:

| Priority | Source | Method |
|:--------:|:-------|:-------|
| 1 | Open Access (Semantic Scholar OA field) | `curl -sL "{oa_url}" -o {key}.pdf` |
| 2 | arXiv | `curl -sL "https://arxiv.org/pdf/{arxiv_id}" -o {key}.pdf` |
| 3 | Sci-Hub via curl_cffi | Python `curl_cffi` + Sci-Hub domain rotation + Referer header |
| 4 | paper-manager download_one.py | `python3 /path/to/download_one.py {doi} {path}` |
| 5 | Blocked/Marked | Write to missing list with reason |

**Verification**: every downloaded file must pass `head -c 5 {file}.pdf` → `%PDF-`.

#### Step 2: Extract full text

```bash
pdftotext {paper}.pdf - > /tmp/{key}_text.txt
# Or use markitdown for better formatting
uvx markitdown {paper}.pdf > /tmp/{key}_md.md
```

#### Step 3: Locate the methods section

Search for key methodological phrases that reveal pipeline order:

```bash
# Search for preprocessing before splitting (LEAKAGE signal)
grep -n -i "up.sampl\|SMOTE\|oversampl\|imput\|scale\|balanc" /tmp/{key}_text.txt | head -20

# Search for train/test split
grep -n -i "train.*test\|split\|80.*20\|70.*30\|CV\|cross.val\|fold" /tmp/{key}_text.txt | head -20

# Search for cross-validation
grep -n -i "fold\|cross.val\|CV\|k.fold\|stratified" /tmp/{key}_text.txt | head -10
```

#### Step 4: Read the precise preprocessing → split sequence

The critical question is **order**: does preprocessing happen *before* or *after* train-test split?

Read the 5-10 lines surrounding each match from Step 3. Determine which sequence applies:

| Sequence | Verdict | Example quote |
|:---------|:--------|:--------------|
| "Preprocessing technique was applied. After that, the data was split into train/test." | 🔴 **LEAKAGE** — synthetic/processed samples leak into test set | `"the up-sampling technique has been used to balance both datasets. After that, 80% of the datasets are used as training data and 20% as testing data"` |
| "First, train/test split. Then, preprocessing was applied only to the training fold." | ✅ Clean | `"within each fold of cross-validation, we apply SMOTE exclusively on the training subset"` |
| "Cross-validation was used." + "SMOTE was applied." (no order specified) | 🟡 Ambiguous — assume leakage unless clarified | |

#### Step 5: Extract exact performance claims

From the abstract and results section, extract the reported performance numbers:

```bash
grep -E "(accuracy|AUC|F1|precision|recall|sensitivity|specificity)" /tmp/{key}_text.txt | grep -E "[0-9]+\.[0-9]+" | head -10
```

For each number, document:
- **Metric name** (Accuracy, AUC, F1, Recall)
- **Claimed value** (e.g., 0.99)
- **Model** (e.g., Extra Trees, XGBoost+SMOTEENN)
- **Method used** (up-sampling, SMOTE, SMOTEENN, etc.)

#### Step 6: Map claim to known leakage baseline

Compare the claimed value against the proper-isolation baseline for the same dataset:

| Dataset | Proper-isolation F1 | Leaky F1 | Source |
|:--------|:-------------------:|:--------:|:-------|
| PIDD (768, 34.9% prevalence) | 0.664 (Helix LDA) | 0.738 (Leaky) | Pima CRISP-DM |
| CDC BRFSS (50K, 13.8%) | 0.451 (Helix AdaBoost) | 0.768 (Leaky) | Pima CRISP-DM |
| Early Diabetes (520, 61.5%) | 0.930 (Helix LR) | 0.915 (Leaky) | Pima CRISP-DM |

Mapping rule:
- **Claim ≈ Leaky baseline** → inflation confirmed
- **Claim ≈ Proper-isolation baseline** → likely clean methodology
- **Claim > Leaky baseline** → investigate for additional data leakage or overfitting

#### Step 7: Produce evidence table

For each verified paper, produce a row in the comparison table:

| Reference | Claimed Metric | Key Leakage Evidence | Verdict |
|:----------|:--------------|:--------------------|:--------|
| Shams2025 | AUC=0.99 | P.3: "up-sampling → After that, 80/20 split" | 🔴 Leakage confirmed |
| Li2024 | F1=0.95 | Baseline F1=0.27 → +355% with SMOTEENN | 🔴 Leakage inferred |

#### Step 8: Use as convergent evidence in Discussion

When writing a paper that includes cross-dataset validation (Helix vs. Leaky), cite the full-text literature audit as **independent convergent evidence**:

- "Our Leaky protocol produced F1=0.768 on CDC BRFSS. The published literature reports AUC=0.99 under identical leaky conditions (Shams2025), confirming our controlled experimental finding."
- "The only BRFSS study using proper stratified CV (Tennessee2025) reports F1=0.37, consistent with our Helix-isolated AdaBoost result (F1=0.451)."

This transforms the paper's claim from "we measured inflation in our lab" to "we measured it, and the published literature independently confirms the pattern."

### Reporting

Include a summary table in the review:
| Reference | Claimed Acc | Pipeline Flaw(s) | Inflation Likelihood |
|-----------|------------|------------------|---------------------|
| Author Year | 98.7% | Global SMOTE; no CV | 🔴 Very High |
| Author Year | 89% | No zero-value correction | 🟡 Moderate |

### Pitfalls (Flaw Analysis)

- **PDF download is not the same as content verification**: many downloaded files are HTML disguised as PDFs. Always check `%PDF-` header.
- **Abstract-only inference is risky**: some papers mention "cross-validation" in the abstract but the methods section reveals the CV is applied incorrectly (e.g., global SMOTE before CV). Full-text verification is essential.
- **False positives in citation count**: Papers claiming "10-fold CV" may still have leakage if feature selection or preprocessing isn't fold-isolated. Don't accept "CV" as proof of cleanliness.
- **Baseline unsampled performance**: When a paper reports both unsampled and SMOTE-augmented performance, the gap between them is a strong indicator of leakage magnitude. A gap >100% F1 inflation from sampling alone is diagnostic of data leakage.
- **Not every inflated claim is fraud**: Some authors simply follow community norms in their field that haven't yet recognized the data leakage problem. Frame findings as methodological critique, not personal accusation.

### Related Skills & References

- `academic-paper-completion` → `references/inflated-metrics-detection.md` — full detection methodology
- `academic-paper-completion` → `references/pidd-inflated-metrics-table.md` — concrete worked example with 10 PIDD papers
- `systematic-review` → `references/brfss-literature-methodology-audit-2026-06-03.md` — full worked example with 6 BRFSS papers

## Narrative Synthesis Process

When meta-analysis is not possible, use structured narrative synthesis:

```
1. Describe and map the evidence
   - What types of studies?
   - What interventions?
   - What populations?
   - What outcomes?

2. Explore relationships
   - Does effectiveness vary by population?
   - Does effectiveness vary by intervention characteristics?
   - Does effectiveness vary by study quality?
   - Are there patterns across studies?

3. Assess certainty of evidence
   - GRADE approach (High/Moderate/Low/Very Low)
   - Consider risk of bias, inconsistency, indirectness, imprecision, publication bias

4. Summarize findings
   - What do we know?
   - What don't we know?
   - What are the implications?
   - What research is needed?
```

## GRADE Approach

Assess certainty of evidence for each outcome:

| Factor | Downgrade By | Upgradable By |
|--------|-------------|---------------|
| Risk of bias | -1/-2 | |
| Inconsistency | -1/-2 | |
| Indirectness | -1/-2 | |
| Imprecision | -1/-2 | |
| Publication bias | -1/-2 | |
| Large effect | | +1/+2 |
| Dose-response | | +1 |
| Plausible confounding | | +1 |

Certainty levels:
- **High**: Very confident in effect estimate
- **Moderate**: Moderately confident
- **Low**: Limited confidence
- **Very Low**: Very uncertain

## Reporting Bias Assessment

```bash
# Check for publication bias
# Funnel plot (visual)
# Egger's test (statistical)
# Trim and fill method
# P-curve analysis

# Also check:
# - Clinical trial registries (ClinicalTrials.gov)
# - Grey literature (thesis, conference proceedings)
# - Non-English publications
# - Negative results databases
```

## Complete Workflow Example

```bash
# STEP 1: Define PICO
P: Adults with vestibular disorders
I: Virtual reality-based rehabilitation
C: Conventional therapy
O: Balance, fall frequency, QoL

# STEP 2: Build search strategy
# PubMed: "vestibular diseases"[MeSH] OR "balance disorders"[All Fields] AND "virtual reality"[MeSH] OR "VR rehabilitation"[All Fields] AND "balance"[MeSH]

# STEP 3: Search all databases
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+QUERY&retmax=500&retmode=json"
curl -s "https://api.openalex.org/works?search=YOUR+QUERY&per_page=500"

# STEP 4: Deduplicate
# Remove duplicates by DOI/PMID

# STEP 5: Screen titles/abstracts
# Use inclusion/exclusion criteria

# STEP 6: Full-text screening
# Read full text of remaining papers

# STEP 7: Quality assessment
# Apply ROB-2, NOS, or appropriate tool

# STEP 8: Data extraction
# Extract data using standardized form

# STEP 9: Synthesis
# Narrative or meta-analysis

# STEP 10: Write up
# Follow PRISMA 2020 checklist
```

## Pitfalls

- **Search string too narrow**: Misses relevant papers. Always include synonyms and variations.
- **Search string too broad**: Thousands of results. Add filters (study design, date range, population).
- **Only PubMed**: Misses Embase, Cochrane, CINAHL, PsycINFO, etc. Use multiple databases.
- **Only English**: Misses non-English papers. Include language filters or search in other languages.
- **No protocol registration**: Register with PROSPERO before starting the review.
- **No PRISMA flow diagram**: Required for reporting.
- **No risk of bias assessment**: Essential for evidence grading.
- **No GRADE assessment**: Essential for interpreting results.
- **Not checking registries**: Misses unpublished studies.
- **Single reviewer**: Always use at least 2 reviewers for screening and data extraction.
- **Not handling heterogeneity**: Check for clinical and methodological heterogeneity before meta-analysis.
- **Publication bias**: Always assess for bias toward positive results.

## Related Tools and Registries

- **PROSPERO**: International prospective register of systematic reviews
- **Cochrane Library**: Best source for Cochrane reviews
- **ClinicalTrials.gov**: Trial registry for publication bias assessment
- **OpenSIGLE**: Grey literature
- **GreyNet**: Grey literature network
- **ASSIA**: Social sciences and health
- **CINAHL**: Cumulative Index to Nursing and Allied Health Literature
- **PsycINFO**: Psychology and behavioral sciences
- **Embase**: Biomedical and pharmacological (subscription)

## Related Skills

- `pubmed` — PubMed search
- `openalex` — OpenAlex search (broader coverage)
- `arxiv` — arXiv search
- `biorxiv` — bioRxiv/medRxiv search
- `ocr-and-documents` — PDF extraction for screening
- `llm-wiki` — Knowledge base for review documentation
- `research-paper-writing` — Paper writing (for the review manuscript)
