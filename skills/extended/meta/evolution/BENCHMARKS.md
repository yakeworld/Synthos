# Synthos Evolution Benchmarks — 功能测试基准

## 概述

结构探测只检查文件是否存在，功能测试验证原子是否能**完成实际任务**。
每个原子有 2-3 个基准测试场景，每轮进化循环随机选 1 个执行。

## 轮转策略

每轮测试 2-3 个原子（非全部，太贵）：
- **奇数轮**：knowledge-acquisition + knowledge-extraction + association-discovery
- **偶数轮**：hypothesis-generation + argument-expression + viewpoint-verification
- **每轮都测**：task-router（简单路由测试，成本低）

## Benchmark 测试场景

### task-router — 路由准确性测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| ROUTE-01 | "找ADHD眼动追踪论文" | 链=[knowledge-acquisition], 复杂度=simple | 1篇论文即可, 不执行下游 @pass=1.0, @partial=0.5 |
| ROUTE-02 | "分析ADHD眼动追踪文献趋势并找出知识空白" | 链≥3个原子 | 路由中应包括acquisition+extraction+association @pass=1.0 |
| ROUTE-03 | "写一篇ADHD+VR的综述论文，并验证结论" | 链=full (6原子) | 路由应包括expression+verification @pass=1.0 |

注：路由测试**不执行原子**，只验证路由器的分析结果。

### knowledge-acquisition — 文献检索功能测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| ACQ-01 | 查询"ADHD eye tracking machine learning" | ≥5篇论文，≥2个来源 | 数量+来源多样性 @pass=1.0, ≥3篇@partial=0.5 |
| ACQ-02 | 查询"头戴式眼动 ADHD 筛查"（中英文） | ≥3篇相关论文 | 需同时搜索中英文 @pass=1.0 |

### knowledge-extraction — 知识提取功能测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| EXT-01 | 从1篇论文摘要提取结构化知识 | 输出含method/finding/conclusion/limitation | 4字段完整@pass=1.0, ≥2字段@partial=0.5 |
| EXT-02 | 从1篇PDF全文提取 | output中存在knowledge_items数组，每项含source_type和content | @pass=1.0 |

### association-discovery — 关联发现功能测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| ASC-01 | 分析2篇ADHD眼动追踪论文的关系 | 至少1个associations条目 | @pass=1.0 |
| ASC-02 | 寻找研究空白 | research_gaps数组非空 | @pass=1.0 |

### hypothesis-generation — 假设生成功能测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| HYP-01 | 基于关联分析结果生成研究假设 | ≥1个hypotheses条目，含rationale和testability | @pass=1.0 |
| HYP-02 | 假设有CRISP-DM方案 | CRISP-DM plan存在 | @pass=1.0 |

### argument-expression — 论证写作功能测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| ARG-01 | 将假设写成论文章节 | 至少1个section，含evidence支撑 | @pass=1.0 |
| ARG-02 | 输出含markdown格式 | 段落完整，有引用标记 | @pass=1.0 |

### viewpoint-verification — 观点验证功能测试

| 测试ID | 输入 | 期望输出 | 评分标准 |
|--------|------|---------|---------|
| VER-01 | 验证一个研究假设 | 至少1个counterargument | @pass=1.0 |
| VER-02 | 输出含confidence评估 | confidence字段存在且为数值 | @pass=1.0 |

## 综合评分

```
综合分 = 结构分 × 0.30 + 基准分 × 0.40 + 技能树覆盖率 × 0.20 + 外部吸收潜力 × 0.10
```

| 级别 | 综合分范围 | 状态 |
|------|-----------|------|
| EXCELLENT | ≥0.85 | 系统健康 |
| GOOD | 0.70-0.84 | 小幅优化 |
| FAIR | 0.50-0.69 | 需关注 |
| POOR | <0.50 | 需人工干预 |

### Golden 金标准验证（v2.2 新增）

