# PPTX Script Storage Convention

**Date discovered:** 2026-06-11
**Source:** 瓯越英才PPT generation — script was first written to /tmp then needed to be preserved

## Convention

All PPTX generation scripts must be stored in the project directory's `code/` subdirectory, **never in `/tmp`**.

| Location | Lifespan | Reusable? | Auditable? |
|----------|----------|-----------|------------|
| `/tmp/gen_*.py` | Session only | No | No |
| `~/project/code/` | Persistent | Yes | Yes |

## Rationale

1. `/tmp` is ephemeral — scripts disappear at session end
2. Project `code/` directory: survives across sessions, reviewable, traceable
3. Enables reuse: next session can `skill_manage(action='patch')` the script directly
4. Aligns with Synthos codebase convention: code lives in project `code/` not temp dirs

## Examples

- `~/瓯越英才申报材料/code/医工极光智能前庭诊疗_pptx_gen.py`
- `~/Synthos/code/gen_cover.py`
- `~/projects/bci-demo/code/gen_chart.py`

## Related

See references/pptx-generation-template.md for the generation pattern itself.
See references/pptx-nested-tuple-unpacking.md for a common unpacking pitfall in these scripts.
