# Data Leakage Detection in Benchmarks

> 2026-06-01 Pima 实战教训

## 信号：所有模型 F1≈1.0

当 34 模型基准测试中 LogisticRegression、DecisionTree、RandomForest 等全部达到 F1≈1.0 时，**不是模型太好，是数据泄露**。

## 根因

CSV 文件中存在目标变量的副本列（hidden duplicate），加载时只 drop 了原始目标列但未排除副本。

**Pima 实例**：PIDD CSV 同时有 `Outcome`（目标）和 `Diabetes_binary`（完全相同的副本列）。
```python
load_pidd():
    return df.drop('Outcome', axis=1), df['Outcome']  # ❌ Diabetes_binary 仍在特征中！
```

## 审计命令

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data.csv')
target = 'Outcome'
for col in df.columns:
    if col != target and (df[col] == df[target]).all():
        print(f'LEAKAGE: {col} == {target}')
"
```

## 修复

```python
feat = [c for c in df.columns if c not in (target, 'Diabetes_binary', 'target', 'ID', 'Unnamed: 0')]
return df[feat], df[target]
```

## 预防

- 每次加载 CSV 时检查是否有目标列的精确副本
- 列过滤使用白名单（明确列出特征列）而非黑名单（drop 目标列）
- benchmark 脚本在加载数据后加断言：`assert 'Diabetes_binary' not in features.columns`
