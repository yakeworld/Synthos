---
name: research-platform-philosophy
description: "Philosophical and architectural frameworks for self-evolving research platforms. Covers the Synthos Eight-Dimensional Cognitive Framework (八维认知框架) as a meta-principles layer, mapping existing project capabilities to first principles, and guidelines for philosophical alignment during system evolution. Includes falsification methodology for practical skill validation."
category: research
version: 4.4.0
author: Nous Research
license: MIT
---

# Research Platform Philosophy

## Overview

This skill captures the philosophical foundations of self-evolving scientific operating systems, centered on the **Synthos Eight-Dimensional Cognitive Framework (八维认知框架)**. It provides a meta-level lens for evaluating, guiding, and aligning research platform evolution.

## The Synthos Eight-Dimensional Cognitive Framework

Synthos defines eight scientific philosophy principles that form the inner logic of the system. These are governed by a 4-article constitution (P0-P3) and implemented through 7 cognitive atoms plus an evolution engine, **now extended with a meta-reflection layer for self-evolution from project experience**.

### Four-Layer Architecture (v4.4)

```
Meta-Reflection Layer (P0)     → project-experience-distillation + quality-gate + conversation-to-memory
       ↑ 每次 quality-gate PASS 或 evolution DIAGNOSE 后自动触发
       │
Constitution (P0-P6)           → 不可违反的底线（自 P0 证据可溯性至 P6 数据分级）
       ↓ 驱动
Eight-Dimension Framework       → 哲学方向，指引每个原子"为什么存在"
       ↓ 实现
8 Cognitive Atoms + Evolution   → 具体执行的认知单元 + 自进化引擎（v2.4）
       ↓ 扩展
Extended Skills (dynamic)      → 可动态增长（bppv-expert, figure-generation 等）
```

### Self-Evident Testimony (自指证言)

A philosophical insight from project practice: **the system's operation is its own testimony.** Rather than collecting external user testimonials, the strongest evidence of Synthos's capability is watching it work — extracting patterns from its own project experience, creating new skills, imposing quality gates, and recording the process. This is self-referential evidence: the proof is the process.

**Implication**: When evaluating Synthos's capabilities, the primary evidence is not what it claims to do, but what it demonstrably does in the course of operation. Each session's CHANGELOG and skill updates are testimonial records.

### Four-Layer Architecture (v4.4, 2026-05-16)

```
Meta-Reflection Layer (P0)     → 从项目经验中提取规律、质量闸门、记忆管理
       ↑ 每次 quality-gate PASS 或 evolution DIAGNOSE 后自动触发
       │
Constitution (P0-P6)           → 不可违反的底线
       ↓ 驱动
Eight-Dimension Framework       → 哲学方向，指引每个原子"为什么存在"
       ↓ 实现
8 Core Atoms + Evolution        → 具体执行的认知单元 + 自进化引擎
       ↓ 扩展
Extended Skills (dynamic)      → 可动态增长（如 latex-output, figure-generation）
```

**New P0 Layer**: Three meta-skills form the self-reflection layer, running at the highest priority:

| Skill | Function | Priority |
|:------|:---------|:---------|
| `project-experience-distillation` | 从项目经验提取规律 → 建/更新 skill | P0 (auto after complex tasks) |
| `quality-gate` | 交付物质量闸门，不通过不停止 | P0 (before task completion) |
| `conversation-to-memory` | 会话价值提取 → 持久记忆 | P0 (after complex tasks) |

### Self-Evident Testimony (自指证言)

A philosophical insight from project practice: **the system's operation is its own testimony.** Rather than collecting external user testimonials, the strongest evidence of Synthos's capability is watching it work — extracting patterns from its own project experience, creating new skills, imposing quality gates, and recording the process. This is self-referential evidence: the proof is the process.

**Implication**: When evaluating Synthos's capabilities, the primary evidence is not what it claims to do, but what it demonstrably does in the course of operation. Each session's CHANGELOG and skill updates are testimonial records.

### Constitution (P0-P3)

| Article | Principle | Meaning |
|---------|-----------|---------|
| P0 | 证据可溯性 | Every output traces to a data source. No ungrounded claims. |
| P1 | 原子可复现性 | Every atom has golden tests + SKILL.md hash + version lock. |
| P2 | 稳定下沉 / 演化上浮 | Core atoms stable. New capabilities via extended skills. |
| P3 | 人机分层 | Critical decisions made by human. Machine does not cross its boundary. |

### Current Implementation Status (2026-05-11)

