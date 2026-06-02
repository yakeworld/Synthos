---
name: openalex
description: "OpenAlex — the open, free, comprehensive academic paper database covering 250M+ papers, authors, institutions, concepts, and journals across all disciplines. No API key needed, no rate limits."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, OpenAlex, Academic-Search, Citations, Cross-disciplinary, Free, No-rate-limit]
    related_skills: [pubmed, arxiv, blogwatcher, llm-wiki, ocr-and-documents]
---

# OpenAlex — Comprehensive Academic Search

OpenAlex is a **completely free, open-source, no-API-key-required** database covering **250M+ papers**, authors, institutions, concepts, and journals across ALL disciplines. It's a powerful alternative to Google Scholar.

## Quick Reference

| Action | Command |
|--------|---------|
| Search papers | `curl -s "https://api.openalex.org/works?search=QUERY&per_page=10&select=title,authorships,cited_by_count,publication_year"` |
| Get paper by DOI | `curl -s "https://api.openalex.org/works/doi:10.xxxx/xxxxx"` |
| Get paper by ID | `curl -s "https://api.openalex.org/works/https://openalex.org/W1234567890"` |
| Search authors | `curl -s "https://api.openalex.org/authors?search=Author+Name&per_page=5"` |
| Get author details | `curl -s "https://api.openalex.org/authors/https://openalex.org/A123456789"` |
| Search institutions | `curl -s "https://api.openalex.org/institutions?search=University+Name&per_page=5"` |
| Search concepts | `curl -s "https://api.openalex.org/concepts?search=Concept+Name&per_page=5"` |
| Search journals | `curl -s "https://api.openalex.org/sources?search=Journal+Name&per_page=5"` |
| Get citations OF paper | `curl -s "https://api.openalex.org/works/WORK_ID/citations?per_page=20"` |
| Get related works | `curl -s "https://api.openalex.org/works/WORK_ID/related_works?per_page=10"` |
| Get author works | `curl -s "https://api.openalex.org/authors/AUTHOR_ID/works?per_page=20&sort=cited_by_count:desc"` |
| Search by keyword | `curl -s "https://api.openalex.org/works?keywords=KEYWORD&per_page=10"` |
| Get institutions by author | `curl -s "https://api.openalex.org/institutions?author=AUTHOR_ID"` |

## Search Papers

### Basic Search

```bash
# Simple keyword search
curl -s "https://api.openalex.org/works?search=ADHD+attention+deficit&per_page=5&select=title,cited_by_count,publication_year" | python3 -m json.tool

# Search with specific fields
curl -s "https://api.openalex.org/works?search=vestibular+disorder+eye+tracking&per_page=5&select=title,authorships,cited_by_count,keywords,open_access,publication_year,primary_location,abstract_inverted_index" | python3 -m json.tool

# Search with citation count sorting
curl -s "https://api.openalex.org/works?search=neural+networks+transformer&sort=cited_by_count:desc&per_page=10&select=title,cited_by_count,publication_year"
```

### Advanced Filters

```bash
# By publication year range
curl -s "https://api.openalex.org/works?search=your+topic&filter=from_publication_date:2024-01-01,to_publication_date:2026-12-31&per_page=20&select=title,publication_year,cited_by_count"

# Only open access papers
curl -s "https://api.openalex.org/works?search=your+topic&filter=open_access.is_oa:true&per_page=20&select=title,primary_location.is_oa,primary_location.landing_page_url"

# Only specific journals
curl -s "https://api.openalex.org/works?search=your+topic&filter=from_pub_date:2023-01-01,to_pub_date:2026-12-31&sort=cited_by_count:desc&per_page=20&select=title,cited_by_count,primary_location.source.display_name,publication_year"

# By research area
curl -s "https://api.openalex.org/works?search=your+topic&filter=primary_location.source.is_in_doaj:true&per_page=20&select=title,primary_location.source.display_name"

# With keywords filter
curl -s "https://api.openalex.org/works?search=vestibular&keywords=vestibular+disorder&per_page=10&select=title,keywords,cited_by_count,publication_year"

# By institution
curl -s "https://api.openalex.org/works?search=your+topic&filter=institutions.id:https://openalex.org/I51158804&per_page=10&select=title,authorships,institutions"
```

