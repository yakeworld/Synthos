# GOLDEN_SET.md — association-discovery

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一模型版本 → 等价结论通过金标准测试）
> golden_set_origin: self_defined

## 设计依据

本原子的金标准为自设（`self_defined`），因为跨论文关联发现目前没有公开的标准测试集。金标准的设计目标是验证：**给定相同的结构化知识项集合，原子能否一致地识别关联类型、构建拓扑正确的知识图谱、检测有意义的研究空白**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 关联类型 | 3/3 种 | contradiction、supplement、evolution |
| 知识项规模 | 2–5 项 | 覆盖最小关联对到中等规模图 |
| 领域 | 2 种 | psychiatry、neurology |
| 边缘案例 | 2 种 | 单知识项（无关联可发现）、全不相关（无关联输出） |
| 空白类型 | 3 种 | population_gap、methodology_gap、domain_gap |

## 测试用例 (cases/)

### case_001: 标准矛盾关联
- **输入**: 2 个 KnowledgeItem，同一主题（ADHD eye-tracking screening），结论方向相反：
  - Item A: "eye-tracking biomarkers show 89% sensitivity" (positive finding)
  - Item B: "eye-tracking did not outperform traditional rating scales" (null finding)
- **期望**: ≥1 association, type=`contradiction`, confidence ≥ 0.6

### case_002: 补充 + 演进混合
- **输入**: 3 个 KnowledgeItem，同一领域（Alzheimer's biomarkers）：
  - Item A (2022): cross-sectional, blood biomarkers for early detection, n=120
  - Item B (2023): machine_learning, multi-modal biomarker fusion, n=500
  - Item C (2024): meta_analysis, validates blood+imaging biomarkers across 15 studies
- **期望**: ≥2 associations，包含 type=`evolution`（A→B 或 B→C），≥1 空白被检测（至少 medium priority）

### case_003: 无关联边缘案例
- **输入**: 3 个 KnowledgeItem，各自属于完全不同的领域和主题：
  - Item A: ADHD / eye-tracking / pediatric_psychiatry
  - Item B: stroke / neuroimaging / neurology
  - Item C: depression / pharmacotherapy / psychiatry
- **期望**: associations=[], knowledge_graph 仅有 3 个孤立节点，edges=0，research_gaps 可能为每个领域产生独立空白

### case_004: 单知识项边缘案例
- **输入**: 仅 1 个 KnowledgeItem
- **期望**: associations=[], knowledge_graph.nodes=1, edges=0，原子**不报错**但返回空关联，research_gaps 可从单篇论文局限推断

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含完整的 Association、KnowledgeGraph、ResearchGap 结构。

期望输出（v0.1.0）采用**语义等价判定**：
- `Association.type` 必须精确匹配期望值
- `Association.item1` 和 `item2` 必须正确引用 KnowledgeItem.id
- `knowledge_graph.statistics` 中 contradictions / supplements / evolutions 计数与期望一致
- `ResearchGap.priority` 精度 ±1 级（如期望 `high`，允许 `critical` 或 `high`，不允许 `medium`）
- `Association.description` 和 `ResearchGap.description` 语义等价（通过 LLM-as-judge）

## pass_threshold: 0.80

含义：4 个测试用例中，至少 3 个通过（75% 向上取整到 80%）。实际评估使用 3/4 = 0.75，但阈值设为 0.80 以推动 v0.2 增加至 5 个 case 后到达 4/5 = 0.80。

### 阈值理由
- **不设 1.0**：语义等价判定允许合理的措辞差异（同一关联的不同描述方式）
- **不设 < 0.75**：关联类型的错误分类会严重污染下游 hypothesis-generation 的输入
- **v0.1 暂时容忍**：自设金标准仍在迭代，4 个 case 中允许 1 个因边界模糊而失败

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-10 | 初始自设金标准，4 个 case | Synthos Agent |
