# 三数据集三损伤模式验证（2026-06-04）

> WDBC + Heart + PIDD 的 CRISP-DM Helix 交叉验证，揭示泄漏损伤的三个不同病理模式。

## 实验设置

所有数据集使用统一协议：
- 10-fold stratified CV
- StandardScaler + SMOTE（折叠内隔离 vs 全局）
- GBC 作为消融基模型（n_estimators=100）
- 软投票集成 Ensemble (GBC+LDA+SVC)

## 核心数值

| 数据集 | N | 特征 | 患病率 | Helix F1 | Severe F1 | ΔF1 | ΔRecall | 模式 |
|:-------|:-:|:----:|:------:|:--------:|:---------:|:---:|:--------|:-----|
| **PIDD** (Pima) | 768 | 8 | 34.9% | 0.6986 | 0.7657 | **+9.6%** | **-11.4%↓** | Recall Paradox |
| **Heart** (Cleveland) | 303 | 13 | 45.9% | 0.7886 | 0.9004 | **+14.2%** | **+10.2%↑** | Universal Metric Inflation |
| **WDBC** (Breast) | 569 | 30 | 37.3% | 0.9693 | 0.9683 | **-0.1%** | **+0.6%↑** | Negligible |

## 三个损伤模式

### 模式 1：Recall Paradox（F1↑, Recall↓）
- **出现条件**: 基线强分类器(Ensemble)在决策边界附近 + 不平衡数据
- **临床风险**: 🔴 高 — F1看起来更好但模型实际上召回更差
- **原因**: 全局SMOTE制造的合成样本扭曲了少数类的决策边界，使Precision提升远超Recall下降
- **典型数据集**: PIDD (Pima Indians)

### 模式 2：Universal Metric Inflation（所有指标↑）
- **出现条件**: 基线有余量 + 中等可分离 + 弱/中强分类器
- **临床风险**: 🟡 中 — 数值全部虚高但方向一致，不产生Recall悖论
- **原因**: SMOTE合成样本增加了可学习的模式，全局缩放提供了测试集分布信息
- **典型数据集**: Heart (Cleveland, 303 samples)

### 模式 3：Negligible（无变化）
- **出现条件**: 高可分离数据集（基线 AUC > 0.99）
- **临床风险**: 🟢 低 — 泄漏无实际影响
- **原因**: 类别分布已经充分分离，额外信息无法改变决策边界
- **典型数据集**: WDBC (Wisconsin Breast Cancer)

## 关键发现

1. **Recall Paradox 不是普遍的** — 仅在特定条件下（强模型+决策边界附近+不平衡）出现
2. **PIDD 的 +6.71% F1 膨胀 + Recall 下降 ≠ 所有数据集的泄漏表现**
3. **Heart 的 +14.2% F1 膨胀伴随 Recall 上升** — 泄漏损伤方向与基线模型强度相关
4. **WDBC 泄漏无效** — F1 变化 -0.1% 在 CV 标准差范围内

## 对论文写作的启示

1. 论文不应声称"泄漏总是同时提升F1降低Recall" — 这是PIDD特例不是普遍规律
2. 应区分两种泄漏损伤模式：Recall Paradox vs Universal Metric Inflation
3. 高分离数据集（如WDBC）的泄漏研究本身有价值——证明泄漏损伤不是统一的

## 代码验证

WDBC: `wdbc_crispdm_helix.py` → `results_wdbc/wdbc_definitive.json`
Heart: `heart_crispdm_helix.py` → `results/heart_definitive.json`
