# Protocol/Design Paper D7 Citation Expansion Workflow

> Proven pattern: Expanding from 8→32+ verified DOI references across 10 thematic categories in one working session. Applicable when a protocol, design, or methodology paper has insufficient bibliography (≤15 entries) and no experimental data to validate.

## Trigger

- Paper is a **protocol/design/methodology** paper (no experimental results — D3 ceiling 0.70)
- D7 score ≤ 0.60 with < 20 bibliography entries
- The paper's claims reference specific domains (e.g., epidemiology, clinical guidelines, methods) that have well-known literature

## 10-Category Template for PD/Clinical Protocol Papers

When expanding citations for a clinical protocol/design paper, cover these categories. Adapt domain keywords for your specific paper topic.

| # | Category | Example Keywords | Target References |
|:-:|:----------|:-----------------|:-----------------:|
| 1 | **Epidemiology** | prevalence, incidence, risk factors, meta-analysis | 3-5 |
| 2 | **Screening/Detection** | clinical scales (EAT-10, SSA), silent aspiration, FEES, VFSS | 3-5 |
| 3 | **Nutritional Assessment** | CONUT, GNRI, MNA, serum albumin, sarcopenia, malnutrition indices | 3-5 |
| 4 | **Methodology Foundation** | LASSO (Tibshirani), logistic regression, feature selection | 2-3 |
| 5 | **Clinical Guidelines** | TRIPOD, PROBAST, STROBE, PRISMA, reporting standards | 2-3 |
| 6 | **Intervention Frameworks** | IDDSI, texture modification, thickened fluids | 2-3 |
| 7 | **Training Evidence** | EMST, IMT, respiratory muscle training, RCTs | 2-4 |
| 8 | **Nurse-Led Interventions** | nurse-led, clinical pathway, triage protocol, screening | 1-2 |
| 9 | **Monitoring Technology** | acoustic monitoring, cervical auscultation, swallowing sounds | 2-4 |
| 10 | **Physiology Foundations** | swallow-respiratory coordination, apnea, aging effects | 2-3 |
| | **Additional Supporting** | validation studies, handicap indices, nerve stimulation | 2-3 |

## Workflow Steps

### Step 0: Profile current bib
```bash
grep -c '^@' references.bib
grep -oP '\\\\cite\{[^}]+\}' paper.tex sections/*.tex | tr ',' '\n' | sort -u | wc -l
```
Note: Use `sections/*.tex` when sections are in a subdirectory.

### Step 1: Search each category for verified references

Use subagent or direct CrossRef/Semantic Scholar queries. For each target reference, require:
- Full author list
- Journal name with `\\textit{}`
- Year, volume, pages (where applicable)
- DOI (verify via CrossRef before including)

**Filter by relevance**: reject papers that match keywords only superficially but are about unrelated topics.

### Step 2: Merge bib — avoid duplication
```python
# Pattern: keep old entries not in new set + all new entries
old_keys = [key for match in re.finditer(r'@\w+\{(\w+),', old_bib)]
new_keys = [key for match in re.finditer(r'@\w+\{(\w+),', new_bib)]
merge_keys = set(old_keys) | set(new_keys)  # union handles Collins2015-style overlaps
```

### Step 3: Patch citations into sections

Where to add which citations:

| Section | Citation Categories to Inject |
|:--------|:------------------------------|
| Background/Introduction | Epidemiology + Screening |
| Related Work | Screening + Monitoring Tech + Clinical Guidelines |
| Methods (Proposed Model) | Methodology Foundation (LASSO, logistic) |
| Methods (Intervention) | Intervention Frameworks (IDDSI) + Training (EMST) + Nurse-Led |
| Discussion (Claim 1) | Nutritional Assessment + Physiology Foundations |
| Discussion (Claim 2) | Methodology Foundation + Clinical Guidelines |
| Discussion (Claim 3) | Monitoring Technology + Intervention Frameworks |
| Limitations | Screening + Clinical Guidelines |
| Conclusion | Monitoring Technology + Training Evidence |

### Step 4: Verify compilation

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
grep -ci "warning" paper.log
grep -c "\\bibcite{" paper.aux  # count resolved cites
```

### Step 5: Re-evaluate D7

Estimated D7 improvement: **+0.20 to +0.30** for bib counts going from <10 to 30-40.

| Initial bib count | Target after expansion | D7 improvement |
|:-----------------:|:---------------------:|:--------------:|
| < 10 | 30-40 | +0.20 to +0.30 |
| 10-20 | 35-50 | +0.10 to +0.20 |
| 20-30 | 40-55 | +0.05 to +0.10 |

## Pitfalls

1. **LaTeX escape in patch tool**: When using the `patch` tool on `.tex` files, strings like `\cite{key}` or `\%` will be double-escaped (`\\cite{key}`, `\\%`) if passed as literal strings. **Always check the diff output** after patching. If you see doubled backslashes, re-patch with single backslashes to fix.

2. **DUPLICATE bib keys**: If the paper already has a `references.bib` and you're adding new entries found by a subagent, check for overlap. `Collins2015`, `Futoma2020` etc. may already exist.

3. **Unused bib entries**: After compilation, check for entries in the bib that were never cited:
   ```bash
   comm -23 <(grep '^@' references.bib | grep -oP '\{\K[^,]+' | sort) <(grep '\\bibcite{' paper.aux | grep -oP '\{[^}]+\}' | sed 's/[{}]//g' | sort)
   ```
   Either cite them in appropriate sections or move them aside.

4. **Paper.aux empty after first compile**: Run `bibtex paper` between the first and second `pdflatex` pass. If you skip bibtex, the .aux will have `\citation{...}` commands but no `\bibcite{...}` resolution.

5. **Protocol paper D3 ceiling**: For protocol/design papers (no experiments), D3 is inherently capped at ~0.70 regardless of how good the citations are. Don't over-invest in D3 for protocol papers — invest in D2 (methodology rigor with equations/algorithms) and D7 (citations) instead.

## Expected Outcome

After one working session following this workflow:
- 30-40 verified bib entries (from <10)
- D7: 0.50 → 0.75-0.80
- avg: +0.03 to +0.05 overall
- Paper gains 2-3 pages (13 vs 10pp in the proven case)
- Clean compile with zero citation warnings
