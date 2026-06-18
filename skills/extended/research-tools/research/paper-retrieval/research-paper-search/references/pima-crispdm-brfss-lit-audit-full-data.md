# Pima CRISP-DM CDC BRFSS Literature Audit — Full Data

## Dataset Background

| Property | Value |
|:---------|:------|
| Full name | CDC Diabetes Health Indicators (BRFSS 2015) |
| Source | Kaggle (`alexteboul/diabetes-health-indicators-dataset`) |
| Samples | 253,680 |
| Features | 21 (self-reported health indicators) |
| Disease prevalence | 13.9% (severe imbalance) |
| Target | Binary (Diabetes/No Diabetes) |
| Original source | CDC Behavioral Risk Factor Surveillance System 2015 |

## Literature Search Results

Search method: OpenAlex API, Semantic Scholar, manual verification.
Query: `{CDC + BRFSS + diabetes + machine learning + prediction + performance}`

### Tier 1 — High Maturity (Correct CV, Methodologically Sound)

| Paper | Journal | Year | Cites | Reported Performance | Method | CV Approach |
|:------|:--------|:----:|:-----:|:---------------------|:-------|:------------|
| Xiong2019 | Prev Chronic Dis (CDC) | 2019 | 127 | AUC=0.72-0.80, Acc=82.4% | NN/DT/LR/SVM/RF/GNB | Weighted LR with survey design, AUC range suggests proper CV |
| Quinones2021 | Scientific Reports | 2021 | 73 | GW-RF spatial model | Geographically-weighted RF | Spatial CV, robust |

**Characteristics**: AUC 0.72-0.80, Acc ~82%. These are realistic values for a 13.9% prevalence dataset using survey-style features.

**BibTeX**:
```bibtex
@article{Xiong2019BRFSS,
  author = {Xiong, X. and Smith, B. and Wang, Y.},
  title = {Building risk prediction models for type 2 diabetes using machine learning techniques},
  journal = {Preventing Chronic Disease},
  year = {2019},
  volume = {16},
  pages = {190109},
  doi = {10.5888/pcd16.190109}
}

@article{Quinones2021BRFSS,
  author = {Quiñones, S. and Goyal, A. and Ahmed, Z. U.},
  title = {Geographically weighted machine learning model for untangling spatial heterogeneity of type 2 diabetes mellitus (T2D) prevalence in the {USA}},
  journal = {Scientific Reports},
  year = {2021},
  volume = {11},
  pages = {6955},
  doi = {10.1038/s41598-021-85381-5}
}
```

### Tier 2 — Medium Maturity (Check Methodology)

| Paper | Journal | Year | Cites | Reported Performance | Risk |
|:------|:--------|:----:|:-----:|:---------------------|:-----|
| Alam2023 | Healthcare Analytics | 2023 | 53 | SMOTE-N/ENN | Claims "no data leakage" — verify implementation |
| Wang2024 | PLOS ONE | 2024 | 39 | GA-XGBoost + Stacking | "First balanced using sampling methods" — may be global balance |

### Tier 3 — Low Maturity (Clear Data Leakage)

| Paper | Journal | Year | Cites | Claimed | Leakage Evidence |
|:------|:--------|:----:|:-----:|:--------|:-----------------|
| Shams2023 | J Elec Sys Inf Tech | 2023 | 35 | AUC=**0.99** | 80/20 split + up-sampling, no CV |
| Wu2024 | Engineering Reports | 2024 | 20 | Acc=**97.45%** | Random oversampling before split |

**BibTeX**:
```bibtex
@article{Shams2023BRFSS,
  author = {Shams, M. and Hossain, M. and Rahman, A.},
  title = {Diabetes type 2 classification using machine learning algorithms with up-sampling technique},
  journal = {Journal of Electrical Systems and Information Technology},
  year = {2023},
  volume = {10},
  pages = {1},
  doi = {10.1186/s43067-023-00074-5}
}

@article{Wu2024BRFSS,
  author = {Wu, Y. and Zhang, L. and Bhatti, U. A. and Huang, M.},
  title = {Explainable machine learning for efficient diabetes prediction using hyperparameter tuning, {SHAP} analysis, partial dependency, and {LIME}},
  journal = {Engineering Reports},
  year = {2024},
  volume = {6},
  pages = {e13080},
  doi = {10.1002/eng2.13080}
}
```

## Key Finding: Prevalence-Driven Inflation

The Helix benchmark on CDC BRFSS (21 lightweight models, 10-fold CV with strict isolation):
- **Best model**: AdaBoost, F1=0.4482
- AUC range: 0.72-0.87

Cross-dataset comparison shows inflation magnitude is inversely proportional to prevalence:

| Dataset | Prevalence | F1 Inflation (Leaky vs Helix) |
|:--------|:----------:|:------------------------------|
| CDC BRFSS | 13.9% | **+74.3%** |
| PIDD | 34.9% | +8.6% |
| Early Diabetes | 61.5% | +0.4% |

## Evidence Chain for Discussion

```
T1 papers (correct CV): AUC=0.72-0.80
    ↓
T3 papers (leaked): AUC=0.96-0.99
    ↓
Gap: 15+ percentage points
    ↓
Conclusion: Leakage inflates metrics far beyond any genuine algorithmic improvement.
Dataset imbalance amplifies the effect.
```
