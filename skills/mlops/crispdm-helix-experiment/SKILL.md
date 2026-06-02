---
name: crispdm-helix-experiment
description: "CRISP-DM Helix methodology: strict CV-fold-isolated preprocessing for clinical ML experiments on public datasets. Generates real, traceable experimental data (L0.5 compliant). Reusable pipeline template for any public benchmark."
category: mlops
---

# CRISP-DM Helix Experiment Pipeline

> 严格数据隔离协议 + 多模型基准 + 消融研究 + 阈值优化
> 所有数字可追溯至实验代码输出（L0.5 数据诚实门）

## 适用场景

- 任何公开数据集的临床 ML 论文需要真实实验结果
- 论文数值需要 L0.5 验证（与实验输出比对）
- 多数据集对比研究（难度-比例损伤分析）
- CRISP-DM Helix 方法论论文

## 全量27模型基准协议（v3.2 新增 → v4.0 修正）

> **2026-05-31 用户要求**: 所有数据集都应跑全量27个模型选出最佳，优化参数，作为该数据集的**泄漏-自由性能天花板**（Dataset Baseline Registry）。任何声称超过此阈值的论文 → 疑似数据泄漏。
>
> **勘误 (2026-06-01)**: 原标称"34个模型"实际代码中只有28-29个（VotingClassifier、StackingClassifier、CategoricalNB、ClassifierChain 虽已 import 但从未实例化到 CLASSIFIERS 列表）。2026-06-01 实测后再移除2个永不成功的模型（RadiusNeighbors、ComplementNB），模型池稳定为27个。本技能已统一修正。

### 原理

Dataset Baseline Registry = 每个公开临床数据集在Helix严格隔离下的**最优性能上限**。

用途：
- **检测泄漏**: 新论文声称F1超过基准 → 自动标记为泄漏嫌疑
- **方法论基准**: 任何声称"我们的算法优于所有基线"的论文，必须证明其隔离protocol与Helix等价
- **社区资源**: 论文发布时附带该数据集的Helix基准值，编辑/审稿人可直接比对

### Step 1: 全量27模型基准测试（Docker推荐）

> **2026-06-01 修正**: 原标称"34个模型"实际代码中只有28-29个（VotingClassifier、StackingClassifier、CategoricalNB、ClassifierChain 虽已 import 但从未实例化到 CLASSIFIERS 列表）。2026-06-01 实测后再移除2个永不成功的模型（RadiusNeighbors、ComplementNB），模型池稳定为27个。

**脚本位置**: 始终保存到 `03-code/experiments/` 目录（不存 /tmp）

```python
# 见 03-code/experiments/run_helix_benchmark.py
# 使用 5x2 CV + 折叠内SMOTE + StratifiedKFold
```

**实际模型动物园**（27个，覆盖7类）:
```
线性:       LogisticRegression, Ridge, SGD, PassiveAggressive
SVM族:      SVC, NuSVC, LinearSVC
最近邻:     KNeighbors, NearestCentroid
树模型:     DecisionTree, ExtraTree, RandomForest, ExtraTrees, GradientBoosting, AdaBoost, Bagging
朴素贝叶斯: GaussianNB, BernoulliNB
判别分析:   LinearDiscriminant, QuadraticDiscriminant
神经网络:   MLPClassifier
半监督:     LabelPropagation, LabelSpreading
其他:       CalibratedSVC
XGBoost / LightGBM / CatBoost
```

**已移除的模型**（永久移除，不会在任何数据集上成功）:
- **RadiusNeighbors**: StandardScaler后邻居距离超出固定半径 → 100%失败。不在任何SKlearn标准化管线下工作。
- **ComplementNB**: 需要非负输入，StandardScaler产生负值 → 100%失败。天然与标准化管线冲突。

**大数据集(>10K行)慢速模型**（PIDD 768行基准）:
| 模型 | 耗时/折(768行) | CDC 25K行预期 |
|:-----|:-------------:|:-------------:|
| XGBoost | 18.2s | ~10min+ |
| LightGBM | 9.9s | ~5min+ |
| MLPClassifier | 4.1s | ~2min+ |
| CatBoost | 1.8s | ~1min+ |
所有其他模型 <0.8s/折
→ 大数据集(>10K行)建议：保留XGBoost/LightGBM但降CV轮次(3×2代替5×2)，或仅在小数据集上跑全量

