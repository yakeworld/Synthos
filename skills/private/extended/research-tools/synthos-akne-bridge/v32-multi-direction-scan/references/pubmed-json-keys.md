# PubMed JSON API Key Reference

> NCBI E-utilities (`esearch.fcgi`, `efetch.fcgi`, `esummary.fcgi`) return JSON with **lowercase keys**, not the mixed-case keys documented in some older references.

## Correct Key Names (esearch.fcgi)

| Old/documented key | Actual key (lowercase) | Type | Description |
|---|---|---|---|
| `Count` | `count` | string | Total hit count |
| `RetMax` | `retmax` | string | Max records returned |
| `RetStart` | `retstart` | string | Start offset |
| `IdList` | `idlist` | list of strings | Matching PMIDs |
| `TranslationSet` | `translationset` | list | Query translation details |
| `QueryTranslation` | `querytranslation` | string | Actual translated query |

## Working Python Pattern

```python
import requests

base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
params = {
    'db': 'pubmed',
    'term': query_string,
    'retmax': 5,
    'retmode': 'json',
}
r = requests.get(base_url, params=params, timeout=15)
data = r.json()

# CORRECT — lowercase keys
count = int(data.get('esearchresult', {}).get('count', '0'))
ids = data.get('esearchresult', {}).get('idlist', [])

# WRONG — these will fail silently with defaults
# count = data.get('esearchresult', {}).get('Count', '0')
# ids = data.get('esearchresult', {}).get('IdList', [])
```

## Query Construction Tips

- Use `[dp]` date filter for year ranges: `2025[dp]:2026[dp]`
- URL-encoding handled automatically by `requests` library — do NOT pre-encode
- Timeout: 15s minimum, 30s for complex queries
- When using `urllib` (via pubmed_utils.py), the same lowercase key pattern applies
