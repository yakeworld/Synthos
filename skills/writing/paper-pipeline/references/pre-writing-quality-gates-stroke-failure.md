# Pre-Writing Quality Gates: 伪UCI管线检测（2026-06-06）

> 在 G1 ACQ 执行前，先检测选题是否属于"伪UCI管线"。如果是，先纠正方向再执行。

## 伪UCI管线判定（2026-06-06 实战）

### 定义

"伪UCI管线"指：使用公开数据集（UCI/Kaggle/OpenML）+ 跑8个ML模型比准确率 的论文方案。

### 特征

1. **无临床问题出发** → 纯算法拼凑，从数据集出发而非从临床需求
2. **无方法论创新** → 无架构创新，无新假设，仅"比准确率"
3. **无研究空白** → 已有大量类似论文，无 gap
4. **数据集依赖** → 方法论价值在数据集本身，不在方法
5. **教学项目** → 适合课程作业，不适合SCI论文

### 判定流程

```
收到论文方向请求
    ↓
检查: 是否"UCI/Kaggle数据集 + N个ML模型比准确率"？
    ↓
是 → 判定为"伪UCI管线" → Method Gate FAIL
    ↓
纠正: 提出 HCS-3WT 模式（临床流程→结构缺陷→方法创新→代码验证）
    ↓
用户选择继续 → 诚实记录局限性，继续管线（压力测试双质量门）
```

### 2026-06-06 实际案例

stroke-prediction 原始方案：
- 声称 UCI Healthcare Dataset
- 跑 LR/DT/RF/GBM/SVM/KNN/NB/ANN 8个模型
- 比 accuracy 和 AUC
- 无临床问题，无方法创新，无gap

→ 判定为"伪UCI管线" → Method Gate FAIL

→ 用户要求继续 → 诚实记录局限性，按完整管线重做

### 成功替代方案

参考 HCS-3WT 乳腺癌论文：
1. 从临床诊断流程出发
2. 发现结构性缺陷（灰区未处理）
3. 提出方法论创新（三向决策架构）
4. 用真实数据验证
5. 核心贡献是架构创新

stroke 方向的类似路径：
- 从 stroke 诊断/风险预测流程出发
- 发现结构性缺陷（时间窗口/异质性/多模态/不确定性）
- 提出方法论创新（如 cascade triage / temporal risk / multi-view）
- 用真实或公开数据验证
- 核心贡献是方法创新，不依赖特定数据集

## HCS-3WT 范式参考

HCS-3WT 乳腺癌论文的核心模式：
1. 临床诊断流程 → 发现"灰区"未处理
2. 提出三向决策 → Clear Negative / Clear Positive / Gray Zone
3. 用真实数据验证 → 10×5 CV
4. 核心贡献是架构创新 → 不依赖特定数据集

stroke 类比：
- 从 stroke 风险预测流程出发
- 发现"不确定区域"未处理
- 提出 cascade/triage/temporal 方法架构
- 用数据验证方法论

## 相关文档

- `../quality-gate/references/stroke-pipeline-failure-case-study.md` — 完整失败案例
- `../quality-gate/SKILL.md` → "方法论文选题质量前置审计"章节
