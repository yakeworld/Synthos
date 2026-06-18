# GOLDEN_SET.md — knowledge-acquisition

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一模型版本 → 等价结论通过金标准测试）
> golden_set_origin: self_defined

## 设计依据

本原子的金标准为自设（`self_defined`），因为多源学术论文检索目前没有公开的标准测试集。金标准的设计目标是验证：**给定相同的搜索查询（topic + keywords），原子能否从多个 API（S2/PubMed/OpenAlex）获取论文并输出结构化 paper 列表**。

核心验证维度：
1. **检索能力**：原子能否从指定源正确发起搜索请求
2. **解析能力**：原子能否正确解析各 API 返回的 JSON/XML 响应，提取 title/doi/year/authors/abstract
3. **标准化能力**：原子能否将异构源的数据统一为 `raw_papers` 契约格式
4. **去重能力**：多源检索后是否按 DOI 去重
5. **空结果处理**：无结果时输出空列表而非报错

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 搜索语言 | 2/2 种 | 纯英文、中英混合 |
| 搜索范围 | 3/3 种 | 窄范围（精准术语）、标准范围（3-5词）、宽范围（领域级） |
| 数据源覆盖 | 3/3 种 | semantic_scholar, pubmed, openalex |
| 源组合 | 3/5 种 | 全源、单源、双源 |
| 结果数量 | 3+ 篇 | 每个期望输出至少 3 篇真实论文 |
| 边缘案例 | 1 种 | 空搜索字符串 |

## 测试用例 (cases/)

### case_001: 标准英文搜索
- **topic**: `"ADHD eye-tracking children screening"`
- **keywords**: `["ADHD", "eye-tracking", "children", "screening"]`
- **sources**: `["semantic_scholar", "pubmed", "openalex"]`
- **期望**: ≥3 篇论文，topic 和 keywords 在标题/摘要中精确匹配或强语义相关；每篇包含完整字段（title, doi, year, authors, abstract_snippet）

### case_002: 中文混合搜索
- **topic**: `"ADHD 眼动追踪 儿童 筛查"`
- **keywords**: `["ADHD", "眼动追踪", "儿童", "筛查"]`
- **sources**: `["semantic_scholar", "pubmed", "openalex"]`
- **期望**: ≥3 篇论文，中英文混合查询正确解析；结果与 case_001 有重叠但不完全相同（跨语言检索的召回效果）

### case_003: 窄范围搜索（精准术语）
- **topic**: `"ADHD saccade inhibition"`
- **keywords**: `["ADHD", "saccade", "inhibition"]`
- **sources**: `["semantic_scholar", "pubmed"]`
- **期望**: ≥3 篇论文；论文应聚焦于眼跳抑制范式（反眼跳/正眼跳任务），比标准搜索更专精；只使用 2 个源验证双源模式

### case_004: 宽范围搜索（领域级）
- **topic**: `"neurodevelopmental disorders eye-tracking"`
- **keywords**: `["neurodevelopmental disorders", "eye-tracking"]`
- **sources**: `["semantic_scholar", "pubmed", "openalex"]`
- **期望**: ≥4 篇论文；领域更广（不限于 ADHD，可能包括 ASD、SLI 等），论文数量和质量因召回范围更宽

### case_005: 边缘案例 — 空搜索
- **topic**: `""`
- **keywords**: `[]`
- **sources**: `["semantic_scholar", "pubmed", "openalex"]`
- **期望**: `total_found: 0`，`papers: []`；原子不报错，返回空结果

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含完整的 papers 列表和 total_found。

期望输出（v0.1.0）采用**语义等价判定**：
- **标题**：与真实论文标题精确匹配（忽略大小写和标点差异）
- **DOI**：正确解析（去除 `https://doi.org/` 前缀）
- **年份**：与真实论文发表年份一致
- **作者列表**：第一作者和末位作者正确即可
- **abstract_snippet**：有效截取摘要的前 1-2 句，与原始摘要语义一致
- **total_found**：≥ 期望值即可（可多于期望值，表示检索成功）

### 可接受的偏差
- 不同数据源的 abstract_snippet 长度可能不同（S2 截断 vs PubMed 完整）
- 作者名格式可能不同（"Wang S" vs "S. Wang"）
- 同一篇论文可能来自不同源（source 字段不同）
- 多源检索时 papers 数组可能包含未在 expected 列出的额外论文（召回成功）

### 不可接受的偏差
- 论文标题不匹配（指示填充或 API 解析错误）
- 论文数量为 0 但期望非空（指示搜索失败）
- DOI 缺失或格式错误
- 年份超出合理范围（<1990 或 > 当前年份）

## pass_threshold: 0.80

含义：5 个测试用例中，至少 4 个通过（80%）。

### 阈值理由
- **不设 1.0**：多源 API 搜索具有非确定性——不同时间搜索结果可能因索引更新而变化
- **不设 < 0.8**：检索准确率是下游原子的基础，错误会传播
- **v0.1 暂时容忍**: 自设金标准仍在迭代，0.80 为初始阈值，随金标准成熟可上调至 0.85

### 单个 case 判定条件
1. `papers` 数组不为空（case_005 必须为空）→ 通过
2. 每篇论文包含 `title`, `doi`, `year`, `authors`（均为非空）→ 通过
3. 至少 1 篇论文的标题/DOI 与 expected 相匹配 → 通过
4. `total_found` ≥ expected 中的 `total_found` → 通过
5. （条件）所有上述条件通过 → case 判定为 PASS

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-11 | 初始自设金标准，5 个 case，覆盖中英文/宽窄范围/空查询 | Synthos Agent |
