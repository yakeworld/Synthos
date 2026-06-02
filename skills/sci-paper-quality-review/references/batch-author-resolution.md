# Batch Author Resolution via Semantic Scholar API

Replace placeholder BibTeX author names (`{XXX Authors}`) with real author names
by querying DOIs through Semantic Scholar's API.

## Prerequisites

- Valid DOIs for each entry (verify first — Crossref/DOI.org resolver)
- Network access to api.semanticscholar.org (rate limit: ~1 req/sec)
- Fallback: Crossref API (`api.crossref.org`)

## Workflow

1. **Extract DOIs** from `references.bib` entries with placeholder authors:
   ```bash
   grep -B5 'author.*=.*[Aa]uthors}' references.bib | grep 'doi'
   ```

2. **Query S2 for each DOI** (1 req/sec):
   ```bash
   curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors"
   ```

3. **Handle rate limiting (HTTP 429)**: Wait 3s and retry. After 3 failures, fall back to:
   ```bash
   curl -s "https://api.crossref.org/works/{doi}"
   ```

4. **Format authors for BibTeX**: Extract `author.name` fields and join with ` and `

5. **Patch the bib file**: Replace the old `author = {XXX Authors},` line.

## Known Issues

- **New arXiv papers** (preprints < 2 weeks): often not indexed in S2 yet.
  Try `ArXiv:{arxiv_id}` instead of `DOI:{doi}` for the S2 query.
- **DOI-to-paper-id failure on first try**: Some DOIs resolve to a different
  S2 paper ID format. Retry with raw DOI string (e.g., `10.1000/xyz123`).
- **304 entries limit**: If batch exceeds this, split into chunks and pause.

## Real Session Metrics (2026-05-18)

| Metric | Value |
|--------|-------|
| Total entries | 12 |
| S2 API calls | ~30 (with retries) |
| 429 retries | 6 |
| Fallback to Crossref | 2 entries |
| Total duration | ~509 sec (for subagent) |
| Author format issues | \{~\} delimiters stripped manually |
