# branches/ — Experimental Evolution Branches

Contains divergent evolution state branches for experimentation without affecting the
main evolution track. Inspired by git branches — each branch is a subdirectory with
its own `state.json`.

## Purpose

- Test aggressive evolution strategies (e.g., high absorption rate)
- Explore different skill tree topologies
- Experiment with new evolution engine parameters
- Compare outcomes before merging back to the main track

## Structure

```
branches/
├── _index.md
├── branch-name-1/
│   ├── state.json
│   └── notes.md
└── branch-name-2/
    ├── state.json
    └── notes.md
```
