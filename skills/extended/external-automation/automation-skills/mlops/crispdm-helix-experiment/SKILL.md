---


name: crispdm-helix-experiment
description: CRISP-DM Helix methodology — strict CV-fold-isolated preprocessing for clinical ML experiments on public datasets. Generates real, traceable L0.5-compliant data.
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
    version: 1.0.0
    author: Synthos
    signature: 'dataset: str -> experiment_results: dict'
    related_skills:
    - experiment-recipes



---



## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# CRISP-DM Helix Experiment Pipeline

## 核心原则

**Helix隔离**：预处理必须严格在CV fold内部执行，防止数据泄漏。

```
原始数据
  ↓
CV Fold分割 (StratifiedKFold, n_splits=5-10)
  ↓
每折内部: 预处理(归一化/降采样/特征选择) → 训练 → 评估
  ↓
跨折汇总指标: mean ± std
```

## 标准模板

```python
import pandas as pd
from sklearn.model_selection import StratifiedKFold

df = pd.read_csv('data.csv')
X = df.drop(columns=['target'])
y = df['target']
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    # 预处理（在fold内部！）
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # 只用train拟合

    # 训练+评估
    # ...
```

## 泄漏模式对比实验

| 模式 | 预处理位置 | 预期效果 |
|:-----|:----------|:---------|
| Helix (正确) | 每折内部fit | 真实泛化性能 |
| No Leakage (理论) | 全部fit | 同上（预处理不影响CV） |
| Medium Leakage | 部分fit | 轻微高估 |
| Severe Leakage | 全局fit | F1虚高5-15% |

## 多数据集验证（2026-06-22 全面更新）

同一代码管线运行于 3+ 数据集，覆盖 Helix → ImputeLeak → SMOTELeak → SevereLeak 四级泄漏：

| 数据集 | N | 患病率 | Helix F1(LR) | SMOTELeak(LR) | 膨胀(LR) | Helix F1(RF) | SMOTELeak(RF) | 膨胀(RF) | 风险 |
|:-------|:-:|:------:|:----------:|:-------------:|:--------:|:----------:|:-------------:|:--------:|:----:|
| Synth-Imb-1% | 5000 | **1.0%** | 0.326 | 0.328 | +0.6% | 0.114 | 0.247 | **+116.6%** | 🔴🔴 |
| Synth-Imb-5% | 5000 | **5.0%** | 0.549 | 0.580 | +5.7% | 0.594 | 0.765 | **+28.8%** | 🔴🔴 |
| PIMA (PIDD) | 768 | 34.9% | 0.636 | 0.712 | +12.0% | 0.635 | 0.856 | **+34.9%** | 🔴 |
| Titanic | 891 | 38.4% | 0.732 | 0.809 | +10.5% | 0.762 | 0.885 | **+16.2%** | 🔴 |
| WDBC | 569 | 62.7% | 0.979 | 0.961 | -1.9% | 0.965 | 0.940 | -2.6% | 🟢 |
| Iris | 150 | 33%×3 | 0.953 | 0.953 | ±0% | 0.946 | 0.946 | ±0% | 🟢 |
| Wine | 178 | 33%×3 | 0.983 | 0.992 | +0.8% | 0.978 | 0.989 | +1.1% | 🟢 |
| Digits | 1797 | 10%×10 | 0.971 | 0.973 | +0.2% | 0.978 | 0.979 | +0.1% | 🟢 |

**核心规律（三阶效应）**：

1. **泄漏损伤 = f(不平衡度, 模型复杂度)** — 1%正类率+RF=116%膨胀；35%+RF=35%膨胀；平衡数据集不受影响
2. **集成模型比线性模型受害更深** — RF 受害程度通常是 LR 的 3-10 倍。原因是 RF 的复杂决策边界更容易被合成样本误导
3. **基本预处理泄漏(全局impute+scale)对LR几乎无影响** — 真正的泄漏来自全局SMOTE和全局特征选择

**注意**: 同一泄漏机制在不同数据集上表现截然不同（PIDD: +12%, Cleveland: -2.0%, WDBC: -2.6%）。不可跨数据集推广泄漏损伤模式。

