# OpenAlex Domain Expansion Probe Pattern

> When Semantic Scholar API is rate-limited (HTTP 429), use OpenAlex as fallback for probing new domain expansion directions.

## Pattern

```
S2 429 → OpenAlex narrow PINN probe → classify results → confirm ABSOLUTE WHITE
```

## Why This Exists

Semantic Scholar has per-key daily rate limits. Even with a valid API key, heavy cron usage can hit these limits. OpenAlex has no API key requirement and generous rate limits (10 req/s). However, OpenAlex broad searches return many irrelevant results (comprehensive surveys, clinical guidelines, materials science, etc.) that inflate hit counts.

## Probe Strategy

### Step 1: Narrow PINN/ODE Queries

Use highly-specific query terms targeting PINN/ODE competition:

```
Query template: "{domain_specific_term} physics-informed neural network"
Query template: "{domain_specific_term} differential equation model parameter estimation"
Query template: "{domain_specific_term} ODE model patient-specific"
```

**Example (from bronchomotor tone probe):**
```
bronchomotor tone physics-informed neural network airway smooth muscle  →  total=0  ✅ ABSOLUTE WHITE
airway smooth muscle neural network differential equation             →  total=39 → inspect titles
bronchial hyperreactivity mathematical model ODE                     →  total=4  → inspect titles
```

### Step 2: Result Classification

Classify each non-zero result into:

| Class | Description | Verdict |
|:------|:------------|:--------|
| **PINN/ODE competitor** | Uses PINN or Neural-ODE for patient-specific parameter inference | ❌ Competition exists |
| **Classical ODE model** | Uses ODEs analytically (not PINN) | ✅ Not competition |
| **Clinical/diagnostic** | Clinical study, not computational model | ✅ Not competition |
| **FEM/PDE model** | Finite element or continuum model, not ODE | ✅ Not competition |
| **Survey/review** | Comprehensive review paper | ✅ Not competition |
| **Irrelevant domain** | Materials science, vision, immunology noise | ✅ Not competition |

### Step 3: Confirmation Query

If narrow queries return zero, confirm with 2 additional orthogonal queries:
```
"{domain} PINN parameter inference"
"{domain} computational model inverse problem"
```

### Step 4: Score via v32 Scoring Matrix

| Score | Feasibility | Action |
|:------|:-----------:|:-------|
| ≥24 | ≥3 | START — create gap analysis |
| ≥24 | <3 | CANDIDATE — lower priority |
| 18-23 | any | CANDIDATE |
| <18 | any | POSTPONE |

### Step 5: Create Candidate Infrastructure

```bash
mkdir -p outputs/papers/_knowledge_only/{candidate-id}/
# Write step_literature_scan.md
# Create state.json
# Update research-queue.json
# Update evolution-state.json  
# Append to agent-log.md
```

## Worked Example: bronchomotor-tone-PINN (2026-06-22)

| Query | Hits | Classification |
|:------|:----:|:--------------|
| `bronchomotor PINN` narrow | 0 | ✅ ABSOLUTE WHITE |
| `airway PINN` narrow | 39 | All irrelevant (materials, vision, immunology) |
| `bronchoconstriction PINN` | 6 | Mechanistic asthma models, not PINN |
| `airway wall ODE` | 44 | Reviews and irrelevant |
| `bronchial hyperreactivity model` | 4 | Lung slice biomechanics, not PINN |
| `respiratory mechanics PINN` narrow | 466 | Mostly surveys, not PINN/ODE |

**Verdict**: Strong ABSOLUTE WHITE. Natural 2-ODE+PINN architecture (ODE-1: airway smooth muscle contraction dynamics; ODE-2: airway wall mechanics/collapse). Clinical: asthma (262M global), COPD (16M US), bronchial hyperreactivity diagnostics.

## Pitfalls

1. **OpenAlex broad queries inflate counts**: A query with 466 results may contain 0 PINN/ODE competitors. Always inspect top 5 titles before concluding.
2. **"Mathematical model" ≠ PINN**: Classical mathematical models (analytical ODE, FEM, PDE continuum) are NOT PINN competition. PINN competition means neural-network-based learning of patient-specific parameters from data.
3. **S2 may recover next session**: If S2 is 429'd, try again next cron run before committing to OpenAlex-only probe.
4. **Always check ORCID/domain collisions**: Abbreviation collisions (like "VCR" matching viral clearance rate) can produce false positive noise.
