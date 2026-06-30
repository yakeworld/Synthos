---
name: proactive-discovery
description: "Proactive Discovery Engine - Automatically discovers new research opportunities, tracks trends, monitors competitors, and identifies gaps. Transforms the system from reactive to proactive."
version: 1.0.0
author: Synthos
license: MIT
allowed-tools: shell (bash, curl, wget), Read (view), Write (write), task_delegation
metadata:
  synthos:
    priority: P1
    atom_type: cognitive_atom
    description: "Proactive discovery - automatically discovers new research opportunities, tracks trends, monitors competitors, and identifies gaps"
    signature: "domains: list[str] -> discoveries: list[dict], opportunities: list[dict]"
    related_skills:
      - knowledge-acquisition
      - association-discovery
      - hypothesis-generation
      - evolution
---

# Proactive Discovery (主动发现)

## Core Positioning

> **知己知彼，百战不殆。** A super individual does not wait for queries - they discover opportunities. This atom transforms Synthos from a research tool to a research scout.

Goal: Automatically track:
1. New papers in key research domains
2. GitHub trending projects
3. Academic social networks (Twitter/X research threads)
4. Conference deadlines and calls for papers
5. Competitor research output

## IO_CONTRACT

- **input**: domains: list[str] - Research domains to monitor
- **input**: frequency: str = "daily" - Scan frequency
- **output**: discoveries: list[dict] - New relevant papers/projects
- **output**: opportunities: list[dict] - Research opportunities (gaps, trends)
- **output**: report: str - Human-readable discovery report

## Discovery Dimensions

### 1. Paper Discovery

Scan these sources daily:
- Semantic Scholar API: new papers in VOR, eye movement, biomechanics
- arXiv: cs.AI, cs.LG, physics.med-ph
- PubMed: new vestibular/neurology papers
- Google Scholar alerts (manual setup)

Each new paper:
- Get abstract and metadata
- Compare with existing knowledge base
- Flag if: novel method, novel domain, novel finding
- Queue for ACQ if quality >= threshold

### 2. Project Discovery

Scan GitHub for:
- Trending repos in AI research agents
- New releases of tools we use (LangGraph, DSPy, PaperQA2)
- Related projects in vestibular/eye tracking
- Open challenges/competitions

Each new project:
- Score quality (1-5)
- If quality >= 4.0, queue for absorption (EVA atom)
- If quality < 3.0, archive as reference only

### 3. Trend Discovery

Track:
- Citation trends for key papers
- Emerging methods (new ML architectures, new ODE solvers)
- Funding opportunities (NSF, NIH calls)
- Conference deadlines (NeurIPS, ICML, ICLR, IEEE conferences)

### 4. Gap Discovery

Cross-reference:
- What methods have we used? What methods are emerging?
- What domains have we covered? What domains are adjacent?
- What questions remain unanswered?

## Discovery Pipeline

```
Scan Sources -> Extract -> Score -> Flag -> Queue
     |             |         |       |        |
  API/crawling   metadata  quality  relevant  ACQ/EVA
                & abstract  1-5 score  items   absorption
```

## Output Files

- outputs/discovery/{date}.md - Discovery report
- outputs/discovery/{date}.json - Structured discovery data
- outputs/papers/new-queue/ - Papers queued for processing

## Quality Control

- P0 Evidence traceability: Every discovery has source URL/API
- P1 Atomic reproducibility: Each scan independently executable
- P2 Stability sinking: Validated discovery patterns become standard
- P3 Human-machine layering: Human approves which discoveries to pursue


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


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

---

*善战者，求之于势，不责于人。发现趋势，创造机会。*



# Proactive Discovery

