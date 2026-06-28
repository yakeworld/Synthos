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

---

*格物致知，知止而后有定. Scattered knowledge, once organized, becomes wisdom.*
