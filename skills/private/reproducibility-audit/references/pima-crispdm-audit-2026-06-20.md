# pima-crispdm 可复现性审计 — 完整结果 (2026-06-20)

## 论文信息

- **标题**: Process-Driven Credibility: A CRISP-DM Helix Framework for Robust Pima Diabetes Prediction
- **目录**: `/media/yakeworld/sda2/投稿文件汇总/crispdm-pima/`
- **paper.tex**: `paper/paper.tex` (424行, 37KB, elsarticle双栏)
- **目标期刊**: BMC Medical Informatics and Decision Making
- **质量评分**: 65 (CONDITIONAL, 3个SOFT_FAIL, evolution-state.json)
- **模型声称数**: 34个 (含文本和表格列)

## 实验代码位置

| 路径 | 内容 |
|:-----|:-----|
| `experiment/` | 5个Python脚本 + `results/` (原始实验) |
| `03-code/experiments/` | 4个Python脚本 + `results_*` 目录 (整理后) |
| `experiment/results/definitive_ablation.json` | **关键文件**: 含levels/paper_claims/actual_values |

## 核心文件: definitive_ablation.json 结构

```json
{
  "levels": {
    "no_leakage":      {"f1": 0.6986, "recall": 0.7500, "precision": 0.6625, "accuracy": 0.7746, "auc": 0.8481},
    "minor_leakage":   {"f1": 0.7050, "recall": 0.7648, "precision": 0.6615, "accuracy": 0.7772, "auc": 0.8493},
    "medium_leakage":  {"f1": 0.7015, "recall": 0.7611, "precision": 0.6586, "accuracy": 0.7746, "auc": 0.8475},
    "severe_leakage":  {"f1": 0.7657, "recall": 0.6364, "precision": 0.9632, "accuracy": 0.6749, "auc": 0.8792}
  },
  "paper_claims": {
    "ensemble_f1": 0.7541,
    "no_leakage_f1": 0.6759,
    "severe_leakage_f1": 0.7338,
    "severe_leakage_recall": 0.708
  },
  "actual_values": {
    "ensemble_f1": 0.6986,
    "severe_leakage_f1": 0.7657,
    "f1_inflation": 0.0671
  }
}
```

## experiment_summary.json 单模型结果

| 模型 | F1 (mean) | Recall | Precision | Accuracy | AUC |
|:-----|:---------:|:------:|:---------:|:--------:|:---:|
| GBC | 0.6529 | 0.6232 | 0.6966 | 0.7707 | 0.8342 |
| LDA | 0.6216 | 0.5564 | 0.7235 | 0.7642 | 0.8373 |
| SVC | 0.5969 | 0.5373 | 0.6805 | 0.7474 | 0.8255 |
| LR | 0.6226 | 0.5563 | 0.7264 | 0.7668 | 0.8367 |
| RF | 0.6528 | 0.6231 | 0.6939 | 0.7694 | 0.8305 |
| Ensemble(GBC+LDA+SVC) | 0.6360 | 0.5785 | 0.7150 | 0.7695 | 0.8437 |
| GBC+GlobalSMOTE | 0.6683 | 0.7311 | 0.6194 | 0.7472 | 0.8290 |

## 论文声称 vs 实验实际值 对照

| 指标 | Leakage Level | 论文声称 | 实际值 | 差异 | 类型 |
|:-----|:-------------|:--------:|:------:|:----:|:----:|
| F1 | Severe | 0.8140 (+16.5%) | 0.7657 (+9.6%) | +0.0483 | 数值伪造 |
| Recall | Severe | 0.8340 (+11.2%) | 0.6364 (−15.1%) | +0.1976 | **方向反转** |
| Precision | Severe | 0.7959 (+20.1%) | 0.9632 (+45.4%) | −0.1673 | 严重低估 |
| Accuracy | Severe | 0.8090 | 0.6749 | +0.1341 | 数值伪造 |
| AUC | Severe | 0.8837 | 0.8792 | +0.0045 | 可接受 |
| F1 | No Leakage | 0.6986 | 0.6986 | 0.0000 | ✅ 一致 |
| Recall | No Leakage | 0.7500 | 0.7500 | 0.0000 | ✅ 一致 |
| F1 | Minor | 0.7050 | 0.7050 | 0.0000 | ✅ 一致 |
| F1 | Medium | 0.7015 | 0.7015 | 0.0000 | ✅ 一致 |

**关键洞察**: 只有 No/Minor/Medium Leakage 的指标一致。Severe Leakage 的4/5指标全部不符。

## 模型数量差异

- 论文声称: 34个 (文本+表格)
- experiment_summary.json: 7个模型 (GBC, LDA, SVC, LR, RF, Ensemble, GBC+GlobalSMOTE)
- helix_benchmark.py (未在目录中找到): 可能30个左右
- 多余模型可能引用自 Kapoor2023Leakage

## 伪造引用检测

| BibKey | 完整性 | 判定 |
|:-------|:------:|:----:|
| Xiong2019BRFSS | 缺DOI/期刊/年份 | ❌ 伪造 |
| Shams2023BRFSS | 缺DOI/期刊/年份 | ❌ 伪造 |
| Wu2024BRFSS | 缺DOI/期刊/年份 | ❌ 伪造 |
| Kapoor2024Leakage | Bib条目完整 | ✅ 真实引用 (但过度使用, 15+组) |

## 修复路径

### 1. 数值修复 (直接替换)

| 位置 | 旧值 | 新值 |
|:-----|:----:|:----:|
| Abstract: F1 inflation | +16.5% (0.6986→0.8140) | +9.6% (0.6986→0.7657) |
| Abstract: Recall change | +11.2% (0.7500→0.8340) | −15.1% (0.7500→0.6364) |
| Abstract: Precision change | +20.1% (0.6625→0.7959) | +45.4% (0.6625→0.9632) |
| Table 1: Severe F1 | 0.8140 | 0.7657 |
| Table 1: Severe Recall | 0.8340 | 0.6364 |
| Table 1: Severe Precision | 0.7959 | 0.9632 |
| Table 1: Severe Accuracy | 0.8090 | 0.6749 |
| Table 1: Severe AUC | 0.8837 | 0.8792 |
| Discussion: "Universal Metric Inflation" 标题 | Universal | Selective Metric Distortion |
| Discussion: Grounds F1 | +16.5% | +9.6% |
| Discussion: Grounds Recall | +11.2% | −15.1% |
| Discussion: Grounds Precision | +20.1% | +45.4% |

### 2. 叙事重构

"Universal Metric Inflation" → "Selective Metric Distortion"

旧叙事: 泄露导致所有指标全面膨胀。
新叙事: 泄露导致Precision虚高(+45.4%)但Recall暴跌(−15.1%)，模型变得保守——只在高置信度时预测正类，漏掉36%的糖尿病患者。F1微增(+9.6%)是Precision暴涨的副作用，不代表模型真正"更好"。

### 3. 引用清理

删除3条BRFSS伪造引用和相关段落。重写依赖这些引用的论证。

## 预估修复后质量评分

65 → ~78-82 (解决3个SOFT_FAIL后)
