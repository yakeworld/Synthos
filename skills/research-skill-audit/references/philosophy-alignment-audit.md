# Philosophy Alignment Audit — Methodology

When auditing a project against a philosophical/architectural framework (e.g., Synthos 八维认知框架), use this repeatable process.

## The 3-Layer Analysis Pattern

The philosophy is NOT a feature checklist. It's a 3-layer system:

| Layer | Question | What to evaluate |
|-------|----------|-----------------|
| **人机关系 (Human-AI Relationship)** | Who makes decisions? | Does the system actually keep humans in the loop, or is it just a UI label? |
| **系统架构 (System Architecture)** | How is it built? | Is it truly modular/composable, or is it a monolith with "modular" labels? |
| **系统行为 (System Behavior)** | What does it do without humans? | Does the system actually self-improve, or does it just have an "auto" button? |

## Audit Method (8 Steps)

1. **Extract the philosophical framework** from project docs (SKILL.md, README, design principles)
2. **Map current capabilities** to each dimension (not as "has it" but "how well does it embody the principle")
3. **Score each dimension 0-100%** using concrete evidence (code files, test results, architecture docs)
4. **Identify the gap**: what's the difference between "tool-level implementation" and "architecture-level embodiment"?
5. **Rank gaps by priority**: 
   - Most important: dimensions where the project's *core identity* depends on it (e.g., human-in-the-loop for a research platform)
   - Second: dimensions that block other improvements
   - Third: nice-to-have dimensions
6. **Propose improvements**: always start with architectural changes (interfaces, metrics, refactoring) before feature additions
7. **Execute improvements**: via parallel delegate_task subagents, one per high-priority gap
8. **Re-scan**: after improvements, re-score dimensions to measure progress

## Critical Pitfall

**NEVER** respond to "improve alignment with philosophy X" with a list of features to add. The most common error is treating a philosophical framework as a feature checklist, producing incremental tool upgrades that don't change the system's cognitive architecture.

The right response: reframe the gap, propose architectural changes, then (if needed) feature additions.

## Example: Synthos 八维 Audit

The 8 dimensions are:
1. 第一性原理 (First Principles)
2. 奥卡姆剃刀 (Occam's Razor)
3. 类比思维 (Analogical Thinking)
4. 系统思维 (Systems Thinking)
5. 贝叶斯思维 (Bayesian Thinking)
6. 证伪主义 (Falsificationism)
7. 模型依赖实在论 (Model-Dependent Realism)
8. 自由能原理 (Free Energy Principle)

For each dimension, evaluate:
- What code/files implement it?
- What metrics measure it?
- What's the current score?
- What's the gap between current state and ideal state?

See `hermes-scientist-mapping-audit.md` for a concrete example.
