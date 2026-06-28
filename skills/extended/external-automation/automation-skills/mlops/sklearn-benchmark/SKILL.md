---


name: sklearn-benchmark
description: 设计、运行和优化scikit-learn多模型基准测试。覆盖预赛时序检测、失败模型预判、大数据集模型过滤、OOM防护、并行策略、结果整合。
version: 1.0.0
license: MIT
author: Synthos
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    author: Synthos
    signature: 'dataset: str, models: list -> benchmark_report: dict'
    related_skills:
    - crispdm-helix-experiment
    - experiment-recipes
    - huggingface-hub
    - medical-image-centerline
    - remote-gpu-training
    version: 1.1.0
    tags:
    - sklearn
    - benchmark
    - model-evaluation
    - mlops



---



## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）




# sklearn-benchmark — 多模型基准测试方法论

## 原理层 · 文言

> **先小后大，预赛定筛。**
> 不将大运行衰模，不因慢堵废全轮。
> 知模之性而用，量数之体而择。

## 核心原则

### 预赛时序检测（Pre-benchmark Timing Test）


## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。

在任何多模型基准测试中，**先用最小数据集做时序预赛**，识别失败和特慢模型，再决定是否在更大数据集上运行。

| 步骤 | 动作 | 目的 |
|:-----|:-----|:-----|
| 1 | 选最小的数据集（如 PIDD 768行） | 最小化等待时间 |
| 2 | 跑 1-2 折 CV（非全量） | 快速评估而非精确评分 |
| 3 | 记录每模型耗时 + 失败率 | 识别要删除/跳过的模型 |
| 4 | 判定：删失败 → 跳慢 → 跑全量 | 优化后续基准 |

### 快速时间测试（先跑一个看时间）

在大型数据集（>50K行）上运行全量基准前，**先跑一个代表性轻量模型**预测总时长：

```bash
# 选LogisticRegression（快且稳定），跑完整CV
t0 = time.time()
clf = LogisticRegression(max_iter=2000)
for rep in range(cv_repeats):
    skf = StratifiedKFold(n_splits=2, shuffle=True, random_state=rep)
    for train_idx, test_idx in skf.split(X, y):
        pipe = Pipeline([('impute', SimpleImputer()), ('scale', StandardScaler()), ('clf', clf)])
        pipe.fit(X_tr, y_tr)
        yp = pipe.predict(X_te)
        f1_scores.append(f1_score(y_te, yp))

elapsed = time.time() - t0
print(f'Time: {elapsed:.1f}s ({elapsed/6:.1f}s per fold)')
# 估算全量：elapsed × N_models × (1 + 慢模型倍率)
```

**实战验证**（CDC BRFSS 253,680行×21特征）：
- LogisticRegression: 4.4s（6折，0.7s/折）
- 轻量模型（~20个）预估：2-5分钟
- 含重型模型（SVC等）：直接OOM

### OOM 防护（exit code 137）

SVC/NuSVC等核方法模型在大型数据集上会触发 **OOM killer（exit 137/SIGKILL）**，与"慢"不同——它们不会完成，直接被杀。

| 模型 | OOM阈值 | 原因 | 处置 |
|:-----|:--------|:-----|:-----|
| `SVC(probability=True)` | >10K行 | O(n²)核矩阵→~40GB | 大型数据集永久跳过 |
| `NuSVC(probability=True)` | >10K行 | 同上 | 永久跳过 |
| `CalibratedClassifierCV(SVC)` | >5K行 | SVC×3折内部CV | 永久跳过 |
| `LabelPropagation` | >10K行 | 图算法O(n²) | 永久跳过 |
| `LabelSpreading` | >10K行 | 同上 | 永久跳过 |
| `MLPClassifier` | >50K行 | 默认3层网络 | 大型数据集跳过 |

**鉴别诊断**：远程SSH任务被杀（exit 137） ≠ 代码bug。检查系统日志 `dmesg | grep -i oom` 或 `journalctl -k | grep oom` 确认。

### LIGHT_CLASSIFIERS 模式（数据集路由）

在脚本中定义双模型列表，按数据集规模路由：

