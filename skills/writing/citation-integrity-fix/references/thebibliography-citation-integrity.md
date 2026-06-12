# thebibliography Citation Integrity Fix — Full Protocol

> Case study from 137-ciliary-body-ODE (2026-06-12). Complete before/after, detection, and verification.

## Problem Pattern

LLM-generated papers often include a `\begin{thebibliography}...\end{thebibliography}` environment with entries but **ZERO** `\cite{}` commands in the text body. The bibliography is structurally disconnected from the paper.

### Detection
```python
import re
with open('paper.tex') as f: tex = f.read()
cites = re.findall(r'\\cite\{([^}]+)\}', tex)
bib = re.findall(r'\\bibitem\{([^}]+)\}', tex)
unique_keys = set()
for c in cites: unique_keys.update(c.split(','))
print(f"Cites: {len(cites)}, Bib: {len(bib)}, D10a: {len(unique_keys)/len(bib)*100 if bib else 0:.0f}%")
```

### Fix Protocol

**Step 1**: Map text claims → bib entries:
- Historical claims (author names, dates) → primary source
- Formula claims → original paper
- Clinical data → source paper
- Model comparisons → baseline paper

**Step 2**: Add `\cite{}` commands throughout text:
```latex
% Before:
Helmholtz mechanism, universally accepted.

% After:
Helmholtz mechanism~\cite{hirsch1937accommodation,navarro1985}, widely accepted.
```

**Step 3**: Verify all entries covered:
```python
unused = set(bib) - unique_keys
print(f"Unused: {unused}")  # Should be empty or ≤2
```

## Case Study: 137-ciliary-body-ODE

### Before
- Cite commands: 0
- Bib entries: 15
- D10a: 0%
- Compilation: Clean but citations were not resolved
- Quality score: 45/100

### Fixes Applied
1. Added 10 `\cite{}` commands across all sections
2. All 15 entries now cited → D10a = 100%
3. Fixed `$15 billion` → `\$15 billion` in abstract (was breaking `\end{abstract}`)
4. Fixed `$15B+` → `\$15B+` in conclusion

### After
- Cite commands: 10
- Bib entries: 15
- D10a: 100%
- Compilation: Clean, 7 pages, 266KB PDF
- Quality score: 55/100 (+10)

## Known Pitfalls

### Unescaped `$` in Text Mode
**Symptom**: `LaTeX Error: Command \end{abstract} invalid in math mode`

**Root cause**: `$15 billion` enters math mode, breaking the abstract environment.

**Fix**: Escape currency notation:
```latex
\$15 billion  (correct)
$15 billion   (wrong — enters math mode)
```

**Detect**: `grep -n '\$[0-9]' paper.tex` — fix all matches.

### Double-Backslash from Patch Tool
**Symptom**: `\\cite` in file (should be single `\cite`).

**Detection**: Python `content.count('\\\\cite')` should be 0.

**Fix**: 
```bash
python3 -c "
p = 'paper.tex'
with open(p) as f: c = f.read()
c = c.replace('\\\\cite', '\\cite')
c = c.replace('\\\\textit', '\\textit')
with open(p, 'w') as f: f.write(c)
"
```

### Cite Commands in Bibliography Section
When editing text, `\cite{}` commands may accidentally be added to the bibliography section itself. Ensure `\cite{}` is in the main text (before `\begin{thebibliography}`), not inside the bibliography block.

## Verification Steps

1. `pdflatex paper.tex` → First pass (citation warnings expected)
2. `pdflatex paper.tex` → Second pass (no undefined references)
3. Check `paper.log` for `Error` → Should be 0
4. Check D10a → Should be ≥ 80%
5. Check unused entries → Should be ≤ 2