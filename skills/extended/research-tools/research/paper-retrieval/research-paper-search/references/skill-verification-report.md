# Literature Search Skill Verification Report

## Validation Summary (2026-05-10)

Validated all 10 literature-retrieval skills via live API calls.

### Pass (6/10)
- pubmed: 100% functional, MeSH terms, batching, clinical queries
- arxiv: 100% functional, XML parsing via ElementTree
- openalex: 100% functional, no key needed, no rate limits
- systematic-review: Methodological framework only (no API)
- journal-selection-medical-ai: Methodological framework only (no API)  
- research-paper-writing: Methodological framework only (no API)

### Partial (2/10)
- research-paper-search: 4/6 sources (pubmed, arxiv, openalex, crossref OK; S2+BASE broken)
- literature-monitor: 4/5 sources (arxiv, pubmed, openalex OK; bioRxiv broken)

### Fail (2/10)
- biorxiv: API returns non-JSON or empty across ALL endpoints. Infrastructure migration suspected.
- semantic-scholar: API key expired 2026-05-10. All endpoints return 403.

## Key Takeaway for Future Sessions

When user asks for "search papers" or "literature review":
1. Default to: pubmed (biomedical) + openalex (cross-disciplinary) + arxiv (CS/AI) + crossref (general)
2. Skip bioRxiv and Semantic Scholar until they recover/re-register
3. OpenAlex can serve as universal fallback for all sources