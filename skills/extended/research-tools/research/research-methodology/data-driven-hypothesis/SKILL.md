---
name: data-driven-hypothesis
related_skills: ["hypothesis-generation"]
description: '从公开数据出发→数据探索→文献调研→发现gap→提出可验证假设。与"先有假设再找数据"相反，适合公开数据集方向探索。'
version: 1.0.0
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'dataset_or_publication_source -> gap_analysis -> hypotheses: list[dict]'

---

## IO_CONTRACT

- **input**: `dataset: dict, domain: str` — 用户请求描述、上下文信息
- **output**: `hypotheses: list — 数据驱动假设`


> 对应原则：P2（机械原子暴露输入输出规范）

# Data-Driven Hypothesis Generation

## 原理层·文言

| 概念 | 文言 | 义 |
|:-----|:-----|:----|
| 先有数据，后有问题 | **先见树，后见林** | 先探索数据特征，再提炼科学问题 |
| 数据即信号 | **数中有象** | 数据的统计异常本身就是研究线索 |
| 文献即镜 | **以文为镜** | 用文献确认哪些gap是真实的，哪些已被填补 |
| 假设即可证 | **假说必立证伪条件** | 每个假设必须有明确的淘汰条件 |

## 流程（四阶段）

```
数据获取 → 数据探索 → 文献调研 → gap→假设
  (1h)       (2h)       (2h)       (1h)
```

### Stage 1: 数据获取（1h）

1. **列出所有可用来源**：OpenML、Kaggle、UCI、HuggingFace、GitHub、直接URL
2. **逐一尝试**：每个来源尝试下载，记录成功/失败
3. **如实报告失败**：不伪造、不跳过。如果所有来源都失败，报告"数据不可访问"
4. **生成合成数据（仅当所有公开源都不可访问时）**：
   - 从原始论文/文档中提取数据集规格（样本量、特征、分布）
   - 使用 `random.seed(42)` 和 `np.random.seed(42)`
   - 匹配已知统计量（均值、标准差、类别分布）
   - **必须在元数据中明确标注"synthetic"**
   - 保存 `dataset_metadata.json` 记录生成方法

**产出**：`04-data/<dataset>.csv` + `04-data/dataset_metadata.json`

### Stage 2: 数据探索（2h）

对每个数据集执行以下分析：

1. **描述性统计**：每个特征的均值/中位数/标准差/最小值/最大值/缺失率
2. **类别分布**：每个分类变量的频数和百分比
3. **目标变量分析**：正负类比例、不平衡比
4. **子群分析**：按主要特征分组，计算各组目标率
5. **相关性分析**：特征与目标的简单相关性
6. **复杂交互**：检查关键特征的交叉组合
7. **缺失模式**：缺失是否随机？与哪些特征相关？
8. **极端值/异常值**：检测异常样本

**关键输出**：`07-quality/data-exploration.json` — 结构化所有发现

**发现原则**：
- 记录所有"不寻常"的统计模式
- 记录子群之间的显著差异
- 记录缺失数据中是否隐藏信号
- 记录单特征预测能力弱但组合预测能力强的现象

### Stage 3: 文献调研（2h）

1. **PubMed搜索**：使用多个关键词变体（≥5个query）
2. **Crossref搜索**：补充DOI信息
3. **提取关键信息**：标题、期刊、年份、摘要
4. **主题聚类**：将论文按方法学主题分组
5. **识别空白**：对比数据发现与文献结论

**产出**：
- `06-references/pubmed_papers.json` — PubMed搜索结果
- `06-references/literature_synthesis.json` — 主题聚类+关键发现

**文献审查原则**：
- 不是数数量，而是看方法论
- 关注：他们用了什么方法？解决了什么问题？
- 关注：哪些数据问题被处理了？哪些被忽略了？
- 关注：论文声称的"贡献"是否真实创新，还是只是"又一个ML对比"？

### Stage 4: Gap + 假设（1h）

1. **数据发现 vs 文献结论** → 找出未解决的问题
2. **Gap判定标准**：
   - Gap必须是数据中发现的，而非凭空想象
   - Gap必须在文献中确实不存在解决方案
   - Gap必须可验证（有具体的淘汰条件）
3. **假设生成格式**：

