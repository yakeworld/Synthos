# AGENTS_CONTRIBUTING.md

> AI agent contribution protocol for Synthos.

## How AI Agents Contribute

Synthos welcomes contributions from both human developers and AI agents. All contributions follow the same process:

1. **Read CONSTITUTION.md** — understand the immutable principles
2. **Familiarize with the skill architecture** — each cognitive atom is a SKILL.md
3. **Submit PRs** — adhere to the format: `type: concise description`
4. **Pass quality gates** — all contributions must pass existing benchmarks

## Skill Modification Rules

- Skills are pure SKILL.md files in `skills/`
- Reference files go in `references/` subdirectory
- Test with `evolution` engine's BENCHMARK step
- Maintain non-overlap principle (no two skills with same scope)

## Key Paths

| Path | Purpose |
|:-----|:--------|
| `CONSTITUTION.md` | Immutable principles |
| `skills/` | Cognitive atoms and extended skills |
| `evolution-state.json` | System state |
| `evolution-log.md` | Evolution history |
