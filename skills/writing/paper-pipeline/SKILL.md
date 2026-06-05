---
name: paper-pipeline
description: '主skill | SCI论文全流程编排器。声明与执行分离、逐问收束、节点闸门、闭环进化。调用子skill: notebooklm-cli, sci-paper-standard-structure, research-paper-search, sci-paper-quality-review。质量检查统一通过 quality-gate。'
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
metadata:
  synthos:
    version: 3.13.0
    author: Synthos
    signature: 'paper_name: str -> pipeline_report: dict'
    absorbed_skills:
    - notebooklm-writing-workflow
    - synthos-writing-workflow
    - scc-paper-writing-norms
    - academic-paper-completion
    - public-dataset-prediction-paper
    - paper-reference-pipeline
    - research-paper-writing
    execution_note: 吸收子skill内容在 references/*-absorbed.md
---

# Paper Pipeline — 科研全流程编排器

## 原理层 · 文言

| 概念 | 文言 | 义 |
|:-----|:-----|:----|
| 声明与执行分离 | **先立后行，不混不乱** | 写好全文再编译，不边写边编 |
| 逐问收束 | **一问一答，渐次收窄** | 每轮NotebookLM问一个具体问题 |
| 节点闸门 | **节不过则停，门不通则返** | 每阶段完成必经质量门 |
| 闭环进化 | **投完不弃，检之改之** | 投稿后仍可自检修订 |
| 论文即验证 | **文以验法，技乃所产** | 可复用的技能才是真正产出 |

## 六阶段流程

```
P0: 预检闸门 → D10a僵尸/孤儿检测 + bib完整性检查
  │   D10a<100% + zombie>0 → bibitem完整性验证(quality-gate)
  │   D10a<100% + orphan>0 → 正文补插入引用
  ↓
P1: 文献检索 → notebooklm-cli逐问法 → Gap/Hypothesis
  ↓
P2: 论文构建 → Results→Methods→Discussion→Introduction (NotebookLM逐节Q&A)
  ↓
P3: LaTeX编译 → pdflatex → 版本文件对比
  ↓
P4: 双质检 → quality-gate (L0.5 + Layer A/B) → 修订循环
  ↓
P5: 投稿准备 → 目录标准化 + 提交包同步
  ↓
P6: 技能提炼 → project-experience-distillation → 进evolution
```

## 关键规则

| 规则 | 说明 |
|:-----|:------|
| **NotebookLM优先** | 所有论文节必须通过notebooklm ask逐节由Gemini生成，跳过=违规。若NotebookLM上传返回400错误，改用`references/notebooklm-fallback-lit-search.md` web_search 5方向法 |
| **09-目录体系** | 01-manuscript / 02-submission / 03-code / 04-data / 05-figures / 06-references / 07-quality / 08-records / 09-background |
| **双质检** | Layer A(本地7维) + Layer B(Gemini评审)，校准分=min(A,B) |
| **修订循环** | 不达标→自动修订，连续3轮无进展→降级目标期刊 |
| **工作目录** | 所有论文统一在 Synthos/outputs/papers/{paper-name}/ |
| **P6强制** | 论文完成后必须提炼skill+修补陷阱+记录进化 |

## 编译策略

```bash
# 方式A（推荐 — thebibliography内嵌，无需bibtex）：
pdflatex paper.tex && pdflatex paper.tex

# 方式B（外部.bib文件，需bibtex）：
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex

# 判断：参考文献≤25篇用方式A（thebibliography），≥30篇用方式B（.bib文件）
```

## 子skill映射

| 阶段 | 加载skill | 产出 |
|:-----|:----------|:-----|
| P-1文献检索 | `research-paper-search` | 候选文献集 |
| P1知识提取 | `notebooklm-cli` (逐问法) **或 web_search 5方向法** | Gap/Hypothesis |
| P2论文写作 | `notebooklm-cli` (逐节ask) | LaTeX节文件 |
| P3编译 | `latex-output` | PDF |
| P4质检 | `quality-gate` | 质量报告 |
| P5投稿 | — | 提交包 |
| P6提炼 | `project-experience-distillation` | 新skill/修补 |

## 关键陷阱

| 陷阱 | 说明 |
|:-----|:------|
| **NotebookLM 400上传错误** | 新notebook上传.ipynb/PDF返回400错误 → 跳过NotebookLM，改用web_search 5方向法做文献检索（`references/notebooklm-fallback-lit-search.md`），直接写论文 |
| **delegate_task大文件超时** | 委托子agent处理源文件>40KB或>500行时，会因token数超限而失败。必须先提取结构/关键内容再传参，或不使用delegate_task直接处理 |
| **手稿中的中文注释** | 从work目录提取BPPV手稿时，中文注释行(含Unicode范围\\u4e00-\\u9fff)需要过滤。使用python3检测并保留纯英文行 |
| **子agent作者信息造假** | 委托delegate_task/subagent写论文时，子agent常使用虚假作者信息（如Yake Wei/weiyake@example.edu）。需在任务描述中显式指定：作者Xiaokai Yang（zhriye@wzhospital.cn），通讯作者Xiaokai Yang, Department of Neurology, Wenzhou People's Hospital |

### T3→T2推高协议

系统综述审核的常见瓶颈（D2/D3/D7）及修复策略见 `references/t3-to-t2-push-protocol.md`。核心：D7全引用→D4 PRISMA流程图→D2误差传播算法→T2(0.80+)推高。T1需要临床验证数据。

## 参考文件

- `references/notebooklm-fallback-lit-search.md` — NotebookLM故障时备用文献检索方案（web_search 5方向法）
- `references/cron-paper-ingestion.md` — Cron论文入库模式（批量手稿→管线）
- `references/manuscript-merging-strategy.md` — 手稿合并模式（同类手稿→一篇论文）
- `references/code-to-paper-workflow.md` — 从已有notebook代码直接生成论文的快捷管线（跳过P1）
- `references/work-directory-scanning.md` — 从work目录发现未论文化的实验代码和手稿
- `references/t3-to-t2-push-protocol.md` — 系统综述T3→T2推高策略
- `references/paper-section-generation.md` — 各节Q&A模板
- `references/latex-editing-pitfalls.md` — LaTeX编辑陷阱
- `references/paper-dir-unification-workflow.md` — 目录统一协议
- `references/submission-preparation.md` — 投稿准备清单
