# Inline thebibliography Compilation Pattern (Paper 182, 2026-06-11)

## When to Use

Use `thebibliography` (inline) instead of `.bib` + `bibliography` command when:
- Papers use inline citation format (no BibTeX dependency)
- Simpler compilation chain needed (no bibtex step)
- 10-15 references that are well-known/standard (not requiring DOI verification)
- Cron/single-session assembly where .bib file management adds complexity

## Compilation Chain

```bash
# Clean
rm -f paper.aux paper.log paper.out paper.dvi

# Run LaTeX twice for cross-references
latex -interaction=nonstopmode paper.tex 2>&1
latex -interaction=nonstopmode paper.tex 2>&1

# Convert DVI to PDF
dvipdfm paper.dvi
```

**Do NOT run bibtex** — there is no .bib file. The `thebibliography` environment is self-contained in paper.tex.

## Pitfalls Discovered (Paper 182)

### 1. siunitx Incompatibility
**Error:** `Package siunitx Error: LaTeX kernel too old.`
**Cause:** MiKTeX 22.1 on this system has an older LaTeX kernel that siunitx rejects.
**Fix:** Remove `\usepackage{siunitx}`. Use plain LaTeX units (e.g., `s^{-1}`) or avoid siunitx formatting.

### 2. Abstract Math Mode
**Error:** `LaTeX Error: Command \end{abstract} invalid in math mode.`
**Cause:** `siunitx` loaded before document class conflicts with `\begin{abstract}` environment in math mode.
**Fix:** After removing siunitx, switch from `\begin{abstract}...\end{abstract}` to inline `{\\bf Abstract.} text...` with horizontal rules.

### 3. Equation References in thebibliography Section
**Error:** `LaTeX Warning: Reference 'eq:cdt' on page 2 undefined`
**Cause:** References to equations defined earlier in the document, but the first pass hasn't written .aux yet.
**Fix:** Run LaTeX twice. After second run, all cross-references resolve. Always verify with:
```bash
latex -interaction=nonstopmode paper.tex 2>&1 | grep -i "Error"
# Should be 0 errors after 2 runs
latex -interaction=nonstopmode paper.tex 2>&1 | grep -i "Error" | wc -l
```

### 4. dvipdfm SDict Warnings
**Symptom:** `dvipdfm:warning: Unknown token "SDict"` — hundreds of lines of noise.
**Cause:** hyperref generates PostScript dictionary code that dvipdfm doesn't fully understand.
**Impact:** NONE — these are warnings, not errors. PDF is valid and complete.
**Rule:** Never treat dvipdfm SDict warnings as compilation failures. The PDF file size and page count confirm validity.

### 5. Dollar Sign Escaping
**Error:** `\` before `$` causes `\$` to render as literal `$` in text mode but may cause issues.
**Fix:** In thebibliography section, financial amounts like `\$50B+` work fine. In math mode, use `$` normally.

## Verification Checklist

- [ ] No `LaTeX Error:` in log after 2 runs (only `Warning:` OK)
- [ ] `paper.dvi` created and ≥ 5 pages
- [ ] `dvipdfm` exits 0 (warnings OK, errors not)
- [ ] `paper.pdf` created and ≥ 5 pages
- [ ] PDF has References section at end
- [ ] All `\ref{}` resolve to correct numbers
- [ ] No `Undefined reference` after 2nd run

## When to Use .bib Instead

Switch to BibTeX-based compilation when:
- References need DOI/PMID cross-verification (quality-gate G3)
- More than ~15 references
- References come from external sources (not inline written)
- Quality gate requires verifiable DOI mapping
- Future sessions need reference auditing

For Paper 182, 13 references were standard, well-known papers — inline was appropriate. But for production submissions, BibTeX is preferred for traceability.
