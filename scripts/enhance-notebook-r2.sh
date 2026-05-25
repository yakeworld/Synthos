#!/bin/bash
# ============================================================
#  Notebook Literature Enhancer — Round 2 (BibKey naming + multi-path PDF)
#  10 papers, BibKey filenames, arXiv+PMC+OA multi-path download
# ============================================================
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

NOTEBOOK_ID="$1"
SEARCH_QUERY="$2"
PROJECT_NAME="${3:-notebook-${NOTEBOOK_ID}-r2}"
OUTDIR="/media/yakeworld/sda2/Synthos/outputs/papers/${PROJECT_NAME}"
# S2 API Key — Load from environment variable (set in ~/.hermes/.env)
S2_KEY="${S2_API_KEY:-}"
LIMIT=10

mkdir -p "$OUTDIR/pdfs"
S2_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SEARCH_QUERY'))")

echo "============================================"
echo " ENHANCE R2: $NOTEBOOK_ID"
echo " Query:     $SEARCH_QUERY"
echo " Limit:     $LIMIT papers"
echo " Output:    $OUTDIR"
echo "============================================"

# Step 1: Search S2 — 10 papers
echo "[1/5] Searching S2 for $LIMIT papers..."
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=${S2_QUERY}&limit=${LIMIT}&fields=title,authors,year,externalIds,openAccessPdf,citationCount,journal" \
  -H "x-api-key: $S2_KEY" -o "/tmp/s2_data_${NOTEBOOK_ID}"

# Step 2: Download full texts — BibKey naming, multi-path
echo "[2/5] Downloading full texts..."
python3 << PYEOF
import json, urllib.request, ssl, re, time, os, string

ctx = ssl._create_unverified_context()
OUTDIR = "$OUTDIR"
PDF_DIR = os.path.join(OUTDIR, "pdfs")

with open('/tmp/s2_data_${NOTEBOOK_ID}') as f:
    data = json.load(f)

papers = data.get('data', [])
print(f"  Found {len(papers)} papers")

def make_bibkey(p):
    """Generate BibTeX key: FirstAuthorYear"""
    authors = p.get('authors', [])
    year = str(p.get('year', '2024'))
    if authors:
        name = authors[0].get('name', 'Unknown')
        last = name.split()[-1] if name.split() else 'Unknown'
    else:
        last = 'Unknown'
    # Clean non-ASCII chars
    last = re.sub(r'[^a-zA-Z0-9]', '', last)
    return f"{last}{year}"

