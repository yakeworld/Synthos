# Retracted Paper Investigation Protocol

## When to Use
During G5 citation audit, when a DOI returns 404, or during manual review when the user provides a DOI that appears retracted.

## Investigation Chain

### Step 1: Crossref API — Basic Status
```bash
curl -s "https://api.crossref.org/works/10.xxxx/xxxxx" | python3 -c "
import sys, json
d = json.load(sys.stdin)
m = d['message']
print('Is retracted:', bool(m.get('update-to', [])))
for upd in m.get('update-to', []):
    print(f'  Label: {upd.get(\"label\",\"?\")}  Type: {upd.get(\"type\",\"?\")}  Source: {upd.get(\"source\",\"?\")}')
"
```

Key signals:
- `update-to` array present with `type: "retraction"` → **RETRACTED**
- `source: "publisher"` → publisher-initiated (more serious than author-initiated)
### Step 2: OpenAlex — Retraction Flag

```bash
curl -s "https://api.openalex.org/works/doi:10.xxxx/xxxxx" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Is retracted:', d.get('is_retracted', False))
print('Cited by:', d.get('cited_by_count', 0))
"
```

### ⚠️ Per-Author Institution Check (Chinese Authors)

When the institution filter `authorships.institutions.id` returns 0 results but you know the author is from that institution:

**The problem**: OpenAlex has TWO levels of institution data:
- **Paper-level** (`institutions` field on the work object) — this is what `authorships.institutions.id:I4210152237` filters on
- **Per-author** (`authorships[].institutions` field on each authorship) — NOT indexed for filtering!

So `filter=authorships.institutions.id:I4210152237,is_retracted:true` misses many papers where the author is listed under Wenzhou People's Hospital at the authorship level but NOT at the paper level.

**Fix**: First get ALL works by the author's OpenAlex ID, then check institutions per-authorship in Python:
```python
for w in openalex_works:
    for a in w['authorships']:
        insts = [i['display_name'] for i in a.get('institutions',[])]
        if any('Wenzhou' in i and 'People' in i for i in insts) or \
           any('Wenzhou' in i and 'Hospital' in i for i in insts):
            # This paper IS from Wenzhou People's Hospital
```

Institution strings to match: `"Wenzhou City People's Hospital"`, `"Wenzhou Medical University"` (secondary affiliation).

### RetractionWatch Database

URL: https://retractiondatabase.org/

Most comprehensive retraction database. Manually maintained. Supports search by:
- Author name, institution, journal, DOI
- Retraction reason (fabrication, plagiarism, paper mill, duplicate publication, etc.)
- Publisher and retraction date range

NOTE: No free public API (as of 2026). Must be queried manually via web interface or browser automation.

### Retraction Reason Inference (when notice text is behind paywall)

| Signal | Likely Reason |
|--------|---------------|
| Published AND retracted same month | Image manipulation / flagged during production |
| Publisher-initiated | Data fabrication / ethical concerns |
| Author-initiated | Error found by authors |
| Microscopy/imaging paper | Image duplication most common |

### Step 3: PubPeer — Community Discussion (HTML data-comments extraction)

PubPeer pages embed comments in a `data-comments` HTML attribute (no JS rendering needed):

```bash
curl -s "https://pubpeer.com/publications/<PUBPEER_ID>" -A "Mozilla/5.0" | python3 -c "
import sys, re, json
html = sys.stdin.read()
match = re.search(r'data-comments=\"([^\"]+)\"', html)
if match:
    comments_json = match.group(1).replace('&quot;', '\"').replace('&lt;', '<').replace('&gt;', '>')
    comments = json.loads(comments_json)
    for c in comments:
        text = re.sub(r'<[^>]+>', ' ', c.get('html', ''))
        text = re.sub(r'\s+', ' ', text).strip()
        print(text)
"
```

This reveals the **full retraction notice text** even when the publisher's page is behind CAPTCHA.

