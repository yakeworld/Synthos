---
name: biorxiv
description: "Search and retrieve preprint papers from bioRxiv and medRxiv — the primary preprint servers for biological and medical sciences."
signature: "query: str -> papers: list[Paper]"
related_skills: [academic-paper-completion, adhd-eye-tracking-review, arxiv, blogwatcher, bppv-expert]
allowed-tools: [terminal, read_file, write_file, search_files]
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Preprint, bioRxiv, medRxiv, Preprints, Biology, Medicine, Open-Access]
    related_skills: [pubmed, arxiv, ocr-and-documents, llm-wiki]
---

# bioRxiv / medRxiv — Preprint Paper Search

bioRxiv (biology) and medRxiv (medicine) are the primary preprint servers for life sciences. Papers appear here **before** peer review, often weeks or months before journal publication.

## Quick Reference

| Action | Command |
|--------|---------|
| Search bioRxiv | `curl -s "https://api.biorxiv.org/details/biorxiv/QUERY"` |
| Search medRxiv | `curl -s "https://api.biorxiv.org/details/medrxiv/QUERY"` |
| Get latest papers | `curl -s "https://api.biorxiv.org/collections/biorxiv/latest"` |
| Get paper details | `curl -s "https://api.biorxiv.org/details/biorxiv/DOI"` |
| Get author papers | `curl -s "https://api.biorxiv.org/details/biorxiv/author/AUTHOR"` |
| Get daily stats | `curl -s "https://api.biorxiv.org/details/biorxiv/0"` |
| Get subject breakdown | `curl -s "https://api.biorxiv.org/subjects/biorxiv"` |

## Installation

No installation needed — the bioRxiv API is free, public, and returns JSON.

## Search Papers

```bash
# Search bioRxiv by keyword (returns up to 100 most relevant)
curl -s "https://api.biorxiv.org/details/biorxiv/vestibular+disorders" | python3 -m json.tool

# Search medRxiv
curl -s "https://api.biorxiv.org/details/medrxiv/ADHD" | python3 -m json.tool

# Search with quotes for exact phrases
curl -s "https://api.biorxiv.org/details/biorxiv/vestibulo-ocular+reflex" | python3 -m json.tool
```

### Search Syntax

The API searches across title, abstract, and keywords. The query is URL-encoded.

```bash
# Basic keyword search
curl -s "https://api.biorxiv.org/details/biorxiv/eye+tracking"

# Complex search with multiple terms
curl -s "https://api.biorxiv.org/details/biorxiv/attention+deficit+hyperactivity"

# Search with subject filter (bioRxiv has specific subject categories)
curl -s "https://api.biorxiv.org/details/biorxiv/brain+computer+interface"
```

## Get Latest Papers

```bash
# Get the 5 most recent bioRxiv preprints
curl -s "https://api.biorxiv.org/details/biorxiv/0" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for paper in data['collection'][0]['papers'][:5]:
    print(f\"[{paper['date']}] {paper['title']}\")
    print(f\"  Authors: {', '.join(paper['authors'].split(','))[:100]}...\")
    print(f\"  DOI: {paper['doi']}\")
    print(f\"  Abstract: {paper['abstract'][:200]}...\")
    print()
"

# Get latest medRxiv preprints
curl -s "https://api.biorxiv.org/details/medrxiv/0"

# Get latest papers from a specific subject category
curl -s "https://api.biorxiv.org/details/biorxiv/Neuroscience"
```

## Subject Categories

bioRxiv has the following subject categories:

| Category | Description |
|----------|-------------|
| Genomics | Genomics and evolutionary biology |
| Proteins and proteomics | Protein structure, function, and interactions |
| Cell biology | Cell biology and biological mechanisms |
| Developmental biology | Development and regeneration |
| Evolutionary biology | Evolution and phylogeny |
| Microbiology | Microbiology and viral biology |
| Plant biology | Plant science |
| Ecology | Ecology and environmental science |
| Neuroscience | Brain and nervous system |
| Bioinformatics | Computational biology and bioinformatics |
| Biophysics | Biophysics and physical chemistry |
| Quantitative biology | Mathematical and computational biology |
| Synaptic function | Synaptic transmission and function |
| Membrane biology | Membrane structure and function |
| Stem cells and regenerative medicine | Stem cells |
| Immunology | Immune system and disease |
| Microbiology and viruses | Microbes and viruses |
| Genes and machines | Gene regulation and expression |
| Microbiology and host interactions | Host-microbe interactions |
| Plant science | Plant biology |
| Single cell | Single-cell biology |

