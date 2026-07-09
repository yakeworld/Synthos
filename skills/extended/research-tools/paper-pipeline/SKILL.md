---
name: paper-pipeline
category: research-tools
signature: "paper_path: str -> analysis_report: dict"
description: 论文管线 — 组合3个核心步骤：检索→下载→质检。所有子步骤走独立脚本。
author: Synthos
license: MIT
version: 3.0.0
metadata:
  synthos:
    atom_type: composite-skill
    description: Paper pipeline — retrieval → download → quality check. All sub-steps call scripts.
    signature: "research_topic: str -> final_paper: str, quality_report: dict"
    related_skills: ['literature', 'pdf-download-engine', 'quality-gate']
---

# Paper Pipeline

> 管线即流程。不写代码，调用脚本。不判断，执行流程。

## 核心流程

```
用户查询
  → [Step 1] 知识获取 (literature search)
    → search_results.json (论文列表)
  → [Step 2] PDF 下载 (literature download)
    → paper.pdf (全文)
  → [Step 3] 质量检查 (quality-gate)
    → quality-report.md (质量报告)
```

## 执行步骤

### Step 1: 知识获取

调用 `literature` 技能的 `literature.py search` 子命令：
- 输入：用户研究主题
- 输出：`search_results.json`（论文列表，含 DOI、标题、摘要、PDF链接）
- 参考：`skills/extended/research-tools/research/literature/SKILL.md`

### Step 2: PDF 下载

对 Step 1 结果调用 `literature` 技能的 `literature.py download` 子命令：
- 输入：`search_results.json`（从 `literature.py search` 输出）
- 输出：PDF 文件 + `download_report.json`
- **内部机制**：使用 `sequential_download()` 串行顺序下载（替代旧的 `race_downloads()` 并行竞态）
- 参考：`skills/extended/research-tools/research/literature/SKILL.md`

**注意**：Sci-Hub 目前不可用（所有域名失效），下载主要依赖 OA 直链（Unpaywall、arXiv、Frontiers 等）。

### Step 3: 质量检查

对下载完成的论文目录调用 `quality-gate` 技能：
- 输入：论文目录路径
- 输出：`quality-report.md` + `quality_report.json`
- 参考：`skills/core/quality-gate/SKILL.md`

### Step 4: 修复循环

如质量检查未通过：
1. 读取 `quality-report.md` 的问题清单
2. 参考 `quality-gate/refs/quality-gate-fix-recipes.md` 获取修复方案
3. 执行修复
4. 返回 Step 3

## 论文标准目录结构

```
{paper-name}/
├── paper.tex          # 主文件
├── paper.bib          # 参考文献
├── state.json         # 状态/评分
├── quality-report.md  # 质量报告
├── 01-manuscript/
├── 02-abstract/
├── 03-introduction/
├── 04-methods/
├── 05-results/
├── 06-discussion/
├── 07-figures/
├── 08-references/
└── 09-appendix/
```

## 陷阱

- 不要跳过 Step 3 — 没有质量检查的论文不能进入管线
- 质量检查失败必须执行修复循环，不能跳过
- 管线输出必须是结构化文件，不是 Agent 口头总结

## Golden

- Golden Input: `{topic: "vestibular ocular reflex"}`
- Golden Output: paper.tex compiled + quality-report.md with score ≥ 0.85
- Golden Error: exit code 1 when pipeline fails at any step

## Supplementary Citation Enrichment (after quality check)

When quality check identifies missing references or when user requests "补充检索更多文献":

1. Analyze existing citations: `grep "cite{" paper.tex | sort -u`
2. Multi-direction search: 5-8 queries covering different sub-domains
3. Score papers by relevance (method + domain + evaluation = 5-point scale)
4. Select 8-15 most relevant papers
5. Download PDFs — expect 30-50% failure rate on Cloudflare-protected journals
6. Convert to Markdown for reference directory
7. Add to `references.bib` and insert `\cite{}` in paper.tex at appropriate locations

## 论文收割（Cron 自动流水线）

从文献监控（literature-monitor）的输出自动收割论文：
1. 读取监控报告（`~/.hermes/cron/output/<job-id>/<latest>.md`）
2. 提取 PMID/DOI/标题/作者
3. PubMed E-utilities XML 模式批量 fetch（**必须用 `retmode=xml`**，JSON 模式经常返回空）
4. 为每篇创建 `outputs/papers/<slug>/` 目录，含 state.json + summary.md
5. 收割完成后，每篇论文进入质量检查流程

详见 `cron-paper-harvest` 技能。

## 相关脚本

- `scripts/literature-download.py` — 从 literature search 结果下载 PDF
- `scripts/unified_scan.py` — 批量扫描工具