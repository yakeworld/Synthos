# Batch Scan v2 — `\input{}` Subfile Trap Resolution (2026-06-04)

## Problem

When running `batch-robust-scan.py` across 57 papers in the Synthos outputs/papers/ directory, three classes of false positives emerged:

| False Positive Type | Papers Affected | Root Cause |
|:-------------------|:---------------|:-----------|
| **Subfile structure** (`\input{}`) | `pd-dysphagia-2026`, `vog-vestibular-review` | Main `.tex` has 0 `\cite{}` calls — all cites in `\input{}`-ed section files. Scanner reports D10a=0%, ZOMBIE |
| **`.tex` in `paper/` subdirectory** | `eye-tracking-4d` (paper/paper.tex), `vor-digital-twin` (paper/paper.tex) | Main `.tex` lives in `paper/` subdir, not root or 01-manuscript/ |
| **`fig_*.tex` selected as primary** | `iris-yolo` (fig_architecture.tex), `vor-digital-twin` (fig_VOR_pipeline.tex) | Small diagram-only `.tex` files (<5KB) picked instead of real paper |

## Resolution: `.bbl`/`.aux` Fallback

For compiled papers, `.aux` and `.bbl` files are more authoritative than `.tex` source:

```python
def get_cites_via_aux(paper_dir):
    """Get all \cite{} keys that bibtex actually saw, from .aux files."""
    for root, dirs, files in os.walk(paper_dir):
        for f in files:
            if f.endswith('.aux') and os.path.getsize(os.path.join(root, f)) > 50:
                with open(os.path.join(root, f)) as fh:
                    aux = fh.read()
                cites = set()
                for m in re.finditer(r'\\citation\{([^}]+)\}', aux):
                    for k in m.group(1).split(','):
                        cites.add(k.strip())
                if cites:
                    return cites
    return None

def get_bib_via_bbl(paper_dir):
    """Get \bibitem{} keys from .bbl files."""
    for root, dirs, files in os.walk(paper_dir):
        for f in files:
            if f.endswith('.bbl'):
                with open(os.path.join(root, f)) as fh:
                    bbl = fh.read()
                keys = set(re.findall(r'\\bibitem\{([^}]+)\}', bbl))
                if keys:
                    return keys
    return None
```

**Rule**: If `.tex` has 0 `\cite{}` calls but `.bbl`/`.aux` exist → use `.bbl`/`.aux` data. This transforms:
- `pd-dysphagia-2026`: ZOMBIE (D10a=0%) → CLEAN (D10a=100%, D8=39)
- `vog-vestibular-review`: ZOMBIE (D10a=0%) → CLEAN (D10a=100%, D8=33)

## Fix: `find_primary_tex()` Priority Rules

```python
def find_primary_tex(paper_dir):
    """Find actual primary .tex, skipping small fig_*.tex files."""
    candidates = []
    for f in os.listdir(paper_dir):
        full = os.path.join(paper_dir, f)
        if f.endswith('.tex') and os.path.isfile(full) and os.path.getsize(full) > 5000:
            candidates.append(full)
    for sub in ['01-manuscript', '02-submission', 'paper']:
        sp = os.path.join(paper_dir, sub)
        if os.path.isdir(sp):
            for f in os.listdir(sp):
                full = os.path.join(sp, f)
                if f.endswith('.tex') and os.path.isfile(full) and os.path.getsize(full) > 5000:
                    candidates.append(full)
    # Priority ordering
    priority = ['article_improved.tex', 'v4-paper.tex', 'paper-synthos.tex',
                'paper.tex', 'main.tex', 'article.tex', 'synthos-paper.tex']
    for p in priority:
        for c in candidates:
            if os.path.basename(c) == p:
                return c
    return sorted(candidates)[0] if candidates else None
```

**Key changes**:
1. Skip files with `os.path.getsize(full) <= 5000` (filters fig_*.tex)
2. Add `paper/` to subdirectory search
3. Add `paper-synthos.tex` to priority list

## Verification Results

After applying both fixes to the batch scanner, the 8 flagged "problems" reduced to 3 real ones:

| Paper | Before | After | Status |
|:------|:-------|:------|:-------|
| pd-dysphagia-2026 | ZOMBIE D10a=0% | CLEAN D8=39 D10a=100% | ✅ Fixed |
| vog-vestibular-review | ZOMBIE D10a=0% | CLEAN D8=33 D10a=100% | ✅ Fixed |
| iris-yolo | D8_LOW D10a=100% | CLEAN D8=30 D10a=100% | ✅ Fixed |
| vor-digital-twin | D8_LOW D10a=100% | CLEAN D8=30 D10a=100% | ✅ Fixed |
| eye-tracking-4d | D8_LOW D10a=100% | BENCHMARK D8=13 | 🟡 Real small-ref |
| crispdm-heart | D8_LOW D10a=100% | BENCHMARK D8=4 | 🟡 Real small-ref |
| portable-et-r2 | D8_LOW D10a=100% | BENCHMARK D8=10 | 🟡 Real small-ref |

## Updated Scanning Protocol

```
Step 1: find_primary_tex() — skip fig_*.tex, search paper/ subdir
  ↓
Step 2: If .tex has 0 \cite{} → check .bbl/.aux
  ├── .bbl/.aux exists → use them (compiled paper, \input{} structure)
  └── No .bbl/.aux → skeleton paper (mark as SKELETON)
  ↓
Step 3: Report
  ├── CLEAN: D8≥30, D10a=100%
  ├── BENCHMARK: D8<30, D10a=100% (small-reference paper — not a problem)
  └── ORPHAN_P0: orphans>0 (P0 must fix)
```
