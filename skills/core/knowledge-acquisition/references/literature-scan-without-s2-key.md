# Literature Scan Without Semantic Scholar API Key

> Proven workflow for confirming ABSOLUTE_WHITE when SEMANTIC_SCHOLAR_API_KEY is unavailable.
> Verified in Cycle 167 (respiratory-mechanics-PINN literature_scan, 7 queries across 3 free APIs).

## Fallback Chain

When `SEMANTIC_SCHOLAR_API_KEY` is not set (returns 403 or empty), use this zero-cost fallback:

```
1. PubMed ESearch + ESummary  (free, 3 req/s)
2. OpenAlex                    (free, no key, sort=cited_by_count)
3. arXiv API                   (free, http://, XML/Atom)
```

## Effective Query Strategy (No S2 Key)

Approach with worst-case bounds: if no S2 key exists → the scan may be slower but equally conclusive.

### Step 1: Narrow PubMed PINN Queries (3 queries, most decisive)

```python
# Query 1 — core narrowest
urllib.parse.quote_plus('(physics-informed neural network OR PINN) AND (target mechanics)')
# Query 2 — alternate domain name
urllib.parse.quote_plus('(physics-informed neural network OR PINN) AND (alternate term)')
# Query 3 — Neural ODE variant
urllib.parse.quote_plus('(neural ODE) AND (target OR alternate)')
```

If ALL 3 return 0: strong ABSOLUTE_WHITE signal.

### Step 2: OpenAlex Broad Confirmation (2 queries)

```python
# Use safe='+' for OpenAlex (urllib.parse.quote not quote_plus)
urllib.parse.quote('PINN target-domain mechanics', safe='+')
# Must add: sort=cited_by_count&filter=cited_by_count:1-
url = f"https://api.openalex.org/works?search={encoded}&sort=cited_by_count&filter=cited_by_count:1-&per_page=5"
```

Examine top-5 titles. If ALL are false positives (blood flow ≠ airway mechanics, etc.), count as 0 true hits.

### Step 3: arXiv Confirmation (1 query)

```python
urllib.parse.quote('physics-informed neural network target domain')
url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&max_results=5"
```

### Step 4: Classical Model Confirmation (2 contextual queries)

Confirm that classical ODE/compartment models exist (100+ hits needed for well-characterized domain):

```python
urllib.parse.quote_plus('("lumped-parameter" OR "compartment model") AND (target OR alternate) AND (ODE)')
```

If classical models exist (100+) AND all 3 PINN queries return 0 → **ABSOLUTE_WHITE confirmed**.

## Performance in Practice

| API | Queries | Time | Hit Quality |
|:----|:-------:|:----:|:------------|
| PubMed narrow | 3 | ~3s | Best (precise, few FPs) |
| OpenAlex broad | 2 | ~2s | OK (many FPs, need title review) |
| arXiv broad | 1 | ~2s | Low (few academic papers) |
| PubMed contextual | 2-4 | ~4s | Good (confirms domain is well-studied) |

Without S2 key, count on ~15s for a complete scan vs ~8s with S2 key. The verdict quality is equivalent because PubMed narrow queries are the most decisive signal.
