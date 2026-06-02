# Pima CRISP-DM L0.5 审计：Ensemble + Ablation 编造数值修复

## 背景

2026-06-01 Pima CRISP-DM 论文双质检中，L0.5 审计发现论文核心实验数值无源代码支撑。

## 发现

| 位置 | 声称值 | 问题 |
|:-----|:------:|:-----|
| §4.2 Voting Ensemble (GBC+LDA+SVC) | F1=0.7541, Recall=0.7500, Acc=0.7746 | 无对应实验代码，benchmark 最优仅 0.6678 |
| §4.1 Ablation Table 1 (LDA 基线，3 场景) | F1=0.6759/0.6777/0.7338 | 无独立消融实验代码 |
| §4.2 GBC personal performance | F1=0.6857 | Benchmark 实际 GBC=0.6379 |
| §4.1 F1 inflation | +8.6% | 实验值 +9.7% |
| §4.1 Recall decline | -1.2% | 实验值 -3.0% |
| §4.1 Lambda | 0.090 | 实验值 0.002 |

## 根因

LLM 在写作过程中生成了"听起来合理"的实验数值，但实际从未运行过对应实验。
与引用链传播（Type B）不同，这是 Type A（纯编造）。

## 修复

### 1. 写实验代码

```python
# run_ensemble.py — GBC+LDA+LR soft voting, 5x2 CV Helix isolation
# run_ablation.py — LDA baseline, 3 leakage scenarios, 5x2 CV
```

两个脚本均使用严格 Helix 隔离（impute+scale+SMOTE inside CV folds）。

### 2. 跑实验 → 获取真实值

```json
{
  "ensemble": {"f1": 0.6699, "recall": 0.7142, "acc": 0.7542, "prec": 0.6328, "auc": 0.8291},
  "ablation": {
    "no_leakage": {"f1": 0.6647, "recall": 0.7104},
    "medium_leak": {"f1": 0.6647, "recall": 0.7104},
    "severe_leak": {"f1": 0.7290, "recall": 0.6888}
  }
}
```

### 3. 更新论文

替换全部 12 处编造数值为实验值（Abstract、§4.1、§4.2、Conclusion、Clinical Implications）。

### 4. 保存痕迹

```
03-code/experiments/
  ├── run_ensemble.py          ← 实验代码
  ├── ensemble_results.json    ← 实验输出
  ├── run_ablation.py          ← 消融代码
  └── ablation_results.json    ← 消融输出
```

## 教训

- 论文中每个实验数值必须有对应的实验代码文件
- ensemble/voting 是 LLM 编造的常见重灾区（LLM 喜欢"集成总是更好"的叙事）
- 论文写完但实验目录只有 2 个 .py 文件 → red flag
- L0.5 应在编译后、报结果前自动执行，不等用户问
