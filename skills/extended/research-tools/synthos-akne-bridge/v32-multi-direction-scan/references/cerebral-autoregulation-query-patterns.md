# Cerebral Autoregulation Query Patterns (CA Domain)

**Domain**: BP→CBF closed-loop feedback — natural extension from K-010 baroreflex
**First Probe**: Cycle 152 (2026-06-21)
**Verdict**: ABSOLUTE_WHITE — 0 PINN/NeuralODE/ODE across 14 queries

## CA1: TFA Dominance ≠ PINN Competition

The cerebral autoregulation (CA) literature is dominated by **Transfer Function Analysis (TFA)** — 416 PubMed hits.

- TFA is a frequency-domain spectral method (coherence, phase, gain between BP and CBF oscillations)
- It is NOT a time-domain ODE formulation for patient-specific parameter inference
- **Detection**: if a CA paper title contains "transfer function", "coherence", "phase", or "spectral" — it's TFA, not PINN competition
- Compare this to baroreflex (K-010) where system identification dominates — TFA is even further from PINN because it doesn't even produce a parametric model

## CA2: Classical Lumped-Parameter ≠ PINN

The CA literature contains multi-compartment physiological models of cerebral blood flow:

- Lumped-parameter Windkessel models (preterm newborns, CBF autoregulation)
- Multi-physics CFD models (cerebral arterial networks)
- Coupled cerebro-ocular-CSF models

**Diagnostic rule**: if the title references "lumped-parameter", "compartment model", "multi-physics", "CFD", "finite element", or "mathematical model" without "neural network" or "learning", classify as classical physiological model — NOT PINN competition.

This pattern is structurally similar to classical-biomechanics false positives (cupula K-003, arterial wall models).

## CA3: Clinical Dominance — 1000+ Diagnostic Studies

Broad CA queries return >1000 clinical papers:

- Valsalva maneuver CA assessment
- Squat-stand/orthostatic CA protocols
- TBI/stroke/SVD clinical CA studies
- Anti-hypertensive treatment CA effects

**All diagnostic/clinical** — none contain PINN/ODE computational parameter inference.

**Query strategy**: use AND clauses for "model" OR "computational" OR "differential equation" to filter. Even then, ~7-11 hits return classical models (CA1-CA2).

## CA4: System Identification ≠ PINN

11 PubMed hits for "cerebral autoregulation AND (parameter estimation OR parameter inference OR system identification)":

- Black-box ARX/ARMAX models
- Nonlinear system identification
- Optimizing CA assessment from black box models

**Detection**: if the paper title contains "system identification", "ARX", "ARMAX", "black box", or "optimising assessment" — it's classical sysID, NOT PINN.

This mirrors the **B1 baroreflex pattern** — baroreflex had 32 sysID hits, CA has 11. Both are signal-processing/control-theoretic, not physics-informed.

## CA5: OpenAlex Cross-Domain Noise

OpenAlex broad queries on CA terms return cross-domain noise from:
- "cerebral autoregulation" colliding with gene regulation / neurodevelopment papers
- "autoregulation" in cellular/molecular contexts
- C. elegans / developmental biology papers with "autoregulation" meaning gene transcription regulation

**Detection**: always check top-3 titles. OpenAlex count of 3 per query is typical — if any result's title references non-cardiovascular physiology (gene regulation, C. elegans, neurons/development), skip it.

## Query Template

```python
# Standard CA probe (10 queries)
queries = [
    # PubMed narrow PINN/NeuralODE (5)
    '"cerebral autoregulation" AND PINN',
    '"cerebral autoregulation" AND "physics-informed"',
    '"cerebral autoregulation" AND "neural ODE"',
    '"cerebral autoregulation" AND "neural network" AND "differential equation"',
    '"cerebral autoregulation" AND (ODE OR "differential equation") AND (model OR parameter)',
    
    # OpenAlex (5)
    'cerebral autoregulation PINN',
    'cerebral autoregulation physics-informed neural network',
    'cerebral autoregulation neural ODE',
    '"cerebral autoregulation" "computational model" parameter inference',
    '"cerebral autoregulation" hemodynamics model differential equation',
]
```

Expected result: 0 PINN/NeuralODE across all 10 queries. TFA hits (416) + sysID hits (11) + clinical hits (1000+) are ALL false positives — none are PINN/ODE parameter inference for patient-specific models.

## Stability

| Check | Status | Date |
|:------|:-------|:-----|
| Initial probe | ✅ ABSOLUTE_WHITE | 2026-06-21 |
| Re-scan needed | Not before 2026-08 | — |
