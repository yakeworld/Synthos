---
name: personal-knowledge
description: "Personal Knowledge Management - Integrates 44 papers, 33 literature reviews, 90+ project outputs into structured searchable knowledge. Converts scattered step_*.md, reference_*.md, paper.tex files into a connected knowledge graph."
version: 1.0.0
author: Synthos
license: MIT
allowed-tools: shell (bash, find, grep, awk, sort, uniq), Read (view), Write (write), glob, Edit (edit)
metadata:
  synthos:
    priority: P1
    atom_type: cognitive_atom
    description: "Personal knowledge management - integrates and indexes all research outputs into a structured, searchable knowledge graph"
    signature: "query: str, scope: str -> knowledge_items: list[dict], gaps: list[str]"
    related_skills:
      - knowledge-acquisition
      - knowledge-extraction
      - association-discovery
      - argument-expression
      - evolution
---

# Personal Knowledge Management (个人知识管理)

## Core Positioning

> **格物致知，知止而后有定.** Collect is not the goal; organization is. 947 reference files and 934 step files are not clutter - they are an unindexed goldmine.

Goal: Convert all Synthos outputs across 98 evolution cycles, 103 paper projects, and 44 formal papers into structured personal knowledge for fast retrieval, cross-connection, and trend analysis.

## IO_CONTRACT

- **input**: query: str - Natural language search query
- **input**: scope: str = "all" - Search scope (papers/references/output/logs)
- **output**: knowledge_items: list[dict] - Structured knowledge entries (title, summary, source, date, links)
- **output**: summary: str - Synthesized answer to the query
- **output**: gaps: list[str] - Knowledge gaps (valuable but uncovered areas)

## Knowledge Domains Index

| Domain | Papers | Primary Methods | Keywords |
|--------|--------|-----------------|----------|
| Vestibular (VOR) | 15+ | ODE, PINN | VOR, saccade, vestibular, compensation, adaptation |
| Eye Movement | 10+ | ODE, PINN | saccade, pursuit, fixation, blink, vergence |
| Inner Ear/Vestibular Disease | 8+ | ODE, PINN | BPPV, Meniere, vestibular schwannoma, tinnitus |
| Cornea/Anterior Segment | 5+ | ODE, PINN | cornea, IOP, sclera, hydration, wound healing |
| Iris/Sclera | 4+ | 3D modeling, segmentation | iris, sclera, 3D, normalization |
| Visual-Vestibular Cross | 3+ | ODE, PINN | auditory-vestibular, tinnitus, multisensory |
| Breast Cancer Dx | 1+ | Methodology paper | breast cancer, HCS-3WT, ML |
| Methodology | 7+ | Lit review, CRISP-DM | research methods, experimental design, data science |
| Neurology | 4+ | Review, case study | PD, concussion, stroke, neurology |

## Execution Steps

### Step 1: Knowledge Scan

Scan all output files:
- Paper files: find outputs/papers -name "*.tex"
- Step files: find . -name "step_*.md"
- Reference files: find . -name "*reference*.md" -o -name "*-review.md"
- Logs: evolution-log.md, agent-log.md

### Step 2: Structure Extraction

Extract from each file:
- Title (from filename, content, or LaTeX title)
- Domain (topic keywords: VOR, PINN, ODE, BPPV, iris, etc.)
- Method (ODE, PINN, literature review, systematic review)
- Date (extracted from filename or content)
- Status (draft/complete/pending/publication)
- Connections (cites other papers, cited by others)

### Step 3: Association Building

- Topic networks: papers on same topic
- Method evolution: method progression (e.g., ODE -> PINN)
- Timeline: chronological knowledge progression
- Citation chains: inter-paper citation relationships

### Step 4: Knowledge Graph

Generate knowledge-graph.json with:
- Nodes: each knowledge entry
- Edges: topic, method, citation associations
- Properties: date, status, quality score

### Step 5: Query Interface

Support these query patterns:
- Domain search: "all papers about VOR"
- Method search: "all studies using PINN"
- Time search: "all outputs from May 2026"
- Status search: "all pending submissions"
- Association search: "which studies use same math methods?"
- Gap discovery: "which areas remain unstudied?"

## Quality Control

- P0 Evidence traceability: Every knowledge entry must have a source file
- P1 Atomic reproducibility: Every knowledge extraction step independently executable
- P2 Stability sinking: Validated patterns sink to standard classifications
- P3 Human-machine layering: User decides what knowledge to keep

## Output Files

- knowledge-graph.json - Structured knowledge graph
- knowledge-index.md - Knowledge index by topic/time/method
- research-timeline.md - Chronological research progress
- knowledge-roi.md - Time/output ROI analysis per domain


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

---

*格物致知，知止而后有定. Scattered knowledge, once organized, becomes wisdom.*