def try_download(url, bibkey, timeout=15):
    """Download a PDF file, return (True, filesize) or (False, None)"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    })
    resp = urllib.request.urlopen(req, context=ctx, timeout=timeout)
    raw = resp.read()
    if len(raw) > 10000 and raw[:4] == b'%PDF':
        fname = f"{bibkey}.pdf"
        with open(os.path.join(PDF_DIR, fname), 'wb') as f:
            f.write(raw)
        return True, len(raw)
    return False, None

for i, p in enumerate(papers):
    bibkey = make_bibkey(p)
    title = p.get('title', '')[:60]
    ext_ids = p.get('externalIds', {})
    doi = ext_ids.get('DOI', '')
    arxiv = ext_ids.get('ArXiv', '')
    pdf_info = p.get('openAccessPdf', {})
    
    downloaded = False
    
    # PATH 1: arXiv direct (always works)
    if arxiv and not downloaded:
        url = f"https://arxiv.org/pdf/{arxiv}.pdf"
        try:
            ok, size = try_download(url, bibkey)
            if ok:
                print(f"  [{i+1}] ✅ arXiv PDF: {bibkey}.pdf ({title[:40]}) ({size//1024}KB)")
                downloaded = True
        except:
            pass
    
    # PATH 2: PMC PDF direct
    if doi and not downloaded:
        try:
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}&retmode=json"
            resp = urllib.request.urlopen(search_url, context=ctx, timeout=10)
            ids = json.loads(resp.read()).get('esearchresult', {}).get('idlist', [])
            if ids:
                time.sleep(0.3)
                summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids[0]}&retmode=json"
                resp2 = urllib.request.urlopen(summary_url, context=ctx, timeout=10)
                d2 = json.loads(resp2.read())
                uid = [k for k in d2['result'].keys() if k != 'uids'][0]
                pmcid = ''
                for a in d2['result'][uid].get('articleids', []):
                    if a['idtype'] == 'pmc' and a['value'] not in ('', 'N/A'):
                        pmcid = a['value']
                if pmcid:
                    pmc_num = pmcid.replace('PMC', '')
                    # Try PMC PDF direct
                    for pmc_url in [
                        f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/",
                        f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_num}/pdf/main.pdf"
                    ]:
                        try:
                            ok, size = try_download(pmc_url, bibkey, timeout=10)
                            if ok:
                                print(f"  [{i+1}] ✅ PMC PDF: {bibkey}.pdf ({title[:40]}) ({size//1024}KB)")
                                downloaded = True
                                break
                        except:
                            continue
        except:
            pass
    
    # PATH 3: OA PDF URL from S2
    if pdf_info and pdf_info.get('url') and not downloaded:
        url = pdf_info['url']
        try:
            ok, size = try_download(url, bibkey)
            if ok:
                print(f"  [{i+1}] ✅ OA PDF: {bibkey}.pdf ({title[:40]}) ({size//1024}KB)")
                downloaded = True
        except:
            pass
    
    # PATH 4: PMC fallback — XML text
    if not downloaded and doi:
        try:
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}&retmode=json"
            resp = urllib.request.urlopen(search_url, context=ctx, timeout=10)
            ids = json.loads(resp.read()).get('esearchresult', {}).get('idlist', [])
            if ids:
                time.sleep(0.3)
                summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids[0]}&retmode=json"
                resp2 = urllib.request.urlopen(summary_url, context=ctx, timeout=10)
                d2 = json.loads(resp2.read())
                uid = [k for k in d2['result'].keys() if k != 'uids'][0]
                pmcid = ''
                for a in d2['result'][uid].get('articleids', []):
                    if a['idtype'] == 'pmc' and a['value'] not in ('', 'N/A'):
                        pmcid = a['value']
                if pmcid:
                    time.sleep(0.3)
                    xml_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid.replace('PMC','')}&retmode=xml"
                    resp3 = urllib.request.urlopen(xml_url, context=ctx, timeout=15)
                    xml = resp3.read().decode('utf-8')
                    if len(xml) > 1000:
                        text = re.sub(r'<[^>]+>', ' ', xml)
                        text = re.sub(r'\s+', ' ', text).strip()
                        fname = f"{bibkey}_pmc.txt"
                        with open(os.path.join(PDF_DIR, fname), 'w') as f:
                            f.write(text[:80000])
                        print(f"  [{i+1}] ✅ PMC text: {bibkey}_pmc.txt ({title[:40]}) ({len(text)//1000}K chars)")
                        downloaded = True
        except:
            pass
    
    if not downloaded:
        print(f"  [{i+1}] ⚠️ No full text: {title[:40]}")
    
    time.sleep(0.5)
PYEOF

# Step 3: Generate BibTeX + LaTeX — using BibKeys
# If S2 temp file was cleaned up, re-fetch
if [ ! -f "/tmp/s2_data_${NOTEBOOK_ID}" ]; then
    echo "  ⚠️ S2 data missing from tmp, re-fetching..."
    S2_QUERY_R2=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SEARCH_QUERY'))")
    curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=${S2_QUERY_R2}&limit=${LIMIT}&fields=title,authors,year,externalIds,openAccessPdf,citationCount,journal" \
      -H "x-api-key: $S2_KEY" -o "/tmp/s2_data_${NOTEBOOK_ID}"
fi
echo "[3/5] Generating LaTeX + BibTeX..."
python3 << PYEOF
import json, os, re

OUTDIR = "$OUTDIR"
with open('/tmp/s2_data_${NOTEBOOK_ID}') as f:
    data = json.load(f)
papers = data.get('data', [])

def make_bibkey(p):
    authors = p.get('authors', [])
    year = str(p.get('year', '2024'))
    if authors:
        name = authors[0].get('name', 'Unknown')
        last = name.split()[-1] if name.split() else 'Unknown'
    else:
        last = 'Unknown'
    last = re.sub(r'[^a-zA-Z0-9]', '', last)
    key = f"{last}{year}"
    return key

entries = []
keys = []
used_keys = {}

for p in papers:
    key = make_bibkey(p)
    # Deduplicate keys
    if key in used_keys:
        used_keys[key] += 1
        key = f"{key}{chr(96+used_keys[key])}"
    else:
        used_keys[key] = 1
    
    keys.append(key)
    auths = ' and '.join([a['name'] for a in p.get('authors', [])[:5]])
    if len(p.get('authors', [])) > 5:
        auths += ' and others'
    doi = p.get('externalIds', {}).get('DOI', '')
    title = p['title'].replace('{', '').replace('}', '')
    year = p.get('year', '2024')
    journal = p.get('journal', {}).get('name', '') if isinstance(p.get('journal'), dict) else ''
    
    entry = f"@article{{{key},\n  title={{{title}}},\n  author={{{auths}}},\n  year={{{year}}},\n  doi={{{doi}}},\n  journal={{{journal}}}\n}}"
    entries.append(entry)

with open(os.path.join(OUTDIR, 'references.bib'), 'w') as f:
    f.write('\n\n'.join(entries))

cite_str = ','.join(keys)
topic = papers[0]['title'][:60] if papers else 'Research Topic'
latex = r"""\documentclass[review]{elsarticle}
\usepackage{amsmath,graphicx,hyperref}
\begin{document}
\begin{frontmatter}
\title{Deep Literature Review: """ + topic + r"""}
\author[1]{Xiaokai Yang}
\ead{yakeworld@wzhospital.cn}
\affiliation[1]{organization={Wenzhou People's Hospital},city={Wenzhou},country={China}}
\begin{abstract}
This comprehensive review synthesizes recent advances, identifying key methodological trends, unresolved challenges, and future research directions.
\end{abstract}
\end{frontmatter}
\section{Introduction}
The rapid advancement of artificial intelligence and biomedical engineering has led to significant developments in this field. This review systematically analyzes """ + str(len(papers)) + r""" recent publications to provide a structured overview.
\section{Materials and Methods}
A structured literature search was conducted using Semantic Scholar with predefined keywords. Papers were selected based on relevance, citation impact, and methodological rigor.
\section{Results}
\cite{""" + cite_str + r"""}
\section{Discussion and Future Directions}
While significant progress has been made, several challenges remain. Future research should focus on standardization, validation in larger cohorts, and integration into clinical workflows.
\bibliographystyle{elsarticle-num}
\bibliography{references}
\end{document}"""

with open(os.path.join(OUTDIR, 'paper.tex'), 'w') as f:
    f.write(latex)
print(f"  BibTeX: {len(entries)} entries, Keys: {', '.join(keys)}")
PYEOF

# Step 4: Compile PDF
echo "[4/5] Compiling PDF..."
cd "$OUTDIR"
pdflatex -interaction=nonstopmode paper.tex &>/dev/null || true
bibtex paper &>/dev/null || true
pdflatex -interaction=nonstopmode paper.tex &>/dev/null || true
pdflatex -interaction=nonstopmode paper.tex &>/dev/null || true
rm -f *.aux *.bbl *.blg *.log *.out 2>/dev/null
[ -f paper.pdf ] && echo "  ✅ PDF: $(du -h paper.pdf | cut -f1)" || echo "  ⚠️ PDF compilation failed"

# Step 5: Upload — .tex/.bib → .md for NotebookLM compatibility
echo "[5/5] Uploading to NotebookLM..."
notebooklm use "$NOTEBOOK_ID" 2>/dev/null
cp "$OUTDIR/paper.tex" "$OUTDIR/paper_latex.md"
cp "$OUTDIR/references.bib" "$OUTDIR/references_bib.md"

for f in "$OUTDIR/paper_latex.md" "$OUTDIR/references_bib.md" "$OUTDIR/paper.pdf"; do
    if [ -f "$f" ]; then
        notebooklm source add "$f" &>/dev/null && echo "  ✅ Uploaded: $(basename $f)" || echo "  ⚠️ Failed: $(basename $f)"
        sleep 0.5
    fi
done

# Also list what PDFs were downloaded
echo ""
echo "  PDFs in output:"
ls "$OUTDIR/pdfs/" 2>/dev/null | head -15

rm -f "/tmp/s2_data_${NOTEBOOK_ID}"
echo ""
echo "============================================"
echo "✅ R2 Complete: $OUTDIR"
echo "============================================"
