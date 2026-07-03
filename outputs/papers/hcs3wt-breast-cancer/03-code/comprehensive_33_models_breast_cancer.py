"""
HCS-3WT Breast Cancer: Comprehensive 33-Model Benchmark
=========================================================
Complete scan of all major classifier families on WDBC + Coimbra.
Helix strict methodology: fold-isolated imputation → scaling → SMOTE → training.
"""
import numpy as np
import pandas as pd
import json
import time
import sys
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.base import clone
from sklearn.metrics import (f1_score, accuracy_score, precision_score,
                             roc_auc_score, recall_score)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from sklearn.linear_model import (LogisticRegression, RidgeClassifier,
    SGDClassifier, Perceptron, PassiveAggressiveClassifier, RidgeClassifierCV,
    LogisticRegressionCV)
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import (RandomForestClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, AdaBoostClassifier, BaggingClassifier,
    HistGradientBoostingClassifier)
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.discriminant_analysis import (LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis)
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.semi_supervised import LabelPropagation, LabelSpreading

try:
    from xgboost import XGBClassifier; HAS_XGB = True
except ImportError: HAS_XGB = False
try:
    from lightgbm import LGBMClassifier; HAS_LGB = True
except ImportError: HAS_LGB = False
try:
    from catboost import CatBoostClassifier; HAS_CB = True
except ImportError: HAS_CB = False

RANDOM_STATE = 42
OUTPUT_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers/hcs3wt-breast-cancer/03-code"
RESULTS_FILE = f"{OUTPUT_DIR}/comprehensive_breast_results.json"


def build_model_list():
    """Build 33 model list matching Pima methodology."""
    m = {}
    # Ensemble
    m['AdaBoostClassifier'] = lambda: AdaBoostClassifier(random_state=RANDOM_STATE)
    m['BaggingClassifier'] = lambda: BaggingClassifier(random_state=RANDOM_STATE, n_jobs=-1)
    m['ExtraTreesClassifier'] = lambda: ExtraTreesClassifier(n_estimators=300, max_depth=12, min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=-1)
    m['GradientBoostingClassifier'] = lambda: GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=RANDOM_STATE)
    m['HistGradientBoostingClassifier'] = lambda: HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=RANDOM_STATE)
    m['RandomForestClassifier'] = lambda: RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=-1)
    # Linear
    m['LogisticRegression'] = lambda: LogisticRegression(random_state=RANDOM_STATE, max_iter=5000, C=1.0)
    m['LogisticRegressionCV'] = lambda: LogisticRegressionCV(random_state=RANDOM_STATE, n_jobs=-1, cv=5)
    m['RidgeClassifier'] = lambda: RidgeClassifier(random_state=RANDOM_STATE, alpha=1.0)
    m['RidgeClassifierCV'] = lambda: RidgeClassifierCV(cv=5)
    m['SGDClassifier'] = lambda: SGDClassifier(random_state=RANDOM_STATE)
    m['Perceptron'] = lambda: Perceptron(random_state=RANDOM_STATE)
    m['PassiveAggressiveClassifier'] = lambda: PassiveAggressiveClassifier(random_state=RANDOM_STATE)
    # SVM
    m['SVC'] = lambda: SVC(kernel='rbf', probability=True, random_state=RANDOM_STATE, C=1.0, gamma='scale')
    m['NuSVC'] = lambda: NuSVC(kernel='rbf', probability=True, random_state=RANDOM_STATE, nu=0.5)
    m['LinearSVC'] = lambda: LinearSVC(random_state=RANDOM_STATE, C=1.0, max_iter=5000)
    # KNN
    m['KNeighborsClassifier'] = lambda: KNeighborsClassifier(n_neighbors=5)
    m['NearestCentroid'] = lambda: NearestCentroid()
    # NB
    m['GaussianNB'] = lambda: GaussianNB()
    m['BernoulliNB'] = lambda: BernoulliNB()
    # DA
    m['LinearDiscriminantAnalysis'] = lambda: LinearDiscriminantAnalysis()
    m['QuadraticDiscriminantAnalysis'] = lambda: QuadraticDiscriminantAnalysis()
    # Tree
    m['DecisionTreeClassifier'] = lambda: DecisionTreeClassifier(random_state=RANDOM_STATE)
    m['ExtraTreeClassifier'] = lambda: ExtraTreeClassifier(random_state=RANDOM_STATE)
    # NN
    m['MLPClassifier'] = lambda: MLPClassifier(random_state=RANDOM_STATE, max_iter=1000, hidden_layer_sizes=(100, 50))
    # GP
    m['GaussianProcessClassifier'] = lambda: GaussianProcessClassifier(random_state=RANDOM_STATE)
    # Cal
    m['CalibratedClassifierCV'] = lambda: CalibratedClassifierCV(cv=5)
    # Dummy
    m['DummyClassifier'] = lambda: DummyClassifier(strategy='stratified', random_state=RANDOM_STATE)
    # Semi
    m['LabelPropagation'] = lambda: LabelPropagation()
    m['LabelSpreading'] = lambda: LabelSpreading()
    # External
    if HAS_XGB:
        m['XGBClassifier'] = lambda: XGBClassifier(eval_metric='logloss', random_state=RANDOM_STATE, verbosity=0, n_estimators=200, max_depth=6)
    if HAS_LGB:
        m['LGBMClassifier'] = lambda: LGBMClassifier(verbose=-1, random_state=RANDOM_STATE, n_jobs=-1, n_estimators=200, max_depth=6)
    if HAS_CB:
        m['CatBoostClassifier'] = lambda: CatBoostClassifier(verbose=0, random_state=RANDOM_STATE, iterations=200, depth=6)
    return m


