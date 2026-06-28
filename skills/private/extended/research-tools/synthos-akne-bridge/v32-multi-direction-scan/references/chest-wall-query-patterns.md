# Chest Wall / Diaphragm Mechanics Query Patterns

> Domain-specific patterns for literature scanning in chest wall and respiratory muscle mechanics.
> Discovered during Domain Expansion #8 literature_scan (Cycle 171, 2026-06-23).

## Domain Summary

Chest wall mechanics extends from K-015 (lower airway lung mechanics) to the active respiratory system: rib cage + abdominal wall + diaphragm. Unlike passive lung mechanics (measurable via FOT), chest wall mechanics traditionally requires invasive esophageal pressure (Pes). This domain is under-modeled computationally compared to lung mechanics.

## Known False Positive Patterns (PINN + Chest Wall / Diaphragm)

| Pattern | Query Trigger | Why False Positive | How to Filter |
|:--------|:-------------|:-------------------|:--------------|
| **Breast/Chest Imaging** | `physics-informed neural + diaphragm` | "Breast" in "breathing" or chest CT — PINN for medical image reconstruction, NOT diaphragm mechanics | Exclude "breast", "CT reconstruction", "image segmentation", "imaging" |
| **Loudspeaker/Acoustic Diaphragm** | `PINN + diaphragm` | Engineering papers about loudspeaker diaphragm vibration modeling using PINN — acoustic engineering, NOT physiology | Exclude "loudspeaker", "acoustic", "speaker", "microphone", "vibration" |
| **Optical/Lens Diaphragm** | `PINN + diaphragm` | Camera/lens aperture diaphragm modeled with PINN — optics engineering | Exclude "aperture", "lens", "camera", "optical" |
| **MEMS/Pump Diaphragm** | `diaphragm + mechanics + model` | Micro-diaphragm pumps and MEMS actuators modeled with FEM/PINN | Exclude "MEMS", "pump", "actuator", "micro-diaphragm", "microfluidic" |
| **Cardiac Imaging Confusion** | `chest wall + model + patient-specific` | Cardiac MRI/CT that happens to pass through chest wall — cardiology, NOT respiratory mechanics | Exclude "cardiac", "myocardial", "coronary", "echocardiography" |
| **Weaning Prediction Clinical** | `mechanical ventilation + weaning + model` | Clinical/statistical prediction models for weaning success (RSBI, rapid shallow breathing index) — NOT computational ODE | Clinical prediction ≠ PINN parameter inference |

## Effective Query Strategies

### Narrow PINN Queries (Best — use title_and_abstract.search)

```python
# Query 1: PINN + diaphragm (narrowest)
'physics-informed neural network diaphragm respiratory muscle'

# Query 2: PINN + chest wall  
'physics-informed neural network chest wall mechanics'

# Query 3: NeuralODE variant catch
'neural ordinary differential equation respiratory muscle chest wall'

# Query 4: Inverse parameter inference
'PINN lung mechanics parameter identification inverse'
```

### Broad Classical ODE Queries

```python
# Query 5: Classical lumped-parameter
'lumped parameter model chest wall respiratory mechanics'

# Query 6: Mechanical ventilation models
'mechanical ventilation respiratory mechanics parameter estimation patient specific'

# Query 7: Chest wall compliance
'chest wall compliance resistance elastance model respiratory'
```

### OpenAlex Queries

```python
# Always use filter=title_and_abstract.search: (NOT search=) — see openalex-search-strategy.md

# Narrow:
filter=title_and_abstract.search:physics-informed+neural+network+diaphragm+respiratory+muscle

# Broad classical:
filter=title_and_abstract.search:mechanical+ventilation+respiratory+mechanics+model+parameter+estimation+patient+specific
```

## Verdict Assessment Criteria (Chest Wall Specific)

| Narrow PINN | NeuralODE | Classical ODE | Clinical Hits | Verdict |
|:-----------:|:---------:|:-------------:|:-------------:|:--------|
| 0 | 0 | 100+ | 500+ | ✅ **ABSOLUTE_WHITE** |
| 0 | 0 | 10-50 | 100+ | ✅ **CONDITIONAL_WHITE** |
| 0 | 0 | <10 | all | ⚠️ **CONDITIONAL_WHITE (sparse)** |
| 1+ (real) | any | any | any | ❌ **OCCUPIED** |

**Note**: Chest wall / diaphragm has inherently fewer classical ODE models than lower airway (K-015 had 985+ classical hits). 10-50 classical models is normal for this domain because chest wall mechanics requires invasive Pes measurement. The lower classical count does NOT reduce white space quality — it reflects measurement difficulty, not literature completeness.

## 2-ODE+PINN Architecture (Proposed K-016)

| Component | State | Parameters | Notes |
|:----------|:------|:----------|:------|
| ODE-1: Chest Wall Passive | P_cw(t) | C_cw [0.05-0.20], R_cw [1-5], I_cw [0.01-0.02] | Rib cage + abdominal wall compliance/resistance |
| ODE-2: Diaphragm Active | P_di(t) | P_di_max [80-200], τ_fatigue [2-15min], k_gain [0.5-2.0] | Force-length-velocity + fatigue dynamics |
| Cross-coupling | P_tot(t) = P_cw(t) + P_di(t) | — | Series pressure summation |
| PINN target | Patient-specific C_cw, R_cw, P_di_max | 5-7 params | From surface EMG + US + flow |

## Clinical Targets

| Condition | Prevalence | Current Metric | PINN Advantage |
|:----------|:----------:|:--------------|:--------------|
| COPD diaphragm dysfunction | 30-50% of 16M | Pdi sniff test (invasive) | Non-invasive EMG → Pdi inference |
| ICU weaning failure | 20-30% of ventilated | RSBI (indirect) | Direct C_cw, R_cw estimation |
| ALS respiratory decline | 30K new/yr | FVC (late) | Early P_di_max decline detection |
| Muscular dystrophy | 1:3500 births | MIP (volitional) | Independent diaphragm assessment |
| Sleep apnea (OSA) | 39M | AHI (apnea index) | C_cw + P_di from overnight monitoring |

## Data Sources

| Dataset | Type | Size | Access |
|:--------|:-----|:----:|:-------|
| MIMIC-III Ventilator | ICU vent + Pes | 40K+ | PhysioNet |
| UK Biobank | PFT only (no Pes) | 500K+ | Application |
| PLATIAL (open) | Respiratory mechanics | 2K | Open |
| Mouse diaphragm EMG | Animal data | N/A | Research use |
