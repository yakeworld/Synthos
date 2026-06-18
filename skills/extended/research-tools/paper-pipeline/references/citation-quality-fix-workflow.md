# Citation Quality Fix Workflow — 替换 GitHub 引用为学术文献

> 用途：当 NotebookLM 7维质量评审的 D7（引用质量）评分 < 0.85 时，按此流程修复。
> 实战验证：Synthos 论文 D7 0.75→0.95（2026-05-23）

## 核心观察

系统论文（描述框架/架构/工具本身）天然依赖 GitHub 项目引用。审稿人会质疑高比例的 GitHub 引用（>1/3）拉低权威性。**修复目标不是删除所有 GitHub 引用，而是为每条 GitHub 引用找到对应的学术文献作为理论支撑。**

## 三步修复流程

### Step 1: 识别问题引用

```bash
# 列出论文中所有 bibitem
grep '\\bibitem{' paper.tex   # 内联式 thebibliography
# 或
grep '@' references.bib       # 独立 bib 文件

# 分类：有 arXiv/DOI 的 ✅ | 纯 GitHub 链接 🔴
```

**常见场景**：

| 原始引用形式 | 问题等级 | 典型示例 |
|:-------------|:--------:|:---------|
| `GitHub URL only` | 🔴 | 大量 AI Agent 项目 |
| `GitHub URL + arXiv ID` | 🟡 | 已有预印本链接但可改进 |
| `正式会议/期刊论文` | ✅ | 无需处理 |

### Step 2: 搜索学术替代

使用两个 API 串行搜索：

```python
# Semantic Scholar（串行，3.2s 间隔）
url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=3&fields=title,year,externalIds"
# 返回: ArXiv ID, DOI

# OpenAlex（无限制）
url = f"https://api.openalex.org/works?search={query}&per_page=3&sort=cited_by_count:desc"
# 返回: publication_year, doi, ids.arxiv
```

**搜索关键词策略**：

| 目标类型 | 搜索词示例 |
|:---------|:-----------|
| 大型开源项目 | `"项目名" + "论文标题关键词"` |
| 框架/库 | `"项目名" + "sota OR survey OR benchmark"` |
| 方法论 | `"核心概念" + "original paper author names"` |
| 无对应论文 | 改进 GitHub 引用格式（去⭐标，加描述） |

**搜索执行规范**：
- 所有请求串行，每请求后 sleep ≥ 3.2s
- 达到 429 → 切到 OpenAlex
- arXiv 不稳定（export.arxiv.org 经常 down），优先 Semantic Scholar / OpenAlex

### Step 3: 更新引用并验证

```latex
% ❌ 旧格式（纯 GitHub，带⭐标）
\bibitem{project2024}
  Author, ``Project Name,'' 2024. [Online]. Available: \url{https://github.com/...}

% ✅ 新格式（学术论文优先）
\bibitem{author2024paper}
  Author et al., ``Title,'' \textit{arXiv:XXXX.XXXXX}, 2024.

% ✅ 保留 GitHub 引用的正确格式（无⭐标）
\bibitem{project2024}
  Author, ``Project Name,'' GitHub repository, 2024. [Online]. Available: \url{https://github.com/...}
```

**验证**：
```bash
# 1. 检查 cite × bib 匹配度
grep -oP '\\cite\{[^}]+\}' paper.tex | tr ',' '\n' | sed 's/.*{//;s/}.*//' | sort -u > /tmp/cites.txt
grep -oP '\\bibitem\{[^}]+\}' paper.tex | sed 's/.*{//;s/}.*//' | sort -u > /tmp/bibs.txt
diff /tmp/cites.txt /tmp/bibs.txt  # 空输出 = 完全匹配

# 2. NotebookLM 重评验证
cat paper.tex | notebooklm note create --title "Paper v<N> - citations fixed"
notebooklm ask "请重新评估引用质量D7，评估替换后的学术引用是否合适，给出新评分"
```

## 实战案例：Synthos 论文

| 旧引用（GitHub） | 新引用（学术） | 来源 |
|:----------------|:--------------|:-----|
| SamaAI/AI-Scientist | Lu et al. arXiv:2408.06292 | Semantic Scholar |
| anthropics/claude-code | Bai et al. arXiv:2212.08073 | Semantic Scholar |
| HaiyangDiiing/aris-cli | Yang et al. arXiv:2605.03042 | Semantic Scholar |
| langchain-ai/langgraph | LangChain Preprints DOI:10.20944/preprints202411.0566.v1 | OpenAlex |

**结果**：D7 引用质量评分 0.75 → 0.95 🚀（NotebookLM 验证通过）

## 已知陷阱

1. **无对应论文的项目**：很多开源项目（如 GPT-Researcher, GEPA）没有正式学术论文。不要强行编造引用。正确的做法是：(a) 改进 GitHub 引用格式（删除 ⭐星光标），(b) 在论文正文中用调查类综述（如 Wang et al. 2024 survey）作为上下文支撑。
2. **arXiv 服务不稳定**：export.arxiv.org 经常 down 机。始终用 Semantic Scholar / OpenAlex 作为主搜索源。
3. **引用体操风险**：不要因为替换引用而改变论文正文的论证逻辑。替换引用时，正文中引用的"技术概念"必须与新引用文献的内容一致。
4. **DOI 协商返回 HTML**：`Accept: application/pdf` 对大部分出版商无效。仅用 DOI 查询元数据，不下载 PDF。