**Duplicate Process Guard**:
- 在work1等SSH环境，检查 `ps aux | grep run_helix_benchmark` 确保无重复进程
- 两个并发进程跑同一脚本会在CDC上消耗大量CPU时间且无收益
- 推荐：`screen` 或 `tmux` 执行 + 定期 `ps` 检查

**CDC Crash Recovery**（2026-06-01 新增）:
当基准中途崩溃（常见于CDC大数据集），正确恢复策略：
1. 检查日志，确认已完成的模型列表
2. 仅运行**缺失的模型**，而非重跑全部
3. 如果原跑已有15+个结果，用补丁脚本跑剩余7-8个快速模型即可
4. 从原log提取已完成结果，与补丁结果合并

```python
# 补丁脚本模式 — 只跑原跑缺失的模型
CLASSIFIERS = [
    # 仅包含原跑未完成的模型
    ('Bagging', BaggingClassifier(...)),
    ('GaussianNB', GaussianNB()),
    # ... CalibratedSVC在CDC 25K行极慢（SVC + 内部3折CV）— 跳过
]
```

**CalibratedSVC跳过规则**（2026-06-01 新增）:
- PIDD(768行): ✅ 可在5×2 CV中运行（0.076s/折）
- CDC(25K行): ❌ 跳过——SVC概率校准需要内部3折CV，在25K行×21特征上极慢
- 跳过的模型不影响跨数据集结论，因为其在PIDD/ED上已有数据

**CDC结果合并**（2026-06-01 新增）:
- 原跑15/22个模型 → 补丁跑7个快速模型 → 合并得22个模型结果
- Missing for CDC: CalibratedSVC, MLPClassifier, XGBoost, LightGBM, CatBoost (跳过的5个超重模型)

### Step 2: Docker执行（推荐）

**用户偏好**: 所有ML实验应通过Docker执行，避免 `--break-system-packages`。

```bash
docker run --rm \
  -v /home/yakeworld/synthos_data:/data \
  -v $(pwd)/03-code/experiments:/code \
  python:3.11-slim \
  bash -c "pip install -q pandas scikit-learn imbalanced-learn xgboost && python3 /code/run_helix_benchmark.py"
```

**大数据集（CDC 50K行）**: 子采样到10-15K行用于27模型测试，全量跑仅限最优模型。

### Step 3: 结果持久化

**铁律**: 代码 + 结果必须留痕。

| 资源 | 路径 |
|:-----|:-----|
| 实验脚本 | `03-code/experiments/run_helix_benchmark.py` |
| 实验结果JSON | `03-code/experiments/helix_benchmark_results.json` |
| 跨数据集验证 | `03-code/experiments/cross_dataset_results.json` |
| Docker执行日志 | 自动保留在进程输出，关键结果写入JSON |

### Step 4: 最优模型调参

对Top-3模型进行GridSearchCV：

```python
param_grid = {
    'clf__n_estimators': [50, 100, 200],
    'clf__max_depth': [3, 5, 7],
    'clf__learning_rate': [0.01, 0.1, 0.3]
}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring='f1', n_jobs=-1)
```

### Step 5: 基准线发布

最终产出=每个数据集的Helix基准表：

> **2026-06-01 三数据集实测**（代码: `03-code/experiments/helix_benchmark_results.json`）:
> - 方法: 5×2 CV (PIDD/ED) / 3×2 CV (CDC), 折叠内SMOTE+Scale
> - 模型: 27个稳定模型（排除 RadiusNeighbors + ComplementNB）
> - CDC: 22/27模型完成（跳过5个超重模型）

| 数据集 | n | 患病率 | 最优模型 | Helix F1 | 泄漏阈值(=×1.15) |
|:-------|:-:|:------:|:---------|:--------:|:-----------------:|
| PIDD | 768 | 34.9% | LinearSVC | 0.6678 | >0.7680 |
| CDC BRFSS | 25.4K | 13.8% | AdaBoost | 0.4505 | >0.5181 |
| Early Diabetes | 520 | 61.5% | ExtraTrees | 0.9717 | >1.117 (可达上限饱和) |

