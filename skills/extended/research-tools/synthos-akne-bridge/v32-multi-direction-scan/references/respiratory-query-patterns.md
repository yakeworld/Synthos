# Respiratory / Lower Airway Query Patterns

> Domain-specific patterns for literature scanning in respiratory mechanics / lung dynamics.
> Discovered during Domain Expansion #7 literature_scan (Cycle 167, 2026-06-22).

## Known False Positive Patterns (PINN + Respiratory)

| Pattern | Query Trigger | Why False Positive | How to Filter |
|:--------|:-------------|:-------------------|:--------------|
| **Pulmonary Blood Flow** | `PINN + lung/pulmonary` | Pulmonary artery PINN (blood flow, CFD) is vascular NOT airway mechanics. Most common FP. | Exclude "blood flow", "pulmonary artery", "pulmonary vein", "cardiac", "right ventricle" |
| **CT/MRI Sinogram** | `PINN + lung mechanics` | Sinogram-based flow estimation in CT uses PINN for image reconstruction, NOT respiratory mechanics | Exclude "sinogram", "CT reconstruction", "image reconstruction", "perfusion" |
| **Cerebral/Cardiac** | `PINN + lung dynamics` | "PINNing cerebral blood flow" as false hit — cerebral perfusion unrelated to lung mechanics | Exclude "cerebral", "brain", "cardiac" |
| **3D Bioprinting / Surgical** | `PINN + respiratory` | Surgical deformation models and bioprinting tissue analogs — computational geometry not respiratory dynamics | Exclude "bioprint", "surgical", "deformation" |
| **In Silico Twins / Review** | Broad `PINN + respiratory` | Review papers and frameworks about digital twins that mention respiratory as one domain — NOT PINN applied to respiratory | Filter to papers with actual PINN methods, not reviews |

## Effective Query Strategies

### Narrow PINN Queries (Best)

```python
# Query 1: Inverse PINN for lung mechanics (narrowest, best signal)
'(physics-informed neural network OR PINN) AND (lung mechanics OR respiratory mechanics OR airway resistance)'

# Query 2: Neural ODE for respiratory (catches Neural ODE variants)
'(neural ODE OR neural ordinary differential equation) AND (respiratory OR lung)'
```

### Broad Contextual Queries

```python
# Query 3: Classical ODE models (confirms well-characterized domain)
'("lumped-parameter" OR "resistance-compliance" OR "lung model") AND (respiratory OR lung) AND (ODE OR "ordinary differential equation")'

# Query 4: Patient-specific lung models (catches non-PINN competition)
'(patient-specific OR personalized) AND (lung OR respiratory) AND (model OR parameter estimation)'
```

### OpenAlex Queries

```python
# Always use sort=cited_by_count + filter=cited_by_count:1- to avoid zero-citation noise
# Narrow: PINN + respiratory mechanics
search=PINN+respiratory+mechanics+lung+pulmonary

# Broad: PINN + respiratory
search=physics-informed+neural+network+respiratory+lung
```

## Verdict Assessment Criteria

| PubMed Narrow | OpenAlex Narrow | Classical Model Count | Verdict |
|:-------------:|:---------------:|:---------------------:|:--------|
| 0 | 0 | 100+ | ✅ **ABSOLUTE_WHITE** — strong candidate |
| 0 | 1-3 (all FP) | 100+ | ✅ **CONDITIONAL_WHITE** — verify FPs |
| 0 | 5+ (mixed) | 100+ | ⚠️ **CONDITIONAL_WHITE** — manual review |
| 1+ | any | any | ❌ **OCCUPIED** — competition exists |

## Clinical Data Sources (Respiratory)

| Dataset | Type | Size | Access |
|:--------|:-----|:----:|:-------|
| NHANES Spirometry | PFT (FEV1, FVC, FEF25-75) | 30K+ | Public |
| COPDGene | CT + PFT + outcomes | 10K+ | Application |
| MIMIC-III Ventilator | ICU ventilation waveforms | 40K+ | PhysioNet |
| UK Biobank | PFT + outcomes | 500K+ | Application |
| SPIROMICS | COPD deep phenotyping | 3K | Application |