### Citation Analysis

```bash
# Get papers that cite a specific work (forward citations)
curl -s "https://api.openalex.org/works/https://openalex.org/W2741809404/citations?per_page=20&select=title,cited_by_count,publication_year,primary_location"

# Get papers cited by a specific work (backward references)
curl -s "https://api.openalex.org/works/https://openalex.org/W2741809404?select=title,cited_by_count,concepts,open_access,authorships"

# Get related works
curl -s "https://api.openalex.org/works/https://openalex.org/W2741809404/related_works?per_page=10&select=title,cited_by_count,publication_year"

# Get most cited papers in a topic
curl -s "https://api.openalex.org/works?search=your+topic&sort=cited_by_count:desc&per_page=10&select=title,cited_by_count,publication_year,primary_location"
```

## Search Authors

```bash
# Search by name
curl -s "https://api.openalex.org/authors?search=Yang+Shi-Ming&per_page=5&select=display_name,works_count,cited_by_count,last_known_institutions,topics" | python3 -m json.tool

# Get full author profile
curl -s "https://api.openalex.org/authors/https://openalex.org/A123456789" | python3 -m json.tool

# Get author's most cited works
curl -s "https://api.openalex.org/authors/https://openalex.org/A123456789/works?sort=cited_by_count:desc&per_page=10" | python3 -m json.tool

# Get author's topics/research areas
curl -s "https://api.openalex.org/authors/https://openalex.org/A123456789?select=display_name,works_count,cited_by_count,topics" | python3 -m json.tool
```

## Search Institutions

```bash
# Search by name
curl -s "https://api.openalex.org/institutions?search=Harvard+University&per_page=5"

# Get institution details
curl -s "https://api.openalex.org/institutions/https://openalex.org/I51158804"

# Get institution's research output
curl -s "https://api.openalex.org/institutions/https://openalex.org/I51158804/works?sort=cited_by_count:desc&per_page=10"
```

## Search Concepts/Topics

```bash
# Search concept
curl -s "https://api.openalex.org/concepts?search=attention&per_page=5&select=display_name,description,works_count,level"

# Get concept details
curl -s "https://api.openalex.org/concepts/https://openalex.org/C123456789"

# Get papers under a concept
curl -s "https://api.openalex.org/concepts/https://openalex.org/C123456789/works?sort=cited_by_count:desc&per_page=10"
```

## Search Journals/Sources

```bash
# Search by name
curl -s "https://api.openalex.org/sources?search=New+England+Journal+Medicine&per_page=5"

# Get source details
curl -s "https://api.openalex.org/sources/https://openalex.org/S123456789"

# Get latest papers from a journal
curl -s "https://api.openalex.org/sources/https://openalex.org/S123456789/works?sort=date:desc&per_page=10"
```

## Response Structure

### Work (Paper) Response

