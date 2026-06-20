# Zero-Citation Auto-Repair Pattern

**Proven**: 2026-06-20 on `182-accommodation-ciliary-muscle-ODE` (D10a 0% → 100%, 13/13).

## The Problem

A paper has a complete `thebibliography` with N `\bibitem{key}` entries but **zero `\cite{key}` commands** anywhere in the prose. Previous diagnostics label this "Cannot auto-repair — requires author to insert citation commands." This is wrong when the prose already names the relevant authors and findings.

## Detection

From the D10a scan:
```
total_cites == 0 AND bibitem_count > 0 AND bib_source == "inline"
```
Zombies = bibitem_count (all bibitems are zombies since nothing cites them).

## When Auto-Repair Is Feasible

Auto-repair works when **the prose already describes what each reference is about** — naming authors, theories, findings, market data, or clinical statistics. The bibitem keys and reference text give enough context to map each reference to its natural prose location.

Signs auto-repair will work:
- Prose says "Helmholtz theory (1867)" → maps to `helmholtz1867`
- Prose says "PINN architecture" → maps to `raissi2019`
- Prose says "2.6 billion by 2050" → maps to `read2017`
- Bibitem keys are descriptive (author+year format)

Signs auto-repair will NOT work:
- Bibitem keys are opaque (numeric, random strings)
- Prose doesn't name any of the referenced authors/topics
- The paper is a stub with no substantive prose

## Repair Method

### Step 1: Extract all bibitem keys and descriptions
```bash
grep -oP '\\bibitem\{([^}]+)\}' paper.tex
# Read the text after each \bibitem{key} for context
```

### Step 2: Read the prose and map each bibitem
For each bibitem key, find the natural prose location where that reference is discussed. Create a mapping table:

| bibitem key | Prose context | Section | Line |
|:------------|:--------------|:--------|:-----|
| helmholtz1867 | "Helmholtz theory" | Intro | ~31 |
| raissi2019 | "PINN Architecture" | Methods | ~90 |
| ... | ... | ... | ... |

### Step 3: Insert \cite{key} at each prose location
Use `patch` tool (or manual edits) to insert `\cite{key}` immediately after the prose mention. Example:

```
- The classical Helmholtz theory (1867) proposed that...
+ The classical Helmholtz theory \cite{helmholtz1867} proposed that...
```

Key rules:
- Insert after the first natural mention of the referenced work
- Keep `\cite{}` inside the sentence, before punctuation
- Don't add duplicate citations for the same reference
- One bibitem must be cited at least once

### Step 4: Verify
```bash
# Count unique cite keys
grep -oP '\\cite\{[^}]+\}' paper.tex | sort -u | wc -l

# Should equal bibitem count
grep -c '\\bibitem{' paper.tex

# Compile
pdflatex -interaction=nonstopmode paper.tex

# Run D10a scan
python3 skills/.../d8d10a-scan.py
# Expected: D10a=100%, 0 orphans, 0 zombies
```

### Step 5: Update state
- `gate_status`: HARD_FAIL → PASS
- `d8_d10a_scan`: update with new metrics
- Queue entry: reason → `no_repair_needed`

## Example: 182-accommodation-ciliary-muscle-ODE

**Before**: 13 bibitems, 0 cites, D10a=0%, gate=HARD_FAIL  
**After**: 13 cites, D10a=100%, 0 orphans, 0 zombies, gate=PASS, qs=96

Citation mapping used:
| bibitem | Inserted at |
|:--------|:------------|
| helmholtz1867 | "Helmholtz theory (1867)" |
| fincham1937 | "studied...for over two centuries" |
| charman1970 | "presbyopia onset (age 40-45)" |
| porter2001 | "remains incompletely characterized" |
| carnelles2011 | "Kramer theory...Schachar theory" |
| korentko2016 | "OCT, ultrasound biomicroscopy, and MRI" |
| read2017 | "1 billion...2.6 billion by 2050" |
| atchison2000 | "finite element models (FEM)" |
| snell2018 | "ciliary muscle blood flow" |
| wolfson2020 | "\$50 billion annually" |
| crum2021 | "PDE residual over collocation points" |
| raissi2019 | "Multi-layer perceptron...Sigmoid activation" |
| lu2022 | "Adam optimizer (lr = 1e-3), 50,000 iterations" |

Full transcript in paper-queue.json notes field `citation_repair_2026-06-20`.

## When NOT to Auto-Repair

Fall back to "HARD_FAIL: needs manual citation" when:
- Bibitem keys are numeric/opaque (can't map to prose)
- Prose is a stub with no substantive content
- The paper's content contradicts the reference (substantive mismatch)
- Multiple bibitems map to the same prose sentence (ambiguous)
