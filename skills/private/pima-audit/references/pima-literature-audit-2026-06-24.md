# PIMA Literature Audit — 2026-06-24

## Scope
23 papers analyzed from `Synthos/outputs/papers/pima-crispdm/06-references/`:
- 15 PIMA/BRFSS empirical papers
- 8 methodology papers (Kapoor2024, Collins2015, Chawla2002, etc.)

## Method
1. `pdftotext` batch extraction of all PDFs
2. Pattern-matched accuracy, F1, sensitivity, specificity, AUC, zero handling, SMOTE, CV
3. Traced preprocessing chain per paper to detect leakage
4. Classified severity: CRITICAL / MODERATE / MILD / NONE

## Output Files
- `/tmp/pima_literature_analysis_v2.csv` — CSV with all 23 papers, 14 columns
- `/tmp/pima_literature_analysis_v2.md` — 206-line Markdown report with full leakage analysis
- `/tmp/table1_latex.tex` — Publication-ready LaTeX longtable (70 lines)
- `/tmp/table1_preview.md` — Markdown preview of Table 1

## Key Findings

### Severity Distribution
| Severity | Count | Papers |
|:---------|:-----:|:-------|
| CRITICAL | 2 | Akbar2023 (99.6%), Talari2024 (99.14%) |
| MODERATE | 6 | Kalagotla2021 (78.2%), Hossain2025 (94.17%), Ali2025 (77.1%), Perdana2023 (77.86%), Shams2025 (89%), Naz2020 (98.07%) |
| MILD | 1 | Chinnababu2024 (83.11%) |
| NONE | 3 | Smith1988 (original), Pranto2020 (review), Kurniawan2026 (non-PIDD) |
| Methodological | 8 | Kapoor2024, Collins2015, Chawla2002, Stekhoven2012, Batista2004, Blagus2013, etc. |

### Zero-Value Handling
Only 2/15 (13%) correctly identified medical zeros (insulin=0, BP=0, skin thickness=0):
- ✅ Ali2025 (Sci. Rep.): `"Zero values in pregnancy, BP, skin, insulin, BMI are not biologically conceivable"`
- ✅ Hossain2025: `"Examine zero values; replace with mean of column"`
- ❌ All others: ignored or handled incorrectly

### Leakage Typology Found
1. **Global SMOTE** (Akbar2023, Talari2024): SMOTE applied to full dataset before any split
2. **Global Feature Selection** (Talari2024, Kalagotla2021, Perdana2023): info gain / correlation on full dataset
3. **Global Preprocessing** (many): imputation, scaling, outlier removal on full dataset before CV
4. **Global Up-sampling** (Shams2025): duplicate-based before train-test split
5. **Zero imputation before split** (Hossain2025, Ali2025): correct identification but wrong execution order

### Critical Leakage Chains

**Akbar2023**: PIDD → SMOTE(global) → K-Means(global) → Outlier removal(global) → 10-fold CV → 99.6% Acc
**Talari2024**: PIDD → SMOTE(global) → InfoGain(global) → Correlation(global) → 10-fold CV → 99.14% Acc
**Kalagotla2021**: PIDD → IQR(global) → Impute(global) → Scale(global) → FeatSel(global) → Stack CV → 78.2% Acc

### Papers NOT focused on PIDD (excluded from main table)
- Kurniawan2026: multi-disease physical examination records (110,300 patients), not PIDD
- Tong2024: COVID-19 mortality (OpenSAFELY), not diabetes
- Amri2025: ocean optics, not medical
- Lohani2025: manifold learning theory, not PIDD
- Dey2023: review paper, no experiments
- Pranto2020: review paper, no experiments

## Table 1 Format
```
{longtable}{p{2.2cm} p{2.5cm} p{1.3cm} c c c c c c c p{2.5cm} p{2.8cm} c}
Reference & Journal & Dataset & Acc(%) & F1 & Sens.(%) & Spec.(%) & AUC & Zero Handling & SMOTE & CV Method & Leakage Path & Severity
```