def strict_helix_benchmark(X, y, dataset_name, model_list, n_splits=10, apply_smote=True):
    """Run ALL models under strict Helix CV isolation."""
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    results = []
    n_models = len(model_list)
    
    for mi, (model_name, clf_fn) in enumerate(model_list.items(), 1):
        start = time.time()
        f1_s, recall_s, acc_s, prec_s, auc_s = [], [], [], [], []
        n_success = 0
        
        for train_idx, test_idx in skf.split(X, y):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y[train_idx], y[test_idx]
            
            try:
                pipe = ImbPipeline(steps=[
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                    *([('smote', SMOTE(random_state=RANDOM_STATE))] if apply_smote else []),
                    ('classifier', clone(clf_fn()))
                ])
                pipe.fit(X_tr, y_tr)
                y_pred = pipe.predict(X_te)
                
                f1_s.append(f1_score(y_te, y_pred))
                recall_s.append(recall_score(y_te, y_pred))
                acc_s.append(accuracy_score(y_te, y_pred))
                prec_s.append(precision_score(y_te, y_pred))
                
                if hasattr(pipe, 'predict_proba'):
                    try:
                        auc_s.append(roc_auc_score(y_te, pipe.predict_proba(X_te)[:, 1]))
                    except:
                        pass
                n_success += 1
            except Exception as e:
                pass
        
        elapsed = time.time() - start
        print(f"  [{mi}/{n_models}] {model_name:40s} folds={n_success}/{n_splits} time={elapsed:6.2f}s f1={np.mean(f1_s):.4f}" if f1_s else f"  [{mi}/{n_models}] {model_name:40s} folds={n_success}/{n_splits} time={elapsed:6.2f}s FAILED", file=sys.stderr)
        
        if n_success >= n_splits - 2 and f1_s:
            results.append({
                'model': model_name,
                'f1_mean': float(np.mean(f1_s)), 'f1_std': float(np.std(f1_s)),
                'recall_mean': float(np.mean(recall_s)), 'recall_std': float(np.std(recall_s)),
                'accuracy_mean': float(np.mean(acc_s)), 'accuracy_std': float(np.std(acc_s)),
                'precision_mean': float(np.mean(prec_s)), 'precision_std': float(np.std(prec_s)),
                'auc_mean': float(np.mean(auc_s)) if auc_s else np.nan,
                'auc_std': float(np.std(auc_s)) if auc_s else np.nan,
                'n_success': n_success, 'time_sec': round(elapsed, 2),
            })
    
    results.sort(key=lambda x: x['f1_mean'], reverse=True)
    return results


def load_wdbc():
    data = load_breast_cancer()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target
    return X, y, "WDBC (sklearn - Diagnostic)"


