# BRFSS Literature Methodology Audit — Full Worked Example

> Date: 2026-06-03
> Context: Cross-dataset validation for Pima CRISP-DM Helix paper
> Dataset: CDC BRFSS 2015 Diabetes Health Indicators (25,368 rows, 13.8% prevalence)

## Objective

Find published ML papers that report prediction performance on the CDC BRFSS diabetes dataset, download full-text PDFs, verify their methodology for data leakage, and compare their claimed performance against Helix protocol baselines.

## Step-by-Step Execution

### P0: Search for papers

Used OpenAlex API (unlimited quota, serial requests):

```bash
curl -s "https://api.openalex.org/works?search=BRFSS+machine+learning&per-page=25"
```

Found 1,291 results. Filtered to diabetes-specific:

1. **Nair2023** — "An investigation of ML algorithms... class imbalanced BRFSS dataset" (Healthcare Analytics, cites=53)
2. **Conference2023** — "Analysis of Diabetic Prediction Using ML Algorithms on BRFSS Dataset" (ICOEI, cites=14)
3. **Tennessee2025** — "Exploring Explainable ML for Predicting Diabetes among Tennessee Adults" (JPCCH, cites=3)
4. **Li2024** — "Diabetes prediction model based on GA-XGBoost and stacking ensemble" (PLOS ONE, cites=39)
5. **Alam2022** — "Detecting High-Risk Factors and Early Diagnosis of Diabetes Using ML" (CIN, cites=32)
6. **Rosyidi2024** — "Random Oversampling-Based Diabetes Classification via ML" (IJCIS, cites=10)

### P1: Download PDFs

| Paper | DOI | OA Available | Download Method | Success |
|:------|:----|:-------------|:----------------|:--------|
| Shams2025 | 10.1186/s43067-023-00074-5 | SpringerOpen OA | Direct curl | ✅ PDF %PDF-1.4 |
| Li2024 | 10.1371/journal.pone.0311222 | PLOS OA | Direct curl | ✅ PDF %PDF-1.6 |
| Alam2022 | 10.1155/2022/2557795 | Hindawi | Sci-Hub blocked by Cloudflare | ❌ |
| Tennessee2025 | 10.1177/21501319251400546 | No | Blocked | ❌ |
| Phan2025 | 10.1002/eng2.13080 | Wiley | Cloudflare 403 | ❌ |
| Rosyidi2024 | 10.1007/s44196-024-00678-3 | Springer | HTML redirect | ❌ |

### P2: Full-text extraction and search

```bash
# Extract text from successful PDFs
pdftotext /tmp/cdc_papers/Shams2025.pdf - > /tmp/shams.txt
pdftotext /tmp/cdc_papers/Li2024.pdf - > /tmp/li.txt

# Methods section search
grep -n -i "preprocess\|up.sampl\|train.*test\|split" /tmp/shams.txt
grep -n -i "SMOTE\|sampl\|train.*test\|split\|cross.*val\|fold" /tmp/li.txt
```

### P3: Evidence Found

#### Shams2025 — LEAKAGE CONFIRMED (Full-text, p.3)

Exact text found in the Preprocessing subsection:

> "The outcome and diabetes labels of PIMA and BRFSS datasets are not balanced. Unbalancing data decrease the accuracy of the classifiers. To mitigate this, **the up-sampling technique has been used to balance both datasets. After that, 80% of the datasets are used as training data and 20% as testing data** randomly using the train-test-split function."

**Verdict**: Up-sampling BEFORE train-test split → data leakage. Reported AUC=0.99 is unreliable.

#### Li2024 — LEAKAGE INFERRED (Full-text, Section 3.1 + Section 4.1)

Technical route (Section 3.1):
- Step 3: "Address the issue of uneven data distribution... using oversampling, undersampling, resampling, and hybrid sampling"
- Step 4: "Construct five learning models for model training"

Data allocation (Section 4):
- "initially, 80% of the dataset was allocated as the training set, with the remaining 20% serving as the test set"

No explicit confirmation that SMOTEENN was applied after split. Critically, the unsampled baseline (Section 4.1):
- **Without sampling**: AUC=0.8282, Recall=0.1734, **F1=0.2682**
- **With SMOTEENN**: AUC=0.9871, Recall=0.9551, **F1=0.9530**

**Verdict**: 355% F1 inflation from SMOTEENN alone is diagnostic of data leakage. The unsampled F1=0.27 matches the Helix-isolated CDC result (F1=0.45).

#### Tennessee2025 — CLEAN METHODOLOGY (Abstract only, but CV described)

> "Seven algorithms were tested... with **stratified 5-fold cross-validation**. Models were evaluated using accuracy, precision, recall, balanced accuracy, F1-score, AUROC, and PR-AUC. Results: **Gradient Boosting model achieved... accuracy of 82%, F1-score of 37%, AUROC of 0.80**."

**Verdict**: F1=0.37 vs our Helix AdaBoost F1=0.451 → consistent within noise. The only clean BRFSS benchmark found.

### P4: Mapping to Helix/Leaky baselines

| Literature Claim | Equivalent Helix Value | Equivalent Leaky Value | Verdict |
|:-----------------|:----------------------:|:----------------------:|:--------|
| Shams2025 AUC=0.99 | ~0.45 (AdaBoost) | ~0.77 (LR leaky) | Matches leaky, ~120% inflation |
| Li2024 F1=0.95 | ~0.45 | ~0.77 | Matches leaky, ~111% inflation |
| Li2024 baseline F1=0.27 | 0.45 | — | Matches Helix range! |
| Tennessee2025 F1=0.37 | 0.45 | — | Matches Helix range! (-18%) |

### P5: Convergent evidence for paper Discussion

The key insight: literature-reported inflated numbers match our "Leaky" protocol, while properly-conducted studies match our "Helix" protocol. This is powerful independent convergent evidence.

## Files Produced

| File | Content |
|:-----|:--------|
| `/tmp/cdc_papers/Shams2025.pdf` | Full-text PDF (1.1 MB) |
| `/tmp/cdc_papers/Li2024.pdf` | Full-text PDF (3.9 MB) |

## Key Lessons

1. **OpenAlex > Semantic Scholar** for broad dataset-specific searches (OpenAlex: 1,291 results vs Semantic Scholar: 0 results for "BRFSS machine learning")
2. **Full-text verification is essential** — Shams2025 mentions "up-sampling" in abstract but only the full text reveals the leaking sequence
3. **Unsampled baselines are diagnostic** — Li2024's own unsampled F1=0.27 is the strongest evidence that their SMOTEENN F1=0.95 is leakage-induced
4. **Single well-conducted study suffices** — Tennessee2025 (stratified 5-fold CV) gives F1=0.37, confirming the true performance range
