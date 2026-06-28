# Evolution Engine — Boundary Definition

## What Evolution Covers
- Structural health of all 7 atom SKILL.md files
- API endpoint availability (Semantic Scholar, PubMed, OpenAlex)
- Reference file completeness
- Golden test suite existence
- evolution-state.json and evolution-log.md maintenance
- Minor documentation fixes (version numbers, changelogs)

## What Evolution Does NOT Cover

| Area | Reason | Owner |
|------|--------|-------|
| Atom core logic | User-designed cognitive workflows | Human |
| I/O contract changes | Cross-atom compatibility constraint | Human |
| New atom creation | Architecture decision (P2.3 stable set) | Human |
| File deletion | Irreversible operation | Human |
| External API integration | Depends on credentials/permissions | Human |
| Performance optimization | Requires benchmark infrastructure | Human |
| Security patches | Requires security expertise | Human |

## Overlap with Other Atoms

| Atom | Boundary |
|------|----------|
| task-router | Evolution does NOT modify routing logic; only structural checks |
| knowledge-acquisition | Evolution checks API health but does NOT add/remove search sources |
| All cognitive atoms | Evolution patches structure only; reasoning logic is human-domain |
