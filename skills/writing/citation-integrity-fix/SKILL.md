---
name: citation-integrity-fix
description: Fix papers where \begin{thebibliography} has entries but ZERO \cite{} commands in the text. A common LLM generation failure mode. Covers D10a detection, citation mapping, $ escaping, double-backslash traps.
version: 1.0.0
author: "Synthos"
license: MIT
tags: [latex, citation, bib, paper-quality, thebibliography]
---

# Citation Integrity Fix

> Fix papers where \begin{thebibliography} has entries but ZERO \cite{} commands in the text body. A common LLM generation failure mode.

## Detection

```python
import re
with open('paper.tex') as f: tex = f.read()
cites = re.findall(r'\\cite\{([^}]+)\}', tex)
bib = re.findall(r'\\bibitem\{([^}]+)\}', tex)
unique_keys = set()
for c in cites: unique_keys.update(c.split(','))
d10a = len(unique_keys) / len(bib) if bib else 0
print(f"Cites: {len(cites)}, Bib: {len(bib)}, D10a: {d10a:.0%}")
```

**Thresholds**:
| D10a | Status | Action |
|:-----|:-------|:-------|
| 0% | **Critical** — no citations at all | Add \cite{} commands |
| 0–50% | Poor — mostly uncited | Add \cite{} commands |
| 50–80% | Partial | Add missing citations |
| ≥80% | Healthy | No action needed |

## Fix Protocol

### Step 1: Identify claims that need citations
Map every claim in the text to a bib entry:
- Historical claims (author, date) → primary source
- Formula claims → original paper
- Clinical data (ranges, percentages) → source paper
- Model comparisons → baseline paper
- Mechanism descriptions → foundational paper

### Step 2: Add \cite{} commands
```latex
% Before:
Helmholtz mechanism, universally accepted.

% After:
Helmholtz mechanism~\cite{hirsch1937accommodation,navarro1985}, widely accepted.
```

### Step 3: Verify D10a ≥ 80%
```python
unused = set(bib) - unique_keys
assert len(unused) <= max(1, len(bib) * 0.2), f"{len(unused)} unused entries"
```

## Known Pitfalls

### Unescaped `$` in Text Mode
- **Symptom**: `Command \end{abstract} invalid in math mode`
- **Root cause**: `$15 billion` enters math mode, breaks abstract
- **Fix**: Escape currency: `\$15 billion`
- **Detect**: `grep -n '\$[0-9]' paper.tex`

### Double-Backslash from Patch Tool
- **Symptom**: `\\cite` appears in file (2 backslashes instead of 1)
- **Fix**: Python `content.replace('\\\\cite', '\\cite')`

### Zero-Count Cite Before Text Edit
When editing text in the bib section area, `\cite` commands added to the bibliography section itself (not the text body). Ensure `\cite{}` is in the main text, not in the `\begin{thebibliography}...\end{thebibliography}` block.

## Verification

1. `pdflatex paper.tex` → First pass (citation warnings expected)
2. `pdflatex paper.tex` → Second pass (no undefined references)
3. Check `paper.log` for `Error` → Should be 0
4. Check D10a → Should be ≥ 80%
5. Check unused entries → Should be ≤ 2

## Reference

- `paper-pipeline/references/thebibliography-citation-integrity.md` — Full protocol with case study