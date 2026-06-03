# Pima Ensemble Severe Leakage — 实测 vs 论文声称

## 核心矛盾
论文Table 2中No/Minor/Medium三行使用的是正确的Ensemble值（已验证），
但Severe行（F1=0.7657, Rec=0.6364, Prec=0.9632, Acc=0.6749）**全部是编造的**。

## 实测Ensemble Severe值

```python
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC

ensemble = VotingClassifier(estimators=[
    ('gbc', GradientBoostingClassifier(random_state=42)),
    ('lda', LinearDiscriminantAnalysis()),
    ('svc', SVC(probability=True, random_state=42))
], voting='soft')
```

4级消融：全部用Ensemble，10-fold Stratified CV

| 水平 | F1 | Recall | Precision | Accuracy | AUC |
|:-----|:--:|:------:|:---------:|:--------:|:---:|
| No Leakage | 0.6986 | 0.7500 | 0.6625 | 0.7746 | 0.8481 |
| Minor | 0.7050 | 0.7648 | 0.6615 | 0.7772 | 0.8493 |
| Medium | 0.7015 | 0.7611 | 0.6586 | 0.7746 | 0.8475 |
| Severe | **0.8140** | **0.8340** | **0.7959** | **0.8090** | **0.8837** |
| Inflation | +16.52% | +11.20% | +20.10% | +4.44% | +4.19% |

## 为什么论文值0.7657/0.6364/0.9632/0.6749不可能是正确的

| 指标 | 论文值 | LR实测 | Ensemble实测 | 最接近哪个？ |
|:-----|:------:|:------:|:------------:|:------------:|
| F1 | 0.7657 | 0.7338 | 0.8140 | **两者都不像** |
| Recall | 0.6364 | 0.7080 | 0.8340 | **两者都不像** |
| Precision | 0.9632 | 0.7643 | 0.7959 | **两者都不像** |
| Accuracy | 0.6749 | 0.7430 | 0.8090 | **两者都不像** |

**结论**：这4个数值不是任何实验的真实输出。属于LLM生成论文时的虚构数值。