## Paper Detail Response

The response from the API includes:

```json
{
  "collection": [
    {
      "papers": [
        {
          "title": "Paper Title",
          "abstract": "Full abstract text...",
          "authors": "Author 1, Author 2, Author 3",
          "author_count": 3,
          "first_author": "Author 1",
          "subject": "Neuroscience",
          "doi": "10.1101/2024.01.01.574321",
          "url": "https://www.biorxiv.org/content/10.1101/2024.01.01.574321v1.full.pdf",
          "pdf_url": "https://www.biorxiv.org/content/10.1101/2024.01.01.574321v1.full.pdf",
          "comment": "",
          "response_count": 0,
          "tweet_count": 5,
          "tweet_author": "",
          "tweet_status": "",
          "tweet_date": "",
          "tweet_abstract": "",
          "tweet_url": "",
          "tweet_id": "",
          "tweet_handle": "",
          "tweet_followers": 0,
          "tweet_date": "",
          "tweet_status": "",
          "is_in_toc": false,
          "media_category": "",
          "category_label": "Neuroscience",
          "date": "2024-01-01",
          "updated": "2024-01-02",
          "score": 1.0
        }
      ]
    }
  ]
}
```

## Extracting Clean Output

```bash
# Clean, readable output
curl -s "https://api.biorxiv.org/details/biorxiv/eye+tracking" | python3 -c "
import sys, json

data = json.load(sys.stdin)
papers = data['collection'][0]['papers']

for i, paper in enumerate(papers):
    print(f'{i+1}. {paper[\"title\"]}')
    print(f'   Date: {paper[\"date\"]} | Subject: {paper[\"subject\"]}')
    print(f'   First Author: {paper[\"first_author\"]}')
    print(f'   Authors: {paper[\"authors\"][:150]}...')
    print(f'   DOI: {paper[\"doi\"]}')
    print(f'   Abstract: {paper[\"abstract\"][:300]}...')
    print(f'   PDF: {paper[\"pdf_url\"]}')
    print(f'   bioRxiv: https://www.biorxiv.org/content/{paper[\"doi\"]}')
    print(f'   Tweets: {paper[\"tweet_count\"]} | Score: {paper[\"score\"]}')
    print()
"
```

## Get Paper by DOI

```bash
# Get details for a specific preprint by DOI
curl -s "https://api.biorxiv.org/details/biorxiv/10.1101/2024.01.01.574321" | python3 -m json.tool
```

## Get Author Papers

```bash
# Get all papers by an author
curl -s "https://api.biorxiv.org/details/biorxiv/author/Kim" | python3 -m json.tool
```

## Daily Statistics

```bash
# Get daily upload statistics for bioRxiv
curl -s "https://api.biorxiv.org/details/biorxiv/0" | python3 -c "
import sys, json
data = json.load(sys.stdin)
papers = data['collection'][0]['papers']

# Group by subject
from collections import Counter
subjects = Counter(p['subject'] for p in papers)

print(f\"Total new preprints: {len(papers)}\")
print(\"By subject:\")
for subject, count in subjects.most_common():
    print(f\"  {subject}: {count}\")
"
```

## Subject Breakdown

```bash
# Get subject category breakdown
curl -s "https://api.biorxiv.org/subjects/biorxiv" | python3 -m json.tool
```

## Downloading Full Text

```bash
# Download PDF
curl -sL "https://www.biorxiv.org/content/10.1101/2024.01.01.574321v1.full.pdf" -o preprint.pdf

# Get HTML version (if available)
curl -s "https://www.biorxiv.org/content/10.1101/2024.01.01.574321v1" | grep -o 'https://www.biorxiv.org/content/.*html' | head -1
```

