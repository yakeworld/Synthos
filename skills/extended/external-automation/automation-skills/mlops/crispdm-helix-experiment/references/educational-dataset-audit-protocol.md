# 教育数据集泄露审计协议

> 2026-06-22 第一次执行创建。项目路径见下方。

## 项目结构

```
Synthos/outputs/papers/kaggle-leakage-audit/
├── 01-datasets/          # 数据集（手动下载或从本地复制）
│   ├── pima/
│   ├── titanic/
│   ├── heart/
│   └── ...
├── 02-benchmarks/        # 审计脚本
│   └── run_audit.py      # Helix vs Leaky 对比管线（5x2 CV, LogisticRegression）
├── 03-reports/           # 自动输出的 JSON 报告
│   └── kaggle_audit_results.json
└── 04-standards/         # 教学规范文档（待填充）
    └── {dataset}_standard.md
```

## 审计脚本

`02-benchmarks/run_audit.py` — 单文件全功能审计管线：

- 支持多个数据集加载器（本地 CSV / sklearn 内置 / UCI）
- 执行 5×2 CV StratifiedKFold 对比（Helix 内部预处理 vs 全局预处理）
- 输出 F1 / Recall / Precision / AUC 指标和膨胀百分比
- 自动保存 JSON 报告到 `03-reports/`

## 数据集加载策略

| 数据集 | 加载方式 |
|:-------|:---------|
| PIMA (PIDD) | 本地 CSV（列名: Pregnancies,Glucose,...,Outcome） |
| Iris | `sklearn.datasets.load_iris()` |
| WDBC | `sklearn.datasets.load_breast_cancer()` |
| Titanic | Kaggle train.csv（需下载） |
| Heart Disease | UCI heart.csv（需下载） |
| Wine Quality | UCI winequality-*.csv（需下载） |
| Credit Card Fraud | Kaggle creditcard.csv（需下载） |

## 泄漏模式分级

| 级别 | 操作 | 预期 F1 膨胀 |
|:-----|:-----|:-------------|
| L0 — 无泄漏 | fold 内 impute + scale | 0%（基线） |
| L1 — 轻微泄漏 | 全局 impute | <1% |
| L2 — 中等泄漏 | 全局 impute + scale | +1-3% |
| L3 — 严重泄漏 | 全局 impute + scale + SMOTE | +5-30%（取决于不平衡程度） |

**2026-06-22 实证**: L1-L2 对 LR 膨胀 < 0.2%。真正的教学陷阱在 L3（全局 SMOTE），这是 Kaggle 高赞 notebook 的常见错误。

## 基础脚本引用

`run_audit.py` 的核心架构可复用。如需扩展（如增加 CatBoost/XGBoost 或多折验证），参考 `crispdm-helix-experiment` 技能的主 SKILL.md 中的 33 模型实验模板。
