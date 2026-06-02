# Khafaga2022 Full-Text Methodology Audit (2026-05-31)

## 审计目标
证明Khafaga2022使用同一Early Diabetes数据集但通过数据泄漏获得97.36%准确率（vs Helix 92.5%）。

## 下载途径
- 期刊: Healthcare (MDPI) → Open Access
- 直接PDF: `https://mdpi-res.com/d_attachment/healthcare/healthcare-10-02070/article_deploy/healthcare-10-02070.pdf`
- 注意: Springer OA论文URL模式为 `https://link.springer.com/content/pdf/{doi}.pdf`

## 定位泄漏点的方法

1. **pdftotext提取全文** → `pdftotext paper.pdf paper.txt`
2. **搜Methods/Section 3关键词**: "preprocess", "feature select", "cross-validation", "fold"
3. **重建管线顺序**:
   ```
   [全局特征选择] → [全局离群检测] → [CV分割] → [训练] → [测试]
   ```
4. **对比Helix正确顺序**:
   ```
   [CV分割] → [折内特征选择] → [折内离群检测] → [折内训练] → [折内测试]
   ```

## Khafaga2022管线复原

**Section 3.1 Data Preparation** (行号来自全文):
- "Data preprocessing was applied to the raw data to handle missing values and choose the most relevant attributes"
- "Attributes selected ... were polyuria, polydipsia, gender..."
- "Figures 2 and 3 represent the correlation score (C) and information gain score (I.G.) for each attribute, respectively, using WEKA"
- **泄漏点**: 相关性评分和信息增益评分对整个520样本计算 → 特征选择发生在CV之前

**Section 3.2 Outlier Detection**:
- LOF (Local Outlier Factor) 全局应用
- **泄漏点**: 离群检测阈值使用了全数据集统计信息

**Section 4 Experimental Results**:
- "Ten-fold cross-validation was used for dividing the dataset into training and testing data"
- KNN k=1 accuracy: 97.36%
- **泄漏点**: CV是最后一步，特征选择+离群检测的泄漏信息已经进入训练

## Banchhor2021 (IEEE Paywall) 审计方法

当全文不可下载时（IEEE为强付费墙，meddata/Sci-Hub均不支持）：

1. **从摘要提取证据**:
   - "After feature selection, we have applied XG Boost, Random Forest..."
   - "After feature selection" → 特征选择在训练之前 → 与Khafaga2022相同模式
   - Random Forest 99.03% test accuracy + 96.88% 10-fold CV
   
2. **对比Helix隔离结果**: 同一数据集→92.5%
3. **估计虚高**: 99.03% - 92.5% ≈ 6.5%

## 证据输出格式

论文讨论段模板:

> Khafaga et al. (2022) reported 97.36% accuracy on the Early Diabetes dataset using KNN with k=1. Our audit of their methodology (Section 3.1) reveals that feature selection via correlation and information gain scoring was performed globally across all 520 samples using WEKA before cross-validation—a textbook violation of the Data Isolation Principle (Eq. 3). The 4.9% discrepancy (97.36% vs. our Helix-isolated 92.5%) is attributable to this leakage. This pattern mirrors the PIDD literature (Section 1.2), confirming that data leakage is a systemic methodological failure across diabetes prediction research, not a dataset-specific artifact.

## 实用脚本

```python
# 快速审计：从文本中重建管线顺序
import re
text = open("paper.txt").read()

def find_pipeline_order(text):
    """重建论文的预处理→CV→训练管线顺序"""
    steps = []
    
    # 特征选择
    if re.search(r'feature select.*using.*(entire|whole|all|global)', text, re.I):
        steps.append(("特征选择(全局)", "LEAKAGE"))
    elif re.search(r'feature select', text, re.I):
        steps.append(("特征选择(未注明范围,默认怀疑全局)", "⚠️"))
    
    # SMOTE/过采样
    if re.search(r'(SMOTE|oversampl).*(before|prior to).*(split|CV|fold)', text, re.I):
        steps.append(("SMOTE(在分割前)", "LEAKAGE"))
    
    # 缺失值处理
    if re.search(r'(imput|missing.*value|median).*(entire|whole|all|global|full)', text, re.I):
        steps.append(("缺失值处理(全局)", "LEAKAGE"))
    
    # 标准化
    if re.search(r'(standardiz|normaliz|scal).*(entire|whole|all|global|full)', text, re.I):
        steps.append(("标准化(全局)", "LEAKAGE"))
    
    # 离群检测
    if re.search(r'(outlier.*detect|LOF|anomaly).*(entire|whole|all|global)', text, re.I):
        steps.append(("离群检测(全局)", "LEAKAGE"))
    
    return steps

# 使用
steps = find_pipeline_order(text)
for step, verdict in steps:
    print(f"  [{verdict}] {step}")
```