## Full Text via PMC (for older/bioRxiv papers that got published)

```bash
# Check if a preprint has been published in PMC
# Convert bioRxiv DOI to PMID via Crossref
curl -s "https://api.crossref.org/works/10.1101/2024.01.01.574321" | python3 -m json.tool | grep -A5 "link"
```

## Rate Limits

- **No rate limit** — the bioRxiv API is free and does not require authentication
- However, be reasonable: max 1 query per second is a good practice

## ⚠️ CRITICAL: API Status — UNRELIABLE (2026-05-10)

The bioRxiv API has been returning non-JSON responses, empty collections,
and error messages ("no posts found") across ALL endpoints:
- `/details/biorxiv/0` → `{"messages": [{"status": "no posts found"}], "collection": []}`
- `/details/biorxiv/Neuroscience` → JSON parse error or empty
- `/subjects/biorxiv` → JSON parse error or empty

The server responds HTTP 200 with Apache/Python but the content is
malformed or empty. This affects:
- Keyword search (`/details/biorxiv/QUERY`)
- Latest papers (`/details/biorxiv/0`)
- Subject search (`/details/biorxiv/SubjectName`)
- Collection/list endpoints (`/collections/biorxiv/latest`)

**Root cause**: bioRxiv API has likely migrated from Heroku to a new
infrastructure (Apache/Python 3.6/PHP 8.2 stack detected) and the
endpoints are broken or require different parameters.

**Workaround**: Use OpenAlex for preprint coverage:
```bash
curl -s "https://api.openalex.org/works?search=TOPIC&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=20&select=title,publication_date,open_access,primary_location"
```
OpenAlex includes bioRxiv/medRxiv preprints and has been reliable.

Also try medRxiv separately:
```bash
curl -s "https://api.biorxiv.org/details/medrxiv/0"
```
If medRxiv also fails, both bioRxiv and medRxiv are down.

**For systematic reviews**: Consider alternative preprint sources
(Crossref preprint DOI resolution, Europe PMC preprint section) until
bioRxiv recovers.

**Status**: Flag as UNRELIABLE. Do NOT rely on for production research
workflows. Check periodically — may recover.

## Pitfalls

- **Not peer-reviewed**: Preprints have NOT been peer-reviewed. Content may change significantly before publication.
- **DOI changes**: The bioRxiv DOI may change when the paper is revised (new version). Always use the latest version.
- **Abstract length**: Abstracts may be truncated in the API response — check length.
- **Author name parsing**: Author names come as a single comma-separated string — split carefully for edge cases.
- **Duplicate content**: The same paper may appear on bioRxiv and later on PubMed. Deduplicate by DOI/PMID.
- **PDF access**: PDF links are direct but may change. The HTML version is more stable.
- **No full-text search in abstract**: The API searches title/abstract/keywords, but some papers have incomplete abstracts.

## Research Workflow Integration

### 1. Daily Preprint Check

```bash
# Check for new preprints on your topics
curl -s "https://api.biorxiv.org/details/biorxiv/0" | python3 -c "..."
curl -s "https://api.biorxiv.org/details/medrxiv/0" | python3 -c "..."
```

### 2. Literature Review Companion

```bash
# Find preprints related to your research topic
curl -s "https://api.biorxiv.org/details/biorxiv/your+topic"
```

### 3. Track Author Activity

```bash
# Track a specific author's latest preprints
curl -s "https://api.biorxiv.org/details/biorxiv/author/AuthorName"
```

### 4. Feed into Knowledge Base

```bash
# Store preprints in llm-wiki or NotebookLM for later analysis
```

## Related Skills

- `pubmed` — PubMed MEDLINE search (complementary: PubMed has peer-reviewed, bioRxiv has preprints)
- `arxiv` — arXiv search (for CS/AI topics)
- `ocr-and-documents` — PDF extraction
- `llm-wiki` — Knowledge base storage
