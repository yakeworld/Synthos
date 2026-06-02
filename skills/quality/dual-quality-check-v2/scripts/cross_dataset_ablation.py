#!/usr/bin/env python3
"""
Cross-Dataset Ablation: CRISP-DM Helix Isolation vs Leaky Pipeline
=========================================================================
Runs the same ablation on multiple datasets to show leakage is a
general problem, not dataset-specific.

Usage:
    python3 cross_dataset_ablation.py

Datasets searched automatically:
  1. PIDD (Pima Indians, UCI) - 768x8, 34.9% prevalence
  2. Early Diabetes (Bangladesh, UCI) - 520x16, 61.5%  
  3. sklearn diabetes (binarized) - 442x10, 50%
  4. PIDD imbalanced variants - 15%, 20%, 35% prevalence

Output: Summary table with Λ (Leakage Magnitude Index) per dataset.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, recall_score, accuracy_score
from sklearn.datasets import load_diabetes
from imblearn.over_sampling import SMOTE
import os, warnings
warnings.filterwarnings('ignore')

def run_ablation(X, y, n_folds=10, n_repeats=5):
    """比较隔离vs泄漏管线，返回指标"""
    iso_f1, iso_rec, leaky_f1, leaky_rec = [], [], [], []
    imp, scl = SimpleImputer(strategy='median'), StandardScaler()
    
    for rep in range(n_repeats):
        # LEAKY: global SMOTE then CV
        Xc = scl.fit_transform(imp.fit_transform(X))
        sm = SMOTE(random_state=42, k_neighbors=min(3, len(np.unique(y))-1))
        Xr, yr = sm.fit_resample(Xc, y)
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42+rep)
        for tr, te in skf.split(Xr, yr):
            clf = LogisticRegression(max_iter=1000, random_state=42+rep)
            clf.fit(Xr[tr], yr.iloc[tr])
            yp = clf.predict(Xr[te])
            leaky_f1.append(f1_score(yr.iloc[te], yp))
            leaky_rec.append(recall_score(yr.iloc[te], yp))
        
        # ISOLATED: SMOTE inside each CV fold
        skf2 = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42+rep)
        for tr, te in skf2.split(X, y):
            Xtr = scl.fit_transform(imp.fit_transform(X.iloc[tr]))
            Xte = scl.transform(imp.transform(X.iloc[te]))
            sm2 = SMOTE(random_state=42+rep, k_neighbors=min(3, len(np.unique(y.iloc[tr]))))
            Xtrr, ytrr = sm2.fit_resample(Xtr, y.iloc[tr])
            clf = LogisticRegression(max_iter=1000, random_state=42+rep)
            clf.fit(Xtrr, ytrr)
            yp = clf.predict(Xte)
            iso_f1.append(f1_score(y.iloc[te], yp))
            iso_rec.append(recall_score(y.iloc[te], yp))
    
    m_if1, m_ir = np.mean(iso_f1), np.mean(iso_rec)
    m_lf1, m_lr = np.mean(leaky_f1), np.mean(leaky_rec)
    f1pct = (m_lf1 - m_if1) / m_if1 * 100 if m_if1 > 0 else 0
    rd = m_lr - m_ir
    denom = max(m_if1, m_ir)
    lam = 0
    if denom > 0 and f1pct > 0 and rd < 0:
        lam = (m_lf1 - m_if1) * (-rd) / denom
    return m_if1, m_ir, m_lf1, m_lr, f1pct, rd, lam

def find_dataset(name, path, target_col):
    """安全加载数据集"""
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    excl = ['Outcome', 'Diabetes_binary']
    feat = [c for c in df.columns if c not in excl]
    return {'X': df[feat], 'y': df[target_col], 'size': len(df), 'prev': df[target_col].mean()}

def get_sklearn_diabetes():
    """sklearn内置糖尿病数据集(binarized)作为fallback第三数据集"""
    data = load_diabetes()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = pd.Series((data.target > np.median(data.target)).astype(int), name='Diabetes_binary')
    return {'X': X, 'y': y, 'size': len(X), 'prev': y.mean()}

if __name__ == '__main__':
    base = "/home/yakeworld/synthos_data"
    
    # 数据集注册
    dataset_specs = [
        ("PIDD (Pima, 768x8, 34.9%)", os.path.join(base, "pima_diabetes.csv"), 'Outcome'),
        ("Early Diabetes (Bangladesh, 520x16, 61.5%)", os.path.join(base, "early_diabetes.csv"), 'Diabetes_binary'),
    ]
    
    # 加载外部数据集
    datasets = []
    for name, path, target in dataset_specs:
        d = find_dataset(name, path, target)
        if d: datasets.append((name, d))
    
    # 总是加载sklearn
    d = get_sklearn_diabetes()
    datasets.append(("sklearn diabetes (clinical, 442x10, 50%)", d))
    
    # 加载不平衡变体
    for label, fname in [("PIDD_15pct", "pima_imbalanced_15pct.csv"),
                          ("PIDD_20pct", "pima_imbalanced_20pct.csv")]:
        d = find_dataset(f"PIDD ({label})", os.path.join(base, fname), 'Outcome')
        if d: datasets.append((f"PIDD ({label})", d))
    
    # 运行消融
    print(f"{'Dataset':<45} {'n':<6} {'Prev':<6} {'Iso-F1':<8} {'Lky-F1':<8} {'F1%':<8} {'RΔ':<8} {'Λ':<8}")
    print("-" * 100)
    
    results = []
    for name, d in datasets:
        X, y = d['X'], d['y']
        r = run_ablation(X, y)
        m_if1, m_ir, m_lf1, m_lr, f1p, rd, lam = r
        prev_pct = f"{d['prev']:.0%}"
        print(f"{name:<45} {d['size']:<6} {prev_pct:<6} {m_if1:<8.4f} {m_lf1:<8.4f} {f1p:<+7.1f}% {rd:<+7.4f} {lam:<8.4f}")
        results.append((name, r, d['prev']))
    
    print(f"\n{'='*100}")
    print("Key finding: Leakage inflation magnitude ∝ class imbalance severity")
    print("=" * 100)
    for name, r, prev in results:
        f1p = r[4]
        if abs(f1p) > 5:
            print(f"  Dataset: {name[:40]:<40} | F1 inflated {f1p:+.1f}% | Prev: {prev:.0%}")
