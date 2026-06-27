# cross-dataset-consistency-check

## crispdm-wdbc 实战案例（2026-06-27）

### 背景
state.json audit_history 记录："P2: Cross-dataset delta convention inconsistency (PIDD=absolute, Heart F1=relative, mixed)"

### 重验证过程
独立计算三个数据集的 F1 和 Recall 的绝对差值和相对百分比：

| 数据集 | F1 绝对差 | F1 相对% | Recall 绝对差 | Recall 相对% |
|:-------|:---------:|:--------:|:------------:|:------------:|
| PIDD   | +0.0671 | +9.60% | -0.1136 | -15.15% |
| Heart  | +0.1118 | +14.18% | +0.1023 | +12.82% |
| WDBC   | -0.0010 | -0.10% | +0.0056 | +0.58% |

### 发现
**三个数据集使用完全相同的约定：绝对差值 × 100**

- Paper text: +6.71% = 0.0671 × 100 (PIDD F1)
- Paper table: +0.0671 (PIDD F1)
- 三数据集一致，所有文本和表格都使用绝对值×100

### 结论
**state.json P2 标记为假阳性**。旧审计直接引用了之前的记录，没有独立计算验证。

### 教训
1. **永远不要假设 state.json 中的 P2 标记正确** — 它只是历史声称
2. 每次重验证必须独立计算绝对差值和相对百分比
3. 当绝对值×100 的数值恰好等于相对百分比时（如 Heart F1 14.18%），容易掩盖约定是否一致
4. 高基线值（WDBC F1>0.96）使绝对值和相对值几乎相同，更难区分
