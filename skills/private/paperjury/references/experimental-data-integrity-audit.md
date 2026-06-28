# 论文数值 claim 代码回查协议

> 当论文包含实验指标数值（F1、AUC、Recall、Precision、Accuracy、膨胀百分比等）时，必须逐条验证是否有对应的代码输出支撑。

## 核心原则

1. **不信任任何来源的数字** — paper.tex、state.json、notebook cell output 中的数值都可能被修改过、过时了、或伪造的
2. **只信任独立运行的代码输出** — JSON + CSV 双文件归档，可复现
3. **发现断裂即记录** — 哪行数值没有对应代码，明确记录

## 审计步骤

### Step 1: 提取论文中的数值 claim

```bash
grep -n "0\.[0-9]\{4\}" paper.tex | grep -i "f1\|auc\|recall\|precision\|accuracy\|inflation\|metric"
```

### Step 2: 逐个检查是否有代码输出

对每个数值：
1. 搜索 03-code/ 目录下是否有生成该数值的代码
2. 检查代码输出（JSON/CSV）是否包含该数值
3. **如果没有 → 标记为 FABRICATED**
4. **如果有但数值不匹配 → 标记为 MISMATCH**

### Step 3: 运行独立复现

如果数值没有代码支撑或数值不匹配：
1. 编写独立复现代码（放在 `03-code/experiment/` 下）
2. 使用与论文相同的数据、相同的预处理逻辑、相同的评估指标
3. 运行 10-fold CV（或论文指定的 CV 策略）
4. 输出 JSON（汇总结果）+ CSV（逐 fold 原始数据）
5. 在 summary 中标注：claimed vs actual，diff 和匹配状态

### Step 4: 报告结果

```
Paper claim: F1=0.6878 (No Leakage)
Actual:      F1=0.6857 (±0.0767)
Diff:        -0.0021
Status:      ✓ CLOSE (within 0.02 tolerance)

Paper claim: F1=0.8140 (Severe Leakage)
Actual:      F1=0.6661 (±0.0656)
Diff:        -0.1479
Status:      ✗ FABRICATED (no code backing)
```

## 常见陷阱

1. **Notebook 输出可能是旧的** — 代码修改后 notebook 输出未更新
2. **不同代码路径产生不同结果** — Cell 24 的 Pipeline+cross_validate 与 manual folds 结果不同
3. **参数差异** — 相同的模型名但不同 hyperparameters 产生不同结果
4. **版本差异** — sklearn/imblearn 版本不同导致数值波动
5. **Ensemble 组件不同** — 论文说 GBC+LDA+LR，代码实现是 GBC+LDA+SVC

## 输出格式

JSON 必须包含：
- `experiment`: 实验名称
- `dataset`: 数据集信息
- `levels`: 各实验条件的描述
- `summary`: 每个条件的完整指标
- `experiment_date`: 执行日期
- `level_names`: key 到名称的映射

CSV 必须包含逐 fold 原始数据。
