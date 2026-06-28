# OpenAlex Search Strategy

> Discovered during Cycle 171 (2026-06-23) domain expansion probe for chest wall mechanics.
> Generic `search=` is dangerously noisy; `title_and_abstract.search` is the correct approach for white space confirmation.

## The Problem: Generic Search is Noisy

OpenAlex `search=` parameter matches across full text, abstracts, concepts, and keywords. For physiological/clinical domains, this returns massive irrelevant noise.

**Example**: `search=diaphragm+mechanics+mathematical+model` returns:
- AI/machine learning in construction (cited_by=912)
- Deep physical neural networks (cited_by=701) — matches "deep" + "neural"
- Optical metrology review (cited_by=654)
- **Zero** actual diaphragm mechanics papers

Root cause: "diaphragm" matches lens diaphragms in optics, loudspeaker diaphragms in acoustics, camera diaphragms in photography, and pump diaphragms in fluid dynamics — ALL different from the physiological diaphragm.

## The Solution: title_and_abstract.search

Use `filter=title_and_abstract.search:` instead. This limits matching to title + abstract fields only.

```python
# WRONG — noisy:
search=chest+wall+mechanics+mathematical+model

# CORRECT — clean:
filter=title_and_abstract.search:chest+wall+mechanics+mathematical+model
```

**URL construction**: Append filter parameter as url-encoded query string:
```python
url = 'https://api.openalex.org/works?filter=title_and_abstract.search:' + urllib.parse.quote(query) + '&per_page=10&sort=cited_by_count:desc'
```

## Proven Query Sequence for White Space Probing

### Step 1: Narrow PINN (precision check)
```
filter=title_and_abstract.search:physics-informed+neural+network+<domain>
```
Returns 0 or 1-3 for true white space. If >3, check each result manually.

### Step 2: NeuralODE variants
```
filter=title_and_abstract.search:neural+ordinary+differential+equation+<domain>
```
Catches Neural ODE / graph ODE variants that don't use "PINN" keyword.

### Step 3: Classical ODE models (domain characterization)
```
filter=title_and_abstract.search:lumped+parameter+model+<domain>
filter=title_and_abstract.search:<domain>+ODE+model+parameter+estimation
```
Assesses classical literature size (100+ = well-characterized domain, <50 = sparse).

### Step 4: Patient-specific / inverse (non-PINN competition)
```
filter=title_and_abstract.search:patient+specific+<domain>+model+parameter+estimation
```
Detects clinical studies doing parameter estimation without PINN (Bayesian, Kalman filter, system ID).

## When Generic Search Is Acceptable

Only for exploratory/brainstorming queries where you want to see concept associations:
- "What fields overlap with our domain?"
- "Which research areas cite these papers?"
- Cross-domain inspiration queries

For white space confirmation, always use title_and_abstract.search.

## APA Key-Free Access

No API key needed — OpenAlex accepts anonymous requests at ~10/sec rate limit. This makes it the most reliable external search API for cron jobs (no credential management or rotation needed).

## Known OpenAlex Limitations

| Issue | Impact | Mitigation |
|:------|:------|:-----------|
| Stop words ignored | "and", "or", "not" in queries may be stripped | Use `+` between words, avoid natural language phrasing |
| Old paper dominance (1960s+) | Cited_by sorting favors old papers with high citation counts | Filter `cited_by_count:10-` or `cited_by_count:5-` to focus on active literature |
| Year metadata may be null | Some papers missing publication_year | Filter `from_publication_date:1990-01-01` for modern literature |
| Preprint + published versions | Same paper may appear multiple times | Deduplicate by DOI after retrieval |
