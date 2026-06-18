# SKILL-spec-profile Authoring Guide

When creating a Synthos cognitive atom SKILL.md, follow SKILL-spec-profile.md v1.0:

## Mandatory metadata fields (16 for cognitive atoms)

synthos_atom_type, synthos_version, synthos_skill_md_hash, synthos_model_version_pin,
synthos_model_tested_on, synthos_io_contract_ref, synthos_evidence_schema_ref,
synthos_golden_set_ref, synthos_golden_set_origin, synthos_pass_threshold,
synthos_boundary_proof_ref, synthos_change_log_ref, synthos_asserted_compliance,
synthos_mechanical_atoms

## SHA-256 hash algorithm

1. Write SKILL.md with synthos_skill_md_hash: "<PENDING>"
2. Read file, replace the hash value with "<PENDING>", compute SHA-256
3. Write back the computed hash

## File structure per atom (spec §8)

```
atom-name/
├── SKILL.md                    # ≤500 lines, ≤5000 tokens
├── references/
│   ├── IO_CONTRACT.md          # P2: input/output schema
│   ├── EVIDENCE_SCHEMA.md      # P0: evidence chain rules
│   ├── BOUNDARY.md             # P2: non-overlap proof vs other atoms
│   └── CHANGE_LOG.md           # P3: version history
└── golden/
    ├── GOLDEN_SET.md           # P1: gold standard spec
    ├── cases/                  # Test inputs
    └── expected/               # Expected outputs
```

## Body skeleton (§7.3)

```markdown
## 1. 职责（Scope）
## 2. 输入输出（Contract Summary）
## 3. 推理流程（Procedure）
## 4. 边界判断（When NOT to use）
## 5. 证据链输出要求（Evidence Summary）
## 6. 示例（Minimal Example）
## 7. 参考文件索引（References）
```

## Validation

Run: `python3 scripts/validate_skill.py <atom_name>`
Checks: YAML validity, all mandatory fields, hash match, reference files exist, body constraints, golden/ directory.
