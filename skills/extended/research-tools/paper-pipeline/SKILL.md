---
name: paper-pipeline
category: research-tools
signature: "paper_path: str -> analysis_report: dict"
description: 论文管线 — 组合3个核心步骤：检索→下载→质检。所有子步骤走独立脚本。
author: Synthos
license: MIT
version: 2.0.0
priority: P0
allowed-tools: terminal, Read, Write, task_delegation
metadata:
  synthos:
    atom_type: composite-skill
    description: Paper pipeline — retrieval → download → quality check. All sub-steps call scripts.
    signature: "research_topic: str -> final_paper: str, quality_report: dict"
    related_skills: ['knowledge-acquisition', 'pdf-download-racing', 'quality-gate']
---

# Paper Pipeline

> 管线即流程。不写代码，调用脚本。不判断，执行流程。

## 核心流程

```
用户查询
  → [Step 1] 知识获取 (knowledge-acquisition)
    → papers.json (论文列表)
  → [Step 2] PDF 下载 (pdf-download-racing)
    → paper.pdf (全文)
  → [Step 3] 质量检查 (quality-gate)
    → quality-report.md (质量报告)
```

## 执行步骤

### Step 1: 知识获取

调用 `knowledge-acquisition` 技能：
- 输入：用户研究主题
- 输出：`papers.json`（论文列表，含 DOI、标题、摘要、PDF链接）
- 参考：`skills/core/knowledge-acquisition/SKILL.md`

### Step 2: PDF 下载

对 Step 1 结果调用 `pdf-download-racing` 技能：
- 输入：`papers.json`
- 输出：PDF 文件 + `download_record.json`
- 参考：`skills/extended/research-tools/research/paper-retrieval/research-paper-search/SKILL.md`

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

## 相关脚本

- `scripts/paper_dir_validator.py` — 论文目录结构验证
- `scripts/unified_scan.py` — 批量扫描工具
