# Synthos-NotebookLM 整合工作流

> Synthos ACQ/EXT 原子 ↔ NotebookLM 笔记本的双向知识管理

## 工作流：ACQ检索 → 创建摘要 → 添加到NotebookLM

当用户要求「用Synthos系统管理NotebookLM」时，执行以下工作流：

### Step 1: 检查环境
```bash
notebooklm list --json          # 确认NotebookLM可用
notebooklm use <notebook_id>    # 切换到目标笔记本
notebooklm source list          # 确认现有来源，避免重复
```

### Step 2: 用Synthos ACQ检索新文献
```bash
# OpenAlex (最新年度)
curl -s "https://api.openalex.org/works?search=KEYWORDS&filter=from_publication_date:YYYY-01-01&per_page=5&select=id,title,publication_year,doi,authorships"

# PubMed (按日期排序)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=KEYWORDS&retmax=5&sort=date&retmode=json"
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=IDS&retmode=json"
```

### Step 3: 过滤去重
- 对比 `notebooklm source list` 输出
- 排除标题已存在的论文
- 排除DOI已存在的论文

### Step 4: 创建摘要Markdown
```markdown
# Latest PAPERS (YYYY)
> Auto-discovered by Synthos ACQ on YYYY-MM-DD
> Source: OpenAlex + PubMed

## 1. Paper Title
- **Year**: YYYY
- **DOI**: xxx
- **Source**: OpenAlex/PubMed
- **Relevance**: High/Medium — 一句话说明与本笔记本主题的关联
- **Novelty**: 核心贡献描述
```

### Step 5: 添加到NotebookLM笔记本
```bash
notebooklm source add /tmp/latest_papers.md
```

### Step 6: 验证
```bash
notebooklm source list | grep "latest\|ADDED"    # 确认来源已添加
notebooklm summary                                # 确认AI能识别新内容
```

## 工作流：NotebookLM审计 → 发现缺口 → Synthos填补

1. 执行完整审计工作流（见 `references/notebooklm-audit-workflow.md`）
2. 识别single-source笔记本（🔴标志）
3. 用Synthos ACQ搜索该主题的最新文献
4. 创建结构化摘要并添加为来源
5. 对于标书/项目文书类缺口：在本地文件系统中搜索 `*标书*` / `*project*` / `*grant*` 等

## 已知缺口模式

| 审计发现 | Synthos行动 | 典型文件位置 |
|---------|------------|-------------|
| NSFC笔记本仅1来源 | 添加ADHD标书全文 | `~/project_application_reconstructed.md` |
| 系统笔记本仅PPTX | 添加建设说明书+技术路线图 | `project/docs/智能体建设说明书.md` |
| 文献笔记本缺最新论文 | ACQ检索2025-2026年文献 | 创建摘要 → notebooklm source add |
| PDF命名不规范 | 建议重命名 | 12字符UUID前缀法 |

## 关键规则

- **私人审计报告目录**：`~/notebooklm-audit/`（非公开项目docs/下）  
- **来源不可跨笔记本移动**：NotebookLM没有"move source"功能。如需重组（如拆分一个大杂烩笔记本）：(1) 重命名原笔记本为"归档-原名"，(2) 新建聚焦笔记本，(3) 用Synthos ACQ检索最新文献填充新笔记本。**不要试图迁移旧笔记**——新文献比旧笔记更有价值。
- **批量添加**：一次添加1-3个来源即可，避免notebooklm source list超时
- **来源命名**：摘要文件用 `YYYY_Topic_关键词.md` 格式
