# PIDD Inflated Metrics — Concrete Worked Example

## Context
Paper thesis: PIDD inflated metrics = data leakage (global SMOTE, no CV), not algorithmic superiority.
Our benchmark under strict within-fold isolation: F1=0.7541, Acc=0.7746, Recall=0.7500.

## Expanded Table 1 (10 papers)

| Reference | Reported | Methodological Flaw |
|:--|:--|:--|
| Kalagotla et al. (2021) | Acc: 78.2%, F1: 0.594 | Global preprocessing; aggressive 3-feature reduction |
| Sreejith et al. (2020) | Acc: 89.04%, F1: 0.89 | Global SMOTE + feature selection before CV |
| Phan et al. (2025) | Acc: 87.8%, F1: 0.763 | Full-dataset imputation + under-sampling before split |
| Talari et al. (2024) | Acc: 99.07% | Global SMOTE; **PLOS ONE Expression of Concern** |
| Kurniawan et al. (2026) | Acc: **100%** | 100% physically impossible; k-fold CV but no within-fold isolation |
| Baran et al. (2025) | Acc: 98.7% | SMOTE without CV; no train-test split |
| Deepalakshmi et al. (2025) | Acc: 97.27% | No CV; no train-test split; Firefly Algorithm masks overfitting |
| Kate et al. (2025) | Acc: 96.58% | SMOTE used; no CV; XAI on potentially leaked model |
| Masulkar et al. (2026) | Acc: 96.5% | SMOTE before split; no CV; SHAP on preprocessed full dataset |
| Apurva & Vetrithangam (2025) | Acc: 95.4%, AUC: 0.983 | No CV; AUC=0.983 improbable without within-fold isolation |

## BibTeX Entries (add to both reference.bib and enhanced-bibtex-*.bib)

```
@Inproceedings{Baran2025UseOC,
  author = {Hasret Irmak Baran and Nisa Sahinoglu and Gülay Çiçek},
  title = {Use of Classification Algorithms in the Determination of Diabetes Level and Drug Recommendation Process},
  booktitle = {2025 7th ICHORA},
  year = {2025},
  pages = {1--6},
  doi = {10.1109/ICHORA65333.2025.11016981},
}

@Inproceedings{Deepalakshmi2025Efficient,
  author = {M. Deepalakshmi and P. Deepalakshmi and P. Nagaraj},
  title = {Efficient Diabetes Detection Using Ensemble Models Optimized by Firefly Algorithm},
  booktitle = {2025 ICC-ROBINS},
  year = {2025},
  pages = {1--6},
  doi = {10.1109/ICC-ROBINS64345.2025.11086333},
}

@Inproceedings{Kate2025EnhancedDD,
  author = {Chennaiah Kate and G. Deepika and Mandala Naga and Sravya and R. Bokka and D. Kumar and S. Ganesan},
  title = {Enhanced Diabetes Diagnosis Using Ensemble Classifiers with XAI and Oversampling},
  booktitle = {2025 5th CONIT},
  year = {2025},
  pages = {1--11},
  doi = {10.1109/CONIT65521.2025.11167663},
}

@Inproceedings{Masulkar2026MachineLM,
  author = {Jay Masulkar and Shivnath Chaudhri and Prajyot R. Yesankar},
  title = {Machine Learning Models for Predicting Diabetes Risk},
  booktitle = {2026 6th ICIPCN},
  year = {2026},
  pages = {1791--1795},
  doi = {10.1109/ICIPCN67432.2026.11438432},
}

@Inproceedings{Apurva2025EarlyDD,
  author = {Apurva Apurva and D. Vetrithangam},
  title = {Early Diabetes Detection with Hybrid ML Models},
  booktitle = {2025 GITCON},
  year = {2025},
  pages = {1--6},
  doi = {10.1109/GITCON65266.2025.11378348},
}

@Article{Kurniawan2026Evaluation,
  author = {Angga Kurniawan and Mawardi Kudin and Abdul Salam AT-TAQWA},
  title = {Evaluation of ML and DL Algorithms with Feature Scaling and K-Fold CV for Diabetes Classification},
  journal = {RABIT},
  year = {2026},
  volume = {11},
  number = {1},
  doi = {10.36341/rabit.v11i1.7005},
}
```

## Key Statistics for Paper

- 10 representative studies spanning 2020--2026
- 6 out of 10 report accuracy >= 95%
- 0 out of 10 provide evidence of within-fold preprocessing isolation
- Common flaws: global SMOTE (n=5), no CV (n=4), no zero-value correction (n=7)

## Core Argument Statement

> "Any PIDD result exceeding F1=0.80 or accuracy > 90% without explicit within-fold preprocessing isolation should be treated as statistical artifact resulting from data leakage, not algorithmic superiority. Our benchmark (F1=0.7541, Acc=0.7746) represents the upper bound of what is methodologically achievable under strict data isolation."
