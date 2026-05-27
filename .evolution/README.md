# .evolution/ — Synthos State Separation

## Purpose

This directory separates Synthos **evolution state** from code/knowledge. Inspired by
ResearcherSkill's `.lab/` directory concept — binary/state lives here, while the main
project tree (skills/, docs/, etc.) remains clean.

## Structure

```
.evolution/
├── README.md        ← This file
├── state.json       ← Core evolution state (no quality_metrics)
├── history/         ← Snapshot history of past evolution states
│   └── _index.md
├── branches/        ← Experimental evolution branches
│   └── _index.md
└── analysis/        ← Evolution analysis artifacts
    └── _index.md
```

## Phasing Note

The original `evolution-state.json` at the project root remains the active tracking file.
`.evolution/state.json` is a separated copy that will be phased in gradually. Quality
metrics stay in the main `evolution-state.json` — they belong to the runtime, not the
evolution state.

## Key Differences from evolution-state.json

| Field | Main file | .evolution/state.json |
|---|---|---|
| quality_metrics | ✅ Present | ❌ Removed |
| evolution engine state | ✅ Present | ✅ Present |
| trust_db | ✅ Present | ✅ Present |
| skill_tree | ✅ Present | ✅ Present |
| history/ snapshots | ❌ N/A | ✅ Planned |
| branches | ❌ N/A | ✅ Planned |
| analysis artifacts | ❌ N/A | ✅ Planned |
