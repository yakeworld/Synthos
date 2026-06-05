# vHIT-ML Papers for BPPV-PINN Reference

> Direct citations for BPPV-PINN-canalolithiasis paper — competitive ML baseline section (vHIT domain)

## Core References (Cite in BPPV-PINN paper)

### Primary vHIT-ML References (Black-box baseline)

1. **Wang et al. (2025)** — J Neurol. DOI: 10.1007/s00415-025-12918-3
   - ML on raw vHIT eye/velocity data: stroke vs vestibular neuritis
   - 87.8% accuracy, comparable to expert clinicians
   - Cite in Method section: "Similar to Wang et al. who applied ML to vHIT time series for stroke diagnosis, we apply PINN to canalith dynamics"

2. **Korda et al. (2022)** — Front Neurol. DOI: 10.3389/fneur.2022.919777
   - LSTM on unprocessed vHIT time series for vestibular stroke
   - 57 AVS patients, 87.9% accuracy
   - Cite in related work: "Deep learning approaches to vestibular dynamics (LSTM: Korda 2022, accuracy 87.9%)"

3. **Du et al. (2022)** — Auris Nasus Larynx. DOI: 10.1016/j.anl.2021.10.003
   - Random forest on vestibular indicators including vHIT gain/saccade
   - 1491 patients, 90-91% accuracy for syndrome classification
   - Cite as: "Random forest classification using vHIT variables (Du 2022, 90% accuracy)"

### Citation Pattern for BPPV-PINN Paper

In the Method section, contrast approach:
> "While recent ML approaches have applied black-box classifiers to vestibular time series data [Wang2025, Korda2022, Du2022], these methods learn input-output mappings without encoding the underlying physics. Our PINN approach embeds the canalith ODE dynamics directly in the loss function..."

In Related Work:
> "vHIT-ML: Wang et al. applied ML to vHIT for stroke/VN differentiation (87.8%), Korda et al. used LSTM on vHIT time series for vestibular stroke (87.9%), Du et al. used Random Forest on vHIT variables (90%). These demonstrate the clinical value of vHIT data, but use black-box approaches."