```json
{
  "id": "https://openalex.org/W1234567890",
  "title": "Paper Title",
  "abstract_inverted_index": {
    "word1": [position],
    "word2": [position]
  },
  "cited_by_count": 1234,
  "publication_year": 2024,
  "publication_date": "2024-01-15",
  "type": "journal-article",
  "primary_location": {
    "is_oa": false,
    "landing_page_url": "https://doi.org/10.xxxx/xxxxx",
    "pdf_url": null,
    "source": {
      "id": "https://openalex.org/S123456789",
      "display_name": "Journal Name",
      "issn_l": "0000-0000",
      "issn": ["0000-0000", "1234-5678"],
      "is_oa": false,
      "is_in_doaj": false,
      "is_core": true,
      "host_organization": "https://openalex.org/P123456789",
      "type": "journal"
    }
  },
  "authorships": [
    {
      "author_position": "first",
      "author": {
        "id": "https://openalex.org/A123456789",
        "display_name": "Author Name",
        "orcid": "https://orcid.org/0000-0000-0000-0000"
      },
      "institutions": [
        {
          "id": "https://openalex.org/I123456789",
          "display_name": "Institution",
          "ror": "https://ror.org/123456789",
          "country_code": "US",
          "type": "education"
        }
      ],
      "is_corresponding": true,
      "raw_author_name": "Author Name",
      "raw_affiliation_string": "Department, Institution"
    }
  ],
  "keywords": ["keyword1", "keyword2"],
  "concepts": [
    {
      "id": "https://openalex.org/C123456789",
      "display_name": "Concept Name",
      "description": "Concept description",
      "level": 1,
      "score": 0.95
    }
  ],
  "open_access": {
    "is_oa": true,
    "oa_status": "gold",
    "oa_url": "https://doi.org/..."
  },
  "counts_by_year": [
    {"year": 2024, "cited_by_count": 50, "works_count": 1},
    {"year": 2023, "cited_by_count": 30, "works_count": 1}
  ],
  "best_oa_location": {
    "is_oa": true,
    "landing_page_url": "https://...",
    "pdf_url": "https://...",
    "source": {...}
  }
}
```

### Author Response

```json
{
  "id": "https://openalex.org/A123456789",
  "orcid": "https://orcid.org/0000-0000-0000-0000",
  "display_name": "Author Name",
  "works_count": 100,
  "cited_by_count": 5000,
  "last_known_institutions": [
    {
      "id": "https://openalex.org/I123456789",
      "display_name": "Institution",
      "ror": "https://ror.org/123456789",
      "country_code": "CN"
    }
  ],
  "works_api_url": "https://api.openalex.org/authors/https://openalex.org/A123456789/works",
  "x_concepts": [
    {
      "id": "https://openalex.org/C123456789",
      "display_name": "Concept",
      "score": 0.95
    }
  ]
}
```

## Clean Output Examples

### Search Papers with Clean Output

```bash
curl -s "https://api.openalex.org/works?search=ADHD+attention&sort=cited_by_count:desc&per_page=5&select=title,cited_by_count,publication_year,primary_location,concepts,open_access" | python3 -c "
import sys, json
data = json.load(sys.stdin)

for i, work in enumerate(data['results']):
    title = work.get('title', 'N/A')
    cited = work.get('cited_by_count', 0)
    year = work.get('publication_year', 'N/A')
    
    journal = work.get('primary_location', {}).get('source', {}).get('display_name', 'N/A')
    is_oa = work.get('primary_location', {}).get('is_oa', False)
    oa_url = work.get('best_oa_location', {}).get('landing_page_url') if work.get('open_access', {}).get('is_oa') else None
    
    concepts = [c['display_name'] for c in work.get('concepts', [])[:5]]
    authors = [a['author']['display_name'] for a in work.get('authorships', [])]
    
    print(f'{i+1}. [{year}] {title}')
    print(f'   Journal: {journal}')
    print(f'   Citations: {cited} | OA: {\"Yes\" if is_oa else \"No\"}')
    print(f'   Authors: {\", \".join(authors[:3])}')
    print(f'   Concepts: {\", \".join(concepts)}')
    if oa_url:
        print(f'   OA URL: {oa_url}')
    print()
"
```

### Citation Network Analysis

```bash
# Get top 20 papers citing a specific work
curl -s "https://api.openalex.org/works/https://openalex.org/W2741809404/citations?per_page=20&select=title,cited_by_count,publication_year" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print(f\"Papers citing the reference (top {len(data.get('results', []))}):\")
for i, work in enumerate(data.get('results', [])[:20]):
    title = work.get('title', 'N/A')
    cited = work.get('cited_by_count', 0)
    year = work.get('publication_year', 'N/A')
    print(f\"  {i+1}. [{year}] {title} (cited by: {cited})\")
"
```

### Author Research Profile

