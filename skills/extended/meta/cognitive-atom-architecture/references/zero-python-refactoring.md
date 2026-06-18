# Zero-Python Refactoring: Synthos v4.0 → v4.2

> How a design contradiction ("技能驱动" vs "Python代码") led to deleting ~4,100 lines of code and making the Agent the sole runtime.

## Timeline

### v4.0 — "Agent IS the cognitive engine" (but atom1 was still Python)

- Architecture claimed: "Python = mechanical I/O only. Agent does the thinking."
- Atom1 (knowledge-acquisition) was 939 lines of Python: S2/PubMed/arXiv search, PDF download, caching, dedup — all in `atom1_knowledge_acquisition.py`
- Atoms 2-6 were marked "cognitive" but had Python skeleton files (3,027 lines total) that were never called
- Pipeline (atom_pipeline.py) had an `if MECHANICAL: run Python else: generate prompt` branch

### v4.1 — Atom1 made Agent-native

- User asked: "Synthos 应该是技能驱动的，为什么会变成python代码？"
- Patched _S2_DISABLED flag (was hardcoded True)
- Rewrote atom1 SKILL.md as Agent-executable: load Hermes skills + terminal/curl → search → dedupe → save JSON
- Changed ATOM_REGISTRY type from MECHANICAL to COGNITIVE
- Removed short-circuit logic (tied to mechanical-only execution)
- Violation: atom2-6 Python files remained as dead code

### v4.2 — Pure skill-driven, zero Python

- User asked: "如果Synthos 是skills驱动的，为什么需要python代码执行？"
- Realization: ALL Python code (including pipeline + context + trust) violates skill-driven principle
- Deleted: `core/` (entire directory, 16 files) and `run_pipeline.py`
- Rewritten: task-router SKILL.md as the single Agent entry point
- Architecture: Agent loads task-router → determines chain → loads each atom's SKILL.md → executes → saves JSON
- Stats: 4,099 lines Python removed, 7 SKILL.md + references remain

## Design Constraint Cascade

```
发现: atom1 是 Python (939行)
  → 修复: SKILL.md 覆盖
    → 发现: atom2-6 也有 Python (3,027行死代码)
      → 修复: 全部删除
        → 发现: pipeline 也是 Python (编排 = Python 在控制)
          → 修复: 全部删除, Agent 是运行时
            → 结果: 纯技能驱动
```

## What NOT to do (learned the hard way)

1. **Don't keep dead Python files**. If a SKILL.md replaces Python, DELETE the .py file. Dead files confuse future readers and the Agent may accidentally re-import them.

2. **Don't have a Python pipeline that "generates prompts for the Agent."** This means Python controls execution flow — the Agent is just a prompt-execution engine. Flip it: the Agent reads a SKILL.md that says "execute these steps" and does them.

3. **Don't think "this Python is just infrastructure."** Everything the Agent can do with its tools (read/write files, curl APIs, make decisions) should be in a SKILL.md, not Python. Infrastructure Python is still Python — it still makes implicit design decisions that the skils don't document.

4. **Don't distinguish mechanical vs cognitive atom execution**. All atoms execute the same way: Agent loads SKILL.md → does the work → saves JSON. A `if type == MECHANICAL` branch means two systems.

## Key Figures

| Version | Python lines | SKILL.md files | Execution model |
|---------|-------------|----------------|-----------------|
| v3.2 (rule-based) | 4,500+ | 7 (documentation only) | Python calls all atoms |
| v4.0 (hybrid) | 4,099 | 7 (atom1 docs, at2-6 agent) | Python runs atom1, Agent runs atoms 2-6 |
| v4.1 (agent-native) | 3,160 | 7 (atom1 rewritten) | Agent runs all atoms, Python orchestrates |
| v4.2 (pure skill) | 0 | 7 (all agent-executable) | Agent IS the runtime |

## References

- `/media/yakeworld/sda2/Synthos/skills/task-router/SKILL.md` — Agent entry point
- `/media/yakeworld/sda2/Synthos/skills/knowledge-acquisition/SKILL.md` — Agent-native search
- `/media/yakeworld/sda2/Synthos/evolution-state.json` — v4.0→4.1→4.2 change log