每轮BENCHMARK新增 golden 验证子步骤。加载被测试原子的 `golden/cases/case_001.json` 作为输入，与 `golden/expected/case_001.json` 的格式/结构做对比，验证 I/O 契约一致性。

| 测试ID | 类型 | 原子 | 验证内容 | 评分标准 |
|--------|------|------|---------|---------|
| GOLD-ROUTE | golden | task-router | 加载case_001，验证complexity字段类型正确 | @pass=1.0 |
| GOLD-ACQ | golden | knowledge-acquisition | 输入含topic/keywords/sources，输出含papers/total_found | @pass=1.0 |
| GOLD-EXT | golden | knowledge-extraction | 输入含raw_papers，输出含extracted_knowledge/field_summary | @pass=1.0 |
| GOLD-ASC | golden | association-discovery | 输入含knowledge_items，输出含associations/research_gaps | @pass=1.0, part=0.5 |
| GOLD-HYP | golden | hypothesis-generation | 输入含associations/research_gaps，输出含hypotheses | @pass=1.0, part=0.5 |
| GOLD-ARG | golden | argument-expression | 输入含hypotheses/structure，输出含sections/references | @pass=1.0, part=0.5 |
| GOLD-VER | golden | viewpoint-verification | 输入含hypothesis/argument，输出含verdict/confidence_score | @pass=1.0, part=0.5 |

### PW-Bench 评价模式（v4.0 新增 — 吸收自 PaperOrchestra/PaperWritingBench）

新增三种评价维度，用于评估**论文产出质量**而非单一原子功能：

| 测试ID | 原子 | 类型 | 输入 | 期望输出 | 评分标准 |
|--------|------|:----:|:----:|:--------:|:--------:|
| **CITATION-F1** | argument-expression | quality | 生成论文段落 + 引用列表 | citation_f1: {p0_precision, p0_recall, p0_f1, p1_precision, p1_recall, p1_f1, overall_f1} | JSON含所有字段 @pass=1.0 |
| **LITREVIEW-6AXIS** | argument-expression | quality | Introduction/Related Work 章节 | 6轴评分(0-100) + overall + penalties | 总分≥40 @pass=1.0 |
| **SXS-PAPER** | viewpoint-verification | quality | 两篇论文(A, B) | winner ∈ {A, B, tie} + justification | JSON字段完整 @pass=1.0 |
| **SXS-LITREVIEW** | viewpoint-verification | quality | 两篇论文的Introduction | winner ∈ {A, B, tie} + justification | JSON字段完整 @pass=1.0 |

评分整合机制：PW-Bench 评价分作为**吸收潜力因子**纳入综合分计算，不替代现有基准分。

### 反膨胀规则（LitReview 6轴评价必读）

| 规则 | 硬上限 |
|:----|:------:|
| 默认期望 | 总分 45-70 |
| > 85 需六轴全强证据 | — |
| > 90 极罕见（综述级） | — |
| 任何一轴 < 50 | 总分 ≤ 75 |
| 描述性综述 | 轴3(批判分析) ≤ 60 |
| 无对比创新声明 | 轴4(定位) ≤ 60 |
| 稀疏引用 | 轴6(引用严谨性) ≤ 60 |

**golden 得分规则**：
1. 加载 case_NNN.json（输入）和 expected/case_NNN.json（期望输出）
2. 验证输入 JSON 必须包含 GOLDEN_SET.md 描述的所有必填字段
3. 验证期望输出 JSON 必须包含所有必填结构字段
4. 如果 JSON 有效且字段完整 → PASS
5. 如果 JSON 有效但缺少 1-2 个次要字段 → PARTIAL
6. 如果 JSON 解析失败或缺失 → FAIL

## 基准分计算

```
基准分 = (API测试通过数 + golden测试通过数) / (API测试总数 + golden测试总数)
```

每轮不通过的测试在 report 中记录失败原因，连续 3 轮同一测试失败 → 标记为 DEGRADED。
