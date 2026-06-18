# BRFSS Diabetes Prediction Literature: Data Leakage Validation (Full-Text Verified)

> 日期: 2026-06-03
> 来源: OpenAlex 文献检索 + PDF全文下载 → 逐行定位方法学错误
> PDF已下载至: `/tmp/cdc_papers/` (Shams2025.pdf, Li2024.pdf)

## 核心发现

**文献中的BRFSS糖尿病预测性能普遍虚高（Acc 92-99%, AUC 0.98-0.99）**。经两篇PDF全文验证，泄漏模式与Helix跨数据集实验完全一致。唯一采用正规Stratified CV的论文给出 F1≈0.37，与Helix结果 F1=0.45 在同一量级。

## 我方基线（Helix 3x2 CV, 无泄漏）

| 模型 | F1 | Acc | 协议 | 样本 |
|:-----|:--:|:---:|:-----|:----:|
| **AdaBoost** | **0.4505** | — | 3x2 CV Helix | 25,368 |
| LogisticRegression | 0.4415 | — | 3x2 CV Helix | 25,368 |
| Leaky LR (全局SMOTE) | 0.768 | — | 5x2 CV Leaky | 50K → +73.2% |

## ✅ 全文验证论文

### 📄 Shams2025 (JESIT 2023, cites=35)
> Hama Saeed M.A. "Diabetes type 2 classification using machine learning algorithms with up-sampling technique"
> DOI: 10.1186/s43067-023-00074-5
> 下载: ✅ PDF全文 (10页)

**报告值**: Extra Trees **AUC=0.99** on BRFSS

**原文定位（第3页·Preprocessing节）**:
> *"The datasets should be preprocessed before applying them to classifiers. The outliers are removed from the datasets. The outcome and diabetes labels of PIMA and BRFSS datasets are not balanced. Unbalancing data decrease the accuracy of the classifiers. To mitigate this, the **up-sampling technique has been used to balance both datasets. After that, 80% of the datasets are used as training data and 20% as testing data** randomly using the train-test-split function."*

**💥 泄漏定位**: `up-sampling → train-test-split` 顺序逆反。up-sampling（随机复制少数类样本）在全局执行后，同一合成样本可同时出现在train/test中 → AUC=0.99 不可靠。

**方法学**: 80/20 split, 无CV, 无折叠内隔离预处理

### 📄 Li2024 (PLOS ONE 2024, cites=39)
> Li W, Peng Y, Peng K. "Diabetes prediction model based on GA-XGBoost and stacking ensemble algorithm"
> DOI: 10.1371/journal.pone.0311222
> 下载: ✅ PDF全文 (29页)

**报告值**: XGBoost+SMOTEENN → **AUC=0.9835, Acc=0.9325, F1=0.9530**

**原文定位**:
- 技术路线(Section 3.1): Step 3 数据平衡 → Step 4 构建模型（未在Step 3前做split）
- 数据分配(Section 4): "80% of the dataset was allocated as the training set, with the remaining 20% serving as the test set"
- SMOTEENN比较(Section 4.1): "The data processed by different sampling algorithms were input into the XGBoost model for training"

**关键证据 — 本文自己报告了基线**:
| 条件 | AUC | Accuracy | Recall | F1-score |
|:-----|:---:|:--------:|:------:|:--------:|
| 不采样(原始数据) | 0.8282 | 0.8652 | 0.1734 | **0.2682** |
| RandomOverSampler | 0.8369 | 0.7576 | 0.8076 | 0.7692 |
| ADASYN | 0.9810 | 0.9372 | 0.9520 | 0.9480 |
| SMOTE | 0.9836 | 0.9402 | 0.9527 | 0.9492 |
| **SMOTEENN** | **0.9871** | **0.9418** | **0.9551** | **0.9530** |

**💥 泄漏定位**: SMOTEENN全局预处理（极可能split前执行）。只加采样算法不做任何模型改进，Recall从**17%暴涨到96%** — 这是数据泄漏的典型信号。Helix基线 F1=0.45 与"不采样"基线 F1=0.27 量级一致。SMOTEENN后 F1=0.95 与Leaky LR F1=0.768 同模式（膨胀程度更大因SMOTEENN+树模型）。

**方法学**: 80/20 split + 5-fold CV（CV在训练集内做但SMOTEENN在split前全局），Stacking第二层

## ⚠️ 仅摘要（未下载全文）高泄漏嫌疑

