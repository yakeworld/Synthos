# Academic API Troubleshooting — PubMed, OpenAlex, Semantic Scholar

## PubMed E-utilities Pitfalls

### Silent Failures (rc=0 but empty results)

1. **Multi-word term expansion fails** — terms like `"ocular torsion"` or `"tear film"` often expand to MeSH + All Fields searches that no paper matches due to strict AND logic. Result: `rc=0`, `count=0`, no IDs.
   - **Fix**: Use `+` as OR separator: `term=ocular+torsion` instead of `term=ocular torsion`
   - Or use `AND` for explicit Boolean: `term=ocular+AND+torsion`

2. **Rate limiting** — consecutive calls within < 2 seconds cause silent empty responses.
   - **Fix**: Add `time.sleep(1.5-2)` between calls. Max ~10 calls/minute.

3. **eSummary/eFetch pipeline failure** — if `esearch` succeeds but `efetch` fails (paper retracted, non-English journal), the abstract text may be empty or contain only journal metadata.
   - **Fix**: Validate `len(abstract) > 100` before treating as useful.

### Correct Pattern
```python
# Step 1: Search with + separator for multi-word terms
search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmax={max_n}&retmode=json"
# Step 2: Sleep 1.5s
# Step 3: Fetch each PMID
fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=text&rettype=abstract"
# Step 4: Validate abstract length
```

## OpenAlex API Pitfalls

### Parameter Misunderstandings

1. **`search` is full-text, not keyword** — `search=nystagmus` searches ALL fields including abstract, keywords, concepts. Returns thousands of results. Not a targeted keyword search.
   - **Fix**: Combine with other filters: `search=nystagmus&filter=publication_year:2024`

2. **`from_publication_date` is INVALID** — OpenAlex API silently ignores this parameter. Query returns but with wrong date range.
   - **Fix**: Use `filter=publication_year:YYYY` for year filtering.

3. **Space in search term** — `search=ocular torsion` may be interpreted as two separate terms. URL-encode spaces.
   - **Fix**: Use `search=ocular+torsion` or URL-encode properly.

4. **Abstract inverted index** — OpenAlex returns `abstract_inverted_index` as `{word: [positions]}` dict. Must reconstruct by sorting on position minimum.
   - **Fix**:
     ```python
     ab = " ".join(word for word, pos in sorted(ab_inv.items(), key=lambda x: min(x[1])))
     ```

## Semantic Scholar Pitfalls

### API Key Dependency

1. **No API key = empty results** — Without `SEMANTIC_SCHOLAR_API_KEY` env var, all S2 queries return `[]` with no error.
   - **Fix**: Check key presence first. Immediately fallback to OpenAlex.

### Rate Limiting

1. **429 status** — S2 API rate limits at ~100 requests/hour with free key.
   - **Fix**: Exponential backoff, then fall to OpenAlex.

## General Cross-Source Deduplication

When searching across PubMed, OpenAlex, and S2, always deduplicate by:
1. **DOI** (primary key — most reliable)
2. **Title normalization** (lowercase, remove punctuation, strip extra spaces)
3. **PMID ↔ DOI ↔ arXiv ID** cross-referencing

Keep the version with the most complete metadata (abstract, citations, venue).