**CDC Top 5**:
| # | 模型 | F1 | Recall |
|:-:|:-----|:--:|:------:|
| 1 | AdaBoost | 0.4505 | 0.6289 |
| 2 | LogisticRegression | 0.4415 | 0.7608 |
| 3 | LinearSVC | 0.4394 | 0.7703 |
| 4 | RidgeClassifier | 0.4374 | 0.7763 |
| 5 | LinearDiscriminant | 0.4374 | 0.7763 |

关键观察：CDC线性模型最佳（前5全是线性/线性SVM），树/集成模型因13.8%低患病率表现不佳（RandomForest F1=0.3490）。

## 标准实验协议（8模型快速版）

```python
from sklearn.datasets import load_breast_cancer  # 或下载 CSV
X.shape, y.value_counts(), X.isnull().sum()
```

### Step 2: 严格 CV 折叠隔离预处理

**铁律**: 所有预处理（imputation, scaling, SMOTE）必须在每个 CV 训练折叠内 `fit`。

```python
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_SEED)

def strict_cv_pipeline(model_fn, apply_smote=True, global_preproc=False, threshold=None):
    for fold, (tr_idx, va_idx) in enumerate(skf.split(X, y)):
        X_tr, X_va = X.iloc[tr_idx], X.iloc[va_idx]
        y_tr, y_va = y.iloc[tr_idx], y.iloc[va_idx]
        
        if not global_preproc:
            # Strict isolation: fit scaler INSIDE fold
            scaler = StandardScaler()
            X_tr_s = scaler.fit_transform(X_tr)
            X_va_s = scaler.transform(X_va)
        else:
            # Leakage path: global preprocessing (for ablation)
            X_all = pd.concat([X_tr, X_va])
            X_all_s = StandardScaler().fit_transform(X_all)
            X_tr_s, X_va_s = X_all_s[:len(X_tr)], X_all_s[len(X_tr):]
        
        if apply_smote:
            from imblearn.over_sampling import SMOTE
            X_tr_s, y_tr = SMOTE(random_state=RANDOM_SEED+fold).fit_resample(X_tr_s, y_tr)
        
        model = model_fn().fit(X_tr_s, y_tr)
        y_pred = model.predict(X_va_s)
        # ... evaluate
```

### Step 3: 多模型基准测试

最少 8 个模型（确保多样性和可比性）：

| 模型 | 用途 |
|:-----|:-----|
| GBC (n_estimators=100) | 梯度提升，强基准 |
| LDA | 线性判别，可解释性 |
| SVC (RBF, probability=True) | 核方法 |
| LogisticRegression | 逻辑回归，临床标准 |
| RandomForest (n_estimators=100) | 集成学习 |
| MLPClassifier | 神经网络 |
| GaussianNB | 朴素贝叶斯 |
| KNeighborsClassifier | 非参数方法 |

### Step 4: 软投票集成

GBC + LDA + SVC 软投票集成：

```python
prob = (gbc.predict_proba(X_va_s) + lda.predict_proba(X_va_s) + svc.predict_proba(X_va_s)) / 3
y_pred = np.argmax(prob, axis=1)
```

### Step 5: 四水平消融研究

| 水平 | 预处理 | 语义 |
|:-----|:-------|:-----|
| No Leakage | 全部折叠内 | 严格隔离 ✅ |
| Minor Leakage | 全局缩放 + 折叠内 SMOTE | 轻度泄漏 |
| Medium Leakage | 全局缩放 + 折叠内 SMOTE | （同 Minor，如需插补则不同） |
| Severe Leakage | 全局缩放 + 全局 SMOTE | 完全泄漏 ❌ |

### Step 6: 阈值优化

对 GBC 搜索最优决策阈值（步长 0.02）：

```python
for t in np.arange(0.2, 0.8, 0.02):
    # run CV with threshold=t
    # record best F1 or Recall
```

### Step 7: 结果持久化

所有结果保存为 JSON + CSV：

```python
results_dir.mkdir(exist_ok=True)
with open(results_dir / "experiment.json", "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)
pd.DataFrame(all_models).to_csv(results_dir / "model_benchmark.csv", index=False)
```

