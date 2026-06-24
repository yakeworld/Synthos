# 现有审稿/质量评价框架调研

> 来源：2026-06-24 网络搜索（Startpage via Tor）+ 训练数据知识
> 目标：提取可用于改进 Synthos quality-gate 的普适性原则和结构化方法。

## 一、临床预测模型领域四大标准框架

### 1. PROBAST（Prediction model Risk Of Bias Assessment Tool）
- **四个域**：参与者 (P)、预测因子 (P)、结果 (O)、分析 (A)
- **关键贡献**：分析域包含"数据泄露"评估——同行中最早显式警告全局预处理的危害
- **对我们的映射**：L0.5 数据诚实门 + G2.5 实验完整性门覆盖了"分析"域。但"参与者/预测因子/结果"三域未覆盖。

### 2. TRIPOD / TRIPOD+AI（Transparent Reporting...）
- **22/27 个检查项**：定义"什么信息必须在论文中出现"
- **对我们的映射**：G1 只查"有没有 IMRaD"，没查"必报项缺失"——TRIPOD 要求报告缺失值处理方法、模型选择理由等。我们没检查"该写但没写"的内容。

### 3. MI-CLAIM（Minimum Information about Clinical AI Modeling）
- **六个域**：研究问题、数据、方法、复现、伦理、注册
- **对我们的映射**：single-authority-notebook 原则与之对齐。但 MI-CLAIM 要求注册号和伦理审批号——我们没检查。

### 4. CLAIM（Checklist for AI in Medical Imaging）
- 42 项检查清单。"数据描述→预处理→模型→评估→解释→讨论"的结构可推广。

## 二、通用审稿框架

### 5. EQUATOR Network
- 500+ 报告指南的汇总门户。**不同研究类型需要不同审稿模板。**

### 6. PLOS ONE Reviewer Criteria
- 四条标准：①科学严谨 ②方法健全 ③结论有数据支撑 ④伦理合规

### 7. Nature Peer Review Checklist
- 13 个关键问题。要求审稿人明确标注每个发现是"主要"还是"次要"。

## 三、假设与论证框架

### 8. CARS 模型（Creating A Research Space）
- Introduction 三段：建立领地 → 寻找空白 → 占领空白。

### 9. Toulmin 论证模型
- 六元素：Claim、Grounds、Warrant、Backing、Qualifier、Rebuttal。

## 四、系统性评估工具

### 10. AMSTAR 2（系统综述评估）
- 16 项，7 个关键项。**关键项一票否决**。

### 11. Cochrane Risk of Bias 2.0
- 五个域，**领域级判断**（Low / Some Concerns / High Risk）而非总分。

### 12. NHLBI Study Quality Assessment Tools
- 不同研究类型提供不同检查表。

## 五、建议集成的三项改动

| 改动 | 来源 | 做法 |
|:-----|:-----|:------|
| 六域判定取代总分 | Cochrane RoB 2.0 + NHLBI | 质量报告输出各域 PASS/SOFT_FAIL/HARD_FAIL，取消总分 |
| 论文类型分流 | JBI 13 模板 + EQUATOR | L0 层识别论文类型，加载不同检查模板 |
| 关键项一票否决 | AMSTAR 2 | L0.5 数据诚实门 = 关键项。FAIL 则直接锁定 |
