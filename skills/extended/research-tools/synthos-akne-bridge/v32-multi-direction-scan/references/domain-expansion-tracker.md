# Domain Expansion Status

> Track the canonical sequence of domain expansions.
> Updated 2026-06-22 after Cycle 167 (literature_scan for respiratory-mechanics-PINN, K-015).

## Completed Expansions

| # | Domain | Kernel | Candidate | Status | Score |
|:-:|:-------|:------:|:----------|:------:|:-----:|
| — | Oculomotor/Vestibular (Rotation Scan) | K-001 through K-006 | PAN-PINN, GazeStability-ODE, SmoothPursuit-PINN, VestibularCompensation-ODE, CupulaDeflection-PINN, VOR-OKR-Coupling-PINN, OKR-adaptation-PINN, caloric-test-response-ODE, VestibularCollicReflex-PINN, MotionSickness-PINN, 113-scleral-remodeling-ODE | ✅ All 10+ completed | 0.82–0.88 |
| 1 | Cardiac Autonomic | K-009 | cardiac-autonomic-regulation-PINN | ✅ Completed (cycles 141-143) | 0.88 |
| 2 | Baroreflex Cardiovascular | K-010 | baroreflex-regulation-PINN | ✅ Completed (cycles 144-147) | 0.88 |
| 3 | RSA Cardiopulmonary | K-011 | respiratory-sinus-arrhythmia-PINN | ✅ Completed (cycles 148-151) | 0.88 |
| 4 | Cerebral Autoregulation | K-012 | cerebral-autoregulation-PINN | ✅ Completed (cycles 152-155) | 0.88 |
| 5 | Cochlear Auditory | K-013 | cochlear-mechanics-PINN | ✅ Completed (cycles 156-159) | 0.88 |
| 6 | Laryngeal Phonation | K-014 | vocal-fold-phonation-PINN | ✅ Completed (cycles 160-166) | 0.85 |
| 7 | Lower Airway Lung Mechanics | K-015 | respiratory-mechanics-PINN | 🔄 In progress (Cycle 167: literature_scan done) | 21/25 |

## Next Expansion Candidates

After #7 (respiratory mechanics), natural physiological extensions:

| Priority | Domain | Rationale | Clinical Pop. |
|:---------|:-------|:----------|:-------------:|
| **A** | Bronchial tree / small airways | Natural subdivision of lower airway | COPD 16M |
| **B** | Respiratory muscle dynamics (diaphragm) | Mechanical extension of lung pump | MV weaning 2M/yr |
| **C** | Pulmonary gas exchange / diffusion | Chemical extension (DLCO, V/Q) | ILD 200K |

## Expansion Principles

1. **Natural kernel extension**: Each domain must be a physiological continuation from the previous kernel (e.g., auditory → laryngeal → lower airway follows the aerodigestive tract)
2. **ABSOLUTE_WHITE verification**: Every new domain must pass 6+ queries (narrow + broad) with 0 PINN/NeuralODE hits before entering pipeline
3. **Classical model richness**: The domain must have 100+ classical ODE models (confirming well-characterized physiology) to use as forward reference
4. **Zero-equipment requirement**: Clinical translation must not require new hardware
5. **Multi-source free API scan**: When SEMANTIC_SCHOLAR_API_KEY is absent, use PubMed + OpenAlex + arXiv (all free) to confirm ABSOLUTE_WHITE
