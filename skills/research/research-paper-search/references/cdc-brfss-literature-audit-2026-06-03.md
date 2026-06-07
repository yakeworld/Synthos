# CDC BRFSS 糖尿病预测文献审计报告（2026-06-03）

## 搜索记录

**搜索入口**: OpenAlex（Semantic Scholar 429封禁，arXiv无相关）
**搜索词**: `behavioral risk factor surveillance system diabetes predict machine learning`
**结果总数**: 752条，需两次过滤：关键词+语义相关性

## 相关论文完整列表

### Tier 1 — 高成熟度

| # | 论文 | 年份 | 期刊 | 被引 | DOI |
|:-:|:-----|:----:|:-----|:----:|:----|
| 1 | Building Risk Prediction Models for Type 2 Diabetes Using Machine Learning Techniques (Xiong et al.) | 2019 | Preventing Chronic Disease (CDC) | 127 | 10.5888/pcd16.190109 |
| 2 | Geographically weighted ML model for T2D prevalence (Quiñones et al.) | 2021 | Scientific Reports | 73 | 10.1038/s41598-021-85381-5 |

**判断依据**:
- Xiong2019: 加权Logistic回归考虑了调查设计（BRFSS复杂抽样），AUC=0.718-0.795合理
- Quiñones2021: GW-RF模型，10-fold CV + RFE特征选择

### Tier 2 — 中等

| # | 论文 | 年份 | 期刊 | 被引 | DOI |
|:-:|:-----|:----:|:-----|:----:|:----|
| 3 | An investigation of ML algorithms and data augmentation… (Alam et al.) | 2023 | Healthcare Analytics | 53 | 10.1016/j.health.2023.100297 |
| 4 | Diabetes prediction model based on GA-XGBoost and stacking (GA-XGBoost) | 2024 | PLOS ONE | 39 | 10.1371/journal.pone.0311222 |

### Tier 3 — 低（明确泄漏）

| # | 论文 | 声称性能 | 泄漏原因 | DOI |
|:-:|:-----|:---------|:---------|:----|
| 5 | Diabetes type 2 classification using ML with up-sampling (Shams et al.) | AUC=0.99 | 80/20 split + 上采样，无CV | 10.1186/s43067-023-00074-5 |
| 6 | Explainable ML for Efficient Diabetes Prediction (Wu et al.) | Acc=97.45% | 随机过采样 + 简单分割 | 10.1002/eng2.13080 |
| 7 | Random Oversampling-Based Diabetes Classification (2024) | 无具体值 | 随机过采样 | 10.1007/s44196-024-00678-3 |
| 8 | Predictions of diabetes through ML models… (2024) | 未公开 | 会议论文，方法不透明 | 10.54254/2755-2721/32/20230214 |

## 性能区间对比

| 区间 | AUC | Acc | F1 |
|:----|:---:|:---:|:--:|
| Tier 1 (正确CV) | 0.718-0.795 | ~82% | — |
| Tier 3 (泄漏) | 0.96-0.99 | 92-97% | ~0.95 |
| 我方Helix基准 (AdaBoost) | — | — | 0.448 |
| 我方Helix基准 (LR) | — | — | 0.451 |

## 引用BibTeX

已添加到 paper 的 references.bib：Xiong2019BRFSS, Quinones2021BRFSS, Alam2023BRFSS, Shams2023BRFSS, Wu2024BRFSS

## 经验总结

1. OpenAlex对"CDC diabetes health indicators"这种Kaggle数据集名搜索不佳，需用"BRFSS diabetes machine learning"或"behavioral risk factor surveillance system diabetes predict"
2. Semantic Scholar被429封禁后，短时间不可恢复，需切到OpenAlex
3. 泄漏检测最稳定的信号不是被引数，而是分割策略描述——"up-sampling before split"是致命信号
4. 高引用(127) + 低性能(AUC~0.79) = 方法学可靠的信号
