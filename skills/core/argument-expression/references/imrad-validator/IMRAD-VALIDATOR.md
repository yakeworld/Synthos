# IMRaD 结构自动验证器

> 理论来源：IMRaD 标准格式 (ICMJE); 科学写作方法论

## IMRaD 结构定义

IMRaD 是生物医学/自然科学领域最通用的论文结构：
```
I — Introduction (引言)
M — Methods (方法)
R — Results (结果)
d — Discussion (讨论)
```

## 各节强制要素检查

### Introduction 节

| 检查项 | 必须包含 | 检测模式 |
|--------|----------|----------|
| 领域背景 | 至少 3 篇文献引用 | 引言长度 > 300 字 |
| 研究空白 | 明确 Gap 陈述 | "however", "remains", "not yet" |
| 研究目的 | 本文目标声明 | "we aim to", "this study", "here we" |
| 贡献列表 | 编号贡献声明 | "First", "Second", "Third" |
| CARS Move1 | 建立研究领域 | 领域重要性 + 文献综述 |
| CARS Move2 | 定位研究空白 | 转折词 + 空白描述 |
| CARS Move3 | 占领研究空白 | 目的 + 贡献 |

**不合格**:
- 无研究空白声明 → FAIL
- 无贡献列表 → WARNING
- 无 CARS Move2 → FAIL

### Methods 节

| 检查项 | 必须包含 | 检测模式 |
|--------|----------|----------|
| 研究设计 | 设计类型明确 | "randomized", "cohort", "simulation" |
| 材料/受试者 | 样本描述 | 纳入标准 + 样本量 + 来源 |
| 实验流程 | 可复现的流程描述 | 时间顺序/步骤标记 |
| 测量工具 | 工具名称 + 信效度 | "measured by", "using", "validated" |
| 统计方法 | 统计检验明确 | "t-test", "ANOVA", "regression" |
| 伦理声明 | IRB/伦理委员会批准 | "approved by", "informed consent" |

**不合格**:
- 无可复现的流程描述 → FAIL
- 无统计方法描述 → WARNING
- 无伦理声明 (涉及人类/动物) → FAIL

### Results 节

| 检查项 | 必须包含 | 检测模式 |
|--------|----------|----------|
| 主要发现 | 主要结果陈述 | 与 Research Question 对应 |
| 次要发现 | 次要结果 | 补充发现 |
| 统计检验 | p 值/CI/效应量 | 数字 + 统计术语 |
| 表格/图表 | 数据可视化 | Table/Figure 引用 |
| 数据完整性 | 无选择性报告 | 所有预注册结局 |

**不合格**:
- 无统计检验 → FAIL
- 仅文字描述无数据 → FAIL
- 表格/图表 < 2 → WARNING

### Discussion 节

| 检查项 | 必须包含 | 检测模式 |
|--------|----------|----------|
| 主要发现总结 | 回扣 Results | "Our results show" |
| 与文献对比 | 与已有研究比较 | "consistent with", "in contrast" |
| 机制解释 | 为什么这样 | 因果解释/理论支撑 |
| Limitations | 局限性 (≥3条) | "limitation", "despite", "however" |
| 临床/实际意义 | 实际应用价值 | 具体应用场景 |
| 未来方向 | 后续研究建议 | "future work", "further" |

**不合格**:
- Limitations < 3 → WARNING
- 无与文献对比 → WARNING
- 无未来方向 → INFO

### 其他

| 检查项 | 必须包含 |
|--------|----------|
| Abstract | 结构/背景/方法/结果/结论完整 |
| Conclusion | 回扣 Introduction 的 Gap |
| References | 格式一致, DOI 可查 |

## 系统论文特殊规则

系统论文 (如 Synthos) 的 Methods 分裂为:
```
Methods → Architecture (系统是什么) + Evolution (系统怎么生长)
```
- Architecture 必须有: 设计原理 + 核心组件 + 哲学→工程映射
- Evolution 必须有: 进化状态机 + 质量门控 + 外部吸收管线

## 不合格判定

```
直接 FAIL:
- Introduction 无 Gap 声明
- Methods 无可复现流程
- Results 无统计检验
- 涉及人类/动物无伦理声明

WARNING:
- 表格/图表 < 2
- Limitations < 3
- 无与文献对比
- 无统计方法描述

PASS: 无 FAIL 且 WARNING ≤ 1
REVISE: WARNING 2-3
REJECT: WARNING ≥ 4 或有 FAIL
```

## 理论来源

- ICMJE (International Committee of Medical Journal Editors). Recommendations for the Conduct, Reporting, Editing, and Publication of Scholarly Work in Medical Journals.
- IMRaD format standard: Introduction-Methods-Results-and-Discussion
- Wager E & Williams P (2004). "Lessons from EMMA: Evaluating manuscripts using the IMRaD structure." BMJ.