def load_coimbra():
    try:
        import urllib.request, zipfile, io
        url = "https://archive.ics.uci.edu/static/public/451/breast+cancer+coimbra.zip"
        req = urllib.request.urlopen(url, timeout=30)
        zf = zipfile.ZipFile(io.BytesIO(req.read()))
        csv_name = [f for f in zf.namelist() if f.endswith('.csv')][0]
        df = pd.read_csv(zf.open(csv_name))
        X = df[[c for c in df.columns if c != 'Classification']]
        y = (df['Classification'].astype(str).str.lower().isin(['malignant', '2'])).astype(int)
        if len(np.unique(y)) < 2:
            return None, None, None
        return X, y, "Breast Cancer Coimbra (UCI)"
    except Exception as e:
        print(f"  Coimbra load failed: {e}", file=sys.stderr)
        return None, None, None


if __name__ == "__main__":
    ALL_MODELS = build_model_list()
    print(f"Total models: {len(ALL_MODELS)}", file=sys.stderr)
    
    # Run WDBC
    X_wdbc, y_wdbc, name_wdbc = load_wdbc()
    print(f"=== {name_wdbc} ({len(y_wdbc)} samples, {X_wdbc.shape[1]} features) ===", file=sys.stderr)
    t0 = time.time()
    wdbc_results = strict_helix_benchmark(X_wdbc, y_wdbc, name_wdbc, ALL_MODELS, n_splits=10)
    wdbc_elapsed = time.time() - t0
    print(f"\n=== WDBC RESULTS ({len(wdbc_results)} models, {wdbc_elapsed:.1f}s) ===")
    for i, r in enumerate(wdbc_results, 1):
        auc = f"{r['auc_mean']:.4f}" if not np.isnan(r['auc_mean']) else "N/A"
        print(f"  {i:3d}. {r['model']:40s} F1={r['f1_mean']:.4f} Acc={r['accuracy_mean']:.4f} AUC={auc} ({r['time_sec']:.1f}s)")
    
    wdbc_out = {
        'dataset': name_wdbc, 'n_samples': len(y_wdbc), 'n_features': X_wdbc.shape[1],
        'n_positive': int(y_wdbc.sum()), 'n_negative': int((1 - y_wdbc).sum()),
        'prevalence': float(y_wdbc.mean()), 'cv_folds': 10, 'results': wdbc_results,
        'elapsed_sec': round(wdbc_elapsed, 1),
    }
    
    # Run Coimbra
    X_coimbra, y_coimbra, name_coimbra = load_coimbra()
    if X_coimbra is not None and len(np.unique(y_coimbra)) >= 2:
        print(f"\n=== {name_coimbra} ({len(y_coimbra)} samples, {X_coimbra.shape[1]} features) ===", file=sys.stderr)
        t0 = time.time()
        coimbra_results = strict_helix_benchmark(X_coimbra, y_coimbra, name_coimbra, ALL_MODELS, n_splits=5)
        coimbra_elapsed = time.time() - t0
        print(f"\n=== COIMBRA RESULTS ({len(coimbra_results)} models, {coimbra_elapsed:.1f}s) ===")
        for i, r in enumerate(coimbra_results, 1):
            auc = f"{r['auc_mean']:.4f}" if not np.isnan(r['auc_mean']) else "N/A"
            print(f"  {i:3d}. {r['model']:40s} F1={r['f1_mean']:.4f} Acc={r['accuracy_mean']:.4f} AUC={auc} ({r['time_sec']:.1f}s)")
        
        coimbra_out = {
            'dataset': name_coimbra, 'n_samples': len(y_coimbra), 'n_features': X_coimbra.shape[1],
            'n_positive': int(y_coimbra.sum()), 'n_negative': int((1 - y_coimbra).sum()),
            'prevalence': float(y_coimbra.mean()), 'cv_folds': 5, 'results': coimbra_results,
            'elapsed_sec': round(coimbra_elapsed, 1),
        }
    else:
        coimbra_out = {'dataset': name_coimbra, 'error': 'Not available'}
        print("\n  Coimbra not available, skipping.", file=sys.stderr)
    
    output = {'wdbc': wdbc_out, 'coimbra': coimbra_out}
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")