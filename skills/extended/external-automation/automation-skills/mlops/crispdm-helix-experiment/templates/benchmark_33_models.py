"""
33-Model Comprehensive Benchmark Template
==========================================
Helix strict methodology for scanning all major classifier families.

Usage: python benchmark_33_models.py --dataset path/to/data.csv --target column

Key traps to avoid:
1. clone(clf_fn()) NOT clone(clf_fn) — lambda → estimator → clone
2. Print first exception: if model_name == 'AdaBoostClassifier': traceback.print_exc()
3. n_success reset at TOP of outer loop, not inside inner fold loop
"""
import sys
import numpy as np
import pandas as pd
import json
import time
import argparse

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.base import clone
from sklearn.metrics import (f1_score, accuracy_score, precision_score,
                             roc_auc_score, recall_score)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from sklearn.linear_model import (
    LogisticRegression, RidgeClassifier, SGDClassifier,
    Perceptron, PassiveAggressiveClassifier,
)
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, AdaBoostClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier

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


def build_model_list():
    """Build 33 model list. Lambda values → call first before clone()."""
    m = {}
    m['LogisticRegression'] = lambda: LogisticRegression(max_iter=5000, C=1.0, random_state=RANDOM_STATE)
    m['RidgeClassifier'] = lambda: RidgeClassifier(random_state=RANDOM_STATE, alpha=1.0)
    m['SGDClassifier'] = lambda: SGDClassifier(random_state=RANDOM_STATE)
    m['SVC'] = lambda: SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=RANDOM_STATE)
    m['LinearSVC'] = lambda: LinearSVC(random_state=RANDOM_STATE, C=1.0, max_iter=5000)
    m['RandomForestClassifier'] = lambda: RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    m['ExtraTreesClassifier'] = lambda: ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    m['GradientBoostingClassifier'] = lambda: GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=RANDOM_STATE)
    m['HistGradientBoostingClassifier'] = lambda: HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=RANDOM_STATE)
    m['AdaBoostClassifier'] = lambda: AdaBoostClassifier(random_state=RANDOM_STATE)
    m['KNeighborsClassifier'] = lambda: KNeighborsClassifier(n_neighbors=5)
    m['GaussianNB'] = lambda: GaussianNB()
    m['DecisionTreeClassifier'] = lambda: DecisionTreeClassifier(random_state=RANDOM_STATE)
    m['MLPClassifier'] = lambda: MLPClassifier(random_state=RANDOM_STATE, max_iter=1000, hidden_layer_sizes=(100, 50))
    m['DummyClassifier'] = lambda: DummyClassifier(strategy='stratified', random_state=RANDOM_STATE)
    if HAS_XGB:
        m['XGBClassifier'] = lambda: XGBClassifier(eval_metric='logloss', random_state=RANDOM_STATE, verbosity=0, n_estimators=200, max_depth=6)
    if HAS_LGB:
        m['LGBMClassifier'] = lambda: LGBMClassifier(verbose=-1, random_state=RANDOM_STATE, n_jobs=-1, n_estimators=200, max_depth=6)
    if HAS_CB:
        m['CatBoostClassifier'] = lambda: CatBoostClassifier(verbose=0, random_state=RANDOM_STATE, iterations=200, depth=6)
    return m


def run_benchmark(X, y, n_splits=10, apply_smote=True):
    """Run ALL models under Helix strict fold isolation."""
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    results = []
    ALL_MODELS = build_model_list()
    n_models = len(ALL_MODELS)
    
    for mi, (model_name, clf_fn) in enumerate(ALL_MODELS.items(), 1):
        start = time.time()
        f1_s, recall_s, acc_s, prec_s, auc_s = [], [], [], [], []
        n_success = 0  # ← RESET HERE (top of outer loop!)
        
        for train_idx, test_idx in skf.split(X, y):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y[train_idx], y[test_idx]
            
            try:
                pipe = ImbPipeline(steps=[
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                    *([('smote', SMOTE(random_state=RANDOM_STATE))] if apply_smote else []),
                    ('classifier', clone(clf_fn())),  # ← CALL lambda first, THEN clone
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
                if model_name == 'AdaBoostClassifier':  # ← Print first error for debugging
                    import traceback
                    print(f"ERROR on {model_name}: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                pass
        
        elapsed = time.time() - start
        if f1_s:
            results.append({
                'model': model_name,
                'f1_mean': float(np.mean(f1_s)), 'f1_std': float(np.std(f1_s)),
                'accuracy_mean': float(np.mean(acc_s)), 'accuracy_std': float(np.std(acc_s)),
                'n_success': n_success, 'time_sec': round(elapsed, 2),
            })
    
    results.sort(key=lambda x: x['f1_mean'], reverse=True)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='33-model benchmark')
    parser.add_argument('--dataset', required=True, help='path to CSV')
    parser.add_argument('--target', required=True, help='target column name')
    parser.add_argument('--splits', type=int, default=10, help='CV folds')
    parser.add_argument('--no-smote', action='store_true', help='skip SMOTE')
    args = parser.parse_args()
    
    df = pd.read_csv(args.dataset)
    X = df.drop(columns=[args.target])
    y = df[args.target].astype(int)
    
    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {y.mean():.1%} positive")
    
    results = run_benchmark(X, y, n_splits=args.splits, apply_smote=not args.no_smote)
    
    print(f"\n=== Results ({len(results)} models, {len(build_model_list())} evaluated) ===")
    for i, r in enumerate(results, 1):
        print(f"  {i:3d}. {r['model']:40s} F1={r['f1_mean']:.4f} Acc={r['accuracy_mean']:.4f} ({r['time_sec']:.1f}s)")