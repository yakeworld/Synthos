---
name: pubmed
description: "Deep PubMed/MEDLINE/MEDLINE-in-process/NLM Catalog search, retrieval, and analysis via NCBI E-utilities. Covers query construction, MeSH terms, filtering, batch retrieval, author search, and clinical query refinement."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, PubMed, Medical, Literature-Search, E-utilities, MeSH, NCBI, Biomedical, Systematic-Review]
    related_skills: [pubmed, openalex, biorxiv, literature-monitor, systematic-review, arxiv, ocr-and-documents, llm-wiki, notebooklm-cli, research-paper-writing]
---

# PubMed — Deep Biomedical Literature Search

PubMed/MEDLINE is the **primary biomedical literature database** maintained by the US National Library of Medicine (NLM). It contains 39M+ records covering life sciences, biomedicine, and health.

This skill covers **everything** from simple keyword search to systematic review workflows, including MeSH term expansion, clinical queries, batch retrieval, author tracking, and continuous monitoring.

## Quick Reference

| Action | Command |
|--------|---------|
| Search | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=QUERY&retmax=10&retmode=json"` |
| Get details (XML) | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=ID1,ID2&retmode=xml"` |
| Get details (JSON) | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=ID1,ID2&retmode=json"` |
| Get details (abstract) | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=ID1,ID2&rettype=abstract&retmode=text"` |
| Get citations OF a paper | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=ID1,ID2&retmode=json"` |
| Get related articles | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=ID[uid]+AND+last5years[date]&retmax=10&retmode=json"` |
| Get PMC full text | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC_ID&retmode=xml"` |
| Get PMC article metadata | `curl -s "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC_ID"` |
| Get MeSH terms | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=mesh&term=TERM&retmax=10&retmode=json"` |

## Search Query Construction

### Basic Query Syntax

| Prefix | Search | Example |
|--------|--------|---------|
| (none) | All fields | `vestibular disorders` |
| `[All Fields]` or `[TIAB]` | Title + Abstract + MeSH | `vestibular[All Fields] AND eye[All Fields]` |
| `[TI]` | Title only | `vestibular[Title]` |
| `[AB]` | Abstract only | `vestibular[Abstract]` |
| `[MeSH Terms]` | MeSH heading + subheadings | `"vestibular diseases"[MeSH Terms]` |
| `[MeSH]` | MeSH heading only | `"vestibular diseases"[MeSH]` |
| `[TI]` | Title | `"vestibular rehabilitation"[Title]` |
| `[TA]` | Journal abbreviation | `"N Engl J Med"[TA]` |
| `[PPCY]` | Publication country | `"United States"[PPCY]` |
| `[SO]` | Journal name | `"New England Journal of Medicine"[SO]` |
| `[AD]` | Author affiliation | `"Harvard"[Affiliation]` |
| `[AU]` | Author name | `"Smith J"[Author]` or `"Smith J"[1AU]` (first author) |
| `[1AU]` | First author only | `"Wang Y"[1AU]` |
| `[ID]` | PMID | `"12345678"[ID]` |
| `[DOI]` | DOI | `"10.1016/j.neuroscience.2024.01.001"[DOI]` |
| `[PMID]` | PMID synonym | `"12345678"[PMID]` |

### Search Fields Reference

