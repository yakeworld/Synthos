# Batch Optimization + R2 Deep Enhancement Workflow

> Serial batch cycling for continuous NotebookLM literature enrichment.
> Use when user says "继续优化" or asks for recurring notebook improvement.

## Architecture

```
cron */10 * * * *
  └─ batch-runner.sh (serial: ONE at a time)
       └─ enhance-notebook.sh (R1: 5 papers)
       └─ enhance-notebook-r2.sh (R2: 10 papers, BibKey naming)
            ├─ QUEUE.md       ← State tracking
            └─ BATCH_LOG.md   ← Execution log
```

## Files

| Script | Path | Purpose |
|--------|------|---------|
| enhance-notebook.sh | `scripts/enhance-notebook.sh` | R1: 5 papers, paper1.pdf naming |
| enhance-notebook-r2.sh | `scripts/enhance-notebook-r2.sh` | R2: 10 papers, BibKey naming (Author2024.pdf) |
| batch-runner.sh | `scripts/batch-runner.sh` | Serial queue processor (reads QUEUE.md, runs 1 item, logs) |
| batch-runner-r2.sh | `scripts/batch-runner-r2.sh` | R2 version of batch-runner |

## Timeout Resume Procedure — Step 2 Partial Success

When `enhance-notebook-r2.sh` times out at Step 2 (download phase), the script leaves behind:
- `/tmp/s2_data_${NOTEBOOK_ID}` — S2 API JSON response (all 10 papers' metadata)
- `$OUTDIR/pdfs/` — partial set of downloaded PDFs/PMC texts
- `$OUTDIR/` — empty (no .tex, .bib, or .pdf yet since Steps 3-5 never ran)

**Key insight: LaTeX generation does NOT need full-text PDFs on disk.** It reads only the S2 JSON metadata (title, authors, year, DOI, journal). All 10 papers get BibTeX entries even if only 7 have downloadable full text. The 3 publisher-blocked papers still contribute citations.

### Resume Steps (run from the output dir)

```bash
OUTDIR="/media/yakeworld/sda2/Synthos/outputs/papers/<project-name>"
NID="<notebook-partial-id>"  # e.g. e9b9ee07
cd "$OUTDIR"
```

**Step 1: Verify prerequisites**
```bash
test -f /tmp/s2_data_${NID} && echo "S2 data: OK" || echo "S2 data: MISSING — must re-fetch"
ls pdfs/ 2>/dev/null | wc -l       # count partial downloads
```

**Step 2: Generate LaTeX + BibTeX** (reuses make_bibkey logic from the script)
```python
# Read S2 data, generate references.bib and paper.tex
# Use ALL 10 results — blocked papers still contribute citations
with open(f'/tmp/s2_data_{NID}') as f:
    papers = json.load(f).get('data', [])
# ... (identical make_bibkey + BibTeX entry generation as Steps 3-4)
# Write references.bib + paper.tex
```

**Step 3: Compile PDF** (4-pass: pdflatex → bibtex → pdflatex × 2)
```bash
cd "$OUTDIR"
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
# Verify: test -f paper.pdf && du -h paper.pdf
```

**Step 4: Upload to NotebookLM**
```bash
notebooklm use "$NID"
cp paper.tex paper_latex.md && cp references.bib references_bib.md
for f in paper_latex.md references_bib.md paper.pdf; do
    echo "y" | notebooklm source add "$f" && echo "✅ $f" || echo "⚠️ $f"
    sleep 1
done
```

**Step 5: Update QUEUE.md**
- Move completed row from Queue → Done section
- Increment progress counter (e.g. 9/12 → 10/12)
- Update BATCH_LOG.md

### Why Step 2 times out

The serial download loop tries up to 4 paths per paper, each with 10-15s timeouts. For a query where 3/10 papers are publisher-blocked (Elsevier, Springer, Taylor & Francis), worst-case latency:

```
7 good papers × ~15s  +  3 blocked × ~90s each  +  0.5s sleep × 10  ≈ 380s
```

This fits within 600s but barely — the blocking publishers each consume: arXiv timeout (5s) + esearch (10s) + esummary (10s) + PMC PDF × 2 attempts (20s) + efetch XML (15s) = ~60s per blocked paper. Real-world runs sometimes exceed 600s when NCBI rate-limiting adds latency.

### Mitigation for future runs

The R2 script has NO skip-already-downloaded logic — it re-downloads all 10 papers from scratch every time. Re-running times out at the same spot because the 3 blocked papers don't get any faster. The proper fix is to add a file-exists check before each paper's download loop:

```python
# Pseudo-fix for Step 2 (not yet applied):
bibkey = make_bibkey(p)
pdf_path = os.path.join(PDF_DIR, f"{bibkey}.pdf")
txt_path = os.path.join(PDF_DIR, f"{bibkey}_pmc.txt")
if os.path.exists(pdf_path) or os.path.exists(txt_path):
    print(f"  [{i+1}] ⏭️ Already downloaded: {bibkey}")
    continue
```

Until this fix is applied, use the resume procedure above when Step 2 times out.

## Known Bugs Fixed in R2 Scripts

### Bug 1: Doubled `papers/papers/` path (fixed 2026-05-15)
`batch-runner-r2.sh` had `PDF="$OUTDIR/papers/$PROJ/paper.pdf"` but `OUTDIR` already ends with `papers`. Resolved path was `.../papers/papers/<proj>/paper.pdf` — always reporting ❌ even on success.

**Fix**: Changed to `PDF="$OUTDIR/$PROJ/paper.pdf"`.

### Bug 2: S2 temp file cleared between Step 2→3 (fixed 2026-05-15)
`enhance-notebook-r2.sh` reads `/tmp/s2_data_${NOTEBOOK_ID}` in two separate Python heredocs. If the file is cleaned up between steps (by stale `rm -f` or trap handler), Step 3 fails with `FileNotFoundError`.

**Fix**: Added re-fetch guard before Step 3:
```bash
if [ ! -f "/tmp/s2_data_${NOTEBOOK_ID}" ]; then
    echo "  ⚠️ S2 data missing from tmp, re-fetching..."
    S2_QUERY_R2=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SEARCH_QUERY'))")
    curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=${S2_QUERY_R2}&limit=${LIMIT}&fields=title,authors,year,externalIds,openAccessPdf,citationCount,journal" \
      -H "x-api-key: $S2_KEY" -o "/tmp/s2_data_${NOTEBOOK_ID}"
fi
```

## Key Practices

### 1. PATH for cron
```bash
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
```
Always set explicit PATH in scripts — cron has minimal PATH.

### 2. `set +e` for batch runners
Use `set +e` (not `set -e`) in batch-runner scripts. Subprocesses (enhance-notebook.sh) return non-zero due to `notebooklm source add` warnings — never let the exit code kill the batch runner before logging writes.

### 3. BibKey file naming
```python
def make_bibkey(p):
    last = authors[0]['name'].split()[-1]
    last = re.sub(r'[^a-zA-Z0-9]', '', last)
    return f"{last}{year}"
```
Files: `Smith2024.pdf`, `Smith2024_pmc.txt` — never `paper1.pdf`.

### 4. PDF download priority (R2 multi-path)
```
arXiv direct → PMC PDF direct → OA URL from S2 → PMC XML text (last resort)
```
- arXiv: `https://arxiv.org/pdf/{arxiv_id}.pdf` (always works)
- PMC PDF: `https://www.ncbi.nlm.nih.gov/pmc/articles/{PMCID}/pdf/` (redirects to PDF)
- OA: publisher URLs are often blocked by anti-bot (301 to HTML)
- PMC text: `efetch.fcgi?db=pmc&id=X&retmode=xml` → strip XML tags → save as `_pmc.txt`

### 5. .tex/.bib upload workaround
NotebookLM rejects `.tex` and `.bib` extensions (400 error). Convert before upload:
```bash
cp paper.tex paper_latex.md
cp references.bib references_bib.md
notebooklm source add paper_latex.md
notebooklm source add references_bib.md
```

### 6. Temporary file isolation
Use `/tmp/s2_data_${NOTEBOOK_ID}` (per-process, no `.json` suffix) to avoid parallel-process race conditions when running multiple enhancers.

## R1 vs R2 Comparison

| Aspect | R1 (basic) | R2 (deep) |
|--------|-----------|-----------|
| Papers per notebook | 5 | 10 |
| Filename | `paper1.pdf` | `Author2024.pdf` |
| Citation key | `\cite{ref1}` | `\cite{Author2024}` |
| Download priority | OA → PMC text | arXiv → PMC PDF → OA → PMC text |
| Upload | .tex/.bib (400 error) | .tex→.md, .bib→.md (works) |
| LaTeX content | Skeleton | Real introduction + methods + discussion |
| S2 temp file guard | ❌ Missing | ✅ Auto-re-fetch if missing |
| PDF path check | ❌ `papers/papers/` | ✅ `$OUTDIR/$PROJ/` (fixed) |
