# PDF Download Multi-Pathway Protocol

## Priority Order (try in this sequence)

### 1. Direct OA Publisher URL
- **BMC/SpringerOpen**: `https://xxx.biomedcentral.com/counter/pdf/10.xxxx` — usually works
- **Frontiers**: `https://www.frontiersin.org/journals/xxx/articles/10.3389/xxx/pdf` — usually works
- **arXiv (CS/ML preprints)**: `curl -sL "https://arxiv.org/pdf/{arxiv_id}.pdf" -o paper.pdf` — works but has HTTP 301 redirect to `/pdf/{arxiv_id}` (no `.pdf` suffix). Always use `-L` (follow redirects).
- **MDPI**: `https://www.mdpi.com/xxxx/xxx/pdf` — returns 403 (known blocked)

**arXiv redirect pitfall**: `https://arxiv.org/pdf/2408.06292.pdf` returns HTTP 301 → `/pdf/2408.06292` (drops `.pdf` suffix). Without `-L`, curl saves the redirect HTML page (10KB, not a real PDF). The `api.export.arxiv.org` endpoint is frequently down (connection established, 0 bytes returned, timeout). The PDF serving endpoint `arxiv.org/pdf/{id}` uses a different server and is more reliable.

### 2. DOI Content Negotiation
```bash
curl -sL -H "Accept: application/pdf" "https://doi.org/10.xxxx"
```
⚠️ **Known limitation**: Most publishers (including arXiv DOI redirects like 10.48550/arXiv...) return an HTML landing page, NOT a PDF. This path has low success rate for automated download. Use only when the paper is verified open-access from a cooperative publisher (BMC/Springer, Frontiers, Nature Communications). Blocked by: BMJ, Elsevier, Wiley, Taylor & Francis.

### 3. PubMed Central OA API (EFetch) ⭐ MOST RELIABLE
When a paper has a PMCID, this is the most reliable way to get full text. BMJ papers claim OA but block crawlers — PMC bypasses this.

```python
# Step 1: Find PMID and PMCID from DOI
import urllib.request, json
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}&retmode=json"
resp = urllib.request.urlopen(url)
data = json.loads(resp.read())
pmid = data['esearchresult']['idlist'][0]

url2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
resp2 = urllib.request.urlopen(url2)
data2 = json.loads(resp2.read())
# Find PMCID in articleids list
uid = [k for k in data2['result'].keys() if k != 'uids'][0]
for a in data2['result'][uid]['articleids']:
    if a['idtype'] == 'pmc':
        pmcid = a['value']  # e.g., "PMC11184186"

# Step 2: Download full text XML
pmc_num = pmcid.replace('PMC', '')
url3 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_num}&retmode=xml"
resp3 = urllib.request.urlopen(url3)
xml = resp3.read().decode('utf-8')

# Step 3: Strip XML tags to plain text
import re
text = re.sub(r'<[^>]+>', ' ', xml)
text = re.sub(r'\s+', ' ', text).strip()
```

### 4. Unpaywall API
```bash
curl -s "https://api.unpaywall.org/v2/{doi}?email=your@email.com"
```
Returns OA status and best_oa_location.url_for_pdf. Use to discover hidden OA URLs, but many still hit anti-bot when fetched.

### 5. Sci-Hub Mirrors (last resort, user-approved)
Try mirrors in order: `sci-hub.se` → `sci-hub.ru` → `sci-hub.st` → `sci-hub.ee`
```bash
for mirror in "sci-hub.se" "sci-hub.ru" "sci-hub.st"; do
    curl -sL -m 10 "https://${mirror}/${doi}" -o output.html
    pdf_url=$(grep -oP 'https?://[^"]+\.pdf[^"]*' output.html | head -1)
    if [ -n "$pdf_url" ]; then
        curl -sL "$pdf_url" -o paper.pdf
        break
    fi
done
```
Note: Sci-Hub mirrors often redirect back to publisher URLs that are still blocked. Only effective when Sci-Hub hosts a local copy.

### 6. arXiv (for CS/ML preprints)
```bash
curl -sL "https://arxiv.org/pdf/{arxiv_id}.pdf" -o paper.pdf
```

### 7. CORE API
```bash
curl -s "https://api.core.ac.uk/v3/discover?q=doi:{doi}&limit=1"
```
Rarely returns results. Last resort.

## Publisher Compatibility Matrix

| Publisher | Direct URL | DOI Negotiation | PMC API | Unpaywall | Sci-Hub | Best Path |
|-----------|-----------|----------------|---------|-----------|---------|-----------|
| **BMJ** | ❌ Blocked | ❌ Blocked | ✅ **Works** | Finds OA URL (blocked) | ❌ Redirects to blocked BMJ | **PMC API** |
| **MDPI** | ❌ 403 | — | ✅ **Works** | Finds OA URL (blocked) | ❌ | **PMC API** |
| **Elsevier** | Depends | ❌ Blocked | ✅ **Works** if in PMC | — | Sometimes | **PMC API** |
| **Springer/BMC** | ✅ **Works** | — | ✅ Works | — | — | **Direct URL** |
| **Frontiers** | ✅ **Works** | — | ✅ Works | — | — | **Direct URL** |
| **Wiley/BJET** | ❌ Blocked | ❌ Blocked | ✅ **Works** | — | — | **PMC API** |
| **IEEE Access** | ✅ Works | — | ✅ Works | — | — | **Either** |
| **SAGE** | ❌ Blocked | — | ✅ **Works** | — | — | **PMC API** |
| **Taylor & Francis** | ❌ Blocked | — | ❌ Not in PMC | — | — | Abstract only |
| **Lancet** | ❌ Blocked | ❌ Blocked | ❌ Not in PMC | Finds OA URL (blocked) | — | Abstract only |
| **Nature Portfolio** | ✅ **Works** (Communications titles) | — | ✅ Works | — | — | **Direct URL** |

## When Full Text is Unavailable

If all 7 pathways fail (typically because the paper is not in PMC and the publisher blocks crawlers):
1. Document the block: `# [Paper Title] - Paywalled\n# Publisher blocks automated download. PubMed abstract as fallback.\n`
2. Upload PubMed abstract as fallback to NotebookLM
3. Note the DOI and PMCID status for future retry
