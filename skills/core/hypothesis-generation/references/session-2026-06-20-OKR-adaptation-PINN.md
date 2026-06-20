# Example Session: OKR-adaptation-PINN Hypothesis Generation

**Date**: 2026-06-20 | **Model**: deepseek-v4-flash | **Domain**: Vestibular Oculomotor / Cerebellar Adaptation

## Input Context

| Field | Value |
|:------|:------|
| White Space | ✅ ABSOLUTE_WHITE — zero PINN/NeuralODE models of OKR adaptation |
| Classical Prior Art | Cerebellar LTD/STDP spike-based models, VOR adaptation studies |
| Proposed Architecture | 2-ODE (OKR Visuomotor + Cerebellar Adaptation) + 44K PINN residual |
| Clinical Targets | Cerebellar ataxia, MS, oscillopsia, spatial disorientation |
| Feasibility | 0.78 (HIGH) |

## Generated Hypotheses

### H1: Gain-Frequency Sigmoidal Response (0.74, HIGH)

**Statement**: OKR gain follows sigmoidal frequency response learnable by PINN from sparse data.

**Falsifiability**: RMSE > 0.12 between sigmoidal fit and data, or PINN test error > 10% on held-out frequencies from 3-point training.

**Supporting**: Cohen 1977, Paige 1983, Demer 1990, Leigh & Zee 2015.

### H2: Logarithmic Adaptation Rate Scaling (0.74, HIGH)

**Statement**: Cerebellar adaptation rate scales logarithmically with retinal slip error magnitude (α = α₀ + k·log(|ε| + ε₀)).

**Falsifiability**: R² < 0.4 for log-linear fit, or k outside [0.001, 0.5] s⁻¹.

**Supporting**: Raymond & Lisberger 1998, Ito 2006, Lisberger 2010, Badura & De Zeeuw 2018.

### H3: Adaptation Time Constant as Ataxia Biomarker (0.84, HIGHEST)

**Statement**: τ_adapt is more sensitive than VOR gain for early cerebellar dysfunction detection (ROC AUC > 0.85 vs < 0.70).

**Falsifiability**: τ_adapt ROC AUC ≤ 0.70, or AUC difference from VOR gain < 0.1.

**Supporting**: Tarnutzer et al. 2021, Kheradmand & Zee 2011, Manto & Marmolino 2009.

## Key Patterns Demonstrated

1. **Falsifiability first**: Every hypothesis begins with "Falsified if: [quantitative condition]"
2. **Evidence matrix**: 4-5 supporting references + counter-evidence per hypothesis
3. **Clinical anchor**: H3 ties directly to SARA score (clinical gold standard)
4. **Composite scoring**: 5-dimension weighted rubric
5. **Distinguishing test**: Between H1/H2 (retrospective existing data) vs H3 (prospective clinical study)

## Files Produced

- `outputs/papers/_knowledge_only/OKR-adaptation-PINN/step_hypothesis_generation.md` — full 120-line output
- `outputs/papers/_knowledge_only/OKR-adaptation-PINN/state.json` — updated with hypotheses array + scores
