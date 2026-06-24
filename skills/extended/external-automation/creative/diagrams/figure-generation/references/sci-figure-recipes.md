# SCI 图表代码示例 (PIMA-CRISP-DM实战, 2026-06-24)

## ROC曲线 (Nature语义色板, 10-fold CV with std shading)

关键设置：
- 画布大小: `figsize=(5.0, 4.0)` — 适用单栏排版
- 随机基线: 灰虚线 `#999999`, lw=0.6, alpha=0.4
- 模型线: CatBoost=蓝(#0F4D92), GBC=青(#42949E), LR=红(#B64342)
- 填充: 均值±标准差, alpha=0.08
- 图例: `loc='lower right'`, 带灰边框

```python
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
for name, builder, color in models_roc:
    tprs, aucs = [], []
    mean_fpr = np.linspace(0, 1, 200)
    for tr, va in skf.split(X, y):
        X_tr, X_va = X.iloc[tr], X.iloc[va]
        y_tr, y_va = y.iloc[tr], y.iloc[va]
        # ... build pipeline within fold ...
        clf = builder(); clf.fit(X_tr_r, y_tr_r)
        fpr, tpr, _ = roc_curve(y_va, clf.predict_proba(X_va_pp)[:, 1])
        aucs.append(roc_auc_score(y_va, clf.predict_proba(X_va_pp)[:, 1]))
        tprs.append(np.interp(mean_fpr, fpr, tpr))
    mean_tpr = np.mean(tprs, axis=0)
    std_tpr  = np.std(tprs, axis=0)
    mean_auc = np.mean(aucs); std_auc = np.std(aucs)
    ax.plot(mean_fpr, mean_tpr, color=color, linewidth=1.2,
            label=f'{name} (AUC={mean_auc:.3f}$\\pm${std_auc:.3f})')
    ax.fill_between(mean_fpr, mean_tpr-std_tpr, mean_tpr+std_tpr,
                     color=color, alpha=0.08, linewidth=0)
```

## SHAP重要性柱状图

```python
# 1. 提取预处理后的特征矩阵
pipe.fit(X, y)
zr = ZeroReplacer(); imp = SimpleImputer(strategy='median'); scaler = StandardScaler()
X_zr = zr.fit_transform(X); X_imp = imp.fit_transform(X_zr); Xp = scaler.fit_transform(X_imp)

# 2. SHAP分析 (TreeExplainer for GBC)
exp = shap.TreeExplainer(pipe[-1])
sv = exp.shap_values(Xp)
mean_shap = np.abs(sv).mean(axis=0)
si = np.argsort(mean_shap)

# 3. 水平柱状图, Nature蓝渐变色
fig, ax = plt.subplots(figsize=(4.5, 3.2))
colors = [plt.cm.Blues(0.25 + 0.75*i/len(si)) for i in range(len(si))]
bars = ax.barh(range(len(si)), mean_shap[si], color=colors, height=0.65,
               edgecolor='white', linewidth=0.3)
ax.set_yticks(range(len(si)))
ax.set_yticklabels(feature_names[si], fontsize=8)
ax.set_xlabel('Mean |SHAP Value|', fontsize=8)
ax.invert_yaxis()
# 值标签
for b, v in zip(bars, mean_shap[si]):
    ax.text(b.get_width()+0.02, b.get_y()+b.get_height()/2,
            f'{v:.3f}', va='center', fontsize=7, color='#333333')
```

## 出口契约 (SCI期刊)

```python
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 8, 'axes.titlesize': 9, 'axes.labelsize': 8,
    'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'legend.fontsize': 7,
    'figure.dpi': 300, 'savefig.dpi': 300,
    'savefig.bbox': 'tight', 'svg.fonttype': 'none',
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': 0.6,
})
```
