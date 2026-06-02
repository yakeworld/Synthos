# Standard Atom Frontmatter Template

Every Synthos cognitive atom SKILL.md must use this canonical YAML frontmatter format.
Do NOT use bare `version:` or `stability:` fields — they belong inside `metadata:`.

```yaml
---
name: <kebab-case-atom-name>
description: "≥80 characters of clear, concrete description of what this atom does and when to use it."
license: MIT
allowed-tools: terminal Read Write
metadata:
  synthos_atom_type: "cognitive"           # or "router" for task-router
  synthos_version: "0.1.0"                # Semantic version
  synthos_skill_md_hash: "pending"        # Set on first stable version
  synthos_model_tested_on: "2026-05-13T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_evidence_schema_ref: "references/EVIDENCE_SCHEMA.md"
  synthos_golden_set_ref: "golden/GOLDEN_SET.md"
  synthos_golden_set_origin: "self_defined"
  synthos_pass_threshold: "0.80"
  synthos_boundary_proof_ref: "references/BOUNDARY.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P1,P2"  # Comma-separated: P0/P1/P2/P3/P4/P5
  synthos_depends_on: "<upstream-atom-name>"
  synthos_author: "Synthos Agent"
---
```

## Field Requirements

| Field | Required | Notes |
|-------|:--------:|-------|
| `name` | ✅ | Must match directory name (kebab-case) |
| `description` | ✅ | ≥80 characters; describe both function and trigger |
| `license` | ✅ | `MIT` for all Synthos atoms |
| `allowed-tools` | ✅ | At minimum `terminal Read Write` |
| `metadata:` block | ✅ | All sub-fields below unless noted |
| `synthos_atom_type` | ✅ | `cognitive` or `router` |
| `synthos_version` | ✅ | Use semver, not bare `version:` |
| `synthos_io_contract_ref` | ✅ | Path relative to atom directory |
| `synthos_change_log_ref` | ✅ | Path relative to atom directory |
| `synthos_depends_on` | ✅ | Comma-separated upstream atom names |
| `synthos_asserted_compliance` | ✅ | At minimum the P-levels this atom must satisfy |
| `synthos_skill_md_hash` | 🟡 | Set to `"pending"` initially; compute on first stable version |
| `synthos_model_tested_on` | 🟡 | Date of last model test |
| `synthos_evidence_schema_ref` | 🟡 | Required if atom produces evidence records |
| `synthos_golden_set_ref` | 🟡 | Required if atom has golden tests |
| `synthos_golden_set_origin` | 🟡 | Required if golden_set_ref present |
| `synthos_pass_threshold` | 🟡 | Required if golden_set_ref present |

## Common Drift Patterns (to avoid)

1. **Bare `version:` instead of `metadata: synthos_version:`** — The evolution engine's PROBE step checks desc length + allowed-tools + ref files, but does NOT validate metadata section structure. A bare `version:` field will pass structural probe but marks the atom as non-standard.
2. **Missing `allowed-tools:`** — Causes structural score deduction (−0.10 per atom). All cognitive atoms must declare `terminal Read Write` minimum.
3. **Short description (< 80 chars)** — The most common issue. Chinese descriptions often come in at 30-50 characters. Expand to include what the atom does, when to use it, and what it depends on.
4. **Inconsistent `synthos_asserted_compliance`** — Each atom must declare which constitution principles (P0-P5) it satisfies. Newer atoms (HYP, GAP) may have P4/P5 that older atoms lack — this is correct as long as it's explicitly stated.
5. **Missing `synthos_depends_on`** — Every atom except task-router must declare its upstream dependency. This is critical for the task-router to build correct atom chains.
