---
name: research-thinking-framework
description: >-
  Research methodology knowledge base derived from AKNE's five philosophical
  principles: First Principles (第一性原理), Systems Thinking (系统思维),
  Bayesian Thinking (贝叶斯思维), Falsificationism (证伪主义), and
  Model-Dependent Realism (模型依赖实在论). Provides structured reasoning
  patterns for hypothesis generation, experimental design, and paper critique.
tags: [research-methodology, epistemology, reasoning, critical-thinking, science-philosophy]
---
# Research Thinking Framework — Extended Skill for Synthos

## Trigger
- User needs to evaluate a research methodology
- User asks about hypothesis generation, experiment design, or argument structure
- User wants to critique a paper's reasoning from first principles
- User asks about FEP (Free Energy Principle) as research guidance
- User needs to distinguish facts vs interpretations in their research

## Knowledge Sources
Absorbed from AKNE knowledge graph → concepts/:
- `第一性原理.md` — First Principles: reasoning from physical fundamentals
- `模型依赖实在论.md` — Model-Dependent Realism: "best model" epistemology
- `自由能原理.md` — Free Energy Principle: entropy minimization as research drive
- `科研思维层级.md` — Research Thinking Layers (tactical → strategic → iron law)
- `MOC.md` — Map of Content: high-level knowledge navigation

## Core Reasoning Patterns

### Pattern 1: First Principles Decomposition
When faced with a complex problem:
1. Identify the fundamental physical/biological constraints (cannot be broken)
2. Strip away all assumptions inherited from existing literature
3. Rebuild the solution from constraints upward
4. Compare against literature — differences reveal innovation opportunity

### Pattern 2: Bayesian Hypothesis Updating
For incremental research:
1. State current belief + confidence (prior)
2. New evidence (data/paper) → likelihood function
3. Update: posterior = prior × likelihood / evidence
4. Report: how much did confidence change? What would falsify the new belief?

### Pattern 3: Model-Dependent Reality
For choosing between competing models:
1. Each model is a lens, not "truth"
2. Evaluate: predictive power > correspondence to intuition
3. Select the simplest model that fits the data (Occam's Razor)
4. Document: what the chosen model cannot explain (known limitations)

### Pattern 4: Free Energy Research Guidance
For setting research direction:
1. Minimize free energy = reduce surprise between model predictions and observations
2. Two strategies: (a) update model to fit data (learning), (b) act on environment to fit model (intervention)
3. Research projects should reduce uncertainty about a well-defined question
4. Kill projects where the free energy gradient is flat (no more uncertainty to reduce)

## Input/Output Contract
```yaml
input_contract:
  inputs:
    - problem: str  # Research problem statement
    - context: str  # Known facts, constraints, literature summary
    - pattern: str  # Which reasoning pattern to apply (1-4)
  outputs:
    - analysis: str  # Structured reasoning output
    - next_steps: list[str]  # Actionable research directions
    - pitfalls: list[str]  # Common mistakes to avoid
```

## Usage Examples

### First Principles Applied to Clinical AI
Problem: "Why do PIDD papers report 95-100% accuracy?"
1. Physical constraint: 768 samples, 500:268 imbalance → maximum reliable F1 ~0.75
2. Strip assumptions: "high accuracy means good model" is not fundamental
3. Rebuild: accuracy ceiling = information content of 8 features × 768 samples
4. Insight: claims exceeding this bound must involve data leakage

### FEP Applied to Research Strategy
Problem: "Should I invest in PIDD methodology or BPPV simulation?"
Compare uncertainty reduction per unit effort:
- PIDD methodology: uncertainty about reproducibility is high, but corpus is small
- BPPV simulation: uncertainty about canalith dynamics is high, large space to explore
- Decision: BPPV has higher free energy gradient → more discovery potential

## Origin
Absorbed from AKNE knowledge graph (yakeworld/.knowledge/) — 2026-05-12
