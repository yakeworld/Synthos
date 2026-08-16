#!/usr/bin/env python3
"""
Kaggle 教育数据集数据泄露审计 v2
覆盖四种泄漏模式 + 多模型 + 多数据集
"""
import os, sys, json, warnings
from datetime import datetime
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')

AUDIT_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers/kaggle-leakage-audit"
DATA_DIR = os.path.join(AUDIT_DIR, "01-datasets")

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, recall_score, precision_score, accuracy_score, roc_auc_score
from imblearn.over_sampling import SMOTE

def load_pima():
    path = os.path.join(DATA_DIR, "pima", "diabetes.csv")
    cols = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigree','Age','Outcome']
    if os.path.exists(path):
        df = pd.read_csv(path, header=None, names=cols)
        for c in ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']:
            df[c] = df[c].replace(0, np.nan)
        return df, 'Outcome', [c for c in cols if c != 'Outcome']
    return None, None, None

def load_iris():
    from sklearn.datasets import load_iris
    d = load_iris()
    df = pd.DataFrame(d.data, columns=[c.replace(' ','_') for c in d.feature_names])
    df['target'] = d.target
    return df, 'target', [c for c in df.columns if c != 'target']

def load_wdbc():
    from sklearn.datasets import load_breast_cancer
    d = load_breast_cancer()
    df = pd.DataFrame(d.data, columns=[c.replace(' ','_') for c in d.feature_names])
    df['target'] = d.target
    return df, 'target', [c for c in df.columns if c != 'target']

def load_titanic():
    for p in [os.path.join(DATA_DIR, "titanic", "titanic.csv"), "/tmp/titanic_test.csv"]:
        if os.path.exists(p):
            df = pd.read_csv(p)
            df['Title'] = df['Name'].str.extract(r' ([A-Za-z]+)\.', expand=False).fillna('Unknown')
            df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
            df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
            df['AgeFill'] = df.groupby('Title')['Age'].transform(lambda x: x.fillna(x.median()))
            df['FareFill'] = df['Fare'].fillna(df['Fare'].median())
            features = ['Pclass', 'Sex', 'AgeFill', 'FareFill', 'FamilySize', 'IsAlone', 'SibSp', 'Parch']
            df['Sex'] = (df['Sex'] == 'male').astype(int)
            df = pd.get_dummies(df, columns=['EmbarkedFill'], prefix='Emb', drop_first=True)
            return df, 'Survived', [c for c in features if c in df.columns]
    return None, None, None

def load_wine():
    from sklearn.datasets import load_wine
    d = load_wine()
    df = pd.DataFrame(d.data, columns=[c.replace(' ','_') for c in d.feature_names])
    df['target'] = d.target
    return df, 'target', [c for c in df.columns if c != 'target']

def load_digits():
    from sklearn.datasets import load_digits
    d = load_digits()
    df = pd.DataFrame(d.data, columns=[f'p{i}' for i in range(d.data.shape[1])])
    df['target'] = d.target
    return df, 'target', [c for c in df.columns if c != 'target']

def load_highly_imbalanced(name, n_samples=5000, imbalance=0.01, n_features=20):
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=n_samples, n_features=n_features,
        n_informative=n_features//2, weights=[1-imbalance, imbalance],
        flip_y=0.01, random_state=42)
    df = pd.DataFrame(X, columns=[f'V{i+1}' for i in range(n_features)])
    df['target'] = y
    return df, 'target', [f'V{i+1}' for i in range(n_features)]

DATASETS = [
    ("PIMA (PIDD)", load_pima), ("Titanic", load_titanic),
    ("Iris", load_iris), ("WDBC (Breast Cancer)", load_wdbc),
    ("Wine (Multiclass)", load_wine), ("Digits (MNIST-like)", load_digits),
    ("Synth-Imb-1%", lambda: load_highly_imbalanced("imb1", 5000, 0.01, 20)),
    ("Synth-Imb-5%", lambda: load_highly_imbalanced("imb5", 5000, 0.05, 20)),
]

MODELS = {
    'LR': LogisticRegression(max_iter=2000, random_state=42),
    'RF': RandomForestClassifier(n_estimators=100, random_state=42),
}
LEAKAGE = ['Helix', 'ImputeLeak', 'SMOTELeak', 'SevereLeak']

