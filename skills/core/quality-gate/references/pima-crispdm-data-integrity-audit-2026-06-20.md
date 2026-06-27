# PIMA-CRISPDM 数据完整性审计失败记录

## 事件

2026-06-20 用户要求 Review pima-crispdm 论文投稿。独立复现发现数据一致性严重问题。

## 发现

### Notebook 多配置冲突
Notebook `crisp-dm-pima.ipynb` 包含 8+ code cells，其中 4 个不同 VotingClassifier 配置产生不同结果：

| Cell | 配置 | F1 | Acc | Recall |
|:---|:---|:---:|:---:|:---:|
| 24 | Curated Voting CV (best) | 0.6878 | 0.7655 | 0.7426 |
| 26 | Pipeline 10-fold CV | 0.6420 | 0.7734 | 0.5825 |
| 27 | Pipeline variant A | 0.6330 | 0.7682 | 0.5789 |
| 28 | Pipeline variant B | 0.6907 | 0.7681 | 0.7426 |
| 31 | Standalone test | 0.6522 | 0.7500 | 0.6716 |

论文声称 **F1=0.6857** — 在 notebook 中**不存在**任何匹配。最接近的是 Cell 24 (0.6878) 和 Cell 28 (0.6907)，差异 0.001-0.005。

### 独立复现
独立复现得到 F1=**0.6177**，与论文声称差异 **-11.3%**，超出 L0.5 容忍阈值。

### 根因分析
1. Notebook 不是确定性管线：多个 cell 测试不同配置，结果差异达 0.07 F1
2. 论文选择了"最佳"而非"最稳定"的输出
3. 论文数字 0.6857 无法对应任何 cell 输出 — 可能是中间状态、不同随机种子、或手动调整
4. state.json notes 声称 "Data fabrications replaced with actual experiment output"，但实际数字仍不可复现

## 判定

**DATA_SUSPECT** — 该论文不满足 L0.5 数据诚实门。核心数字无法从提供的代码复现。

## 修复建议

1. 精简 notebook 为单一确定管线（只保留最终使用的配置）
2. 用精简后的管线重新跑实验，得到可复现的 F1 值
3. 论文数字必须与 notebook 输出精确匹配（<1% 浮点误差）
4. 若 F1=0.6177 是正确值，需要重写论文中的 0.6857 所有出现
5. 多配置 notebook 的论文不适合投稿 — 必须用独立脚本替代

## 影响

此案例导致 pima-crispdm 论文**不适合直接投稿**。建议优先处理其他论文管线。

---

## 后续审计：2026-06-25 — 修复后验证

### 背景
对修回后版本（01-manuscript/paper.tex）进行第二次数据完整性审计。修回已处理：作者署名、SHAP标注、CatBoost 10-fold统一、SMOTE数学推导等。目的是验证"修复后是否满足 L0.5 数据诚实门"。

### 审计方法
遍历 paper.tex 中所有数值声明（35个关键数值），与以下多源交叉比对：
1. `all_results.json` — 综合结果
2. `comprehensive_results.json` — SHAP+Ensemble
3. `cross_dataset_catboost_10fold.json` — CatBoost 10-fold验证
4. `cross_dataset_xgb_results.json` — XGBoost跨数据集

### 发现

| 类别 | 可追溯 | 不可追溯 | 通过率 |
|:-----|:------:|:--------:|:------:|
| 抽象四阶段泄漏 | 6/6 | 0 | 100% |
| CatBoost主基准 | 5/5 | 0 | 100% |
| SHAP特征值 | 3/3 | 0 | 100% |
| CatBoost 10-fold | 2/2 | 0 | 100% |
| XGBoost跨数据集 | 3/3 | 0 | 100% |
| **Ensemble组成+统计量** | **0/2** | **2** | **0%** |
| **总计** | **19/21** | **2** | **90.5%** |

### 不可追溯项

#### 1. Ensemble 组成矛盾 🔴 P0
| 来源 | Ensemble成员 | F1值 |
|:-----|:-------------|:----:|
| 论文声称（L30/L264） | **CatBoost+GBC+LR** | **0.6973** |
| `all_results.json` | GBC+LDA+LR | 0.6857 |
| `comprehensive_results.json` | VotingClassifier(LDA+GBC+LR) | 0.6878 |
| `ensemble_results.json` | GBC+LDA+SVC | 0.6699 |

**判决：论文声称的 Ensemble 组成和 F1 值在三份独立代码输出中均不存在。** 三份不同 JSON 输出互相一致（GBC+LDA+LR 系），而论文单独声称了不同的组成和更高的 F1。

#### 2. 统计值无源 🟡 P1
论文声称 `p=0.59, d=0.28`（CatBoost vs Ensemble 配对t检验），但在 `all_results.json`、`comprehensive_results.json`、任何 JSON 输出或 Python 脚本中都**找不到对应的统计检验代码或输出**。

### 修复建议
1. Ensemble 描述修正为 GBC+LDA+LR，F1=0.686
2. 删除 p=0.59, d=0.28，或补写配对t检验脚本并运行

### 关键教训
- **JSON-to-JSON 三角校验**是否执行不能只检查"有没有跑"，还要看"输出是否一致"。本例中多JSON源一致（GBC+LDA+LR），论文声称不一致（CatBoost+GBC+LR）
- **Ensemble 组成**是最容易被 LLM 编造的声明之一——比单个数值更容易被改（因为改一个模型名不影响其他数字）
- **统计量**（p值、Cohen's d）必须有对应的统计检验脚本 + 输出文件，不可仅作为文本写入 paper.tex
- **修复后的 L0.5 门**：19/21（90.5%）通过，2个不可追溯项仍需人工修复
