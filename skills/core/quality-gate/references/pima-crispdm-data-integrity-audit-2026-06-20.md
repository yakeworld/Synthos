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
