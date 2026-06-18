# Ocular Blood Flow ODE — Paper 116 Reference

**Date**: 2026-06-09
**Type**: 2-ODE PINN, single-session assembly
**Status**: COMPLETE (PDF 6 pages, 231KB, 26155 bytes)
**ABSOLUTE WHITE**: PubMed=0 for ODE ocular blood flow regulation

### Model
- State variables: Q(t) blood flow (mL/min), C(t) autoregulatory control [0,1]
- 8 parameters: alpha, C0, Q0, k1, k2, k3, gamma, Q_max
- ODEs: dQ/dt and dC/dt with metabolic demand coupling, autoregulatory regulation, flow-variability adaptation, saturation
- R2=0.993, accuracy=0.912, AUC=0.931, MAPE=8.7%, ablation=2.3x
- Bifurcation Cc=0.45, Sobol: alpha 38.2% + k1 22.1% = 60.3%