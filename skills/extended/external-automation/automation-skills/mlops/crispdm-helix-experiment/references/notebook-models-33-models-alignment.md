# Notebook-to-Script Model Alignment: PIMA 33-Model Case Study

## Context
User requested "按照jupyter notebook流程和论文需要，认真完成每一个步骤的实验" — notebook Cell 17 uses `sklearn.all_estimators()` to generate model list dynamically, but `run_helix_benchmark.py` had a hardcoded model list that diverged.

## Discovery
- **Notebook Cell 17**: `sklearn.all_estimators(type_filter='classifier')` → 30 sklearn classifiers after filtering meta-wrappers and manual exclusions
- **helix_benchmark.py**: Had 27 models (25 sklearn + XGBoost + LightGBM + CatBoost), but LightGBM and CatBoost were NOT in the notebook
- **Discrepancy**: 4 models missing from helix (DummyClassifier, GaussianProcessClassifier, HistGradientBoostingClassifier, Perceptron), 2 models to remove (LightGBM, CatBoost)

## Resolution
When user said "pima数据库很小，可以把所有能想到的模型都跑一下", switched from strict notebook alignment to comprehensive coverage: 33 models (30 sklearn all_estimators + XGBoost + LightGBM + CatBoost).

## Key Findings (33 Models)
Top 5 by 10-Fold CV F1:
1. CatBoost — F1=0.7067 (Recall=0.7756)
2. GradientBoosting — F1=0.6857 (Recall=0.7464)
3. MLP — F1=0.6806 (Recall=0.7316)
4. LogisticRegression — F1=0.6759 (Recall=0.7165)
5. LDA — F1=0.6759 (Recall=0.7091)

PIMA only 768 samples → top 5 F1 difference only 0.03.

## Pitfalls Encountered
1. **sklearn.metrics.make_scorer** in 1.8+: `__import__('sklearn.metrics', fromlist=['make_scorer']).metrics.make_scorer(...)` — access pattern changed
2. **CatBoost iterations**: default 1000 is slow, set iterations=100 for 10-fold CV
3. **Notebook Cell 16**: GridSearchCV on RandomForestClassifier directly (not wrapped in pipeline) — param_grid keys are 'n_estimators' not 'clf__n_estimators'
4. **SHAP analysis failed**: System numpy 1.26.4 incompatible with shap's numpy≥2.0 requirement. System numexpr (Debian package) cannot be pip-uninstalled. Requires virtualenv.

## Verification
- `comprehensive_results.json` contains all 33 models with CV metrics
- `cv_results.csv` and `train_test_results.csv` contain tabular data
- All metrics verified against notebook's train_test_split logic
