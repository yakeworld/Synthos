# Article Todo Workspace — D10a Check Methodology

## Purpose

Targeted D10a citation health check for papers in `~/桌面/article_todo/` — the writing workspace containing mature core-direction manuscripts. These papers are NOT tracked in the main pipeline (`/media/yakeworld/sda2/Synthos/outputs/papers/`) and need a separate scan.

## When to Use

- Paper-repair cron job (after main pipeline D10a scan)
- Before article_todo pipeline onboarding
- Quality gate assessment of writing workspace papers

## Prerequisites

- Python 3.x
- Access to `~/桌面/article_todo/`

## Step-by-Step Methodology

### Step 1: Discover Valid TeX Files

The workspace contains multiple tex files per paper — drafts, templates, revisions. Find the correct one:

```python
import re
from pathlib import Path

article_todo = Path.home() / "桌面" / "article_todo"

for paper_dir in sorted(article_todo.iterdir()):
    if not paper_dir.is_dir():
        continue
    
    real_texes = []
    for t in sorted(list(paper_dir.glob("*.tex")) + list(paper_dir.glob("*/*.tex"))):
        try:
            with open(t) as f:
                head = f.read(10000)
        except:
            continue
        if '\\begin{document}' not in head:
            continue
        cites = len(re.findall(r'\\cite[sp]?\{', head))
        loc = str(t.parent.name) if t.parent != paper_dir else 'root'
        real_texes.append((t, t.stat().st_size, cites, loc))
```

### Step 2: Select the Correct TeX

Selection rules (in priority order):

1. **Skip templates**: exclude tex with `template` or `Sage_` in filename
2. **Skip figure-only**: exclude tex with 0 `\cite{}` commands but `\begin{figure}` present
3. **Prefer latest revision**: `revision20241118v4.tex` over `revision20241118v1.tex`
4. **Prefer root-level** over subdirectory copies when identical
5. **For elsarticle papers**: `elsarticle-template-num.tex` IS the manuscript (elsarticle class convention — not actually a template despite filename)

**Pitfall**: `Sage_LaTeX_Guidelines.tex` is a real template with placeholder cites (R1/R2/R3). Never select it. Look for `articlev1.tex`, `articlev2.tex`, or `paper.tex` in sibling directories.

### Step 3: Find Matching BBL

```python
# Priority 1: same stem as tex
bbl = paper_dir / (main_tex.stem + '.bbl')
# Priority 2: same directory, any .bbl
if not bbl.exists():
    bbls = list(main_tex.parent.glob("*.bbl"))
    # Prefer bbl with same basename stem (e.g., articlev2.bbl for articlev2.tex)
    bbl = bbls[0] if bbls else None
```

**Pitfall**: `articlev1.tex` may match `articlev2.bbl` (alphabetically first .bbl found). Always pair same-version tex+bbl. The bbl is from a different revision → stale → wrong bibitems.

### Step 4: Extract and Compare

```python
cite_re = re.compile(r'\\cite[sp]?\{([^}]+)\}')
bibitem_re = re.compile(r'\\bibitem\{([^}]+)\}')

# Cites from tex
unique_cites = set()
for m in cite_re.finditer(tex_content):
    for key in m.group(1).split(','):
        unique_cites.add(key.strip())

# Bibitems: prefer .bbl if non-empty, otherwise tex thebibliography
if bbl and bbl.stat().st_size > 0:
    with open(bbl) as f:
        bibitem_keys = bibitem_re.findall(f.read())
else:
    bibitem_keys = bibitem_re.findall(tex_content)
```

### Step 5: Filter Template Artifacts

elsarticle class templates contain sample citations that are NOT real references:

| Artifact | Pattern | Action |
|:---------|:--------|:-------|
| `<label>` | Angle-bracket placeholder | **Filter out** — not a real cite |
| `lamport94` | LaTeX manual auto-reference | **Filter out** — JabRef/elsarticle artifact |
| `R1`, `R2`, `R3` | Sage template placeholders | **Filter out** — template only |