```
[All Fields]  - All searchable fields (default)
[TI]          - Title
[AB]          - Abstract
[TIAB]        - Title + Abstract
[TIABFA]      - Title, Abstract, Financial Support, Associated data
[JP]          - Journal Issue
[JT]          - Journal Title (full name)
[TA]          - Journal ISO abbreviation
[SO]          - Source (journal name and year)
[AD]          - Author's affiliation
[AU]          - Author name (last name followed by initials)
[1AU]         - First author
[LR]          - Language of publication
[DP]          - Date of Publication
[MD]          - Medium of Publication
[PT]          - Publication Type
[PTYPE]       - Publication Type (alternative)
[ISBN]        - ISBN of cited book
[ISBN/OT]     - Old ISBN or ISBN
[ISBN/NM]     - Newly-assigned ISBN
[CST]         - Copyright Status
[DA]          - Date Completed
[EDAT]        - Electronic Date of Publication
[MH]          - MeSH terms (same as [MeSH Terms])
[MAJR]        - Major Topic MeSH only
[MH]          - MeSH heading
[OUDT]        - Online Date
[MHHT]        - Heading History
[OT]          - Other Terms (MeSH non-descriptors and synonyms)
[PT]          - Publication Type
[PSY]         - Publication Type Subheading
[PTYPE]       - Publication Type (alternative)
[RGD]         - Record Generation Date
[SAD]         - Supplemental Concept Number
[SN]          - ISSN/ISBN
[LID]         - DOI or other identifier from the end of the record
[PMID]        - PubMed ID
[DOI]         - Digital Object Identifier
[PMCA]        - PubMed Central Accession Number
[PMC]         - PubMed Central ID
[PMCID]       - PubMed Central ID
[PMCURN]      - PubMed Central Reference Number
[PMCRN]       - PubMed Central Reference Number
[LID]         - Other identifier (end of record)
[MED]         - MEDLINE Unique ID Number
[PSPLC]       - Publisher Location
[PL]          - Place of Publication
[GR]          - Grant Number
[GRS]         - Grantor
[CN]          - Country
[CC]          - Copyright Information
[OC]          - Other Concepts
[OCCT]        - Other Concept Term
[DC]          - Date Completed
[EDAT]        - Electronic Date of Publication
[LR]          - Language
[MEDL]        - MEDLINE Status
[MM]          - Major/Minor Topic
[MAJR]        - Major Topic Only
[MH]          - MeSH Heading
[MHHT]        - MeSH Heading History
[MSH]         - MeSH Unique ID
[OUDT]        - Online Date
[PT]          - Publication Type
[PSY]         - Publication Type Subheading
[PTYPE]       - Publication Type
[SGD]         - Supplemental Concept Number
[RGD]         - Record Generation Date
```

### Boolean Operators

```
# AND (default for adjacent terms, but explicit is safer)
vestibular AND disorders

# OR
vestibular OR balance

# NOT (use with caution — may exclude relevant papers)
vestibular NOT otitis

# Exact phrase
"vestibular rehabilitation therapy"

# Wildcards
vestibul*           # matches vestibular, vestibule, vestibules, etc.
"eye track?"        # matches eye tracking, eye tracked
"child*[1-5]"       # matches child1, child2, ..., child5

# Proximity
saccade NEAR3 visual     # within 3 words
saccade ADJ visual       # adjacent (any order)
saccule ADJ1 ear         # immediately adjacent
```

### Advanced Query Techniques

```bash
# Expand to synonyms automatically (combines multiple search terms with OR)
"vestibular disorders"[MeSH Terms] OR "balance disorders"[MeSH Terms] OR "vertigo"[MeSH Terms] OR "vestibular"[All Fields] OR "balance"[All Fields] OR "vertigo"[All Fields]

# Search with date filter (last 5 years)
"vestibular disorders"[MeSH Terms] AND "2021/01/01"[Date - Publication] : "2026/12/31"[Date - Publication]

# Search with publication type filter (reviews only)
"vestibular disorders"[MeSH Terms] AND "review"[Publication Type]

# Search clinical articles (includes RCTs, trials, diagnostic studies)
"vestibular disorders"[MeSH Terms] AND "clinical query"[filter]

# Search with language filter
"vestibular disorders"[MeSH Terms] AND english[Language]

# Combine filters
"vestibular disorders"[MeSH Terms] AND "review"[Publication Type] AND "2023"[Date - Publication]
```

## Publication Type Filters

| Filter | Description |
|--------|-------------|
| `review[PT]` | All review articles |
| `systematic review[PT]` | Systematic reviews |
| `meta-analysis[PT]` | Meta-analyses |
| `randomized controlled trial[PT]` | RCTs |
| `clinical trial[PT]` | Clinical trials |
| `guideline[PT]` | Clinical practice guidelines |
| `case reports[PT]` | Case reports |
| `observational study[PT]` | Observational studies |
| `cohort studies[PT]` | Cohort studies |
| `case-control studies[PT]` | Case-control studies |
| `diagnostic accuracy study[PT]` | Diagnostic studies |
| `predictive value studies[PT]` | Predictive studies |
| `etiology[PT]` | Etiology studies |
| `journal article[PT]` | Regular journal articles |
| `letter[PT]` | Letters to the editor |
| `editorial[PT]` | Editorials |
| `comment[PT]` | Comments |
| `news[PT]` | News articles |

## Clinical Query Filters (Case-Sensitive!)

These are **built-in optimized queries** by the NLM for finding high-yield clinical literature:

