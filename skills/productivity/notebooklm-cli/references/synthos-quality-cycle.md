# Synthos Quality Improvement Cycle for NotebookLM Notebooks

> 2026-05-18 session extract: VOR数字孪生项目实践
> 笔记本从3个源→~20个源，D3文献支撑L1→L3

## 适用范围

任何需要系统性质量提升的 NotebookLM 笔记本（文献综述、基金申请、课程设计等），且笔记本是 **Owner** 状态（可上传新源）。

**不适用于**：Shared笔记本（仅可查询，不能上传新源）。

## 完整流程

### Phase 0: 调研与项目选择

```bash
# 1. 全量扫描笔记
notebooklm list --json

# 2. 选择目标笔记本（选Owner且内容可提升的）
# 3. 分析内容
notebooklm use <partial_id>
notebooklm summary      # 获取AI摘要
notebooklm source list  # 查看现有源文件
notebooklm ask "简短聚焦问题"  # 短查询获取深度内容（60s超时阈限）
```

### Phase 0.5: 创建Synthos Workspace

```bash
mkdir -p .hermes/projects/<project-name>/
```

三个核心文件：

| 文件 | 内容 |
|:-----|:------|
| `PROJECT.md` | 项目来源、核心主张、当前评估、P0缺口 |
| `QUALITY.md` | 6维质量矩阵 + 当前等级 + 目标等级 |
| `CHANGELOG.md` | 每Cycle记录：做了什么、效果指标 |

#### 6维质量矩阵

| 维度 | 检查 | L1→L4递进 |
|:-----|:-----|:-----------|
| D1 理论深度 | 数理建模或第一性原理？ | 经验→证伪框架 |
| D2 结构逻辑 | 研究内容递进？ | 碎片→递进多链路 |
| D3 文献支撑 | 笔记本内外部PDF/全文数 | 0篇→≥30篇 |
| D4 创新性 | 突破现有范式？ | 复现→新范式 |
| D5 可视化 | 技术路线图/流程图 | 纯文本→Nature标准 |
| D6 数据证据 | 预实验/已发表论文支撑 | 纯推理→独立验证 |

### Phase 1: quality-gate 基线评估

对所有维度打分当前等级，找出**分数最低的一个维度**（单指标聚焦原则）。标记为P0缺口。

### Phase 2: 修复（文献支撑示例）

#### 搜索策略（当S2 API限流时）

```bash
# 1. PubMed直接搜索
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<query>&retmode=json&retmax=6&sort=relevance"

# 2. 批量获取摘要（esummary — 有DOI和作者信息）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<comma_separated_PMIDs>&retmode=json"

# 3. 检查PMC可用性（esearch in PMC db）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=<pmid>[pmid]&retmode=json"
# 返回pmcid列表，非空＝PMC可用

# 4. 下载PMC全文（efetch — 最可靠的OA路径）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=<pmcid>&retmode=xml"
# 然后用正则去标签：re.sub(r'<[^>]+>', ' ', xml)
```

#### Fallback for non-PMC papers

```python
# 从efetch提取摘要创建Markdown上传
abs_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
# 提取 <AbstractText> 标签内容
# 创建 markdown: title + authors + journal + DOI + abstract
# 上传到NotebookLM
```

#### 批量上传

```bash
for f in "$dir"/*_pmc.txt "$dir"/*_abstract.md; do
  notebooklm source add "$f"
  sleep 0.5  # 避免NotebookLM限流
done
```

### Phase 3: 验证

```bash
notebooklm source list  # 确认所有新源状态为 ready
```

更新QUALITY.md中对应维度的等级评分。

### Phase 4: RECORD

1. 追加CHANGELOG.md（做了什么 + 效果指标表格）
2. `git add` + `git commit -m "[synthos] cycle N: <project> <dimension> Lx→Ly"`
3. 更新memory（可选 — 如session很复杂）

## 一次性原则

- 每Cycle只修**一个维度的一个等级**
- 不并行搜索+可视化+数据证据
- Cycle 1先搜索下载，Cycle 2再查S2恢复后补漏

## 已知陷阱

| 陷阱 | 现象 | 避免 |
|:-----|:-----|:------|
| NotebookLM ask超时 | 60s+的查询被截断 | 每次5-10秒的短问题，多轮追问 |
| S2 429限流 | "Too Many Requests" | 切PubMed直接搜索（无速率限制宽松） |
| PMC elink慢 | 每篇单独查PMC耗时30s+ | 批量查pmid列表，一次elink调用覆盖所有 |
| MDPI 403/HTML | curl下载返回HTML而非PDF | 用Crossref API获取元数据创建.md文件 |
| 发布商封锁 | BMJ/Elsevier/Sci-Hub不工作 | 只依赖PMC efetch + Markdown摘要回退 |
| 非Owner笔记本 | source add报错"Failed to get SOURCE_ID" | 先检查is_owner，不行的建新笔记本 |

## 示例（VOR数字孪生项目）

| Cycle | 聚焦 | 操作 | 效果 |
|:------|:-----|:-----|:-----|
| 0 | 调研 | 75笔记本→选#32 NotablLM | 定位NSFC面上申请 |
| 0.5 | 工作区 | PROJECT+QUALITY+CHANGELOG | 可追踪基线 |
| 1 | D3 L1→L2 | PubMed搜BPPV+Kappa+PINN，PMC下载x3 | 3→7源文件 |
| 2 | D3 L2→L3 | 5query×6=30候选，16下载/创建 | 7→~20源，覆盖5领域 |
| TBD | D5 L2→L3 | 技术路线图Nature风格 | — |
| TBD | D6 L1→L2 | 预实验论文补齐 | — |
