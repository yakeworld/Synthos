# Example Search Queries and Expected Results

## ADHD Eye Tracking Research

### Query: "ADHD eye tracking"
- **Semantic Scholar**: 225 papers (excellent coverage)
- **Crossref**: 5 papers (moderate coverage)
- **OpenAlex**: 5 papers (good coverage, includes open access)
- **arXiv**: 0 papers (arXiv is not a good source for clinical/medical research)
- **PubMed**: 5 papers (excellent for clinical/medical content with abstracts)

### Query: "ADHD"
- **PubMed**: Returns high-quality clinical papers with detailed abstracts, MeSH terms, and keywords
- Expected fields: PMID, DOI, PMCID, abstract, MeSH keywords, journal info

## General Research Patterns

### Medical/Clinical Research
- Best sources: PubMed, Semantic Scholar
- arXiv: almost no results (not a medical/preprint platform for clinical research)
- Crossref: good but may miss open-access PDF links
- OpenAlex: good coverage of OA content

### Computer Science / AI Research
- Best sources: arXiv, Semantic Scholar, OpenAlex, Crossref
- arXiv: primary source for preprints
- Semantic Scholar: best metadata coverage

### General Academic Search
- Use `search_all()` with all sources for maximum coverage
- Deduplication by DOI is the most reliable — most papers have a DOI
- PMID > arXiv > DOI for paper identification priority (from `get_identifier()`)

## Query Best Practices

1. **Short queries work better** — "ADHD" gives better results than long descriptive sentences
2. **Use keywords, not full sentences** — search engines expect keyword-based queries
3. **Try multiple sources** — one source may have no results while another has many
4. **Check open_access field** — only papers where `open_access=True` can be downloaded
5. **Verify PDF URLs** — not all papers have accessible PDFs even when marked as open access