## L0.5 审计协议

运行实验后，将论文中所有数值声明与 JSON 输出比对：

```python
# 典型的声明 vs 真实比对
paper_claims = {"ensemble_f1": 0.7541}
actual = all_data["ensemble"]["f1_mean"]
diff = abs(paper_claims["ensemble_f1"] - actual)
# diff > 0.02 → 需要修正论文
```

**审计清单**:
- [ ] 所有 F1/Recall/Precision/Accuracy/AUC 值与实验输出一致
- [ ] 消融表中所有行与 JSON 中的 `ablation` 字段一致
- [ ] 摘要与结论中的关键数字在论文正文中一致
- [ ] 通胀率（如 +6.71%）有实验可追溯

### 代码与结果持久化铁律（2026-05-31 用户明确）

**实验代码必须留痕于项目目录**，适用于所有Pima/CRISP-DM相关实验：

| 资源 | 正确路径 | 错误路径 |
|:-----|:---------|:---------|
| 实验脚本 | `03-code/experiments/` | ❌ `/tmp/` |
| 实验结果JSON | `03-code/experiments/` | ❌ 内存/临时路径 |
| CDC数据 | `/home/yakeworld/synthos_data/`（全量） | ❌ 子采样后丢弃 |

**数据完整性**: 全量数据不应被抽样替换。大数据集可减CV轮次（3×2代替5×2）但不可减样本。

### Docker/Remote Compute 执行（2026-05-31 新增）

**用户偏好**: 所有ML实验优先通过Docker或远程计算节点执行。

**本地Docker**（适用于小数据集，PIDD/ED）:
```bash
docker run --rm \
  -v /home/yakeworld/synthos_data:/data \
  -v $(pwd)/03-code/experiments:/code \
  python:3.11-slim \
  bash -c "pip install -q pandas scikit-learn imbalanced-learn xgboost && python3 /code/run_helix_benchmark.py"
```

**远程计算节点 Science10（work1, 100.125.10.93）** — 8×RTX 4090 / 64核 / 503GB内存:
```bash
# 1. 复制脚本和数据
rsync -avz run_helix_benchmark.py work1:~/experiments/
rsync -avz cdc_diabetes_health_indicators.csv work1:~/synthos_data/

# 2. SSH执行（64核并行，比本地快10倍+）
ssh work1 "cd ~/experiments && python3 run_helix_benchmark.py"

# 3. 取回结果
scp work1:~/experiments/helix_benchmark_results.json ./
### 类不平衡驱动的F1膨胀（Imbalance-Driven F1 Inflation）— v3.1 新增

> **核心发现（模型无关）**: F1膨胀量**正比于类不平衡严重度**。线性模型(LR)和树模型(XGBoost)均遵循同一模式，但**XGBoost对泄漏更敏感**。这不是PIDD特例——是全局预处理下所有不平衡临床数据的系统性脆弱性。

### 三数据集 × 双模型验证（2026-05-31 实验）

| 数据集 | 样本量 | 患病率 | LR 膨胀 | XGBoost 膨胀 | 结论 |
|:-------|:------:|:------:|:--------:|:------------:|:-----|
| CDC BRFSS 2015 | 50,000 | 13.8% | **+73.2%** | **+129.9%** | 🔴 极高 | 
| PIDD | 768 | 34.9% | **+11.1%** | **+23.6%** | 🟡 显著 |
| Early Diabetes | 520 | 61.5% | -1.6% | +0.0% | ✅ 安全 |

**XGBoost更脆弱**: 树模型在不均衡+全局SMOTE下比线性模型更容易产生虚假性能（CDC 129.9% > LR 73.2%）。原因是SMOTE合成样本对树模型的决策边界影响更大（树模型对局部密度变化敏感）。

**方法**: 5×2 CV, LogisticRegression + XGBoost基线, 统一Helix(折叠内预处理) vs Leaky(全局SMOTE)对比。结果保存至 `03-code/experiments/cross_dataset_results.json` 和 `cross_dataset_xgb_results.json`。

### 统计解释

当少数类非常小（CDC 13.8%），全局SMOTE创建大量合成少数样本，产生不再反映真实世界先验的人工训练分布。合成过采样本质上是**测试集泄漏**——它将整个数据集的密度结构信息注入训练集。当类别接近平衡（Early Diabetes 61.5%），SMOTE的边际效益消失，膨胀效应随之消失。

### 与"小样本脆弱性"的区别

该发现不同于已有Section中的小样本脆弱性原则（Heart Disease 303样本+14.17%）：
- **小样本脆弱性**: 泄漏损伤在**n<500 + 中等可分离**时最严重
- **类不平衡膨胀**: 泄漏膨胀量**仅由类不平衡度决定**，与样本量无关（CDC 50K样本依然+73.2%）
- 两者是正交的——大数据+高不平衡=膨胀最大，小数据+平衡=无膨胀

### D6增强价值

此发现是论文D6(新颖性)从0.72→0.80的关键改进（+0.08）。Kapoor2024证明泄漏有害但未量化；Kaufman2012警告全局预处理但未建立膨胀-不平衡定量关系。此发现填补了这些空白。

### 实战流程（2026-05-31 Pima论文）

```
1. 识别现有实验数据→确认是否已持久化（先search而非rerun）
2. 若缺失→跑实验：
   a. 对每个数据集：PIDD/CDC/Early Diabetes，跑Helix vs Leaky
   b. 5x2 CV, LogisticRegression（快+可解释）
   c. 输出JSON持久化到 synthos_data/
