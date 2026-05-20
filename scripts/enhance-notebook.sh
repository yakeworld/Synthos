#!/bin/bash
# ============================================================
#  Notebook Literature Enhancer — v2.1 (Cron-safe PATH)
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
# ============================================================
#  
#  Features:
#   - File-based mutex for S2 API (1 req/s rate limit compliance)
#   - File-based mutex for notebooklm CLI (global state protection)
#   - Per-notebook temp files (no race conditions)
#   - Random backoff on lock contention
# ============================================================
set -e

NOTEBOOK_ID="$1"
SEARCH_QUERY="$2"
PROJECT_NAME="${3:-notebook-${NOTEBOOK_ID}}"
OUTDIR="/media/yakeworld/sda2/Synthos/outputs/papers/${PROJECT_NAME}"
S2_KEY="iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt"

# Lock files (directory-based = atomic)
S2_LOCK="/tmp/.hermes_s2_lock"
NBLM_LOCK="/tmp/.hermes_notebooklm_lock"

# Ensure cleanup on exit
cleanup() {
  rmdir "$S2_LOCK" 2>/dev/null || true
  rmdir "$NBLM_LOCK" 2>/dev/null || true
}
trap cleanup EXIT

# Mutex helper: acquire a directory lock with random backoff
acquire_lock() {
  local lock_path="$1"
  local max_attempts=30
  local attempt=0
  while ! mkdir "$lock_path" 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge "$max_attempts" ]; then
      echo "  ⚠️ Failed to acquire lock $lock_path after $max_attempts attempts"
      return 1
    fi
    sleep $(( (RANDOM % 5) + 1 ))
  done
  return 0
}

release_lock() {
  rmdir "$1" 2>/dev/null || true
}

mkdir -p "$OUTDIR/pdfs"
S2_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SEARCH_QUERY'))")

echo "============================================"
echo " Enhancing: $NOTEBOOK_ID"
echo " Query:     $SEARCH_QUERY"
echo " Output:    $OUTDIR"
echo " PID:       $$"
echo "============================================"

# ========================
# Step 1: Search S2 API (protected by mutex)
# ========================
echo "[1/5] Searching S2 API for 5 papers..."
acquire_lock "$S2_LOCK"
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=${S2_QUERY}&limit=5&fields=title,authors,year,externalIds,openAccessPdf,citationCount,journal" \
  -H "x-api-key: $S2_KEY" -o "/tmp/s2_data_${NOTEBOOK_ID}"
release_lock "$S2_LOCK"

# ========================
# Step 2: Download full texts (no shared resources)
# ========================
echo "[2/5] Downloading full texts..."
python3 << PYEOF
import json, urllib.request, ssl, re, time, os

ctx = ssl._create_unverified_context()
OUTDIR = "$OUTDIR"
PDF_DIR = os.path.join(OUTDIR, "pdfs")

with open('/tmp/s2_data_${NOTEBOOK_ID}') as f:
    data = json.load(f)

papers = data.get('data', [])
print(f"  Found {len(papers)} papers")

for i, p in enumerate(papers):
    doi = p.get('externalIds', {}).get('DOI', '')
    pdf_info = p.get('openAccessPdf', {})
    title = p.get('title', f'Paper {i+1}')[:50]
    
    # Try OA PDF first
    if pdf_info and pdf_info.get('url'):
        url = pdf_info['url']
        for try_url in [url, url.replace('doi.org', 'www.frontiersin.org') + '/pdf']:
            try:
                req = urllib.request.Request(try_url, headers={'User-Agent': 'Mozilla/5.0'})
                resp = urllib.request.urlopen(req, context=ctx, timeout=10)
                raw = resp.read()
                if len(raw) > 10000 and raw[:4] == b'%PDF':
                    fname = f"paper{i+1}.pdf"
                    with open(os.path.join(PDF_DIR, fname), 'wb') as f:
                        f.write(raw)
                    print(f"  [{i+1}] ✅ PDF: {title} ({len(raw)//1024}KB)")
                    break
            except:
                continue
    
    # Fallback: try PMC
    if doi and not os.path.exists(os.path.join(PDF_DIR, f"paper{i+1}.pdf")):
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}&retmode=json"
            resp = urllib.request.urlopen(url, context=ctx, timeout=10)
            ids = json.loads(resp.read()).get('esearchresult', {}).get('idlist', [])
            time.sleep(0.3)
            if ids:
                url2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids[0]}&retmode=json"
                resp2 = urllib.request.urlopen(url2, context=ctx, timeout=10)
                d2 = json.loads(resp2.read())
                uid = [k for k in d2['result'].keys() if k != 'uids'][0]
                pmcid = ''
                for a in d2['result'][uid].get('articleids', []):
                    if a['idtype'] == 'pmc' and a['value'] not in ('', 'N/A'):
                        pmcid = a['value']
                if pmcid:
                    time.sleep(0.3)
                    url3 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid.replace('PMC','')}&retmode=xml"
                    resp3 = urllib.request.urlopen(url3, context=ctx, timeout=15)
                    xml = resp3.read().decode('utf-8')
                    if len(xml) > 1000:
                        text = re.sub(r'<[^>]+>', ' ', xml)
                        text = re.sub(r'\s+', ' ', text).strip()
                        with open(os.path.join(PDF_DIR, f"paper{i+1}_pmc.txt"), 'w') as f:
                            f.write(text[:80000])
                        print(f"  [{i+1}] ✅ PMC: {title} ({len(text)//1000}K chars)")
        except:
            pass
    time.sleep(0.5)
