# Pima CRISP-DM Definitive Experiment — 2026-06-03

## 背景
Pima论文Table 2的Severe Leakage行数值被证实为编造（F1=0.7657, Rec=0.6364既非LR也非Ensemble的真实输出）。
定稿前重写清理版实验脚本，确保所有数值可追溯。

## 清理版脚本
`03-code/experiments/pima_definitive_experiments.py`

### 结构
1. 数据加载（OpenML data_id=37）
2. LR 4级消融（A-G，不同之处未使用Ensemble）
3. Ensemble 4级消融（GBC+LDA+SVC soft voting）
4. 汇总 + 论文数值验证表

### 验证结果

**Ensemble（主论文用）：**
| 等级 | F1 | Recall | Precision | Accuracy | AUC |
|:-----|:--:|:------:|:---------:|:--------:|:---:|
| No Leakage | 0.6986 ✅ | 0.7500 ✅ | 0.6625 ✅ | 0.7746 ✅ | 0.8481 ✅ |
| Minor | 0.7050 ✅ | 0.7648 ✅ | 0.6615 ✅ | 0.7772 ✅ | 0.8493 ✅ |
| Medium | 0.7015 ✅ | 0.7611 ✅ | 0.6586 ✅ | 0.7746 ✅ | 0.8475 ✅ |
| Severe | **0.8140** | **0.8340** | **0.7959** | **0.8090** | **0.8837** |
| Inflation | +16.52% | +11.20% | +20.14% | — | — |

**LR（对比用）：**
| 等级 | F1 | Recall |
|:-----|:--:|:------:|
| No Leakage | 0.6759 | 0.7165 |
| Severe | 0.7338 | 0.7080 |
| Inflation | +8.57% | -1.19% ↓ |

### 关键发现
- Ensemble下Severe Leakage使**所有指标上升**：无Recall Paradox
- LR下Recall微降1.19%：存在微弱Recall矛盾
- 论文原Severe值（F1=0.7657, Rec=0.6364）**既不匹配LR也不匹配Ensemble**，是LLM编造

### 输出文件
```
results_definitive/
├── ablation_lr.csv
├── ablation_ensemble.csv
└── summary.json
```
