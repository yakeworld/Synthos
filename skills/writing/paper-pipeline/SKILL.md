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
    - data-driven-hypothesis
    execution_note: 吸收子skill内容在 references/*-absorbed.md。data-driven-hypothesis output (gap_analysis.json) feeds into paper-pipeline HYP stage when starting from public datasets.
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
| 持续推进 | **流水线不间歇，论文逐个推进** | paper-orchestrator常驻后台，非cron定时触发 |

## paper.tex 手动装配（paper-orchestrator.py 缺失时）

环境缺少 `scripts/paper-orchestrator.py`，论文从 gap_analysis → abstract → ... → quality_check 必须手动完成，然后手动装配 paper.tex 并编译 PDF。

**Assembly流程**: 见 `references/paper-tex-assembly-pattern.md` — 读取已完成论文模板，复制格式（article class, 作者/地址/期刊），将各 step 文件转换为 LaTeX。

**陷阱：paper.tex 双位置（v50）**: 论文目录中 `paper.tex` 可能同时存在于根目录和 `01-manuscript/` 子目录。`find` 无深度限制会返回两个结果，导致完成计数虚高（如 47 root → 111 total）。只统计根级别（`-maxdepth 2`）。详见 `references/paper-tex-dual-location.md`。

**Template**: 见 `templates/pinn-ode-paper-template.tex` — PINN/ODE 论文的标准 paper.tex 骨架，包含一致的文档结构、隐藏层配置（128-256-256-128, SiLU）、损失权重（λ_data=1.0, λ_ode=0.1, λ_smooth=0.01）、编译步骤。直接复制后替换内容即可。

**Orphaned Paper Recovery**: 当 gap_analysis 存在但 IMRaD 步骤为空时，见 `references/gap-to-imrad-template.md` — 完整的 gap_analysis → IMRaD 步骤 → paper.tex → PDF 恢复流程。

**Caloric Nystagmus Domain**: 见 `references/caloric-nystagmus-computational-model.md` — 前庭温热刺激机制、Azzi 1964经典ODE、临床解释、白空间验证(Paper 70)。

**Binaural-Vestibular-PINN Example**: 见 `references/binaural-vestibular-PINN-paper-71-example.md` — Paper 71 完整单会话管线完成示例，2-ODE coupled 系统，MAPE 7.8%, R² 0.93, AUC 0.90, PDF 9 pages 177KB, 0 errors。

**编译**：`pdflatex -interaction nonstopmode paper.tex`（2次运行以解析交叉引用），典型输出 8-14 页，180-260 KB。