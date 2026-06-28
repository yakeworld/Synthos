---
name: kaggle-leakage-audit
description: Kaggle教育数据集数据泄露审计 — Helix vs Leaky 基准对比，建立每个入门数据集的真实基线 + 预警阈值
version: 1.0.0
author: Synthos
priority: P1
license: MIT
related_skills: [crispdm-helix-experiment, quality-gate]
allowed-tools:
- terminal
- read_file
- write_file
- search_files
- patch
- cronjob

metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'dataset: str -> audit_report: dict'
    atom_type: skill
    priority: P1

---

## BOUNDARY

**范围**：对所有常用教育/入门级别的公开数据集执行 Helix vs Leaky 对比审计。
**不覆盖**：深度学习模型（CNN/Transformer）、图像数据、时序数据。
**触发**：新的教育数据集被发现/需要审计时、Kaggle 热门 notebook 方法论更新时。
**退出**：审计报告写入 `03-reports/`，教学规范更新到 `04-standards/`。

## IO_CONTRACT

- **input**: `datasets: list[str], models: list[str], leakage_levels: list[str]`
- **output**: `audit_report: dict (per-dataset Helix F1, Leaky F1, inflation %, verdict)`

## EVIDENCE_SCHEMA

| 证据类型 | 来源 | 验证方式 |
|----------|------|----------|
| Helix F1 | 5×2 CV 实验输出 | 可复现的 Python 脚本 |
| Leaky F1 | 同样管线 + 全局预处理 | 同一脚本，不同分支 |
| 膨胀率 | (Leaky - Helix) / Helix | 自动计算 |
| 教育规范 | 审计结果汇总 | 人工审核后定稿 |

## CHANGE_LOG

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-22 | 1.0.0 | 创建。初始审计覆盖9数据集（Titanic, PIDD, Iris, WDBC, Wine, Digits + 3合成）。 |

---

# Kaggle 教育数据集数据泄露审计

## 原理

> **核心认知**：入门数据集上的"高准确率"往往不是算法厉害，而是**全局 SMOTE / 全局标准化**泄露了测试集分布到训练过程。

Helix 协议：所有预处理（impute + scale + SMOTE）严格在 CV 折内部执行。
Leaky 协议：全局预处理后分割，模拟 Kaggle 热门 notebook 的常见错误。

## 触发条件

1. 新教育数据集被发现
2. Kaggle 热门 notebook 方法论异常（F1 显著高于 Helix 基线）
3. 定期 cron 审计（季度/半年度）
4. 用户明确要求审计特定数据集

## 执行步骤

### 1. 加载技能

```
skill_view(name='kaggle-leakage-audit')
```

### 2. 添加数据集

编辑 `02-benchmarks/run_audit_v2.py`，在 `DATASETS` 列表末尾添加新条目：

```python
DATASETS = [
    ("PIMA (PIDD)", load_pima),
    ("Titanic", load_titanic),
    ("Iris", load_iris),
    # 添加新数据集:
    ("MyDataset", load_mydataset),
]
```

每个加载器返回 `(df, target_col, features_list)`。

### 3. 运行审计

```bash
cd <audit_dir>/02-benchmarks && python3 run_audit_v2.py
```

输出：JSON 报告到 `03-reports/`。

### 4. 更新教育规范

审计结果出来后，更新 `04-standards/kaggle_leakage_educational_standard.md` 中的表格。

### 5. 标记异常

如果某数据集的 Leak F1 显著高于 Helix F1（膨胀率 > 5%），在该数据集的 01-datasets/ 下创建 `WARNING.md`：

```markdown
# 数据泄露警告

数据集: Titanic
Helix F1(LR): 0.732
Leaky F1(LR): 0.809
膨胀率: +10.5%
高危信号: 任何声称 F1 > 0.85 的教程

## 泄漏方式
全局 SMOTE 在 train_test_split 之前。

## 正确做法
SMOTE 在 CV 折内部。
```

## 项目结构

```
kaggle-leakage-audit/
├── 01-datasets/           # 数据集（每个子目录一个数据集）
│   ├── titanic/
│   ├── pima/
│   └── ...
├── 02-benchmarks/
│   ├── run_audit.py       # v1 基线版本
│   └── run_audit_v2.py    # v2 增强版（多模型+多泄漏模式）
├── 03-reports/
│   └── kaggle_audit_v2.json  # 审计结果
└── 04-standards/
    └── kaggle_leakage_educational_standard.md  # 教学规范
```

## 已知基线（2026-06-22）

| 数据集 | Helix F1(LR) | 预警阈值 | 膨胀率(RF) | 风险 |
|:-------|:-----------:|:---------:|:----------:|:----:|
| Titanic | 0.732 | F1>0.80 | +16.2% | 🔴 |
| PIDD | 0.636 | F1>0.70 | +34.9% | 🔴 |
| Iris | 0.953 | — | ±0% | 🟢 |
| WDBC | 0.979 | F1>0.99 | -2.6% | 🟢 |
| 1%合成 | 0.326 | F1>0.35 | +116.6% | 🔴🔴 |

## 泄漏模式定义

| 模式 | 含义 | 杀伤力 |
|:-----|:-----|:------|
| Helix | 所有预处理在 CV 折内部 | 基线（正确） |
| ImputeLeak | 全局 impute + scale i>- 分割 | 几乎无影响 |
| SMOTELeak | 全局 SMOTE → 分割 | 🔴 主要杀伤来源 |
| SevereLeak | SMOTE + impute + scale 全局 | 🔴 与纯 SMOTE 一致 |

## 规律总结

1. 不平衡度越高 → 泄漏杀伤越大
2. 模型越复杂（RF/XGB）→ 受害越深
3. 只有全局 SMOTE 造成实质性泄漏；全局标准化几乎无害
4. 平衡/多类数据集不受影响
5. 极度不平衡(0.17%)时所有模型 F1≈0，SMOTE 也无法挽救

## 参考

- `references/educational-standard.md` — 完整教学规范（04-standards/）
- `references/run_audit_v2.py` — Python 审计脚本（02-benchmarks/）