```bash
# Therapeutic studies (sensitive — casts a wide net)
"query"[filter]

# Therapeutic studies (specific — more precise, fewer results)
"therapy"[filter]

# Diagnosis studies
"diagnosis"[filter]

# Prognosis studies
"prognosis"[filter]

# Etiology studies
"etiology"[filter]

# Predictive value studies
"predictive value"[filter]

# Case study
"case studies"[filter]

# Clinical prediction rules
"clinical prediction rule"[filter]
```

Usage: `"your topic"[filter]` — note that `[filter]` is case-sensitive!

## MeSH (Medical Subject Headings)

MeSH is the NLM's controlled vocabulary thesaurus. Using MeSH terms improves precision dramatically.

### Find MeSH Terms for a Concept

```bash
# Search for MeSH terms
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=mesh&term=vestibular+disorders&retmax=5&retmode=json" | python3 -m json.tool
```

### Use MeSH in Searches

```
# Exact MeSH heading
"vestibular diseases"[MeSH]

# MeSH heading + subheading
"vestibular diseases"[MeSH] : "therapy"[MH]
"vestibular diseases"[MeSH] : "diagnosis"[MH]
"vestibular diseases"[MeSH] : "physiopathology"[MH]

# Major topic only (the paper focuses on this)
"vestibular diseases"[MAJR]

# MeSH + free text (combination search — most comprehensive)
"vestibular diseases"[MeSH] OR "vestibular disorder"[All Fields] OR "balance disorder"[All Fields] OR "vertigo"[All Fields]
```

### Common MeSH Terms for Ophthalmology/Vestibular Research

```
"Vestibular Diseases"[MeSH]
"Vestibulo-Ocular Reflex"[MeSH]
"Motion Sickness"[MeSH]
"Oculomotor Disorders"[MeSH]
"Eye Movements"[MeSH]
"Ophthalmoplegias"[MeSH]
"Binocular Double Vision"[MeSH]
"Vestibular Evoked Myogenic Potentials"[MeSH]
"Otolaryngologic Diseases"[MeSH]
"Balance Disorders"[MeSH]
"Neurologic Examination"[MeSH]
"Reaction Time"[MeSH]
"Proprioception"[MeSH]
"Central Nervous System"[MeSH]
"Brain"[MeSH]
"Cerebellum"[MeSH]
"Vestibular Nuclei"[MeSH]
"Oculomotor Muscles"[MeSH]
"Visual Perception"[MeSH]
"Attention"[MeSH]
"Attention Deficit Disorder with Hyperactivity"[MeSH]
"Cognitive Dysfunction"[MeSH]
```

## Search Examples by Research Area

### 1. Vestibular Research

```bash
# Comprehensive vestibular search
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Vestibular+Diseases%22%5BMeSH%5D+OR+%22balance+disorders%22%5BAll+Fields%5D+OR+%22vestibular+disorder%22%5BAll+Fields%5D&retmax=20&retmode=json"

# VOR (vestibulo-ocular reflex)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Vestibulo-Ocular+Reflex%22%5BMeSH%5D&retmax=20&retmode=json"

# Motion sickness
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Motion+Sickness%22%5BMeSH%5D&retmax=20&retmode=json"
```

### 2. ADHD Research

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Attention+Deficit+Disorder+with+Hyperactivity%22%5BMeSH%5D&retmax=20&retmode=json"

# ADHD + eye tracking
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Attention+Deficit+Disorder+with+Hyperactivity%22%5BMeSH%5D+AND+%22Eye+Movements%22%5BMeSH%5D&retmax=20&retmode=json"
```

### 3. Systematic Reviews

```bash
# Search for systematic reviews on a topic
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+systematic+review%5Bpt%5D&retmax=20&sort=date&retmode=json"
```

## Batch Retrieval

### Get Multiple Papers at Once

```bash
# Up to 200 PMIDs per request (XML mode)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31066247,40412714,36291303,34667856,38429713&retmode=xml"

# Up to 200 PMIDs per request (JSON mode)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31066247,40412714,36291303,34667856,38429713&retmode=json"

# Get abstracts only (faster)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31066247,40412714,36291303&rettype=abstract&retmode=text"
```

### Parse PubMed XML Response

```python
import xml.etree.ElementTree as ET

xml = """..."""  # Raw XML from efetch
root = ET.fromstring(xml)

