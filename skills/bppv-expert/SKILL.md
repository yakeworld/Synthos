---
name: bppv-expert
description: >-
  Structured BPPV (Benign Paroxysmal Positional Vertigo) medical knowledge
  extracted from AKNE knowledge graph. Covers diagnosis techniques (Dix-Hallpike,
  supine head flexion test), repositioning maneuvers (Epley, Gufoni, Semont,
  Barbecue, roll-over), canalith conversion mechanisms, 3D biomechanical
  simulation, and clinical decision workflows. Source: AKNE wiki (126 nodes,
  137 edges, proven correctness via falsification testing).
tags: [bppv, vestibular, vertigo, diagnosis, repositioning, medical-expert]
---
# BPPV Expert — Extended Skill for Synthos

## Trigger
- User asks about BPPV diagnosis, treatment, or canalith repositioning
- User needs to interpret nystagmus patterns for canal involvement (posterior/horizontal/anterior)
- User asks about 3D biomechanical simulation of BPPV
- User asks about the anatomy of the semicircular canals and otolith organs
- User asks about differential diagnosis of positional vertigo

## Knowledge Sources
Absorbed from AKNE knowledge graph (yakeworld → .knowledge/wiki/):
- `bppv.md` — Disease overview (epidemiology, etiology, clinical presentation)
- `dix-hallpike.md` — Dix-Hallpike diagnostic maneuver
- `ear-stone-repositioning.md` — Repositioning maneuvers (Epley, Gufoni, Semont, Barbecue)
- `supine-head-flexion-test.md` — Supine head flexion test (俯屈仰头试验)
- `skyward-head-lift.md` — Skyward head lift method (仰天叩地法)
- `posterior-canal-new-repositioning.md` — New repositioning method for posterior canal (低头80°+后仰140°)
- `canalith-conversion.md` — Canalith conversion mechanisms between canals
- `vestibular-anatomy.md` — Vestibular system anatomy
- `virtual-simulation.md` — 3D biomechanical simulation research
- `bppv-assets.md` — BPPV knowledge asset inventory (60+ papers)

## Key Capabilities

### 1. Diagnosis Guidance
- Interpret nystagmus direction/pattern → identify involved canal (posterior = upbeating+torsional, horizontal = horizontal, anterior = downbeating+torsional)
- Select appropriate diagnostic test (Dix-Hallpike for posterior/anterior, supine roll test for horizontal)
- Differentiate canalithiasis vs cupulolithiasis based on nystagmus duration

### 2. Treatment Protocol
- Canal-specific repositioning maneuvers with step-by-step instructions
- Home-based self-treatment options (skyward head lift for horizontal, etc.)
- Post-maneuver precautions and recurrence prevention

### 3. 3D Biomechanical Simulation
- Physics-based simulation of otoconia motion during diagnostic/therapeutic maneuvers
- Canal conversion path prediction
- Custom maneuver design and testing before clinical application

### 4. Knowledge Asset Management
- Structured extraction of BPPV papers into knowledge items (知识点/创新点/核心技术)
- Paper-to-practice gap analysis

## Input/Output Contract
```yaml
input_contract:
  input:
    - query: str  # Natural language query about BPPV
    - context: str  # Optional: patient presentation details
  output:
    - answer: str  # Structured response with evidence
    - confidence: float  # 0.0-1.0 confidence score
    - sources: list[str]  # AKNE wiki file paths
```

## Constraints
- Do NOT give medical advice — always state: "This is educational knowledge. Clinical decisions require in-person evaluation."
- Cite specific AKNE wiki pages for every claim
- Distinguish between evidence-based fact (from papers) and hypothesized mechanism
- Maneuver descriptions must include: patient position, head rotation direction/angle, timing, expected nystagmus response

## Origin
Absorbed from AKNE knowledge graph (yakeworld/.knowledge/) — 2026-05-12
