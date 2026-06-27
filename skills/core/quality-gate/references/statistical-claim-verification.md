# 统计声明验证 — t-test / Cohen's d 的可追溯性协议

## 问题

论文中常见的统计声明如 `"p=0.59, Cohen's d=0.28"`（用于证明两个模型之间无显著差异），
如果没有对应的可执行代码，就是**没有源的数据（P0 问题）**。

## 验证步骤

### Step 1: 确认统计声明在论文中的位置

```bash
grep -n "p=[0-9]" paper.tex
grep -n "Cohen" paper.tex
```

### Step 2: 确认实验代码是否生成该统计量

在代码目录中搜索 p-value 和 Cohen's d 的来源：

```bash
grep -rl "ttest\|cohen_d\|scipy.stats" 03-code/ --include="*.py" 2>/dev/null
grep "p=0.59\|Cohen" 03-code/ --include="*.json" -r 2>/dev/null
```

### Step 3: 如果无源，编写验证脚本

必须使用与论文**完全相同的**模型配置和随机种子。关键参数包括：

| 参数 | 检查点 |
|:-----|:-------|
| 随机种子 | paper 和 notebook 使用的 random_state |
| CV 折数 | 论文声明的 n_folds |
| SMOTE 配置 | SMOTE(random_state=?) 是否与 Notebook 一致 |
| 模型超参数 | n_estimators/iterations/max_depth 等 |

脚本结构：

```python
from scipy.stats import ttest_rel
from sklearn.model_selection import StratifiedKFold

# 确保使用与论文一致的参数
cv = StratifiedKFold(n_splits=N, shuffle=True, random_state=RANDOM_SEED)
model_a = CatBoostClassifier(n_estimators=100, random_state=RANDOM_SEED)
model_b = VotingClassifier(...)

a_f1s, b_f1s = [], []
for train_idx, test_idx in cv.split(X, y):
    # Helix 隔离：impute + scale + SMOTE 在折内
    ...
    a_f1s.append(f1_score(y_test, a_pred))
    b_f1s.append(f1_score(y_test, b_pred))

# 配对 t-test（同一折上的两个模型）
t_stat, p_value = ttest_rel(a_f1s, b_f1s)

# Cohen's d（配对版本）
diff = np.array(a_f1s) - np.array(b_f1s)
cohens_d = diff.mean() / diff.std(ddof=1)
```

### Step 4: 保存 per-fold 数据和验证结果

```json
{
  "catboost": {
    "f1_mean": 0.7067,
    "f1_std": 0.0794,
    "per_fold_f1": [0.7463, 0.7586, 0.5714, ...]
  },
  "ensemble": {
    "f1_mean": 0.6993,
    "f1_std": 0.0641,
    "per_fold_f1": [0.6769, 0.7586, 0.6316, ...]
  },
  "paired_ttest": {
    "t_stat": 0.5558,
    "p_value": 0.5919
  },
  "cohens_d": 0.1757
}
```

保存到 `07-quality/ttest_verification.json`。

### Step 5: 更新论文（如需要）

将 Cohen's d 等数值修正为实际代码输出值。

### Step 6: 更新 all_results.json

在论文的 `03-code/all_results.json` 中添加 per-fold 数据和 t-test 结果，
确保下一次质量检查时可以追溯。

## 注意事项

1. **随机种子敏感性**：即使同样的参数，SMOTE 的随机采样也可能导致每折的 per-fold F1
   在不同运行中有 ±0.01 的波动。应运行多次取平均，或在论文中注明"基于一次 10-fold CV 运行"。
2. **配对样本 vs 独立样本**：两个模型使用相同的 CV 折划分时，必须使用**配对** t-test
   （`ttest_rel`），而非独立样本 t-test（`ttest_ind`）。
3. **Cohen's d 的配对版本**：配对版本的公式为 `diff.mean() / diff.std(ddof=1)`，
   其中 diff 是每折上两个模型的 F1 差值。这比独立样本的 Cohen's d 更准确。