```python
# 全部模型（小/中型数据集用）
CLASSIFIERS = [
    ('LogisticRegression', LogisticRegression(...)),  # 快
    ('SVC', SVC(probability=True)),                    # OOM on large
    ...
]

# 手动列出 OOM 模型名
HEAVY_MODELS = {'SVC', 'NuSVC', 'CalibratedSVC', 'LabelPropagation', 'LabelSpreading', 'MLPClassifier'}
# 或从 CLASSIFIERS 中过滤
LIGHT_CLASSIFIERS = [c for c in CLASSIFIERS if c[0] not in HEAVY_MODELS]

# 调用时按数据集路由
for dname, X, y in datasets:
    is_large = (len(X) > 10000)
    models = LIGHT_CLASSIFIERS if is_large else CLASSIFIERS
    results = quick_benchmark(X, y, dname, model_list=models)
```

**quick_benchmark 函数签名**应接受 `model_list` 参数：

```python
def quick_benchmark(X, y, dataset_name, cv_repeats=5, model_list=None):
    if model_list is None:
        model_list = CLASSIFIERS  # 默认全量
    for name, clf in model_list:
        ...  # 原有逻辑
```

### 常见失败模型（sklearn + StandardScaler + SMOTE 管线）

| 模型 | 失败原因 | 处置 |
|:-----|:---------|:-----|
| `RadiusNeighbors` | 标准化后半径内无邻居 | 永久删除 |
| `ComplementNB` | 要求非负输入，StandardScaler产生负值 | 永久删除 |

### 慢模型分级（判定阈值）

依据在 768行×8特征 上的耗时/折（5×2 CV = 10折）：

| 耗时/折 | 分级 | 小型数据(≤1K) | 中型数据(1K-10K) | 大型数据(≥10K) |
|:-------:|:----:|:-------------:|:----------------:|:---------------:|
| <0.5s | ✅ 快 | 全跑 | 全跑 | 全跑 |
| 0.5-5s | ⚠️ 中 | 全跑 | 全跑 | 需评估 |
| 5-20s | 🐌 慢 | 可跑 | 跳或减CV折 | ❌ 跳过 |
| >20s | 🔴 极慢 | 可跑(1折) | ❌ 跳过 | ❌ 跳过 |
| 失败/被杀 | ❌ 废/🧨 OOM | 永久删除 | 永久删除 | 永久删除 |

**典型慢/OOM模型**（在 25K行+ 数据集上需跳过）：
- `SVC` — O(n²)核矩阵，30K行→~30GB ✅ OOM
- `NuSVC` — 同上 ✅ OOM
- `CalibratedClassifierCV(SVC)` — SVC×3 ✅ OOM
- `LabelPropagation` — 图算法 ✅ OOM
- `LabelSpreading` — 同上 ✅ OOM
- `MLPClassifier`(默认) — 3层全连接 ✅ 慢+大内存
- `XGBoost`(默认n_estimators=100) — ~18s/折 on 768行 → 大数据集需调参减量
- `LightGBM` — ~10s/折 on 768行 → 同上
- `CatBoost` — ~2s/折 on 768行 → 大数据集需评估

### 基准协议模板

```python
# 1. 模型列表（预删失败模型）
CLASSIFIERS = [...]

# 2. OOM模型黑名单
HEAVY_MODELS = {'SVC', 'NuSVC', 'CalibratedSVC', 'LabelPropagation', 'LabelSpreading', 'MLPClassifier'}
LIGHT_CLASSIFIERS = [c for c in CLASSIFIERS if c[0] not in HEAVY_MODELS]

# 3. 数据集路由
for dname, X, y in datasets:
    is_large = (dname == 'CDC BRFSS' or len(X) > 10000)
    models = LIGHT_CLASSIFIERS if is_large else CLASSIFIERS
    cv = 3 if is_large else 5  # 大型数据集减少CV折数
    top15, n, prev = quick_benchmark(X, y, dname, cv_repeats=cv, model_list=models)
```

### 结果整合

基准测试产出应为 JSON 格式，按数据集分组，Top-K 模型排行：

```json
{
  "Dataset-A": {
    "n_samples": 768,
    "prevalence": 0.349,
    "top15": [
      {"model": "LinearSVC", "f1": 0.6678, "recall": 0.7142, "auc": 0.0},
      ...
    ]
  }
}
```

**合并来源**：同一数据集多个基准运行（原始15 + 补漏7）合并后统一排序取Top15。

### 验证清单

- [ ] 预赛时序检测已执行（选最小数据集）
- [ ] 失败模型已识别并永久删除
- [ ] OOM模型已识别并加入HEAVY_MODELS黑名单
- [ ] 大型数据集先跑一个快模型估算总时长
- [ ] 大型数据集使用LIGHT_CLASSIFIERS + 减少CV折数
- [ ] 结果已合并、排序、保存为JSON
- [ ] 论文中数值已通过L0.5数据门验证（见 dual-quality-check-v2）