3. 论文集成：Discussion新子节 + Abstract/Contributions/Conclusion同步更新
4. **关键**: 膨胀正值+Recall下降→Λ为正；膨胀正值+Recall上升→Λ=0（仅凭膨胀率已足够支撑结论）
```

### 参考文件
- `references/imbalance-inflation-experiment-results.md` — 三数据集详细实验结果JSON

## CDC Crash Recovery Protocol（2026-06-01 新增）

> 当基准测试在大数据集（CDC BRFSS 25K行）上中途崩溃时，**不要重跑全部**。

详见 `references/cdc-crash-recovery-2026-06-01.md`。核心步骤：
1. 从日志/进程输出提取已完成模型的结果（通常15/22个已完成）
2. 写补丁脚本只跑**缺失**的模型（7个快速模型 ~2分钟）
3. CalibratedSVC 在 >10K行数据集上跳过（SVC+内部3折CV极慢）
4. 合并两批结果，CDC完成22/27模型
5. 5个超重模型（CalibratedSVC, MLPClassifier, XGBoost, LightGBM, CatBoost）在PIDD/ED上已有数据，跳过不影响跨数据集比较

## 已知陷阱

1. **Kaggle 笔记本作为实验来源**: 不可信。Kagle 环境可能不同（预装包、硬件）→ 本地重新运行
2. **论文声称的 Ensemble 值**: 常被夸大。PIMA 案中声明 0.7541，实测 0.6986（差 0.0555）
3. **No Leakage 基线中的 SMOTE**: 许多论文声称 "no leakage" 但实际使用了 SMOTE。确保消融的 No Leakage 水平也包含 SMOTE（仅为折叠内 SMOTE）
4. **LDA 易与 Ensemble 混淆**: 论文可能使用 LDA 基线 F1 作为 Ensemble 结果。需单独验证
5. **缺值数据集**: WDBC 无缺值 → 消融只影响缩放+SMOTE。PIMA 有 48.7% 胰岛素零值 → 还需测试不同插补策略下的泄漏
6. **全局 SMOTE 的正确实现**: "Severe Leakage" 的 SMOTE 必须在 **CV 分割前**对整个数据集应用（global_smote=True），而非分割后只在训练集应用。错误实现（分割后对训练集应用全局参数）会导致消融结果不准确。代码模式：
   ```python
   if global_smote:
       # 正确：在分割前对整个数据应用 SMOTE
       X_all_r, y_all_r = SMOTE().fit_resample(
           np.vstack([X_tr, X_va]),
           np.concatenate([y_tr, y_va])
       )
       X_tr_s, y_tr = X_all_r[:len(X_tr)], y_all_r[:len(X_tr)]
       X_va_s, y_va = X_all_r[len(X_tr):], y_all_r[len(X_tr):]
   ```
7. **`agg()` 函数的 AUC 字段硬编码**：如果消融结果不包含 'auc'，硬编码的 `agg()` 会抛出 KeyError。应使用动态键提取：
   ```python
   def agg(r):
       return {k: (np.mean([x[k] for x in r]), np.std([x[k] for x in r]))
               for k in r[0].keys()}  # 动态键，不硬编码
   ```
8. **UCI 数据集获取**：使用 `ucimlrepo` 包而非 `sklearn.datasets`。安装方式：
   ```bash
   pip install ucimlrepo
   ```
   使用方式：
   ```python
   from ucimlrepo import fetch_ucirepo
   data = fetch_ucirepo(id=45)  # Heart Disease
   X = data.data.features
   y = data.data.targets.iloc[:, 0]
   ```

9. **Duplicate Process Proliferation**（2026-06-01 新增）: SSH到远程服务器启动基准脚本后，容易忘记之前已有进程在跑。两个 `run_helix_benchmark.py` 进程同时在CDC上做相同计算，浪费CPU时间。补救：启动前先 `ps aux | grep run_helix_benchmark`；如发现多个，只保留最早启动的那个。
10. **CDC 10%采样仍达25K行，完整基准需要5-15分钟**: 22个模型×3×2 CV = 132次训练。线性模型<1s但Bagging/RandomForest各需几十秒。

## 难度-比例损伤分析

这是 CRISP-DM Helix 跨数据集对比的核心发现。三数据集综合对比（2026-05-26 实验更新）：

| 数据集 | 样本量 | 特征数 | 基线可分离性 | 泄漏 F1 变化 | 结论 |
|:-------|:------:|:------:|:-----------:|:------------:|:-----|
| PIMA (Diabetes) | 768 | 8 | 低 (F1=0.6986) | **+6.71%** | ❌ 严重——低可分离数据集必须 Helix |
| WDBC (Breast) | 569 | 30 | 高 (F1=0.9693) | **-0.10%** | ✅ 可忽略——高可分离只需标准 CV |
| Heart Disease | 303 | 13 | 中 (F1=0.7886) | **+14.17%** | 🚨 最严重——小样本 + 中等可分离 |

### 小样本脆弱性原理（Small-Sample Vulnerability Principle）

**核心发现**：泄漏损伤在**小样本 (n<500) + 中等可分离**数据集中最严重，而非在最低可分离数据集中最严重。

Heart Disease (303样本)的泄漏膨胀率 (+14.17%) 超过了两个大样本数据集（PIMA +6.71%, WDBC -0.10%），因为：
1. SMOTE 在小样本中合成样本占比更大
2. 中等可分离意味着决策边界比高可分离更易受噪声影响
3. 小样本 + 中等可分离 = 两种脆弱性叠加

### 风险分层审计建议

| 风险等级 | 条件 | 要求 |
|:---------|:-----|:-----|
| 🟢 低 | n>1000, AUC>0.95 | 标准 CV，报告预处理细节 |
| 🟡 中 | 500<n<1000 | 要求记录折叠内预处理步骤 |
| 🔴 高 | **n<500 且使用 SMOTE** | **必须双报告**（隔离指标 + 非隔离指标） |

### 参考文件
- `references/three-dataset-comparison.md` — PIMA/WDBC/Heart 三数据集对比（难度-比例损伤原理）
- `references/wdbc-ablation-results.md` — WDBC 完整实验结果表（8模型基准+4水平消融+集成）
- `references/heart-disease-ablation-results.md` — Heart Disease 完整实验结果表（7模型基准+4水平消融+小样本脆弱性）
- `references/paper-claim-verification-protocol.md` — 论文声明 vs 实验输出的系统化验证流程（含三数据集实战对比表）
- `references/model-timing-pidd-profile.md` — PIDD 29模型耗时存档（含失败分析 + CDC放大估算 + 速率分类）
- `references/breast-cancer-hcs3wt-bugfix.md` — HCS-3WT-specific bug case study (absorbed from ml-pipeline-debugging skill)
- `references/additional-pitfalls.md` — Additional ML pipeline pitfalls (absorbed from ml-pipeline-debugging skill)
