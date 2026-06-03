# OA PDF Download — Biomedical Literature at Scale

> Techniques for downloading open-access (OA) PDFs when supplementing a grant proposal's reference list.
> Validated on: PD误吸风险预测项目 (温州市科技项目, 2026-05-13)

## When to Use

After literature gap analysis identifies replacement/ new references, before uploading to NotebookLM. The user expects **actual PDFs**, not just metadata or abstracts.

## Step 1: Check OA Status via S2 API

Use Semantic Scholar's `openAccessPdf` field to check which papers have freely available PDFs:

```python
url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf"
# If results['openAccessPdf'] has a 'url' key → OA available
# If None → paywalled, fall back to PubMed abstract
```

Rate limit: 1 req/sec. Add `time.sleep(1.0)` between calls.

## Step 2: Download by Publisher

### ✅ BioMedCentral / BMC Series (reliable)
Pattern: `https://bmcXXXX.biomedcentral.com/counter/pdf/10.1186/xxxxx`
- BMC Geriatr: `bmcgeriatr` + `/counter/pdf/`
- BMC Pulm Med: `bmcpulmmed` + `/counter/pdf/`
- J Orthop Surg Res: `josr-online` + `/counter/pdf/`
- Works with plain `curl` or `python urllib`, no special headers needed.

### ✅ Frontiers (reliable)
Pattern: `https://www.frontiersin.org/journals/{journal}/articles/10.3389/{doi}/pdf`
- Example: `fnut` (Frontiers in Nutrition), `fmed` (Frontiers in Medicine)
- Works with plain `curl` or `urllib`, no special headers.

### ❌ MDPI (blocked)
Pattern: `https://www.mdpi.com/{journal-id}/{volume}/{issue}/{article-id}/pdf`
- Returns HTTP 403 even with browser user-agent headers.
- MDPI uses aggressive anti-bot protection.
- **Workaround**: Only possible via browser (session cookies) or manual download.
- **Fallback**: Save the PubMed abstract page as a text source.

### ❌ Springer / Wiley / Elsevier (blocked)
- Most subscription journals return 403/404 to automated PDF requests.
- Exceptions: articles in PMC (PubMed Central) have direct PDF URLs.
- **Fallback**: Save PubMed abstract text only.

### ✅ PubMed Central (PMC)
Pattern: `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{id}/pdf/`
- Search PMC first: `db=pmc` in E-utilities
- All PMC articles are OA by definition.
- Use `efetch` to get the abstract as text fallback.

## Step 3: PubMed Abstract Fallback

For paywalled papers, save the PubMed abstract as a `.txt` file:

```python
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=text&rettype=abstract"
```

These text files are valid NotebookLM sources (Markdown format) and contain the full abstract + metadata.

## Step 4: Upload to NotebookLM

```bash
# Upload PDF
notebooklm source add /path/to/paper.pdf

# Upload abstract text
notebooklm source add /path/to/abstract.txt

# Rename with numbered prefix for organization
echo "y" | notebooklm source rename "<uuid_prefix>" "N_AuthorYear_Title.pdf"
```

## Publisher Success Rate (实测)

| Publisher | Success | Notes |
|-----------|---------|-------|
| Frontiers | ✅ Yes | Direct PDF URL works |
| BMC/BioMedCentral | ✅ Yes | `/counter/pdf/` works |
| MDPI | ❌ No | 403 blocked |
| Wiley | ❌ No | 403 blocked unless PMC |
| Springer | ❌ No | 403 blocked |
| Elsevier | ❌ No | 403 blocked |
| Hindawi | ❌ No | 403 blocked |
| PLOS ONE | ? | Not tested this session |
| PMC/NIH | ✅ Yes | OA by mandate |
| Cureus | ❌ No | 404 not found |

**Rule of thumb**: Expect ~30% of targeted papers to be downloadable as full PDF. The rest get PubMed abstracts. This is sufficient for NotebookLM source enrichment — the AI can still answer questions from abstracts.

## Pitfalls

- **File type confusion**: HTTP 403/404 pages are often saved as PDF-named files but are actually HTML. Always verify: `head -c 4 file.pdf` should show `%PDF`. If it shows `<!DO` or `<htm`, it's an error page — delete and fall back.
- **Rate limits**: S2 API (1 req/sec), PubMed (3 req/sec without API key), E-utilities (3 req/sec). Always add `time.sleep()` between calls.
- **Redirect chains**: Some DOI redirects go through multiple hops. Use `curl -sL` or `urllib` with redirect following enabled.
- **Context-length timeouts**: Downloading 8+ papers sequentially can take 2-3 minutes. The user should be informed of progress.

## Example: This Session's Download Result

Target: 18 papers → 6 real PDFs (33%) + 7 PubMed abstracts (39%) + 5 blocked (28%)
- Real PDFs: Frontiers (2), BMC series (4)
- Abstracts: Wiley (Chua), Springer (Nienstedt, Kim), various
- Blocked: MDPI (5 papers)
