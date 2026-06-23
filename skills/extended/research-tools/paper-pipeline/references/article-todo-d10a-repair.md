# article_todo Workspace D10a Repair Methodology

> Derived from Paper Repair Cycle 2026-06-22. The article_todo workspace (`~/桌面/article_todo/`) contains actively developed papers that are NOT in the main pipeline scan. They need separate D10a checking.

## Quick Scan Script

```python
import re, glob, os

basedir = os.path.expanduser("~/桌面/article_todo")

for paper_dir in sorted(os.listdir(basedir)):
    full = os.path.join(basedir, paper_dir)
    if not os.path.isdir(full):
        continue
    
    # Find best tex: prefer files with \begin{document} and actual cite keys
    tex_files = glob.glob(os.path.join(full, "**", "*.tex"), recursive=True)
    if not tex_files:
        print(f"[NO_TEX] {paper_dir}")
        continue
    
    # Score tex files: prefer those with \begin{document} and most \cite{} calls
    best_tex = None
    best_score = -1
    for tf in tex_files:
        with open(tf) as f:
            content = f.read()
        has_doc = '\\begin{document}' in content
        cite_count = len(re.findall(r'\\(?:cite|citep|citet|nocite)', content))
        score = cite_count + (100 if has_doc else 0)
        if score > best_score:
            best_score = score
            best_tex = tf
            best_content = content
    
    # Extract cites (filter comments)
    cites = set()
    for line in best_content.split('\n'):
        stripped = line.lstrip()
        if stripped.startswith('%'):
            continue
        for m in re.finditer(r'\\(?:cite|citep|citet|citeauthor|citeyear|fullcite|nocite)(?:\[[^\]]*\])?\{([^}]+)\}', line):
            for k in m.group(1).split(','):
                k = k.strip()
                if k and not k.startswith('<'):
                    cites.add(k)
    
    # Check .bbl (most article_todo papers use external bib → compiled .bbl)
    bbl_files = glob.glob(os.path.join(full, "**", "*.bbl"), recursive=True)
    bbl_keys = set()
    if bbl_files:
        with open(bbl_files[0]) as f:
            for m in re.finditer(r'\\bibitem\{([^}]+)\}', f.read()):
                bbl_keys.add(m.group(1).strip())
    
    total = len(cites)
    matched = cites & bbl_keys
    d10a = round(100 * len(matched) / total, 1) if total > 0 else 100.0
    orphans = cites - bbl_keys
    
    status = "OK" if d10a >= 95 else "FIX"
    print(f"[{status}] {paper_dir[:60]:60s} D10a={d10a:5.1f}%  cites={total:>3}  orphans={len(orphans)}")
```

## Top D10a Issues in article_todo (by frequency)

### 1. Stale .bbl from Older Tex Revision (MOST COMMON)

**Symptom**: D10a < 95% even though all orphan keys exist in the .bib file. The .bbl filename doesn't match the tex filename.

**Example**: Tex is `revision20241118v3.tex` but bbl is `revision20241117.bbl`. The old bbl predates newer citations added to the tex.

**Fix**:
```bash
cd "<paper_dir>"
rm -f *.bbl *.blg *.aux
pdflatex -interaction=nonstopmode <tex_file>.tex
bibtex <tex_file>
pdflatex -interaction=nonstopmode <tex_file>.tex
pdflatex -interaction=nonstopmode <tex_file>.tex
# Verify: grep -c "Warning: Citation" <tex_file>.log should be 0
```

### 2. Template .tex File Selected (False Positive)

**Symptom**: D10a=0% with placeholder cites like R1/R2/R3 or `<label>`. Real manuscript (e.g., `articlev2.tex`) exists but scan picked up `Sage_LaTeX_Guidelines.tex` or similar template.

**Fix**: Select the tex with most `\cite{}` calls and `\begin{document}`. Rerun scan with correct tex.

### 3. Missing Bib Entries (Rare in article_todo)

**Symptom**: 1-2 orphans remaining after recompilation. Keys NOT in .bib file.

**Fix**: Search Crossref for the missing reference. Add bib entry. Recompile.

**Example from 2026-06-22**:
- `matsumoto2000algorithm` → DOI: 10.1109/AFGR.2000.840680
- `jain201650` → DOI: 10.1016/j.patrec.2015.12.013

### 4. LaTeX Template Comment Artifacts

**Symptom**: `lamport94` appearing as orphan. Found only in comment lines like `%% Example citation, See \cite{lamport94}.`

**Fix**: Filter comments (lines starting with `%`) before extracting cites. This is a scan script issue, not a paper issue.

## article_todo Paper Inventory (as of 2026-06-22)

| Paper | Core Dir | Status | D10a |
|:------|:--------:|:-------|:----:|
| 3D Eyeball Model-Constrained Iris Segmentation | #1 | Active | 100% (repaired) |
| A Dual-Ellipse Fitting Method | #1 | Mature | 100% |
| A Precise 3D Geometric Transform Method | #1 | Active | 100% (repaired) |
| Correcting Off-Axis Iris Normalization | #1 | Mature | 95% |
| Dual-Ellipse Modeling | #1 | Mature | 95% |
| High-Accuracy Iris Segmentation YOLOv8 | #1 | Mature | 96.4% |
| Three-Dimensional Reconstruction SCC | #3 | Active | 100% |
| Individualized BPPV Repositioning | #4 | Not started | N/A |
| Posterior Canal BPPV Repositioning | #4 | Not started | N/A |
| SCC Spiral Parameters PD Biomarker | #3 | Not started | N/A |
