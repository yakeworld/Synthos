# PMC Efetch — Most Reliable Full-Text Download Method

## Why Use This

Publisher PDF URLs (BMJ, MDPI, Wiley, Elsevier, Lancet, ACM) are blocked by anti-bot protections. PMC (PubMed Central) stores the full text XML for many of these same papers, accessible via NCBI's E-utilities API with no anti-bot blocking. This is the single most reliable pathway — it covered 24/33 references in one session.

## Workflow

### Step 1: Get PMID from DOI

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={DOI}&retmode=json"
```

Parse `esearchresult.idlist[0]` for PMID.

### Step 2: Get PMCID from PMID

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={PMID}&retmode=json"
```

Parse `result.{uid}.articleids[].value` where `idtype == 'pmc'`.

### Step 3: Download Full Text XML

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMCID_NUM}&retmode=xml"
```

Where `PMCID_NUM` is the numeric part without the "PMC" prefix.

### Step 4: Extract Text from XML

```python
import re
text = re.sub(r'<[^>]+>', ' ', xml_content)
text = re.sub(r'\s+', ' ', text).strip()
```

## Success Rate

| Source | Publisher Block | PMC Available | PMC Efetch Works |
|--------|:--------------:|:-------------:|:----------------:|
| BMJ (TRIPOD+AI) | ✅ Blocked | ✅ PMC11184186 | ✅ 50KB XML |
| BMJ (PROBAST+AI) | ✅ Blocked | ✅ PMC11931409 | ✅ 95KB XML |
| MDPI (Sallam 2023) | ✅ 403 | ✅ PMC10048148 | ✅ 84KB XML |
| BJET (Fan 2024) | ✅ Blocked | — (no PMC) | arXiv alternative |
| BJET (Xu 2025) | ✅ Blocked | ✅ PMC11880782 | ✅ 48KB XML |
| IEEE Access | ✅ Blocked | ✅ PMC4120374 | ✅ 44KB XML |
| Frontiers | ✅ Blocked | — | Direct PDF via Frontiers URL |

## Python Implementation (standalone function)

```python
def try_pmc_efetch(doi, timeout=15):
    """Try to get full text via PMC. Returns (text, pmcid) or ('', '')"""
    import json, urllib.request, ssl, re, time
    ctx = ssl._create_unverified_context()
    
    # PMID from DOI
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}&retmode=json"
    resp = urllib.request.urlopen(url, context=ctx, timeout=timeout)
    ids = json.loads(resp.read()).get('esearchresult', {}).get('idlist', [])
    if not ids:
        return '', ''
    time.sleep(0.3)
    
    # PMCID from PMID
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids[0]}&retmode=json"
    resp = urllib.request.urlopen(url, context=ctx, timeout=timeout)
    d = json.loads(resp.read())
    uid = [k for k in d['result'].keys() if k != 'uids'][0]
    pmcid = ''
    for a in d['result'][uid].get('articleids', []):
        if a['idtype'] == 'pmc' and a['value'] not in ('', 'N/A'):
            pmcid = a['value']
    if not pmcid:
        return '', ''
    time.sleep(0.3)
    
    # XML full text
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid.replace('PMC','')}&retmode=xml"
    resp = urllib.request.urlopen(url, context=ctx, timeout=timeout)
    xml = resp.read().decode('utf-8')
    if len(xml) < 1000:
        return '', pmcid
    
    text = re.sub(r'<[^>]+>', ' ', xml)
    text = re.sub(r'\s+', ' ', text).strip()
    return text, pmcid
```

## Limitations

- Only works for papers indexed in PubMed Central (PMC). Not all PubMed papers are in PMC.
- The XML contains full text but may include figure captions, tables, and references — strip XML tags carefully.
- Rate limit: 3 requests/second without API key. Add `time.sleep(0.4)` between calls.
- Some very recent papers (2025-2026) may not yet be XML-indexed in PMC.