```python
TEMPLATE_ARTIFACTS = {'<label>', 'lamport94', 'R1', 'R2', 'R3'}
unique_cites = {k for k in unique_cites if k not in TEMPLATE_ARTIFACTS}
bibitem_keys = [k for k in bibitem_keys if k not in TEMPLATE_ARTIFACTS]
```

### Step 6: Report

```python
orphans = sorted(unique_cites - set(bibitem_keys))
zombies = sorted(set(bibitem_keys) - unique_cites)
d10a = (len(unique_cites) - len(orphans)) / len(unique_cites) * 100 if unique_cites else 100.0
```

## Common Patterns Found

### Pattern 1: Template Artifacts → False D10a < 95%

**Papers**: Precise 3D Geometric Transform, Correcting Off-Axis Iris Normalization, Dual-Ellipse Modeling, High-Accuracy Iris Seg YOLOv8

**Raw D10a**: 87.5%–93.1%  
**Real D10a**: 100% (after filtering `<label>` + `lamport94`)

All use `elsarticle-template-num.tex` as the manuscript file. The elsarticle class includes sample `\cite{<label>}` and `\cite{lamport94}` in the template that carry over into the aux/bbl.

### Pattern 2: Wrong Tex → Wrong BBL Pairing

**Paper**: Three-Dimensional Reconstruction SCC

**Raw D10a**: 93.8% (1 orphan: Bradshaw2010A, 15 zombies)  
**Real D10a**: 100% (articlev2.tex + articlev2.bbl = 30/30)

Scan picked `articlev1.tex` with `articlev2.bbl` (alphabetical mismatch). Correct pairing: `articlev2.tex` + `articlev2.bbl`.

### Pattern 3: Figure-Only TeX Masquerading

**Paper**: Dual-Ellipse Fitting Method

`new graph.tex` has `\begin{document}` and figure content but 0 `\cite{}` commands. The real manuscript is `投稿文件final/elsarticle-template-num.tex` (9 cites). The scan picks `new graph.tex` because it's root-level.

### Pattern 4: Empty BBL from Thebibliography Paper

Same as main pipeline trap: `.bbl` exists (0 bytes) from failed bibtex run. Paper uses inline `thebibliography`. Delete empty .bbl → D10a recovers to 100%.

## article_todo Inventory (as of 2026-06-22)

| # | Paper | Status | D10a | Has TeX |
|:-:|:------|:-------|:----:|:-------:|
| 1 | 3D Eyeball Model-Constrained Iris Seg | Submitted (PR, 2025-03-25) | 100% ✅ | ✅ |
| 2 | Dual-Ellipse Fitting Method | Mature | ~100% | ✅ |
| 3 | Precise 3D Geometric Transform | Mature | 100% ✅ | ✅ |
| 4 | Correcting Off-Axis Iris Normalization | Mature | 100% ✅ | ✅ |
| 5 | Dual-Ellipse Modeling Pupil Localization | Mature | 100% ✅ | ✅ |
| 6 | High-Accuracy Iris Seg YOLOv8 | Mature | ~100% | ✅ |
| 7 | Three-Dimensional Reconstruction SCC | Mature | 100% ✅ | ✅ |
| 8 | Individualized BPPV Repositioning | Not started | N/A | ❌ |
| 9 | Posterior Canal BPPV Virtual Simulation | Not started | N/A | ❌ |
| 10 | SCC Spiral Parameters PD Biomarker | Not started | N/A | ❌ |

6 mature papers with ≥100% real D10a. 3 not started. 1 submitted (awaiting review outcome).

## Pitfalls Specific to article_todo

1. **Multi-tex directories**: Every paper has 3-12 tex files (revisions, templates, figure-only). Always enumerate ALL before selecting.
2. **elsarticle-template-num.tex IS the manuscript**: Despite the filename, this is the actual paper for elsarticle-class submissions. Do not skip it as a template.
3. **投稿文件汇总/ subdirectory**: Contains duplicate tex + submission materials. The root-level tex is the authoritative version.
4. **latexnew/ subdirectory**: Contains older revision copies. Skip when root-level tex exists.
5. **Stale .bbl from different tex version**: `articlev1.tex` may get paired with `articlev2.bbl` if the scan doesn't check stem matching.
