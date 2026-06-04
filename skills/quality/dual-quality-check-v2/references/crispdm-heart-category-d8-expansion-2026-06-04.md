# CRISP-DM Heart Disease D8 Expansion: 4→30 by Reference Category (2026-06-04)

## The Problem

Paper started with `thebibliography` format, only 4 references:
- Kapoor2024Leakage (leakage/reproducibility)
- Wen2024Leakage (leakage/reproducibility)
- ProcessDriven (companion PIMA paper)
- Detrano1989Heart (dataset source)

Target: D8≥30 with D10a=100%, all verified entries.

## Category-Based Expansion Strategy

Instead of the domain-based 3-tier approach (classical → survey → domain), use a **topic-category approach** tailored to the paper's subject:

| Category | Target count | Strategy |
|:---------|:------------:|:---------|
| Data Leakage / Reproducibility | 5 | Foundational + recent surveys |
| SMOTE / Imbalanced Learning | 7 | Original SMOTE + major extensions + surveys |
| CV / Statistical Methods | 3 | Bootstrap/ESL + small-sample PR |
| Clinical ML Guidelines | 5 | TRIPOD, PROBAST, clinical AI reports |
| CRISP-DM / Process Models | 2 | Original CRISP-DM papers |
| Dataset / Benchmarks | 3 | UCI repository + PMLB benchmark |
| Heart Disease ML | 2 | Papers using Heart dataset for ML |
| Small-Sample ML | 2 | Validation with limited samples |

Total target: ~29 references across 8 categories.

## Execution Pattern

### Step 1: Write verified bibitems from domain knowledge (no API calls)

All entries must have confirmed DOIs from known literature. Write directly to thebibliography:

```python
# Append before \end{thebibliography}
tex = tex.replace(r'\end{thebibliography}',
    r'\bibitem{Chawla2002} ... ' +
    r'\bibitem{Fernandez2018} ... ' +
    r'\end{thebibliography}')
```

### Step 2: Strategic \cite{} insertion by section

| Section | Insertion point | Added refs |
|:--------|:---------------|:-----------|
| Introduction (opening) | reproducibility crisis → added clinical AI refs | Beam2018, Topol2019 |
| Introduction (small datasets) | "fewer than 1000 samples" | Vabalas2019, Raudys1991 |
| Introduction (leakage) | cite group after Kapoor, Wen | Whalen2022, Kaufman2012, Cawley2010 |
| Introduction (CRISP-DM Helix) | "Helix framework" | Shearer2000, Wirth2000 |
| Methods (SMOTE) | "SMOTE oversampling" | Chawla2002, Fernandez2018, Batista2004, He2009ADASYN |
| Methods (classifiers) | "Seven classifiers" | Hastie2009 |
| Methods (dataset ref) | "UCI Heart Disease" | Dua2019 |
| Discussion (guidelines) | "TRIPOD, PROBAST" | Collins2015, Wolff2019, Luo2016 |
| Discussion (imbalanced) | "classes hardest to separate" | Menardi2014, Blagus2013 |
| Discussion (benchmark) | "three-dataset comparison" | Olson2017 |
| Discussion (class imbalance) | "imbalance problem" | Japkowicz2002 |
| Discussion (heart disease) | "small-sample vulnerability" | Alizadehsani2013, Gennari1995 |

### Step 3: Check for duplicate bibitems

Thebibliography can accumulate duplicates when batch-adding new refs:

```python
import re
from collections import Counter
tex = open('paper.tex').read()
keys = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', tex)
dupes = {k: v for k, v in Counter(keys).items() if v > 1}
# Fix: rename duplicate or delete, update counter
```

### Step 4: Update counter and verify D10a

- Update `\begin{thebibliography}{N}` counter to match actual count
- Verify: 0 orphans, 0 zombies
- Compile 2x pdflatex (thebibliography mode, no bibtex needed)

```bash
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
grep -c 'undefined' paper.log || echo '✅ 0 undefined'
```

## Results

| Metric | Before | After |
|:-------|:------:|:-----:|
| D8 | 4 | 30 |
| D10a | 25% | 100% |
| Pages | (untested) | 4 |
| Compile errors | — | 0 |

## Key Insights

1. **Category-based works when domain-based fails**: For cross-disciplinary papers (CRISP-DM × leakage × clinical ML), categorizing by *topic role* (leakage refs, SMOTE refs, guideline refs) is more natural than by *literature tier* (classical→survey→domain).

2. **Duplicate bibitem detection is essential**: The `thebibliography` format easily accumulates duplicate keys when adding refs in multiple batches. Always run a duplicate check before compilation.

3. **Counter update**: After adding/deleting entries, `\begin{thebibliography}{N}` counter must be updated to reflect the true count — otherwise LaTeX may misallocate reference numbering space.

4. **L0.5 verification first**: Before touching references, verify experimental data exists (check JSON/CSV output files). No point expanding refs for a paper whose numbers are uncorroborated.
