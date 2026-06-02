# Accuracy Paradox on Imbalanced Data — CDC BRFSS 实战

## 背景

2026-05-31 Pima-CRISP-DM 跨数据集验证中，审计 CDC Diabetes Health Indicators 数据集（UCI 891, 253K rows, 13.6% prevalence）的相关论文。

## 关键发现：Alpan2024

Alpan2024 (IEEE, 1 cite): "Performance Evaluation and Comparison of ML Algorithms in Classification of CDC Diabetes Health Indicators Dataset by WEKA"

**论文宣称**: J48 84.58%, SVM 84.05%, Random Tree 84.25% accuracy

**但全部预测"非糖尿病"的基线: 86.4%!**

### 这意味着什么？

论文跑的最佳结果(84.58%) **低于瞎猜基线(86.4%)**——在13.6%患病率的数据上，什么都不做就已经86.4%了。

### 泄漏为什么没让指标更高？

数据泄漏通常**膨胀F1/Recall/metrics**，但是：
1. Alpan2024只报告了**Accuracy**——在不平衡数据上这是最误导性的指标
2. 我们的Helix消融显示：CDC数据 F1从0.44(隔离)膨胀到0.77(泄漏) = **+73.1%**
3. 但如果只看Accuracy，泄漏模型同样会被Accuracy掩盖（13.6% prevalence的accuracy天然高）

### 对Helix论文的启示

1. **用Accuracy衡量不平衡数据 = 犯了双重错误**
   - 第一：Accuracy对少数类不敏感（86.4%基线随便达到）
   - 第二：泄漏对Accuracy的膨胀效应远小于对F1/Recall的膨胀效应
   - 所以Alpan2024即使有泄漏，Accuracy也看不出问题

2. **我们Helix论文的"Recall优先"+F1+Λ三维评估正是为了解决这个问题**

3. **评论Alpan2024时的表述**：
   > "Alpan2024等人用WEKA在CDC BRFSS上取得84.58%准确率，但该数据集13.6%患病率下全部预测阴性即达86.4%基线——这恰好说明accuracy在不平衡数据上的误导性。即使存在数据泄漏，accuracy也无法反映真实损伤。我们Helix框架通过Recall+F1+Λ三指标避免了此问题。"

## CDC BRFSS 数据集信息

| 属性 | 值 |
|:-----|:---|
| 名称 | Diabetes Health Indicators Dataset |
| 来源 | CDC BRFSS 2015 调查 |
| UCI ID | 891 |
| Kaggle | alexteboul/diabetes-health-indicators-dataset |
| 样本 | 253,680 |
| 特征 | 21 (excl ID + Diabetes_binary) |
| 患病率 | 13.6% |
| 特征类型 | 健康行为调查（BMI, 吸烟, 运动, 果蔬摄入等） |
| 下载URL | `https://archive.ics.uci.edu/static/public/891/data.csv` |
| 下载命令 | `curl -sL --connect-timeout 15 --max-time 300 "https://archive.ics.uci.edu/static/public/891/data.csv" -o cdc_diabetes.csv` |

## Alpan2024 引用分析

| 字段 | 值 |
|:-----|:---|
| 标题 | Performance Evaluation and Comparison of ML Algorithms in Classification of CDC Diabetes Health Indicators Dataset by WEKA |
| DOI | 10.1109/ismsit63511.2024.10757280 |
| 出版 | IEEE (2024) — 付费墙 |
| 工具 | WEKA（与Khafaga2022相同——WEKA默认全局预处理） |
| 宣称 | J48 84.58% accuracy |
| 方法 | 未描述CV/数据分割/SMOTE/隔离 |
| 泄漏推定 | 高（WEKA全局预处理+未提隔离+accuracy选型错误） |