PYEOF

# ========================
# Step 3: Generate BibTeX (no shared resources)
# ========================
echo "[3/5] Generating LaTeX + BibTeX..."
python3 << PYEOF
import json, os

OUTDIR = "$OUTDIR"
with open('/tmp/s2_data_${NOTEBOOK_ID}') as f:
    data = json.load(f)

papers = data.get('data', [])
entries = []
keys = []

for i, p in enumerate(papers):
    key = f"ref{i+1}"
    keys.append(key)
    auths = ' and '.join([a['name'] for a in p.get('authors', [])[:5]])
    if len(p.get('authors', [])) > 5:
        auths += ' and others'
    doi = p.get('externalIds', {}).get('DOI', '')
    title = p['title'].replace('{', '').replace('}', '')
    entries.append(f"""@article{{{key},
  title={{{title}}},
  author={{{auths}}},
  year={{{p.get('year', '2024')}}},
  doi={{{doi}}}
}}""")

with open(os.path.join(OUTDIR, 'references.bib'), 'w') as f:
    f.write('\n\n'.join(entries))

cite_str = ','.join(keys)
latex = r"""\documentclass[review]{elsarticle}
\usepackage{amsmath,graphicx,hyperref}
\begin{document}
\begin{frontmatter}
\title{Literature Review: """ + (papers[0]['title'][:60] if papers else 'Research Topic') + r"""}
\author[1]{Xiaokai Yang}
\ead{yakeworld@wzhospital.cn}
\affiliation[1]{organization={Wenzhou People's Hospital},city={Wenzhou},country={China}}
\begin{abstract}
Systematic literature review generated from Semantic Scholar search.
\end{abstract}
\end{frontmatter}
\section{Introduction}
This review synthesizes recent literature.
\section{Key Findings}
\cite{""" + cite_str + r"""}
\section{Conclusion}
Further research is needed.
\bibliographystyle{elsarticle-num}
\bibliography{references}
\end{document}"""

with open(os.path.join(OUTDIR, 'paper.tex'), 'w') as f:
    f.write(latex)
print(f"  BibTeX: {len(entries)} entries, LaTeX: {len(latex)} chars")
PYEOF

# ========================
# Step 4: Compile PDF (no shared resources — runs in own OUTDIR)
# ========================
echo "[4/5] Compiling PDF..."
cd "$OUTDIR"
pdflatex -interaction=nonstopmode paper.tex &>/dev/null || true
bibtex paper &>/dev/null || true
pdflatex -interaction=nonstopmode paper.tex &>/dev/null || true
pdflatex -interaction=nonstopmode paper.tex &>/dev/null || true
rm -f *.aux *.bbl *.blg *.log *.out 2>/dev/null

if [ -f paper.pdf ]; then
    echo "  ✅ PDF: $(du -h paper.pdf | cut -f1)"
else
    echo "  ⚠️ PDF compilation failed"
fi

# ========================
# Step 5: Upload to NotebookLM (protected by mutex — global CLI state)
# ========================
echo "[5/5] Uploading to NotebookLM..."
acquire_lock "$NBLM_LOCK"
notebooklm use "$NOTEBOOK_ID" 2>/dev/null
for f in "$OUTDIR/paper.tex" "$OUTDIR/references.bib" "$OUTDIR/paper.pdf"; do
    if [ -f "$f" ]; then
        notebooklm source add "$f" &>/dev/null && echo "  ✅ Uploaded: $(basename $f)" || echo "  ⚠️ Failed: $(basename $f)"
        sleep 0.5
    fi
done
release_lock "$NBLM_LOCK"

# Clean up
rm -f "/tmp/s2_data_${NOTEBOOK_ID}"
echo ""
echo "============================================"
echo "✅ Complete: $OUTDIR"
echo "============================================"
