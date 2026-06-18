# Synthos Constitution Compliance (P0-P3)

> Authoritative source: `docs/SKILL-principles.md` v1.0-final (in Synthos project)

## Principle Summary

| Principle | Core Rule | Constrains |
|-----------|-----------|------------|
| **P0** Evidence Traceability | Every output is an evidence chain, not a conclusion. All must trace to external sources. | All layers |
| **P1** Atomic Reproducibility | Atoms are stable. Mechanical=query reproducible. Cognitive=semantic reproducible via golden sets. | Atom layer |
| **P2** Stability Descends / Evolution Ascends | Stable sinks to atoms. Evolution floats to composition. Two-layer contract. | Architecture |
| **P3** Human-Machine Layering | Default: audit (record, don't wait). Exception: approval required for irreversible actions. | Composition delivery boundary |

## Atom Classification

| Type | Stability | ReproContract |
|------|-----------|---------------|
| **MECHANICAL** | Code hash + param lock | `ReproContractMechanical(code_hash, param_lock, external_deps)` |
| **COGNITIVE** | SKILL.md hash + model version + golden set pass | `ReproContractCognitive(skill_md_hash, model_id, model_version, golden_set_ref, pass_threshold)` |

## What Each Atom Must Implement

### P0 Requirements
- `_ok()` envelope includes `evidence_chain` field
- Each output item traces to source DOI/URL/atom_output
- Empty results are structured evidence (not "no data")
- Routing decisions recorded in CallGraph

### P1 Requirements  
- `atom_type` set to MECHANICAL or COGNITIVE
- `version` as SemVer string
- Cognitive atoms: `model_id`, `model_version`, golden set ref
- `non_guarantees` explicitly stated in contract

### P2 Requirements
- Atom exposes `(atom_type, input_schema, output_schema, version, repro_contract)`
- Orchestration logic stays in pipeline, NOT in atoms
- Mechanical atoms: pluggable, no constitution revision needed
- Cognitive atoms: stable set, changes via controlled process

### P3 Requirements
- Atoms NEVER contain P3 logic (no approval dialogs)
- P3 lives at composition layer: `ApprovalGate` for irreversible actions
- `IRREVERSIBLE_ACTIONS` mapping: argument-expression (submission), viewpoint-verification (publishing)

## Key Pitfalls

1. **DO NOT** put short-circuit logic in atoms — it's pipeline's job (P2.2)
2. **DO NOT** use Sci-Hub for PDFs — violates P3 boundary
3. **ALWAYS** include `non_guarantees` in contracts — contract boundaries are themselves evidence (P0 self-reference)
4. **NEVER** add cognitive atoms in a single task — requires cross-task evidence and controlled change process (P2.4)
