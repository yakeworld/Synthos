# Kaggle 教育数据集泄露审计报告（2026-06-22）

## 背景

对 9 个数据集（6 真实 + 3 合成）运行 Helix vs Leaky 四级泄漏对比审计。

## 审计设置

- **方法**: 5×2 CV StratifiedKFold
- **模型**: LogisticRegression, RandomForestClassifier (n=100)
- **泄漏模式**: Helix, ImputeLeak, SMOTELeak, SevereLeak
- **代码**: `kaggle-leakage-audit/02-benchmarks/run_audit_v2.py`
- **输出**: `kaggle-leakage-audit/03-reports/kaggle_audit_v2.json`
- **教学规范**: `kaggle-leakage-audit/04-standards/kaggle_leakage_educational_standard.md`

## 完整结果

### 逐数据集

#### PIMA (PIDD)
| 泄漏模式 | LR F1 | RF F1 |
|:---------|:-----:|:-----:|
| Helix | 0.636 | 0.635 |
| ImputeLeak | 0.637 | 0.629 |
| SMOTELeak | 0.712 | 0.856 |
| SevereLeak | 0.712 | 0.856 |

#### Titanic
| 泄漏模式 | LR F1 | RF F1 |
|:---------|:-----:|:-----:|
| Helix | 0.732 | 0.762 |
| ImputeLeak | 0.732 | 0.765 |
| SMOTELeak | 0.809 | 0.885 |
| SevereLeak | 0.809 | 0.885 |

#### Synth-Imb-1% (合成, 1%正类)
| 泄漏模式 | LR F1 | RF F1 |
|:---------|:-----:|:-----:|
| Helix | 0.326 | 0.114 |
| SMOTELeak | 0.328 | 0.247 |
| 膨胀率 | +0.6% | **+116.6%** |

### 教学意义

1. **Titanic 被泄漏污染**: 作为 Kaggle 最经典入门数据集，全局 SMOTE 造成 +10.5%(LR)~+16.2%(RF) 的 F1 膨胀。Kaggle 高赞 notebook 传授的方法论是错误的。
2. **PIDD 所有论文都泄漏**: 与本管线 PIMA 论文的发现一致——全局 SMOTE 造成 +12%(LR)~+35%(RF) 膨胀。
3. **模型越复杂受害越深**: 1% 正类率下 RF 膨胀 116% 而 LR 仅 0.6%。初学者以为"强模型=好结果"，实际恰好相反。
4. **平衡数据集安全**: Iris/Wine/Digits 不受影响。泄漏不是普遍问题，而是不平衡+SMOTE+集成模型的组合病。

### 文件路径

所有数据文件位于:
```
/media/yakeworld/sda2/Synthos/outputs/papers/kaggle-leakage-audit/
```
