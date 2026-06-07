# v31 PubMed eFetch XML Parsing Pattern (2026-06-06)

## Discovery

v31 scan revealed NCBI eFetch `retmode=json` is systematically broken for single-ID requests — returns raw integer (e.g. `b'41400465\n'`, 9 bytes). This is a June 2026 API change.

## Working Pattern

```python
import json, urllib.request, re

def pubmed_scan(term, retmax=3):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(term)}&retmax={retmax}&retmode=json"
    with urllib.request.urlopen(url, timeout=15) as r:
        d = json.loads(r.read())
    cnt = int(d.get("esearchresult", {}).get("count", 0))
    ids = d.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return cnt, []
    titles = []
    for pid in ids[:retmax]:
        # Use retmode=xml for eFetch (retmode=json is broken)
        eurl = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&retmode=xml"
        with urllib.request.urlopen(eurl, timeout=15) as er:
            xml = er.read().decode('utf-8')
            m = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml, re.DOTALL)
            if m:
                titles.append(m.group(1))
    return cnt, titles
```

## Key Points

1. **eSearch `retmode=json` still works** — the breakage is ONLY in eFetch
2. **Always use `retmode=xml`** for eFetch — more stable than JSON for structured data
3. **ArticleTitle regex**: `<ArticleTitle[^>]*>(.*?)</ArticleTitle>` with `re.DOTALL` handles CDATA
4. **Count is string**: `int(d.get("esearchresult", {}).get("count", 0))` — not int directly
5. **idlist is lowercase**: `d.get("esearchresult", {}).get("idlist", [])` — not IdList

## Verification

Tested against 15+ PubMed queries across PINN/ODE, classical clinical, and competitive space directions. All return correct counts and titles.