for article in root.findall('.//PubmedArticle'):
    citation = article.find('.//MedlineCitation')
    pmid = citation.find('PMID').text
    article_data = citation.find('Article')
    title = article_data.find('ArticleTitle').text
    journal = article_data.find('Journal/Title').text
    journal_iso = article_data.find('Journal/ISOAbbreviation').text
    pub_date = article_data.find('Journal/JournalIssue/PubDate')
    year = pub_date.find('Year').text
    month = pub_date.find('Month').text
    
    # Abstract
    abstract_elem = article_data.find('Abstract')
    if abstract_elem is not None:
        abstract_parts = [t.text for t in abstract_elem.findall('AbstractText')]
        abstract = ' '.join(abstract_parts)
    else:
        abstract = "No abstract"
    
    # Authors
    authors = []
    for author in citation.findall('.//Author'):
        last = author.find('LastName').text
        first = author.find('ForeName').text
        authors.append(f"{last} {first}")
    
    # MeSH terms
    mesh = []
    for heading in citation.findall('.//MeshHeading'):
        descriptor = heading.find('DescriptorName').text
        major = heading.find('MajorTopicYN').text
        mesh.append(f"{descriptor} {'*' if major == 'Y' else ''}")
    
    print(f"PMID: {pmid}")
    print(f"Title: {title}")
    print(f"Journal: {journal} ({journal_iso}, {year}-{month})")
    print(f"Authors: {', '.join(authors)}")
    print(f"Abstract: {abstract[:200]}...")
    print(f"MeSH: {', '.join(mesh[:5])}")
    print("-" * 60)
```

## Article Summary (esummary)

Get compact metadata for multiple PMIDs at once — much faster than efetch for metadata-only needs:

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=31066247,40412714,36291303&retmode=json" | python3 -m json.tool
```

Response includes: title, authors, source, published date, published type, journal article, publication status, language, comment/correction list, citation subset, ISSN, subject area, pmc IDs, DOI, NLM ID, full count, and more.

## Related Articles

Find articles similar to a given PMID:

```bash
# Find related articles to PMID 31066247
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=31066247[uid]+AND+last5years[date]&retmax=10&retmode=json"
```

## Cited References

Find articles that cite a given paper (forward citations) — limited to ~100 results:

```bash
# Papers citing PMID 31066247 (last 5 years)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=31066247%5Bcid%5D+AND+last5years%5Bdate%5D&retmax=10&retmode=json"
```

## Full-Text via PubMed Central (PMC)

For open access full-text:

```bash
# Get PMC full text (XML format)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC6787482&retmode=xml"

# Get PMC article metadata
curl -s "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC6787482" | python3 -m json.tool

# Full-text search in PMC
curl -s "https://www.ncbi.nlm.nih.gov/research/builder/?query=vestibular+eye+tracking&content=abstract&content=full&content=references&content=supp"
```

## Author Search

```bash
# Search by author name
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Yang+SM%5BAuthor%5D+AND+vestibular%5BAll+Fields%5D&retmax=10&retmode=json"

# Search by first author only
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Wang+Y%5B1AU%5D+AND+vestibular%5BAll+Fields%5D&retmax=10&retmode=json"

# Get author's publication history via esummary
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=31066247,40412714&retmode=json"
```

## Date Filters

```bash
# Last 24 hours
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+last24hours[Date+-+Publication]&retmax=10&retmode=json"

# Last 7 days
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+last7days[Date+-+Publication]&retmax=10&retmode=json"

# Last 30 days
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+last30days[Date+-+Publication]&retmax=10&retmode=json"

# Specific date range
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+%222024/01/01%22%5BDate+-+Publication%5D%3A+%222024/12/31%22%5BDate+-+Publication%5D&retmax=20&retmode=json"
```

## Journal/Impact Factor Filtering

```bash
# By journal name
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+%22Nature+Reviews+Neuroscience%22%5BJournal%5D&retmax=10&retmode=json"

# By ISO abbreviation
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders+AND+%22Neuroscience%22%5BJA%5D&retmax=10&retmode=json"
```

## Rate Limits & Best Practices

| Parameter | Limit |
|-----------|-------|
| Free API | 3 requests/second (unauthenticated) |
| With API key | 10 requests/second (recommended) |
| Max per query | 10,000 results |
| Max PMIDs in efetch | 200 |

**Best Practices:**
1. Add a `tool` and `email` parameter: `&tool=hermes-agent&email=user@example.com` to identify your bot
2. Use `retmode=json` for easier parsing (XML for detailed metadata)
3. Use `esummary` for quick metadata, `efetch` for full details
4. Batch PMIDs in groups of 100-200 for efetch
5. Always include `retmax` to control result count
6. Use `sort=date` for recent papers, `sort=relevance` for topic relevance

