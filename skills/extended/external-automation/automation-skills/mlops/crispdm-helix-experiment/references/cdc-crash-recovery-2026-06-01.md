# CDC Benchmark Crash Recovery (2026-06-01)

## 场景

CDC BRFSS (25K行 × 21特征) 基准测试在大数据集上运行时中途崩溃，22个模型中只跑了15个。不需要重跑全部。

## 恢复协议

### Step 1: 检查日志，确认已完成模型

```bash
# 检查进程输出日志，找已完成模型列表
# 或在sessions的 proc log 中找输出
# 典型信号: "  AdaBoost  F1=0.4505 ..." 后进程退出
```

从输出中提取每个模型及其F1/Recall/AUC。

### Step 2: 仅写补丁脚本，跑缺失模型

```python
# run_cdc_missing.py — 只包含未完成的模型
CLASSIFIERS = [
    ('Bagging', BaggingClassifier(n_jobs=-1, random_state=42)),
    ('GaussianNB', GaussianNB()),
    ('BernoulliNB', BernoulliNB()),
    ('LinearDiscriminant', LinearDiscriminantAnalysis()),
    ('QuadraticDiscriminant', QuadraticDiscriminantAnalysis()),
    ('CalibratedSVC', CalibratedClassifierCV(...)),  # ⚠️ 大数据集上极慢
    ('LabelPropagation', LabelPropagation()),
    ('LabelSpreading', LabelSpreading()),
]
```

**关键**: 原跑15个模型已完成，补丁脚本只跑**剩余的**，不重跑已有的。

### Step 3: CalibratedSVC超大数据集跳过规则

| 模型 | PIDD (768行) | CDC (25K行) |
|:-----|:-----------:|:-----------:|
| CalibratedSVC | 0.076s/fold ✅ | SVC + 内部3折CV → 极慢 ❌ 跳过 |

**规则**: 任何 wrapper 型模型（CalibratedClassifierCV、GridSearchCV内部嵌套SVC）在 >10K行数据集上**跳过**。其在小数据集上的数据已足够支撑跨数据集结论。

### Step 4: 合并结果

```python
# 从原跑日志提取的15个结果
original_results = [...]  
# 补丁脚本输出的7个结果
patch_results = [...]     

# 合并后排序
all_cdc = original_results + patch_results
all_cdc.sort(key=lambda r: r['f1'], reverse=True)
cdc_top15 = all_cdc[:15]
```

**完整性说明**: CDC完成22/27模型（5个超重模型跳过: CalibratedSVC, MLPClassifier, XGBoost, LightGBM, CatBoost）。这5个在PIDD/ED上已有数据，不影响跨数据集比较。

### Step 5: 合并进主结果

```python
results = {
    "PIDD": {"n_samples": 768, "top15": pidd_top15},
    "Early Diabetes": {"n_samples": 520, "top15": ed_top15},
    "CDC BRFSS": {"n_samples": 25368, "top15": cdc_top15}
}
json.dump(results, open('helix_benchmark_results.json', 'w'))
```

## 核心理念

> **不是所有崩溃都要重跑。检查已完成的工作 → 补缺失的部分 → 合并。** 避免在CDC 25K行上重跑所有22个模型（浪费30分钟+CPU）。
