# Paper Claim Verification Protocol

> 从实验输出到论文声明的系统化验证流程。
> 2026-05-26 实战累积：PIMA（22处修正）、WDBC（验证通过）、Heart Disease（新论文即合规）

## 核心理念

**实验代码 + 实验输出 JSON = 唯一的 L0.5 真相源。** 
论文写得再漂亮，只要与实验输出不一致，就是编造。

## 三步验证流程

### Step 1: 提取论文全部数值声明

从论文的各节中逐行扫描并提取所有可验证的数值声明：

| 论文位置 | 扫描目标 | 示例 |
|:---------|:---------|:-----|
| Abstract | F1/Recall/Acc/AUC/Δ% | "achieves F1=0.7541" |
| Results | 表格中每行每列 | Table 1: ensemble F1=0.7541 |
| Discussion | 对比性声明 | "outperforms baseline by +8.6%" |
| Conclusion | 关键数字 | "establishes baseline F1=0.7541" |
| Figure captions | 图中标注值 | "F1=0.7541, Recall=0.7500" |

```bash
# 快速提取脚本
grep -oP 'F1[\s=:]+[\d.]+' paper.tex | head -20
grep -oP '[+-]?[\d.]+%' paper.tex | head -20
grep -oP 'Recall[\s=:]+[\d.]+' paper.tex | head -10
```

### Step 2: 从实验 JSON 中提取对应值

```python
import json
with open('results/definitive_experiment.json') as f:
    data = json.load(f)

# 提取所有实验值
experiment_values = {
    'ensemble_f1': data['ensemble']['f1_mean'],
    'ensemble_recall': data['ensemble']['recall_mean'],
    'no_leakage_f1': data['ablation']['no_leakage']['f1'],
    'severe_leakage_f1': data['ablation']['severe_leakage']['f1'],
    'f1_inflation': data['ensemble']['f1_mean'] - data['ablation']['no_leakage']['f1'],
}
```

### Step 3: 逐条比对 + 方向性检查

```python
comparisons = []
for metric, paper_val, exp_val in all_claims:
    magnitude_diff = abs(paper_val - exp_val)
    # 方向性检查
    paper_dir = 'positive' if paper_val > 0 else 'negative'
    actual_dir = 'positive' if exp_val > 0 else 'negative'
    dir_match = paper_dir == actual_dir
    
    status = '✓' if magnitude_diff < 0.02 and dir_match else '✗'
    comparisons.append({
        'metric': metric,
        'paper': paper_val,
        'actual': exp_val,
        'diff': magnitude_diff,
        'direction_match': dir_match,
        'status': status
    })
```

**判定标准**：

| 差异 | 方向一致 | 判定 | 行动 |
|:----:|:--------:|:----|:-----|
| <0.02 | ✓ | 通过 | 保留 |
| <0.02 | ✗ | **方向性错误** | 重写叙事 |
| ≥0.02 | ✓ | 数值偏差 | 修正论文 |
| ≥0.02 | ✗ | 双重失败 | 修正 + 重写 |

## 三数据集实战对比表

| 检查项 | PIMA (n=768) | WDBC (n=569) | Heart (n=303) |
|:-------|:------------|:-------------|:--------------|
| 论文声明 F1 | 0.7541 | 0.9806 | 0.8206 |
| 实验 F1 | 0.6986 | 0.9806 | 0.8206 |
| 差异 | **−0.0555 ✗** | 0.0000 ✓ | 0.0000 ✓ |
| 方向正确 | ✓ | ✓ | ✓ |
| 消融表匹配 | **3/4 行 ✗** | 4/4 ✓ | 4/4 ✓ |
| 通胀率精确 | +6.71% vs +8.6% | N/A | N/A |
| 审计结论 | 22处修正 | 通过 | 通过 |

**关键发现**：
- PIMA 的 LDA 基线值（F1=0.6759）精确匹配 → 说明 LLM 使用了真实 LDA 输出
- PIMA 的 Ensemble 值（F1=0.7541）虚构 → LLM 编造了"最好看"的数字
- WDBC/Heart 全部匹配 → 因为这两篇是新写的（write_file），LLM 直接从实验输出取数

## 常见失败的信号模式

### 信号 1：基线精确 + 主结果夸大
```
LDA F1: paper=0.6759, actual=0.6759 ✓ (exact match)
Ensemble F1: paper=0.7541, actual=0.6986 ✗ (−0.0555)
```
→ LLM 使用了真实 LDA 输出但编造了 Ensemble 值

### 信号 2：方向性反转
```
FN reduction: paper=−67%, actual=+28%
```
→ 叙事驱动数据：LLM "觉得"系统应该更好

### 信号 3：全部数据无源文件
```
实验结果表：✅ 有 ±SD、p 值
实验代码：❌ 不存在
```
→ 可能全量虚构（见 quality-gate Type A 检测）

## 修复后的验证

修正论文后必须重新编译并确认：

```bash
# 验证每个旧值已替换
grep -c '0.7541' paper.tex  # 应为 0
grep -c '0.6986' paper.tex  # 应为 8+
grep -c '8.6' paper.tex     # 应为 0（已改为 6.71）
grep -c '6.71' paper.tex    # 应为 4+

# 编译验证
pdflatex paper.tex && grep -c '!' paper.log  # 应为 0
```