def run_experiment(df, target, features, name, n_splits=5):
    X = df[features].copy().apply(pd.to_numeric, errors='coerce')
    y = df[target].copy()
    multiclass = len(np.unique(y)) > 2
    avg = 'weighted' if multiclass else 'binary'
    results = {}
    for mn, model in MODELS.items():
        for lvl in LEAKAGE:
            scores = {m:[] for m in ['f1','recall','precision','accuracy']}
            skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
            for tr_idx, te_idx in skf.split(X, y):
                X_tr, X_te = X.iloc[tr_idx].copy(), X.iloc[te_idx].copy()
                y_tr, y_te = y.iloc[tr_idx], y.iloc[te_idx]
                
                if lvl == 'Helix':
                    imp, scl = SimpleImputer(strategy='median'), StandardScaler()
                    X_tr = scl.fit_transform(imp.fit_transform(X_tr))
                    X_te = scl.transform(imp.transform(X_te))
                elif lvl == 'ImputeLeak':
                    X_f = np.vstack([X_tr.values, X_te.values])
                    imp, scl = SimpleImputer(strategy='median'), StandardScaler()
                    X_f = scl.fit_transform(imp.fit_transform(X_f))
                    X_tr, X_te = X_f[:len(X_tr)], X_f[len(X_tr):]
                elif lvl == 'SMOTELeak':
                    X_f, y_f = np.vstack([X_tr.values, X_te.values]), np.hstack([y_tr.values, y_te.values])
                    imp = SimpleImputer(strategy='median')
                    X_f = imp.fit_transform(X_f)
                    n_t = len(X_tr)
                    try:
                        X_res, y_res = SMOTE(random_state=42).fit_resample(X_f, y_f)
                        X_tr, X_te = X_res[:n_t], X_res[n_t:]
                    except:
                        X_tr, X_te = X_f[:n_t], X_f[n_t:]
                    scl = StandardScaler()
                    X_tr, X_te = scl.fit_transform(X_tr), scl.transform(X_te)
                elif lvl == 'SevereLeak':
                    X_f, y_f = np.vstack([X_tr.values, X_te.values]), np.hstack([y_tr.values, y_te.values])
                    imp = SimpleImputer(strategy='median'); X_f = imp.fit_transform(X_f)
                    n_t = len(X_tr)
                    try:
                        X_res, y_res = SMOTE(random_state=42).fit_resample(X_f, y_f)
                        X_tr, X_te = X_res[:n_t], X_res[n_t:]
                    except:
                        X_tr, X_te = X_f[:n_t], X_f[n_t:]
                    scl = StandardScaler()
                    X_tr, X_te = scl.fit_transform(X_tr), scl.transform(X_te)
                
                m = model.__class__(random_state=42)
                m.fit(X_tr, y_tr); p = m.predict(X_te)
                scores['f1'].append(f1_score(y_te, p, average=avg))
                scores['recall'].append(recall_score(y_te, p, average=avg, zero_division=0))
                scores['accuracy'].append(accuracy_score(y_te, p))
            
            results[f"{mn}_{lvl}"] = {k: round(float(np.mean(v)),4) for k,v in scores.items()}
    
    inflation = {}
    for mn in MODELS:
        h = results.get(f"{mn}_Helix",{}); s = results.get(f"{mn}_SevereLeak",{})
        inflation[mn] = {m: round((s.get(m,0)-h.get(m,0.001))/h.get(m,0.001)*100,2) for m in ['f1','recall','accuracy']}
    
    return {'dataset':name,'n_samples':len(df),'prevalence':round(float(y.mean()),4),
            'results':results,'inflation':inflation}

def main():
    print("="*80)
    print("KAGGLE 教育数据集 — 数据泄露审计")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*80)
    all_r = []
    for name, loader in DATASETS:
        df,target,features = loader()
        if df is None: continue
        r = run_experiment(df,target,features,name)
        all_r.append(r)
        print(f"\n→ {name}")
        for mn in MODELS:
            infl = r['inflation'].get(mn,{}).get('f1',0)
            hf1 = r['results'].get(f"{mn}_Helix",{}).get('f1',0)
            print(f"  {mn:4s}: Helix F1={hf1:.4f}, 膨胀={infl:+.2f}%")
    
    print(f"\n{'='*80}\n汇总\n{'='*80}")
    print(f"{'数据集':25s} {'LR膨胀':>10s} {'RF膨胀':>10s}")
    for r in all_r:
        li = r['inflation'].get('LR',{}).get('f1',0)
        ri = r['inflation'].get('RF',{}).get('f1',0)
        print(f"{r['dataset']:25s} {li:>+9.2f}% {ri:>+9.2f}%")
    
    out = os.path.join(AUDIT_DIR,"03-reports","kaggle_audit_v2.json")
    os.makedirs(os.path.dirname(out),exist_ok=True)
    with open(out,'w') as f:
        json.dump({'metadata':{'run_date':datetime.now().isoformat()},'results':all_r}, f, indent=2)

if __name__ == '__main__':
    main()
