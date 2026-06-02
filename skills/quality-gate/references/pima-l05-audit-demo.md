# Pima CRISP-DM L0.5 Audit Trace

> Reproducible demonstration of the two-tier L0.5 verification framework.
> Source: Jupyter notebook `crisp-dm-pima (2).ipynb` (2.8MB, 150+ cells)

## Project Overview

- **Task**: Diabetes prediction using Pima Indians Diabetes Dataset (PIDD)
- **Methodology**: CRISP-DM framework with strict isolation principle
- **Pipeline**: zero-value correction → median imputation → StandardScaler → SMOTE → Stratified 10-fold CV → VotingClassifier
- **File**: `/home/yakeworld/下载/crisp-dm-pima (2).ipynb`

## L0.5 Verification Table

| Claim in Manuscript | Code Origin | Verification Method | Pass |
|:-------------------|:------------|:-------------------|:----:|
| 768 samples, 268 diabetic, 500 non-diabetic | `df.shape`, `df.Outcome.value_counts()` | Execute cell → confirm counts | ✅ |
| Insulin zeroes: 374 (48.7%) | `(df[['Insulin']] == 0).sum()` | Execute cell → 374 matches | ✅ |
| LDA: F1=0.6772, Recall=0.7204 | Cell 18 classifier loop output | Output table value match | ✅ |
| Ensemble: Recall=0.7426, F1=0.6878, AUC=0.8466 | Cell 20 VotingClassifier eval | Output table value match | ✅ |
| Ablation: SMOTE improves recall 0.5825→0.7426 (+27.5%) | Cell 22 four-scenario experiment | Row-by-row comparison | ✅ |
| Feature importance: Glucose=1.000, BMI=0.629, Age=0.428 | Cell 15 permutation importance | Output table value match | ✅ |

## Two-Tier Classification

| Tier | Type | Examples | Verdict |
|:-----|:-----|:---------|:--------|
| **Tier 1: Code-traceable** | Project's own experimental results | All 6 claims above | ✅ Auto-pass |
| **Tier 2: Literature claims** | External citations (Gupta 95%, AlSadi 98.38%) | Literature review section | ⚠️ Flagged — PDF verification required; neither paper had reproducible pipeline |

## Lightweight Audit Strategy

L0.5 does NOT recompute algorithms. It checks that the same number appears in:
1. The code output table (e.g., Cell 22's formatted ablation table)
2. The manuscript text

This caught a formatting discrepancy in v1 of the ablation table (SMOTE-only scenario's recall was 0.7426 in code output but transcribed as 0.7402 in manuscript — a copy-paste error).

## Usage

To reproduce:
```bash
jupyter nbconvert --to notebook --execute crisp-dm-pima\ \\(2\\).ipynb --output crisp-dm-pima-executed.ipynb
# Then extract metrics from cell outputs
```

---

## 2026-05-26 追加：主动审计实战记录（实验驱动验证）

### 触发条件
用户将 PIMA 公开数据集论文定位为"突破口"——
数据 100% 真实的论文是其可信度的核心卖点。这触发了**主动 L0.5 审计**：不是检查已有文件，而是从头运行实验。

### 审计结果（PIMA + WDBC）

**PIMA 实验验证（10-fold CV, SMOTE inside fold, Ensemble GBC+LDA+SVC）:**

| 声明值 | 实验值 | 差异 | 判定 |
|:-------|:------:|:----:|:----|
| **Ensemble F1=0.7541** | **0.6986** | **−0.0555** | ✗ 夸大→修正 |
| Ensemble Recall=0.7500 | 0.7500 | 0.0000 | ✓ 精确匹配 |
| No Leakage F1(LDA)=0.6759 | 0.6759 | 0.0000 | ✓ 精确匹配 |
| Severe Leakage F1=0.7338 | 0.7657 | +0.0319 | ✗ 偏差→修正 |
| +8.6% F1通胀 | +6.71% | −1.89% | ✗ 修正 |

**关键发现**: LDA 基线精确匹配（LLM 从实验输出复制了正确数据），
但 Ensemble 值被夸大 0.0555（LLM 倾向于生成"最好看"的数字）。
主动运行实验是唯一能区分这两者的方法。

**Recall Paradox 跨数据集验证:**

| 数据集 | 可分离性 | No Leakage F1 | Severe F1 | ΔF1 | ΔRecall |
|:-------|:--------:|:-------------:|:---------:|:---:|:-------:|
| PIMA | 低 | 0.6986 | 0.7657 | **+6.71%** | **−11.36%** |
| WDBC | 高 | 0.9693 | 0.9683 | **−0.10%** | **+0.56%** |

结论: **泄漏损伤与数据集难度成正比**. 低可分离数据集必须用 CRISP-DM Helix.

### 实验代码位置
```
PIMA: 投稿文件汇总/crispdm-pima/experiment/   (4 Python scripts, 650+ traceable lines)
WDBC: 投稿文件汇总/crispdm-wdbc/experiment/   (1 Python script, JSON results)
```

### 主动审计流程（可重复）
```bash
cd 投稿文件汇总/crispdm-pima/experiment/
python3 pima_correct_ablation.py     # 正确4水平消融
python3 pima_definitive.py           # 完整8模型基准+集成
# 输出: results/definitive_ablation.json
# 然后: 逐字段比对 paper.tex 中的数值
```