```json
{
  "name": "H1",
  "statement": "明确的可验证声明",
  "rationale": "从数据中发现支撑该假设的证据",
  "falsification": "什么结果能证伪该假设",
  "testable_prediction": "具体可测量的预测",
  "baseline_to_beat": "需要超越的基线方法"
}
```

**假设要求**：
- 至少3个假设（H1主攻，H2/H3辅助验证）
- 每个假设必须有falsification条件
- 每个假设必须可量化验证
- 假设之间可以互补或竞争

**最终产出**：`06-references/gap_analysis.json`

## 与"假设驱动"管线的区别

| 维度 | 数据驱动（本技能） | 假设驱动（paper-pipeline） |
|:-----|:---|:---|
| 起点 | 公开数据集 | 已知的研究问题 |
| 方法选择 | 从数据特征推导 | 从问题推导 |
| 适用场景 | 探索公开数据集、发现新问题 | 已有明确方向的论文写作 |
| 输出 | gap_analysis.json → 可作为HYP阶段的输入 | 直接生成论文 |

## 常见陷阱

1. **数据不可访问时不报告**：所有公开源失败必须如实报告，不能跳过
2. **合成数据不标注**：必须明确标注synthetic来源
3. **Gap与数据无关**：Gap必须从数据探索中发现，不是凭空想象
4. **假设不可证伪**：每个假设必须有明确淘汰条件
5. **文献调研走过场**：必须提取方法论信息，不只是数论文数量
6. **单一假设**：至少提出3个假设，覆盖不同维度的gap
7. **UCI数据集已不可访问**：healthcare-dataset-stroke-data.csv已从所有公开源消失。替代方案见 `references/uci-unavailability-2026-06-06.md`
8. **OpenML API格式**：OpenML返回结构为 `{"data": {"dataset": [...]}}` — 不是 `{"data": {"data": [...]}}`。`limit/5` 返回空列表（仅5条），必须用 `/api/v1/json/data/list` 无limit参数获取全部。DID字段是`did`不是`id`。详情见下文。
9. **数据集替代策略**：如果目标数据集不可访问，寻找功能相似的其他公开数据集。例如：没有stroke数据集时，OpenML有Cardiovascular-Disease-dataset（70000条，13个特征，50/50平衡），可作为stroke/CVD研究的替代数据源。

## OpenML 访问经验（2026-06-06 实战）

```bash
# 错误：/limit/5 返回空列表（仅5条不够搜索）
curl https://www.openml.org/api/v1/json/data/list/limit/5  # → 空

# 正确：无limit获取全部6408条数据集
curl -H 'Accept-Encoding: identity' https://www.openml.org/api/v1/json/data/list

# 返回结构：
# {"data": {"dataset": [{"did": 2, "name": "anneal", ...}, ...]}}
# 注意：是 'dataset' 不是 'data'，DID是 'did' 不是 'id'

# 搜索health/cardiovascular相关：
# 遍历全部数据集后本地过滤 name/description 字段
```

**关键教训**：OpenML网站可达（HTTP 200），但API需要正确的headers（`Accept-Encoding: identity`）和正确的端点格式。`/limit/N` 格式不可靠。

## Cardiovascular Dataset 作为替代（2026-06-06）

OpenML Cardiovascular-Disease-dataset (DID=45547) 特点：
- 70,000 条记录，13 个特征
- 目标：cardio（心血管疾病存在/不存在），50/50 类平衡
- 特征：age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active
- 无缺失数据
- 可从 `https://www.openml.org/data/v1/download/{file_id}` 直接下载ARFF格式

**注意**：这是CVD数据，不是纯粹的stroke数据。但在缺乏真实stroke数据集的情况下，它是目前最丰富的公开临床预测数据集。

## 参考文件

- `references/uci-unavailability-2026-06-06.md` — UCI Healthcare Dataset完全不可访问的记录和替代方案
- `references/data-driven-case-stroke.md` — stroke数据集探索完整记录（数据特征+文献+gap+假设）
- `references/hcs3wt-quality-optimization-2026-06-06.md` — 乳腺癌HCS-3WT论文双质量检查优化完整记录（D2-D7修复、LaTeX编译、预期评分提升）
- `templates/gap-analysis-template.json` — gap分析JSON模板