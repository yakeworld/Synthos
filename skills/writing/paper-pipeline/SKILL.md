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
    version: 3.12.0
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
  ↓
P1: 文献检索 → notebooklm-cli逐问法 → Gap/Hypothesis
  ↓
P2: 论文构建 → Results→Methods→Discussion→Introduction (NotebookLM逐节Q&A)
  ↓
P3: LaTeX编译 → pdflatex/bibtex → 版本文件对比
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
| **NotebookLM优先** | 所有论文节必须通过notebooklm ask逐节由Gemini生成，跳过=违规 |
| **09-目录体系** | 01-manuscript / 02-submission / 03-code / 04-data / 05-figures / 06-references / 07-quality / 08-records / 09-background |
| **双质检** | Layer A(本地7维) + Layer B(Gemini评审)，校准分=min(A,B) |
| **修订循环** | 不达标→自动修订，连续3轮无进展→降级目标期刊 |
| **工作目录** | 所有论文统一在 Synthos/outputs/papers/{paper-name}/ |
| **P6强制** | 论文完成后必须提炼skill+修补陷阱+记录进化 |

## 编译与质检

```bash
# 编译
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex

# 质量门
# L0.5数据门 → 提取数值声明→追溯源文件
# Layer A → 7维评分
# Layer B → notebooklm ask "7维SCI评审"

# 清理
rm -f *.aux *.bbl *.blg *.log *.out *.spl
```

## 子skill映射

| 阶段 | 加载skill | 产出 |
|:-----|:----------|:-----|
| P-1文献检索 | `research-paper-search` | 候选文献集 |
| P1知识提取 | `notebooklm-cli` (逐问法) | Gap/Hypothesis |
| P2论文写作 | `notebooklm-cli` (逐节ask) | LaTeX节文件 |
| P3编译 | `latex-output` | PDF |
| P4质检 | `quality-gate` | 质量报告 |
| P5投稿 | — | 提交包 |
| P6提炼 | `project-experience-distillation` | 新skill/修补 |

## 参考文件

- `references/paper-section-generation.md` — 各节Q&A模板
- `references/notebooklm-quality-gates.md` — 5门质量评估Detail
- `references/paper-dir-unification-workflow.md` — 目录统一协议
- `references/latex-editing-pitfalls.md` — LaTeX编辑陷阱
- `references/paper-project-optimization-cycle.md` — 6阶段优化循环
- `references/duplicate-bibliography-fix-2026-05-30.md` — 重复bibliography修复
- `references/citation-quality-fix-workflow.md` — 引用修复工作流
- `references/submission-preparation.md` — 投稿准备清单