### Step 4: PMC — Retraction Notice (if paper has PMC ID)

Check if the paper has a PMC ID via Crossref/PubMed, then fetch the notice:

```bash
# Get PMC ID
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=<DOI>"
# Fetch retraction text  
curl -s "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC<PMC_ID>/" -A "Mozilla/5.0" | python3
```

Hindawi retractions follow a standard template citing: (a) discrepancies in scope, (b) discrepancies in research description, (c) discrepancies between data availability and research described, (d) manipulated or compromised peer review.

### Step 5: Data Integrity Analysis (for QC reports)

When examining a retracted paper, look for these **fabrication/falsification patterns**:

| Pattern | Signal | Example (this session) |
|---------|--------|----------------------|
| **Duplicate table entries** | Same entity in mutually exclusive categories | miR-339-5p in both "upregulated" and "downregulated" lists |
| **Duplicate heatmap entries** | Same gene/miRNA appears >1× in same heatmap | 10 miRNAs duplicated in Figure 1 |
| **Copy-paste text errors** | Repeated numbers/phrases in consecutive sentences | "33 upregulated...33 downregulated" (should be 16/33) |
| **Conference abstracts as references** | JCO abstract #, Cancer Res abstract # | [7][14] cited as full papers |
| **Data "available on request"** | No GEO/ArrayExpress submission | Hindawi mass retraction pattern |
| **Missing multiple comparison correction** | 49 miRNAs tested with t-test only | Expected false positives = 49×0.05 ≈ 2.5 |

### Retracted OA Papers — PDF Access After Retraction

Even papers published under CC BY-NC become **CLOSED access** post-retraction:
- Semantic Scholar reports `openAccessPdf.status: "CLOSED"`
- ScienceDirect adds CAPTCHA
- No PMC deposit (Elsevier doesn't deposit to PMC for this journal)
- Sci-Hub cannot retrieve either (Elsevier block + low demand for 2024 paper)
- **Recommendation**: when the paper is retracted, the PDF is mostly irrelevant. The retraction notice + PubPeer comments provide more forensic value than the paper body.

### Case Studies

#### Case 1: 10.1016/j.biopha.2024.117117 (2026-06-25)
- SNP + diabetic zebrafish larvae, Biomedicine & Pharmacotherapy
- Published & retracted: August 2024 (same month)
- Retraction: **publisher** (Elsevier) initiated — author disputed
- 11 authors, 97 references, 6 citations before retraction
- **PubPeer revealed**: Elsevier Research Integrity team found inconsistent sample sizes, flawed statistical methods, and questionable figures (Fig 2A-2 vs 2C-2, Fig 3G, Fig 4G, Fig 5B, Fig 7B). Authors provided explanation but deemed unsatisfactory.
- **Key lesson**: Elsevier has an active post-publication image/data screening program

#### Case 2: 10.1155/2022/4085039 (2026-06-25)
- miRNA glioma profiling, BioMed Research International (Hindawi)
- Published: 2022-06, Retracted: 2024-03 (Hindawi mass retraction)
- Retraction: **publisher** initiated under systematic manipulation criteria
- **Built-in data integrity issues** (independent of retraction):
  - miR-339-5p in both up/down lists (Table 1)
  - 10+ duplicate miRNAs in heat map (Figure 1)
  - No multiple testing correction (49 miRNAs, unadjusted t-tests)
  - No GEO submission
  - 2/22 references are conference abstracts
- **Relation to user**: authors all from user's institution (Wenzhou People's Hospital)
- **Warning**: even "systematic manipulation" retractions (not individual misconduct) may still have genuine data quality problems

### Actions on Finding a Retracted Reference
1. **Mark citation as INVALID** — retracted papers must not be cited
2. **Search for replacement** via Semantic Scholar / PubMed
3. If no replacement exists, remove the citation
4. Update paper.tex and log in fix-log.md
