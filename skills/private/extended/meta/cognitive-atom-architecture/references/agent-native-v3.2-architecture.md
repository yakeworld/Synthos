# Agent-Native Architecture (Synthos v3.2+)

## Core Insight

**The Agent IS the cognitive engine.** Cognitive atoms 2-6 should NOT be implemented as Python rule-based templates. They should be executed by the Agent's own reasoning capabilities, guided by SKILL.md instructions.

## Two Execution Modes

| Mode | Atoms | Implementation |
|------|-------|---------------|
| Mechanical | Atom 1 | Python script (API calls, file I/O) |
| Agent-Native | Atoms 2-6 | SKILL.md instructions + Agent reasoning |

## Quality Comparison (5-paper ADHD corpus)

| Dimension | Rule-based Python | Agent-Native |
|-----------|------------------|--------------|
| atom2 findings | "No extractable findings" | 5 papers × 5 fields detailed |
| atom3 associations | 0 (keyword overlap < threshold) | 5 nuanced associations |
| atom4 hypotheses | "Investigating [keyword] will uncover..." | Specific, cited, falsifiable |
| atom6 counterarguments | Generic templates | Domain-specific scholarly rebuttals |

## Pipeline Architecture

```
run_pipeline.py run '<query>'
  ├── Phase 1 (Python): atom1 search → papers saved
  └── Phase 2 (Agent): For each cognitive atom:
        ├── Load SKILL.md
        ├── Load upstream context
        ├── Agent reasons → structured JSON output
        └── Save to context/<run_id>/<atom>_agent_output.json
```

## Rule-to-Agent Migration Steps

1. Delete NLP/reasoning logic from Python file
2. Keep only input validation, context loading, output saving
3. Ensure SKILL.md has detailed execution steps
4. Agent executes by reading SKILL.md + context

## DO NOT

- Write Python regex/keyword extraction for cognitive tasks
- Write template-based hypothesis generators
- Write pattern-matched counterargument finders
- Pretend Python can do what the Agent (LLM) does

Python = mechanical I/O. Agent = cognition.