| Principle | Score | Status |
|-----------|-------|--------|
| 第一性原理 (First Principles) | 95% | ✅ Mature |
| 系统思维 (Systems Thinking) | 95% | ✅ Mature |
| 贝叶斯思维 (Bayesian Thinking) | 90% | ✅ Mature |
| 类比思维 (Analogical Thinking) | 80% | ✅ Mature |
| 奥卡姆剃刀 (Occam's Razor) | 80% | ✅ Mature |
| 证伪主义 (Falsificationism) | 80% | ✅ Mature |
| 模型依赖实在论 (Model-Dependent Realism) | 60% | ⚠️ Developing |
| 自由能原理 (Free Energy Principle) | 55% | 🔄 Improving |
| **Overall** | **85%** | Improved from 68% in v3.x |

### Evolution Engine v2.1

9-step autonomous cycle running daily via cron:
LOAD_STATE → LESSONS (learns from history) → PROBE → BENCHMARK → EXTERNAL (every 7 cycles) → DIAGNOSE → IMPROVE → VERIFY → RECORD

External absorption from GitHub/Hermes projects (e.g., AutoResearchClaw: citation verification + LaTeX output). All absorptions require user approval.

## Platform Definition

> Synthos is a self-evolving scientific operating system built on skills, governed by first principles.
> 
> Knowledge is not read — it is called. Not cited — it is executed.

## Three Pillars

1. **Skills as First Principles** — Every research operation encapsulated as a standardized, verifiable, testable, auditable skill unit (skill.yaml: name, input, output, dependencies, tests, trust). No black boxes, no untested skills, no versionless skills.

2. **Agent as Contract Enforcer** — The agent does not "generate" answers; it matches, composes, and calls skills to complete research tasks. Execution in isolated environments with complete logging. Trustworthy execution over common-sense guessing.

3. **Self-Purification via Free Energy** — Each skill call computes prediction error. Failure → lower trust, mark "needs fix". Success → increase weight, recommend more. Weekly adversarial testing. 3 consecutive failures → archive, never recommend again.

> Science is not preserved by authority, it is evolved by error elimination.

## Usage

Load this skill when:
- Defining or revising the philosophical foundation of a research platform
- Evaluating whether a new feature/skill aligns with first-principles thinking
- Conducting a philosophy-to-implementation gap analysis
- Writing project documentation that needs a clear philosophical stance

### Quick Reference

The framework maps to common system qualities:
- First Principles → skill contracts (input/output/dependencies/tests/trust)
- Bayesian Thinking → trust score system with Bayesian updates
- Falsificationism → falsification testing workflow (see 证伪主义实践方法论 section below)
- Systems Thinking → skill network analysis (nodes/edges/betweenness/clustering)
- Free Energy Principle → evolution value (EV) engine driving system evolution direction

## 证伪主义实践方法论 (Falsification Methodology)

证伪主义 (Falsificationism) 是八维认知框架的核心维度之一。以下实践方法来自被吸收的 `falsification-validation` 技能，提供了从哲学原则到可执行测试的具体转化路径。

### 核心原则

1. **Falsificationism (Popper)**: Don't seek to confirm skills work — actively seek disproof through rigorous testing. A skill that survives falsification attempts gains credibility.
2. **Bayesian Thinking**: Trust is a probability that updates with evidence. Start with prior trust, collect evidence, compute posterior trust.
3. **Quantification**: Every skill must have measurable quality metrics, not subjective "looks good" assessments.

### 测试工作流

1. **Design Falsification Test** — realistic input, explicit pass/fail criteria, measurable metrics
2. **Execute Test** — real data, full workflow, collect all outputs
3. **Collect Evidence** — input data, processing results, final output, comparison with ground truth
4. **Bayesian Update** — P(skill correct | evidence) = P(evidence|correct) × P(correct) / P(evidence)
5. **Decision** — High trust (0.9-1.0): continue; Medium (0.7-0.9): increase monitoring; Low (0.5-0.7): redesign; Very low (<0.5): replace

### 测试类型

| Skill 类型 | 典型 falsification 测试 |
|-----------|----------------------|
| 检索/搜索 | Zero results when results exist, results irrelevant, stale info |
| 提取/分析 | Content conflicts with source, misses critical info, poor structured output |
| 推理/生成 | Non-testable hypotheses, contradicts existing knowledge, lacks novelty |
| 验证/审查 | Fails to find counterarguments, ignores negative results, overstates confidence |

### 信任管理

| 事件 | 信任变化 |
|------|---------|
| Successful test | +0.05 to +0.1 |
| Failed test | -0.1 to -0.2 |
| 3+ consecutive successes | Additional +0.02 |
| 3+ consecutive failures | Additional -0.05 |

### 反模式

- Testing with mock data instead of real data
- Subjective "looks good" assessments without metrics
- Only running tests expected to pass
- Ignoring failure evidence
- Not collecting evidence for tests that pass

### 参考文件

- `references/falsification/test-design-reference.md` — test design methodology
- `references/falsification/test-case-knowledge-acquisition.md` — concrete test case for knowledge acquisition
- `scripts/falsification/update_trust.py` — Bayesian trust update script

> **吸收记录**: `falsification-validation` 技能已归档到此方法论中。原技能为独立 skill，但实际上它是 八维认知框架中"证伪主义"维度的实践实现，作为整个哲学框架的一部分比独立 skill 更易发现和维护。

## Usage

### Critical: Do Not Confuse Feature Additions with Architectural Alignment

When the goal is architectural alignment with a philosophical framework (like the Eight-Dimension framework), the agent must NOT respond with "add more tools/features." This is the most common mistake.

**WRONG approach**: "I'll add feature X, I'll add script Y, I'll add endpoint Z" — this treats the framework as a checklist of features to implement, producing incremental tool upgrades that don't change the system's cognitive architecture.

**RIGHT approach**: First reframe the problem in terms of the framework's actual meaning:
- **可计算 (Calculable)**: Not "every script outputs JSON" — it means each step's *cognitive contribution* is quantifiable. Knowledge coverage, uncertainty reduction, epistemic state tracking.
- **可协作 (Collaborative)**: Not "multi-model review" — it means explicit *cognitive interfaces* between agents/subjects. Different actors (human, agent, external system) have well-defined cognitive handoff points.
- **可进化 (Evolvable)**: Not "auto-tool exists" — it means the system has clear criteria for *what counts as progress* and can continuously optimize its realization path, not just fix TODO items.

**When the user says the goal is architectural/philosophical alignment (not feature additions):**
1. Stop listing features to add
2. Re-evaluate: is the improvement "more tools" or "deeper cognitive architecture"?
3. If it's the former, the agent is misunderstanding the task
4. Prioritize: cognitive interface definition > new features; metric redesign (engineering → epistemic) > code additions

This pitfall applies whenever the user invokes a philosophical framework (Synthos, research methodology, etc.) as the guiding principle for system evolution.

## 已知陷阱

与哲学框架（如八维认知框架）对齐时，以下陷阱已被反复观察到：

### 陷阱一：将功能堆叠误认为架构对齐

最常见的错误。当目标是哲学框架对齐时，代理（agent）容易回退到安全的默认行为：列出更多功能、添加更多工具/脚本/端点。但这只是增量式工具升级，没有改变系统的认知架构。

- **表象**：添加了新工具 → 系统 "看起来" 更完善了
- **本质**：工具的堆叠不解决"认知接口是否被定义"、"演进方向是否明确"等架构问题
- **对策**：停止列出待加功能。先问：这个改进是"更多工具"还是"更深层的认知架构"？

### 陷阱二：将哲学框架视为清单（Checklist）

八维框架不是"每个维度都要有一个独立工具"的清单。将哲学维度直接映射为代码模块，会导致系统变得臃肿且失去哲学统一性。

- **表象**：为每个维度创建一个独立模块/技能 → 系统有 8 个模块
- **本质**：哲学维度应作为*约束条件*贯穿所有模块，而非模块本身
- **对策**：评估时问"这个模块是否受八维框架约束"，而非"这个模块对应哪个维度"

### 陷阱三：跳过哲学主张的验证

哲学主张（如"本系统具备可计算性"）如果不经过验证就写进文档，等于在构建不可证伪的信仰体系。

- **表象**：文档声称"系统符合贝叶斯思维"，但没有具体的测试或度量标准证明
- **本质**：哲学框架沦为修辞装饰，而不是可执行的约束
- **对策**：每个哲学主张必须伴随一条可执行的可证伪测试。例如"贝叶斯思维"需要证明 trust 系统确实在执行贝叶斯更新并影响行为

### 陷阱四：混淆"实现维度"与"完成维度"

哲学框架中的每个维度不是"做完一次就永远完成"的状态，而是需要持续维护的进化方向。

- **表象**：某维度标记为"已完成 95%"，之后不再关注
- **本质**：系统进化时可能破坏之前的对齐状态；旧的对齐可能在新的上下文中失效
- **对策**：每次架构变更后重新评估各维度的对齐状态，而非仅在新系统中做一次评估就结束

---

## 触发条件

在以下情况加载本技能：

- 需要评估或对齐项目的哲学基础时
- 将新功能/技能映射到八维认知框架时
- 进行哲学→实现的差距分析时
- 撰写需要明确哲学立场的项目文档时
- evolution 引擎的 DIAGNOSE 检测到架构对齐问题时

## 验证清单

- [ ] 八维框架的每个维度都有对应的实现证据
- [ ] 实现层之间的映射清晰（Constitution→Framework→Atoms→Extended）
- [ ] 没有将"功能堆叠"误认为"架构对齐"
- [ ] 哲学主张有可验证的实现证明
- [ ] 已对照 L1-L4 标准检查本技能等级

---

## Related

- `research-platform-philosophy` — The philosophical framework and methodology
- `synthos-skill-evolution` — The practical skill evolution workflow (skill.yaml spec, trust system, adversarial testing, autonomous execution)
- `research-skill-audit` — General audit process, including philosophy alignment audit methodology
