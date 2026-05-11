# VERIFICATION GATES

> Automated verification pipeline for external agent contributions.
> Every PR from an AI agent passes through these gates before human review.

---

## Overview

```
Gate 1: Identity      → AGENT_MANIFEST.yaml present and valid
Gate 2: Syntax        → YAML, Markdown, Python all parse correctly
Gate 3: Secrets       → No hardcoded API keys, tokens, credentials
Gate 4: Constitution  → Change does not violate P0-P3 principles
Gate 5: Quality       → Contribution scoring ≥ 0.7 threshold
Gate 6: Impact        → Affected atoms/skills mapped
                        │
                        ▼
                  HUMAN GATE
              Review & Decision
```

---

## Gate 1: Agent Identity Check

**Purpose**: Verify the contribution comes from a self-identifying AI agent.

**Checklist**:
- [ ] File `AGENT_MANIFEST.yaml` exists at repo root
- [ ] YAML parses correctly
- [ ] Required fields present: `agent.name`, `agent.framework`, `agent.capability`
- [ ] `agent.verification.self_test_passed` is `true`

**Pass**: Continue to Gate 2
**Fail**: Auto-comment with "Missing or invalid AGENT_MANIFEST.yaml. See AGENTS_CONTRIBUTING.md Section 3.2"

---

## Gate 2: Syntax Validation

**Purpose**: Ensure all files in the PR are syntactically valid.

| File Type | Validator | Action on Fail |
|-----------|-----------|----------------|
| `.yaml`, `.yml` | `yamllint` | Block PR |
| `.md` | `markdownlint` | Warning only |
| `.py` | `python3 -m py_compile` | Block PR |
| `.json` | `python3 -m json.tool` | Block PR |
| `.toml` | `toml-summit` parse check | Block PR |
| `.sh` | `bash -n` | Block PR |

**YAML rules** (yamllint config):
```yaml
rules:
  indentation: {spaces: 2}
  line-length: {max: 120}
  truthy: disable  # allow true/True/yes
  document-start: disable
```

**Pass**: Continue to Gate 3
**Fail**: Auto-comment with file-specific syntax error messages

---

## Gate 3: Secret Scan

**Purpose**: Prevent hardcoded credentials from entering the repository.

**Patterns scanned** (regex):

```python
patterns = [
    r'[\"\'][A-Za-z0-9_-]{20,}[\"\']',           # Generic long tokens
    r'sk-[A-Za-z0-9_-]{20,}',                      # OpenAI keys
    r's2k-[A-Za-z0-9_-]{20,}',                     # Semantic Scholar keys  
    r'[\"\'][A-Za-z0-9]{32,}[\"\']',               # 32+ char hex strings
    r'ghp_[A-Za-z0-9_-]{36,}',                     # GitHub PAT (old format)
    r'github_pat_[A-Za-z0-9_-]{82,}',             # GitHub PAT (new format)
    r'AKIA[A-Z0-9]{16}',                            # AWS access keys
    r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',     # Private keys
]
```

**Special case**: `example_*` or `test_*` prefixed values are allowed (test keys).

**Pass**: Continue to Gate 4
**Fail**: Auto-comment with "Hardcoded secret detected in [file:line]" → PR blocked

---

## Gate 4: Constitutional Compliance

**Purpose**: Verify the change respects Synthos's four constitutional principles.

**The Four Principles** (from CONSTITUTION.md):

### P0: 证据可溯性
*Every claim, decision, and output must be traceable to a verifiable source.*

- **If PR adds new skills**: Must include provenance metadata (source, date, author)
- **If PR modifies outputs**: Must include traceability chain
- **If PR adds literature sources**: Must include DOI or verifiable URL

### P1: 原子可复现性
*Every cognitive atom must be independently executable and testable.*

- **If PR modifies an atom**: Must not break the atom's independent execution
- **If PR adds an atom**: Must include test/simulation case
- **New atoms must declare I/O contract** (inputs, outputs, error states)

### P2: 稳定下沉/演化上浮
*Proven patterns become skills; unproven experiments stay ephemeral.*

- **New contributions start as "proposals"** (marked unstable)
- Only after 2+ successful cycles can be elevated to stable
- **No direct modification of LTS (Long-Term Stable) skills** without explicit human approval

### P3: 人机分层
*Router handles routing; humans handle decisions; atoms handle execution.*

- **PRs cannot change the routing design principle**
- External agents must self-identify in AGENT_MANIFEST.yaml
- **No PR can remove or bypass human-in-the-loop decision points**

**Compliance Scoring**:

