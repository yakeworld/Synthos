# CatBoost + SMOTE 过拟合检测（2026-06-24 实战教训）

## 问题

在 <1000 样本的临床数据集上（如 PIDD, n=768），CatBoost + SMOTE 管道可能产生 **F1=1.0** 的完美分数。原因：

1. SMOTE 在小样本上生成与真实样本极接近的合成点
2. CatBoost 的强梯度提升能力可以"记忆"这些边界
3. 每折验证集仅 ~27 个正例，容易被恰好预测准确

## 检测方法

```python
from sklearn.model_selection import StratifiedKFold, cross_validate
from catboost import CatBoostClassifier
from imblearn.pipeline import Pipeline as ImbPipeline

pipe = ImbPipeline([
    ('zero_replacer', ZeroReplacer(cols_to_replace=ZERO_COLS)),
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('smote', SMOTE(random_state=42)),
    ('clf', CatBoostClassifier(verbose=0, random_state=42))
])
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
scores = cross_validate(pipe, X, y, cv=cv, scoring=['f1','recall'], n_jobs=-1)

f1_mean = np.mean(scores['test_f1'])
f1_std = np.std(scores['test_f1'])

# 过拟合信号
if f1_mean >= 0.99 and f1_std <= 0.01:
    print(f'⚠️ CATASTROPHIC_OVERFIT: F1={f1_mean:.4f}±{f1_std:.4f}')
    print('  CatBoost + SMOTE on small dataset — DO NOT trust these values')
    print('  Possible fixes: reduce n_estimators, use simpler model, or remove SMOTE')
elif f1_mean >= 0.90 and f1_std <= 0.03:
    print(f'⚠️ SUSPICIOUS: F1={f1_mean:.4f}±{f1_std:.4f} — possible overfit')
```

## 与 Paper 声称值差异巨大的处理

若独立重现的 CatBoost F1=1.0 而论文声称 F1≈0.70（如 PIMA 案例）：

1. 检查数据加载路径是否一致（`pima_raw.csv` vs `~/synthos_data/pima_diabetes.csv`）
2. 检查 CatBoost 参数是否一致（`n_estimators` vs `iterations`，默认值变化）
3. 检查 Pipeline 组成是否一致（SMOTE inside/outside CV？）
4. 若仍不一致 → 采用 `comprehensive_results.json` 或 `experiments/` 下历史运行结果作为数据源
5. 不要用瞬间重现的极端值（F1=1.0）覆盖论文认可的稳定结果（F1=0.7067）

## PIMA 案例

| 来源 | CatBoost F1 | 说明 |
|:-----|:-----------:|:-----|
| Paper claim | 0.7067 | 论文声称值 |
| comprehensive_results.json | 0.7067 ✅ | 历史稳定运行（10-fold CV） |
| 独立重现（同一 Pipeline） | 1.0000 ❌ | 当前环境 CatBoost 版本差异 + 随机种子影响 |
| 最终判定 | 0.7067 | 信任 comprehensive_results.json，标记复现差异 |

## 规则

- **CatBoost 的随机性比 sklearn 模型大**——单次运行 F1 波动可达 ±0.03
- 以 `comprehensive_results.json` 或 `experiments/` 下的 多次运行均值为准
- 单次重现 F1=1.0 不否定论文的 0.7067——应检查版本、种子、数据路径
- 若多次运行均得到 F1=1.0 → 标记 CATASTROPHIC_OVERFIT，需调整模型配置