```bash
# Get author's most cited works
curl -s "https://api.openalex.org/authors/AUTHOR_ID/works?sort=cited_by_count:desc&per_page=10&select=title,cited_by_count,publication_year" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print(\"Most cited works:\")
for i, work in enumerate(data.get('results', [])[:10]):
    title = work.get('title', 'N/A')
    cited = work.get('cited_by_count', 0)
    year = work.get('publication_year', 'N/A')
    print(f\"  {i+1}. [{year}] {title} ({cited} citations)\")
"
```

## Search by Topic Hierarchy

OpenAlex has a hierarchical concept system (21 levels). Level 1 is the broadest:

```bash
# Get papers at level 1 (broadest category)
curl -s "https://api.openalex.org/concepts/https://openalex.org/C430096133" | python3 -m json.tool

# Get all concepts under a parent
curl -s "https://api.openalex.org/concepts?ancestor:https://openalex.org/C430096133&per_page=50"
```

## Rate Limits

- **No rate limit** — OpenAlex is completely free with no API key required
- No authentication needed
- No rate limiting
- However, be respectful: avoid making hundreds of requests per second

## Pitfalls

- **Abstract format**: `abstract_inverted_index` is a dictionary mapping words to positions — not a readable string. You need to invert it to get the abstract text.
- **Title-only papers**: Some entries have titles but no abstracts (older papers, conference proceedings).
- **Author name variations**: Author names may have different formats (last name, first name; last, F. M.; etc.).
- **Multiple institutions**: An authorship can have multiple affiliated institutions.
- **Preprint handling**: Preprints from arXiv/bioRxiv are included but may be marked as non-peer-reviewed.
- **DOI vs OpenAlex ID**: Works have both `doi` and `id` (OpenAlex ID). Use `doi:10.xxxx/xxxxx` for DOI searches.
- **Pagination**: Results are paginated. Use `cursor` parameter for next page.
- **Citation count**: May not include very recent papers (citation lag).

## Advanced: Abstract Reconstruction

```bash
# Reconstruct abstract from inverted index
curl -s "https://api.openalex.org/works/doi:10.xxxx/xxxxx&select=title,abstract_inverted_index" | python3 -c "
import sys, json

data = json.load(sys.stdin)
work = data

abstract_index = work.get('abstract_inverted_index', {})
if abstract_index:
    # Reconstruct the abstract
    words_by_position = {}
    for word, positions in abstract_index.items():
        for pos in positions:
            words_by_position[pos] = word
    
    # Sort by position
    abstract = ' '.join(words_by_position[i] for i in sorted(words_by_position.keys()))
    print(abstract)
else:
    print('No abstract available')
"
```

## Pagination

```bash
# First page
curl -s "https://api.openalex.org/works?search=topic&per_page=20"

# Next page using cursor
curl -s "https://api.openalex.org/works?search=topic&per_page=20&cursor=eyJpZCI6IjEyMzQ1In0="
```

## Use Cases for Medical Research

```bash
# 1. Find all papers on a topic from top journals
curl -s "https://api.openalex.org/works?search=vestibular+disorders&filter=primary_location.source.is_in_doaj:true&sort=cited_by_count:desc&per_page=20"

# 2. Find open access papers for free full text
curl -s "https://api.openalex.org/works?search=ADHD&filter=open_access.is_oa:true&per_page=20"

# 3. Find papers by specific institution
curl -s "https://api.openalex.org/works?search=vestibular&filter=institutions.id:https://openalex.org/I123456789&per_page=10"

# 4. Find papers under a specific concept
curl -s "https://api.openalex.org/concepts/https://openalex.org/C123456789/works?sort=date:desc&per_page=10"

# 5. Track an author's latest work
curl -s "https://api.openalex.org/authors/AUTHOR_ID/works?sort=date:desc&per_page=10"
```

## Related Skills

- `pubmed` — PubMed MEDLINE search (complementary: PubMed has structured MeSH, OpenAlex has all disciplines)
- `arxiv` — arXiv search (CS/AI papers)
- `blogwatcher` — RSS feed monitoring
- `llm-wiki` — Knowledge base storage
- `ocr-and-documents` — PDF extraction