| Violation | Score Impact | Action |
|-----------|-------------|--------|
| None | +1.0 | Pass |
| Minor (style, formatting) | 0.8-0.99 | Pass with warning |
| Moderate (missing metadata) | 0.5-0.79 | Review required |
| Major (violates principle) | <0.5 | Block |

**Pass** (score ≥ 0.7): Continue to Gate 5
**Review Required** (score 0.5-0.69): Flag for human attention
**Fail** (score < 0.5): Block with constitutional violation report

---

## Gate 5: Quality Scoring

**Purpose**: Objectively measure contribution quality.

### Scoring Dimensions (each 0-1, weighted)

| Dimension | Weight | Criteria | Metric |
|-----------|--------|----------|--------|
| Completeness | 0.25 | AGENT_MANIFEST, test evidence, documentation | All required files present |
| Clarity | 0.15 | PR description clarity, code comments | Human-readable + machine-parsable |
| Relevance | 0.20 | Alignment with Synthos goals | Maps to ≥1 cognitive atom |
| Safety | 0.25 | No destructive changes, backward compatible | No deletions of existing features |
| Testability | 0.15 | Can the contribution be validated? | Test case or simulation provided |

### Score Calculation

```
Quality Score = Σ(dimension_score × weight)
```

| Score Range | Grade | Action |
|-------------|-------|--------|
| ≥ 0.9 | 🟢 Excellent | Auto-pass, fast-track human review |
| 0.7 - 0.89 | 🟡 Good | Pass, standard human review |
| 0.5 - 0.69 | 🟠 Marginal | Review required, may need revisions |
| < 0.5 | 🔴 Poor | Auto-close with improvement suggestions |

**Pass** (≥ 0.7): Continue to Gate 6
**Fail** (< 0.7): Auto-comment with quality report and suggestions

---

## Gate 6: Impact Analysis

**Purpose**: Map the contribution to Synthos's architecture and determine review priority.

### Impact Mapping

```yaml
impact_categories:
  - level: "cosmetic"
    description: "Documentation, typos, formatting"
    reviewer: "auto-merge (if Gates 1-5 pass)"
    priotity: "low"
    
  - level: "incremental"
    description: "New source, new tool integration, minor improvement"
    reviewer: "human (standard review)"
    priority: "normal"
    
  - level: "structural"
    description: "New skill, new atom, modified core logic"
    reviewer: "human (owner review required)"
    priority: "high"
    
  - level: "constitutional"
    description: "Modifies CONSTITUTION.md or core principles"
    reviewer: "human (owner only)"
    priority: "critical"
```

### Affected Atom Mapping

The CI identifies which cognitive atom(s) the PR affects:

| Atom | Directory | Impact |
|------|-----------|--------|
| ACQ | `skills/knowledge-acquisition/` | Literature sources, search APIs |
| COD | `skills/coding/` (if exists) | Code generation, tool integration |
| ASC | `skills/argument-expression/` | Writing, reasoning improvements |
| EXT | `skills/knowledge-extraction/` | External source absorption |
| ROU | `skills/task-router/` | Task routing logic |
| EVA | `skills/evaluation/` (if exists) | Quality assessment |
| AVA | `skills/association-discovery/` | Knowledge connection |

---

## Human Gate: Final Review

**Purpose**: The ultimate decision gate. Only the repository owner (or delegate) can approve merge.

### Review Checklist for Humans

- [ ] Agent self-identified in AGENT_MANIFEST.yaml?
- [ ] All 6 auto-gates passed?
- [ ] Does the change align with project direction?
- [ ] Are there any security or privacy concerns?
- [ ] Is the change reversible if needed?
- [ ] Does this set a precedent for future agent contributions?

### Decision Outcomes

```
                    ┌─ Merge ──→ Agent registered in pool
                    │            PR labeled `accepted`
                    │
Human Review ──────┼─ Request Changes ──→ Agent re-submits
                    │                      (or human edits)
                    │
                    └─ Close ──→ Feedback documented
                                 PR labeled `declined`
```

---

## Appendix: CI Implementation

The verification gates are implemented as **GitHub Actions** in `.github/workflows/agent-pr-verify.yml`.

### Required GitHub Secrets

| Secret | Used By | Required |
|--------|---------|----------|
| `GITHUB_TOKEN` | GitHub Actions | Yes (auto-provided) |

### Local Testing

To test gates locally before submitting a PR:

```bash
# Gate 2: Syntax check
yamllint path/to/file.yaml
python3 -m py_compile path/to/file.py

# Gate 3: Secret scan
grep -Pn '[\"'"''][A-Za-z0-9_-]{20,}[\"'\"']' path/to/file

# Gate 4: Constitutional (manual review)
# Verify alignment with CONSTITUTION.md
```

---

*Last updated: 2026-05-12 | Version: 1.0*
