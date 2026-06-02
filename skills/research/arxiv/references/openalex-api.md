# OpenAlex API Reference

OpenAlex (https://openalex.org/) is a free, open database of 27M+ works covering arXiv, PubMed, CrossRef, and more. No API key required.

## Base URL

```
https://api.openalex.org
```

## Core Endpoints

### Search Works

```
GET /works?search=KEYWORDS&sort=cited_by_count:desc&per_page=10&select=FIELD1,FIELD2
```

**Common select fields:**
- `title`, `cited_by_count`, `publication_year`, `doi`, `ids` (DOI, PMID, arXiv, etc.)
- `authorships` (array with author info, institutions, countries)
- `keywords`, `concepts` (taxonomy terms with score)
- `primary_location` (journal info, open_access status, PDF URL)
- `open_access` (is_oa, oa_url, oa_download_url)
- `sustainable_development_goals` (SDG alignment)
- `related_works` (similar papers)
- `referenced_works` (what this paper cites — works that are cited BY this paper)
- `cited_by_api_url` (endpoint to get papers that cite this work)
- `publication_date` (YYYY-MM-DD format)
- `last_known_institution` (author's affiliation)
- `best_oa_location` (best open access version)
- `journal` (from primary_location)
- `institutions` (all affiliated institutions)
- `topics` (topical areas with relevance scores)
- `topic_share` (contribution to each topic)
- `count_by_year` (annual metrics)

**Filters:**
- `filter=publication_date:2024-01-01,2024-12-31` (date range)
- `filter=from_publication_date:2020` (min date)
- `filter=cited_by_count:>=100` (min citations)
- `filter=institutions.country_code:US` (country)
- `filter=primary_location.is_oa:true` (open access only)
- `filter=concepts.id:C123` (by concept ID)
- `filter=keywords:reinforcement+learning` (keyword match)

### Get a Single Work

```
GET /works/{DOI_OR_OPENALEX_ID}
```

DOI format: `GET /works/10.1234/example` (no prefix needed)
OpenAlex ID: `GET /works/W1234567890`

### Get Citations (papers citing this work)

```
GET /works/{WORK_ID}/citations?per_page=20&sort=cited_by_count:desc
```

Returns works that cite the given work. Use `cited_by_api_url` from the work metadata for pagination.

### Get Referenced Works (works cited by this paper)

```
GET /works/{WORK_ID}/referenced_works?per_page=20
```

Returns works that the given paper cites.

### Search Authors

```
GET /authors?search=AUTHOR_NAME&per_page=5&select=display_name,works_count,last_known_institutions,topics
```

**Common select fields:**
- `display_name`, `works_count`, `cited_by_count`
- `last_known_institutions` (array with institution info)
- `topics` (research areas)
- `orcid`, `ror`, `gis` (external IDs)
- `counts_by_year` (annual metrics)
- `works_api_url` (endpoint to get all works by this author)

### Search Concepts (taxonomy)

```
GET /concepts?search=CONCEPT_NAME&per_page=5&select=id,display_name,subfield,field,domain
```

OpenAlex has a structured taxonomy: domain > field > subfield > concept.

### Search Institutions

```
GET /institutions?search=INSTITUTION_NAME&per_page=5&select=id,display_name,country_code,raw_affiliation
```

### Search Sources (journals/conferences)

```
GET /sources?search=JOURNAL_NAME&per_page=5&select=id,display_name,host_organization,is_oa,issn_l
```

## Pagination

OpenAlex uses cursor-based pagination. Use `cursor:next` from the `meta` object in the response:

```
GET /works?search=TOPIC&cursor=next
```

For simple queries, `per_page` (max 200) is sufficient.

## Response Structure

```json
{
  "meta": {
    "count": 12345,
    "db_response_time_ms": 80,
    "cost_usd": 0.001
  },
  "results": [...],
  "group_by": null
}
```

For single-item queries, the result may not be wrapped in `results`.

## Useful Queries for Research

```bash
# Find recent high-impact papers on a topic
curl -s "https://api.openalex.org/works?search=TOPIC&filter=from_publication_date:2025&sort=cited_by_count:desc&per_page=10&select=title,publication_year,cited_by_count,authorships,primary_location,open_access" | python3 -m json.tool

# Find all papers by an author
curl -s "https://api.openalex.org/authors?search=AUTHOR&per_page=1&select=works_api_url" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['results'][0]['works_api_url'] if d.get('results') else 'Not found')"

# Find papers in a specific journal
curl -s "https://api.openalex.org/works?filter=source.id:S123456789&per_page=10&select=title,publication_year,cited_by_count" | python3 -m json.tool

# Find open-access papers only
curl -s "https://api.openalex.org/works?search=TOPIC&filter=from_publication_date:2024-01-01&select=title,open_access,doi" | python3 -m json.tool

# Find papers citing a specific paper
curl -s "https://api.openalex.org/works/10.1038/s41586-023-06221-2/citations?per_page=10&sort=cited_by_count:desc&select=title,publication_year,cited_by_count" | python3 -m json.tool
```

## Rate Limits

Practically unlimited. Each query costs ~0.001 USD (free tier). For automated heavy use, consider an API key from openalex.org.

## Differences from Semantic Scholar

- Broader coverage (all fields, not just CS/bio)
- No rate limit pressure
- Includes open access information
- Structured concept taxonomy
- No citation count inflation from self-citations filtering (SSholar filters some)
- Works have `referenced_works` (citations) and `cited_by` (references) endpoints
- Supports author, institution, journal, and concept search

## Limitations

- No full-text access (just metadata and links)
- No abstract for all works
- Citation counts may differ from Web of Science/Scopus
- Author disambiguation is not perfect (merged/split names)