## Notebook-to-Script Alignment Methodology

当用户要求「按照jupyter notebook流程和论文需要，认真完成每一个步骤的实验」时：

1. **完整读取notebook**：用`json.load()`读取.ipynb文件，遍历`nb['cells']`
2. **逐Cell解析**：区分markdown（跳过）和code（提取完整source）
3. **按顺序映射步骤**：Cell 0→N，记录每个Cell的输入/输出关系
4. **忠实还原**：不添加、不删除任何实验步骤；参数必须与notebook完全一致
5. **输出验证**：生成JSON + CSV + Python脚本，与notebook单元格一一对应

**关键陷阱**：
- 外部模型（XGBoost、LightGBM、CatBoost）不在sklearn.all_estimators()中，需单独添加
- `sklearn.metrics.make_scorer()`在sklearn 1.8+中required：不能直接传递函数引用，必须用`make_scorer(func, needs_proba=True)`
- CatBoost的`get_params()`返回空字典——使用`iterations`而非`n_estimators`
  - CatBoost默认1000次迭代→33模型×10折≈950秒。设`iterations=100`提速
  - **NumPy生态锁步升级**：shap/scipy/pandas/numexpr/bottleneck/numba等C扩展包必须numpy版本一致。升级numpy会同时破坏所有依赖（`AttributeError: module 'numpy' has no attribute 'long'`），降级numpy会破坏shap（`numpy.dtype size changed`）。遇到numpy相关ImportError时：①检查pip list中numpy版本 ②检查系统包`/usr/lib/python3/dist-packages/`中的numexpr/bottleneck是否也编译自旧numpy ③统一回退到兼容版本组合（numpy 1.26.4 + scipy 1.11.4 + pandas 2.1.4是已知安全组合） ④shap必须用虚拟环境隔离运行，因为系统numexpr（Debian包）无法通过pip移除且始终编译自旧numpy

## PIDD (PIMA) 基准结果

**33个模型 10-Fold CV Top 10 (F1排序):**

| 排名 | 模型 | F1 | Acc | AUC | Recall |
|:----:|:-----|:---|:----|:----|:-------|
| 1 | CatBoostClassifier | 0.7067±0.0794 | 0.7759 | 0.8422 | 0.7756 |
| 2 | GradientBoostingClassifier | 0.6857±0.0626 | 0.7616 | 0.8378 | 0.7464 |
| 3 | MLPClassifier | 0.6806±0.0584 | 0.7617 | 0.8286 | 0.7316 |
| 4 | LogisticRegression | 0.6759±0.0848 | 0.7603 | 0.8373 | 0.7165 |
| 5 | LinearDiscriminantAnalysis | 0.6759±0.0862 | 0.7629 | 0.8370 | 0.7091 |
| 6 | RidgeClassifier | 0.6759±0.0862 | 0.7629 | 0.8369 | 0.7091 |
| 7 | SVC | 0.6758±0.0654 | 0.7512 | 0.8266 | 0.7422 |
| 8 | AdaBoostClassifier | 0.6758±0.0337 | 0.7500 | 0.8287 | 0.7426 |
| 9 | NuSVC | 0.6756±0.0679 | 0.7512 | 0.8241 | 0.7420 |
| 10 | LogisticRegressionCV | 0.6749±0.0900 | 0.7589 | 0.8366 | 0.7164 |

**关键发现：** Top 10 F1差异极小（0.6749-0.7067），CatBoost领先约3%。LogisticRegression、LDA、Ridge的F1完全一致（0.6759）。Ensemble (LDA+GBC+LR soft voting) F1=0.6878，略优于单模型。PIMA数据太小（768样本），所有模型性能差异极小。

## 教育数据集泄露审计 (Educational Dataset Audit)

> 2026-06-22 新增方向。对 Kaggle/Tianchi 上用于初学者教学的经典数据集进行系统性泄漏检查，形成教学规范。

### 触发条件

当用户提到：
- "检查 Kaggle 热门教程的数据泄露"
- "教育数据集审计 / 教学规范"
- "初学者入门数据集的正确基线"
- "纠正高赞 notebook 的错误预处理"

### 核心发现（基于 PIDD/Iris/WDBC 基线实验）

