# DOI Lookup API Workflow — Reference Guide

## Tier 1: Semantic Scholar (Best for modern/recent papers)

**Endpoint**: `https://api.semanticscholar.org/graph/v1/paper/search`

**Parameters**:
- `query`: Paper title (max 100 chars, use shorter title for best match)
- `limit`: Number of results (1-50, default 1)
- `fields`: Comma-separated fields to return (title, authors, year, externalIds, venue)
- `query.author`: Optional — author names for disambiguation

**Headers**:
- `User-Agent: synthos-audit/1.0 (yakeworld@wmu.edu.cn)` — REQUIRED

**Response structure**:
```json
{
  "data": [
    {
      "title": "Paper Title",
      "authors": [{"name": "First Last"}],
      "year": 2024,
      "externalIds": {
        "DOI": "10.xxxx/yyyy",
        "SEMANTIC_SCHOLAR": "s2_id",
        "arXiv": "XXXX.XXXXX",
        "PubMed": "PMID"
      }
    }
  ],
  "total": 1
}
```

**When to use**:
- arXiv preprints (returns paper even without DOI)
- Recent conference papers (2015+)
- Papers not yet in Crossref
- Papers with known authors for disambiguation

**When NOT to use**:
- Very old papers (pre-2000) — may not be indexed
- Non-English papers — limited coverage
- Very narrow niche venues

## Tier 2: Crossref API (Best for journals/book chapters)

**Endpoint**: `https://api.crossref.org/works`

**Parameters**:
- `query.title`: Paper title for search
- `rows`: Number of results (1-100)
- `mailto`: Your email (REQUIRED for rate limiting)
- `select`: Fields to return (title, author, DOI, published-print, container-title)
- `sort`: "relevance" or "published"

**Response structure**:
```json
{
  "status": "ok",
  "message": {
    "items": [{
      "DOI": "10.xxxx/yyyy",
      "title": ["Paper Title"],
      "author": [{"given": "First", "family": "Last"}],
      "published-print": {"date-parts": [[2024]]},
      "container-title": ["Journal Name"]
    }]
  }
}
```

**When to use**:
- Journal articles (IEEE, Elsevier, Springer, ACM)
- Book chapters
- Papers from established publishers

**When NOT to use**:
- arXiv papers (not indexed)
- Very old papers (may not be in Crossref)
- Pre-DOI era papers (before ~2000)

**Important**: Clean DOI before lookup:
- Replace `\\_` with `_` (LaTeX escaped underscore)
- Example: `10.1007/978-3-031-37660-3_8` → `10.1007/978-3-031-37660-38`

## Tier 3: PubMed (For medical/clinical papers)

**Endpoint**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

**Step 1 — Search**:
```
GET esearch.fcgi?db=pubmed&term={title}&retmax=5&usehistory=y
```

**Step 2 — Fetch details**:
```
GET efetch.fcgi?db=pubmed&id={PMID1},{PMID2}&rettype=abstract&retmode=xml
```

**Response**: XML with ArticleTitle, ELocationID (DOI), Journal, ArticleDate

**When to use**:
- Clinical/medical papers
- Papers not found by Semantic Scholar or Crossref
- Papers with medical/biological focus

## Error handling

| Status | Cause | Action |
|--------|-------|--------|
| HTTP 404 (Crossref) | DOI not found | Try Semantic Scholar; may be unindexed or wrong DOI |
| HTTP 429 (Crossref) | Rate limited | Add `mailto:` header, 5 req/sec max |
| Empty results (SS) | No match | Try broader title; may be too niche/old |
| XML parse error | Malformed response | Check if request succeeded; retry with simpler query |

## DOI pattern reference

| Publisher | Pattern | Example |
|-----------|---------|---------|
| IEEE | `10.1109/XXXXX.YYYYYYY` | `10.1109/TPAMI.2008.183` |
| Elsevier | `10.1016/j.xxxx.yyyy.zz` | `10.1016/j.patcog.2019.04.010` |
| Springer | `10.1007/xxxx-yyyyyyy` | `10.1007/978-3-031-37660-38` |
| ACM | `10.1145/XXXXX.XXXXXX` | `10.1145/3204493.3204525` |
| arXiv | `10.48550/arXiv.XXXXX` | `10.48550/arXiv.2408.17231` |
| MDPI | `10.3390/journal-volume-number-page` | `10.3390/s21144769` |