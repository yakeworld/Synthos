# Self-Consistency Audit for Cognitive Atom Systems

> 6-dimension audit to verify that a set of cognitive atoms forms a logically coherent system.
> Designed for Synthos-style skill-driven architectures. Run after any structural evolution or when adding/removing atoms.

## The 6 Dimensions

### D1. Dependency DAG — No Cycles, No Dead Ends

Verify the directed graph of `depends_on` declarations:

```yaml
checks:
  - is_acyclic: true       # topological sort succeeds
  - no_orphans: true       # every atom has at least one upstream OR is a root
  - no_redundant_edges: true  # skip transitive deps (e.g. if A→B→C, don't also declare A→C)
  - every_declared_dep_exists: true  # depends_on names match actual atom names
```

**Pitfall**: `depends_on` pointing to Hermes skills (e.g. `semantic-scholar`) rather than other atoms. This is valid for root atoms but creates a format inconsistency with non-root atoms.

### D2. Boundary Non-Overlap — Every Atom Has a "Not-My-Job" Statement

Each atom's BOUNDARY.md or equivalent must explicitly state:

```yaml
checks:
  - exclusive_claim: true   # "this atom does X and ONLY X"
  - negation_claim: true    # "this atom does NOT do Y" for every adjacent atom
  - mutual_verification: true  # atom A says "not Y", atom B says "does Y" — check pairs match
```

**Adjacent pair test**: For every edge A→B in the DAG, verify:
- A's boundary says "I don't do what B does"
- B's boundary says "I do what A doesn't, and A's output is my input"

Example (verified OK in Synthos v4.3):
| Atom | Negation | Confirmed by |
|------|----------|-------------|
| ACQ | "不做文本分析" | EXT "做单论文提取" |
| EXT | "不做跨论文比较" | ASC "做跨论文关联" |
| ASC | "不做假设生成" | HYP "做假设生成" |

### D3. Compliance Declaration vs Constitution — No Drift

Maintain a matrix mapping constitution principles to atoms:

```
Constitution P0-P5  →  atom compliance declarations  →  verified match
```

Common drift patterns:

| Pattern | Symptom | Fix |
|---------|---------|-----|
| **GAP absorption** | GAP principle (e.g. P5) is declared for GAP, GAP gets absorbed into ASC, but ASC's compliance declaration is never updated | Update ASC to declare the absorbed principle |
| **Over-claim** | Atom declares P3 but constitution says P3 only applies to router | Either constitution is wrong (update it) or atom is wrong (remove P3) |
| **Stale P0/P1** | Atom drops P0 after refactoring but still generates evidence chains | Declare the correct set |
| **Hash mismatch** | `synthos_skill_md_hash: "pending"` | Regenerate hash after content freeze |

### D4. IO Contract Chain — Downstream Gets What Upstream Produces

Each pair (A → B) must satisfy:

```
output_fields(A) ⊇ input_fields(B)
```

For every field that B declares as `required: true` in its input, A's output must guarantee it.

**Check method**:
1. Read upstream's output schema / IO_CONTRACT.md
2. Read downstream's input schema / IO_CONTRACT.md
3. Verify required downstream fields are produced by upstream

Common failure: **templated IO contracts**. If 5/6 atoms have IO_CONTRACT.md that says "详见 docs/atom-io-schemas.md" instead of the actual schema, the chain is not locally verifiable — the contract lives in a center document, not the atom.

### D5. Frontmatter Format Consistency — One Standard, Not N

All atoms should share the same frontmatter structure. Key fields to check uniformly:

```yaml
name:                    # kebab-case, matches directory name
description: >           # ≥80 chars, concrete noun-verb pairs
license: MIT
allowed-tools:           # present, non-empty
metadata:
  synthos_atom_type:     # "cognitive" or "meta-evolution"
  synthos_version:       # semver, no "v" prefix
  synthos_io_contract_ref:
  synthos_evidence_schema_ref:  # optional if P1 not claimed
  synthos_boundary_proof_ref:   # mandatory for cognitive atoms
  synthos_change_log_ref:
  synthos_golden_set_ref:
  synthos_pass_threshold:       # ≤0.80
  synthos_model_version_pin:    # format: "provider/model@date"
  synthos_skill_md_hash:        # sha256, NOT "pending"
  synthos_asserted_compliance:
  synthos_depends_on:
```

**Common violations**:
- `synthos_skill_md_hash: "pending"` — placeholder leaked to production
- No `metadata:` block at all (router atoms often miss this)
- `synthos_model_version_pin` missing on newly created atoms
- `stability: unstable` field on atoms that have passed ≥2 evolution cycles

### D6. Version Chain — Semantic Consistency

Check that upstream bumps propagate:

| Pattern | Meaning | When to flag |
|---------|---------|-------------|
| All atoms at 0.y.z | Everything is initial — OK | — |
| One atom at higher major | Major change absorbed from external | Verify changelog explains jump |
| Downstream older than upstream | Upstream changed, downstream not re-tested | ⚠️ Evolutionary skew |
| No CHANGELOG entries | Changes occurred but no documentation | Patch omission |

## Quick Audit Script (python)

```python
import json, os, re, yaml

SKILLS_DIR = "/media/yakeworld/sda2/Synthos/skills"
ATOMS = ["task-router", "knowledge-acquisition", "knowledge-extraction",
         "association-discovery", "hypothesis-generation", 
         "argument-expression", "viewpoint-verification"]

def audit():
    report = {"dag": {}, "boundaries": {}, "compliance": {}, 
              "io_contracts": {}, "frontmatter": {}, "versions": {}}
    
    for a in ATOMS:
        md_path = f"{SKILLS_DIR}/{a}/SKILL.md"
        with open(md_path) as f:
            content = f.read()
        
        # Extract frontmatter
        fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            report["frontmatter"][a] = "NO FRONTMATTER"
            continue
        
        front = yaml.safe_load(fm_match.group(1))
        meta = front.get("metadata", front)
        
        report["frontmatter"][a] = {
            "has_metadata": "metadata" in front,
            "hash": meta.get("synthos_skill_md_hash", "MISSING"),
            "model_pin": meta.get("synthos_model_version_pin", "MISSING"),
            "allowed_tools": "allowed-tools" in content[:200],
            "desc_length": len(front.get("description", "")),
        }
        
        report["compliance"][a] = meta.get("synthos_asserted_compliance", "MISSING")
        report["versions"][a] = meta.get("synthos_version", "MISSING")
        
        # IO contract size
        io_path = f"{SKILLS_DIR}/{a}/references/IO_CONTRACT.md"
        if os.path.exists(io_path):
            report["io_contracts"][a] = os.path.getsize(io_path)
        else:
            report["io_contracts"][a] = 0
    
    return report
```

## When to Run

| Trigger | Action |
|---------|--------|
| After atom creation/deletion | Full 6-dimension audit |
| After absorption event | D3 (compliance drift) + D6 (version chain) |
| Every 3 evolution cycles | D1 + D2 (structural integrity) |
| Before competition submission | All 6 dimensions |