使用 **LogisticRegression + 仅全局 imputation/scaling**（不含 SMOTE）时：

| 数据集 | Helix F1 | Leaky F1 | F1 膨胀 | 判定 |
|:-------|:--------:|:--------:|:-------:|:----:|
| PIDD | 0.6360 | 0.6373 | +0.2% | ✅ 干净 |
| Iris | 0.9566 | 0.9566 | +0.0% | ✅ 干净 |
| WDBC | 0.9807 | 0.9807 | +0.0% | ✅ 干净 |

**关键结论**：
1. **基本预处理泄漏（全局 imputation + scaling）对 LR 影响极小**（+0.2% 以内）
2. **真正的数据泄漏来源于全局 SMOTE 和全局特征选择** — 这才是 Kaggle 高赞 notebook 的常见错误
3. 入门级教育数据集（Iris）太简单，泄漏难以体现
4. 不平衡数据集（PIDD 35%, WDBC 37%）在不同泄漏模式下表现截然不同

### 审计协议（四步法）

```python
# 标准审计管线流程
1. 加载数据集（本地 / sklearn / UCI / Kaggle / synthetic）
2. 对每种泄漏模式（Helix, ImputeLeak, SMOTELeak, SevereLeak）运行5×2 CV：
   - Helix: impute+scale 在每折内部
   - ImputeLeak: 全局 impute+scale 后分割
   - SMOTELeak: 全局 SMOTE 后分割
   - SevereLeak: 全局 SMOTE + impute + scale 后分割
3. 对每个协议收集 LR 和 RF 的 F1/Recall/Precision
4. 对比输出 JSON 报告 → 生成教学规范文档
```

### 合成高不平衡数据集方法

当真实极端不平衡数据集（Credit Card Fraud 66MB）无法下载时，使用 sklearn 合成数据：

```python
from sklearn.datasets import make_classification
X, y = make_classification(
    n_samples=10000, n_features=29, n_informative=14,
    n_redundant=2, n_clusters_per_class=1,
    weights=[0.9983, 0.0017],  # 0.17% 患病率
    flip_y=0.01, random_state=42
)
```
这在教学上反而更优——已知真实分布，可精确控制不平衡度，完全可复现。

### 教育数据集优先级

| 优先级 | 数据集 | 难度 | 泄漏检查要点 |
|:------:|:-------|:----:|:------------|
| P0 | Titanic | 入门 | 全局填充 + 特征工程泄漏 |
| P0 | House Prices | 入门 | 全局标准化 + 特征选择泄漏 |
| P0 | Credit Card Fraud | 不平衡 | 全局 SMOTE 泄漏（最严重） |
| P1 | Wine Quality | 分类 | 全局标准化泄漏 |
| P1 | Diabetes 130-US | 医疗 | 全局 SMOTE 泄漏 |
| P2 | MNIST | 图像 | 预处理泄漏（像素标准化） |

### 教学规范输出格式

每篇数据集产出一份 `04-standards/{dataset}.md`：
1. 数据集描述和统计
2. Kaggle 高赞 notebook 常见的泄漏模式
3. 正确的 Helix 基线指标
4. "为什么你的 99% 是假的" — 面向初学者的解释
5. 正确和错误的代码对比示例

### 参考文件

- `references/educational-dataset-audit-protocol.md` — 审计协议详解（项目路径、脚本、数据源）

- `references/helix-pipeline-template.py` — 完整Helix实验代码
- `references/cross-dataset-protocol.md` — 跨数据集验证协议
- `references/leakage-patterns.md` — 四种泄漏模式详解
- `references/cleveland-heart-leakage-experiment.md` — Cleveland Heart 泄漏消融实验（Negligible/反向模式）
- `references/notebook-to-script-alignment.md` — Notebook→Script对齐方法论
- `references/model-list-reconciliation.md` — Notebook模型清单与script硬编码清单的对齐方法论（含PIMA 33模型案例、已验证陷阱列表）
- `references/notebook-models-33-models-alignment.md` — PIMA 33模型对齐案例：notebook all_estimators()动态生成 vs helix硬编码清单的差异发现与修复过程