## Complete Research Workflow

### 1. Discover Relevant Papers

```bash
# Step 1: Find MeSH terms for your topic
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=mesh&term=your_topic&retmax=5&retmode=json"

# Step 2: Search using MeSH + free text
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Your+Topic%22%5BMeSH%5D+OR+%22your+topic%22%5BAll+Fields%5D&retmax=50&retmode=json"
```

### 2. Filter by Quality/Type

```bash
# Systematic reviews only
# RCTs only
# Clinical queries (high-yield clinical literature)
```

### 3. Retrieve Details

```bash
# Get summaries for all PMIDs
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=ID1,ID2,ID3&retmode=json"

# Get full XML for key papers
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=ID1&retmode=xml"
```

### 4. Find Related Work

```bash
# Related articles to key papers
# Papers citing your key papers
# Papers by same authors
```

### 4. Validate Clinical Measurement Tools

When evaluating whether a clinical measurement tool (screening scale, lab test, questionnaire) is adequate for its claimed purpose, use these three search patterns:

**Search pattern A: Tool vs gold standard diagnostic accuracy**
```bash
# Check a screening tool's sensitivity/specificity in the target population
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%28%22{tool_name}%22%5Btiab%5D+OR+%22{tool_abbr}%22%5Btiab%5D%29+AND+%28FEES%5Btiab%5D+OR+VFSS%5Btiab%5D+OR+videofluoroscopy%5Btiab%5D%29+AND+%28sensitivity+OR+specificity+OR+%22diagnostic+accuracy%22%29&retmax=10&retmode=json"
```
- Real example: `EAT-10` in PD → found sensitivity 71.42%, specificity 45.45% (Ponsoni 2024, PMID: 38325386) — confirmed the tool misses ~30% of aspiration cases

**Search pattern B: Is the tool still being extended/improved?**
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%28%22{tool_name}%22%5Btiab%5D%29+AND+%28extended+OR+modified+OR+improved+OR+enhancement%29&retmax=10&retmode=json"
```
- If academia is still actively trying to improve the tool, the original version likely has known limitations

**Search pattern C: Find objective physiological alternatives**
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%28%22{objective_measure}%22%5Btiab%5D%29+AND+%28aspiration+OR+dysphagia%29+AND+%28predict*+OR+risk%29+AND+%28Parkinson*+OR+elderly%29&retmax=10&retmode=json"
```
- Example: `"Peak Cough Flow"` → 144+ papers supporting it as an objective measure of airway protection

This three-pattern approach was validated in a 2026-05-13 grant review session where the user pointed out that a water swallow test + EAT-10 combination was insufficient for aspiration prediction (see `nsfc-grant-audit/references/measurement-tool-adequacy.md`).

### 5. Store in Knowledge Base

```bash
# Save to llm-wiki, NotebookLM, Obsidian
```

## Pitfalls

- **URL encoding**: All query terms must be URL-encoded. Spaces become `+` or `%20`.
- **Case sensitivity**: `[filter]` is CASE-SENSITIVE. Use `review[PT]` not `Review[PT]`.
- **Bracket escaping**: When using MeSH terms, the brackets `[]` are part of the syntax and must be preserved.
- **XML namespaces**: PubMed XML has no namespaces — use simple tag names (no prefix).
- **PMID limits**: Maximum 200 PMIDs per efetch request. Split larger batches.
- **Rate limiting**: 3 req/s free, 10 req/s with API key. Add a `&tool=hermes-agent&email=user@example.com` parameter.
- **No abstract**: Some older papers have no abstract — check before parsing.
- **Multiple abstract sections**: AbstractText may have labels (BACKGROUND, METHODS, RESULTS, CONCLUSION) — concatenate them.
- **Author name formats**: Some authors have "Von" prefixes, middle initials, or corporate authors — handle edge cases.
- **Retraction warnings**: Always check if a paper has been retracted — use `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=PMID[ID]&retracted[filter]&retmode=json"` to check.

## Related Skills

- `arxiv` — arXiv paper search (complementary to PubMed)
- `openalex` — OpenAlex cross-disciplinary search
- `blogwatcher` — RSS feed monitoring for journal alerts
- `ocr-and-documents` — PDF/abstract extraction
- `llm-wiki` — Knowledge base storage
- `notebooklm-cli` — AI-powered literature analysis
- `research-paper-writing` — Paper writing pipeline