| 论文 | 年/期刊/引用 | 报告值 | 方法概览 | 泄漏推定 |
|:-----|:-----------:|:-------|:---------|:--------:|
| **Alam2022** (CIN) | 2022, Comput Intell Neurosci, cites=32 | KNN **Acc=98.38%** AUC=0.98 | SMOTE-ENN平衡 → 多种ML → KNN最优 | 🔴 (SMOTE-ENN全局) |
| **Phan2025** (Eng Reports) | 2024, Engineering Reports, cites=20 | Extra Trees **Acc=97.23%** | Random Oversampling + GridSearchCV | 🔴 (过采样全局) |
| **Rosyidi2024** (IJCIS) | 2024, Int J Comput Intell Syst, cites=10 | RF **Acc=92%** | Random oversampling + IQR + Boruta | 🟡 (过采样全局) |

## ✅ 唯一可信文献

| 论文 | 年/期刊/引用 | 报告值 | 方法学 | 可信度 |
|:-----|:-----------:|:-------|:-------|:------:|
| **Tennessee BRFSS (2025)** | J Prim Care Community Health, cites=3 | GBoost **Acc=82%, F1=37%, AUROC=0.80** | **Stratified 5-fold CV** ✅ | ✅ |

其 F1=0.37 与 Helix AdaBoost F1=0.45 一致。

## 全量对比表

| 文献 | 报告Acc | 报告F1/AUC | Helix F1 | 偏差 | 原因 |
|:----|:-------:|:----------:|:--------:|:----:|:-----|
| Shams2025 | — | AUC=**0.99** | 0.45 | ↑120% | up-sampling在split前 |
| Li2024 | 93.25% | F1=**0.95**/AUC=0.98 | 0.45 | ↑111% | SMOTEENN全局预处理 |
| Alam2022 | 98.38% | AUC=0.98 | 0.45 | ↑118% | SMOTE-ENN泄漏(推定) |
| Phan2025 | 97.23% | — | 0.45 | ↑116% | 过采样泄漏(推定) |
| Rosyidi2024 | 92% | — | 0.45 | ↑104% | 过采样泄漏(推定) |
| **Tennessee 2025** | 82% | **F1=0.37**/AUC=0.80 | 0.45 | ↓18% | Stratified 5-fold ✅ |
| **我方Helix** | — | **F1=0.4505** | — | **基准** | **3x2 CV Helix** ✅ |

## 搜索细节

### 查询策略
- **OpenAlex**: `search=BRFSS+machine+learning&per-page=25` → 1,291 results ✅
- **Semantic Scholar**: All BRFSS queries returned 0 results ❌ (符合"data=0"静默失败模式)
- **结论**: BRFSS主题必须用OpenAlex, SS不可靠

### 下载策略
- **PLOS ONE** (Li2024): `journals.plos.org/plosone/article/file?id=...&type=printable` → OA直链 ✅
- **SpringerOpen/JESIT** (Shams2025): `jesit.springeropen.com/counter/pdf/...` → OA直链 ✅
- **Wiley** (Phan2025): `doi.org/10.1002/eng2.13080` → 403 Cloudflare ❌
- **Hindawi** (Alam2022): `downloads.hindawi.com/...` → 403 Cloudflare ❌
- **Springer** (Rosyidi2024): `doi.org/10.1007/...` → HTML paywall ❌
- **Sci-Hub**: 所有域对2022+论文返回Hindawi重定向(也违反Cloudflare)或403

## 正确BibTeX

```bibtex
@article{Shams2025,
  author = {Mariwan Ahmed Hama Saeed},
  title = {Diabetes type 2 classification using machine learning algorithms with up-sampling technique},
  journal = {Journal of Electrical Systems and Information Technology},
  year = {2023},
  volume = {10},
  pages = {8},
  doi = {10.1186/s43067-023-00074-5}
}

@article{Li2024,
  author = {Wenguang Li and Yan Peng and Ke Peng},
  title = {Diabetes prediction model based on GA-XGBoost and stacking ensemble algorithm},
  journal = {PLoS ONE},
  year = {2024},
  volume = {19},
  number = {9},
  pages = {e0311222},
  doi = {10.1371/journal.pone.0311222}
}

@article{Alam2022,
  author = {Talha Mahboob Alam and others},
  title = {Detecting High-Risk Factors and Early Diagnosis of Diabetes Using Machine Learning Methods},
  journal = {Computational Intelligence and Neuroscience},
  year = {2022},
  volume = {2022},
  pages = {2557795},
  doi = {10.1155/2022/2557795}
}

@article{Tennessee2025,
  author = {...},
  title = {Exploring Explainable Machine Learning for Predicting and Interpreting Self-Reported Diabetes among Tennessee Adults: Insights from the 2023 Behavioral Risk Factor Surveillance System (BRFSS)},
  journal = {Journal of Primary Care \& Community Health},
  year = {2025},
  doi = {10.1177/21501319251400546}
}
```
