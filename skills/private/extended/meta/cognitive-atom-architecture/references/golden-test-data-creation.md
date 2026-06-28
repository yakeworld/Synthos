# Golden Test Data Creation Pattern

> Creating `cases/case_NNN.json` and `expected/case_NNN.json` for atomic-level golden tests.
> Pattern discovered during Synthos Cycle 4 prep (2026-05-11).

## When to Use

When atoms have GOLDEN_SET.md specs but empty `cases/` and `expected/` directories. The GOLDEN_SET.md defines test cases (4-5 per atom); the JSON files make them executable by the evolution engine's BENCHMARK step.

## Parallel Creation Strategy

Do not create 62 files serially. Use `delegate_task` with 3 parallel workers:

### Worker Assignment

| Worker | Atoms | Case Count | Est. Time |
|--------|-------|-----------|-----------|
| 1 | knowledge-acquisition | 5 cases | ~3 min |
| 2 | association-discovery + hypothesis-generation | 4+5=9 cases | ~5 min |
| 3 | argument-expression + viewpoint-verification + task-router | 5+4+5=14 cases | ~5 min |

### Inputs to Each Worker

Each worker receives:
1. The atom's `GOLDEN_SET.md` content (defines test case specs)
2. `knowledge-extraction`'s real case JSON as format reference (the only atom with pre-existing cases)
3. Exact file paths: `skills/<atom>/golden/cases/case_NNN.json` and `skills/<atom>/golden/expected/case_NNN.json`
4. The JSON schema for both input and expected output (from the atom's IO_CONTRACT.md)

### JSON Format Rules

- **cases/case_NNN.json**: The input that would be given to the atom. Must match all required fields from GOLDEN_SET.md.
- **expected/case_NNN.json**: The semantically correct output. Must match all output fields from GOLDEN_SET.md.
- All files: valid UTF-8 JSON, no trailing commas, standardized indent.
- Use real paper titles, DOIs, and findings from the project's domain (e.g., ADHD eye-tracking research) for consistency.

### Verification

After creation, run: `ls skills/*/golden/cases/ skills/*/golden/expected/` and `python3 -c "import json; json.load(open('path'))"` on each file.

## Single-Atom (knowledge-acquisition) Special Case

knowledge-acquisition lacked even a `GOLDEN_SET.md` — needed to create it first. Its test format differs: input = `{topic, keywords, sources}`, expected = `{papers[], total_found}`. Handle as a standalone worker with its own GOLDEN_SET.md creation.

## Edge Cases to Cover

Each atom's GOLDEN_SET.md defines edge cases (empty input, single-item, error conditions). These are the most important tests — they catch real bugs.

## Pitfalls

- **Consistency across atoms**: Different workers may generate incompatible DOIs or paper titles. Pre-define a common pool of 4-5 real papers for all workers to reference.
- **knowledge-extraction is the only atom with real JSON**: Use its format as the anchor; all other atoms must output formats compatible with its output (since they consume each other's outputs).
- **Expected outputs should be plausible, not aspirational**: Don't write expected outputs the atom couldn't reasonably produce. If the atom's max confidence is 0.9, don't set expected to 1.0.
