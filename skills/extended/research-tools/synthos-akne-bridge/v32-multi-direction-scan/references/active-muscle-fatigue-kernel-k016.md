# K-016 Active Muscle Contraction + Fatigue Kernel

**Established**: Domain Expansion #8 (cycle-173, 2026-06-22)
**Domain**: Chest Wall / Diaphragm Active Mechanics
**Candidate**: chest-wall-mechanics-PINN

## When to Apply This Template

Any future candidate involving **active muscle force generation** with **fatigue dynamics** should use K-016's architecture as the template. This includes: cardiac contractility, skeletal muscle fatigue, bladder detrusor mechanics, smooth muscle peristalsis, and any system where (a) an active contractile element generates force and (b) sustained force production leads to progressive performance decline.

## Core Architecture

### Two-ODE Structure

```
ODE-1: Passive Structural Mechanics — second-order R-C-I or mass-spring-damper
  State: displacement/volume/pressure
  Parameters: compliance/stiffness (C_cw/k), resistance/damping (R_cw/b), inertance/mass (I_cw/m)
  
ODE-2: Active Force Generation + Fatigue — force-length-velocity + fatigue accumulator
  State: force/pressure (P_di), fatigue level (F_di)
  Parameters: max contractile capacity (P_di_max), fatigue onset time constant (tau_fatigue),
              fatigue recovery time constant (tau_recovery), neuromechanical coupling gain (k_neural),
              optimal length (L_di_opt), fatigue threshold (theta)
```

### Parameter Multiplicative Confound Pattern

The defining mathematical challenge of muscle kernels is a **multiplicative confound** where multiple parameters all scale the same observable:

```
P_active(t) = P_max · F_L(L(t)) · F_V(V̇(t)) · (1 − F(t)) · k_neural
```

In this formulation, P_max, k_neural, L(t), and (1−F(t)) all multiply together — their individual contributions are indistinguishable from the temporal waveform alone.

### Mitigation Template

| Confound Pair | Anchor | Method | Cost |
|:-------------|:-------|:-------|:----:|
| Max capacity vs gain | External maximal-effort test | SNIP/MIP (respiratory), grip strength (skeletal), LVEF (cardiac) | $0 (standard clinical test) |
| Length vs capacity | Length measurement | Ultrasound (all striated muscle), plethysmography (respiratory/limb) | $50-200/study |
| Fatigue vs gain | Timescale separation | F=0 at t=0 → k_neural identified from first few contractions | $0 (built into protocol) |

**General rule**: For N-way multiplicative confound, (N−2) external anchors are needed. The remaining 2-parameter confound can be resolved by timescale separation if one parameter evolves slowly (fatigue) and the other is static (gain).

## Dual-Timescale Training Strategy

Muscle fatigue operates on a fundamentally slower timescale than the mechanical contraction. This introduces a **RED multi-scale** problem (300× to 12000× gap) that requires:

1. **Fast head** (breath-level/beat-level): Train on short segments (5-30s) to learn mechanical dynamics (P_max, k, stiffness)
2. **Slow head** (fatigue-level): Freeze fast parameters, train on long recordings (30-180 min) to learn fatigue dynamics (tau_fatigue, tau_recovery)
3. **Alternating training**: Interleave fast and slow loss terms with different temporal downsampling rates

## When K-016 Replaces / Extends Prior Patterns

- **Unlike K-003 (cupula, passive mechanical oscillator)**: K-016 adds active force generation — the system drives itself, rather than just responding to stimuli.
- **Unlike K-014 (vocal fold, Bernoulli coupling)**: K-016 adds fatigue — performance declines under sustained load. K-014 has no fatigue dimension.
- **Unlike K-012 (cerebral autoregulation, vascular resistance)**: K-016 has direct cross-bridge contractile mechanics rather than molecular signaling cascades.

## Future Muscle Candidates Expected to Use This Template

| Domain | ODE-1 Analog | ODE-2 Analog | Clinical Data | Expected Confound |
|:-------|:-------------|:-------------|:--------------|:-----------------|
| Cardiac contractility | Ventricular pressure-volume | Sarcomere length-tension + calcium dynamics | Echocardiography, catheterization | P_max × F_Ca × k_contractile |
| Skeletal muscle fatigue | Limb force-length-velocity | EMG-force + fatigue accumulation | Force transducer, sEMG, Ultrasound | P_max × F_di × k_neural × L |
| Bladder detrusor | Wall stress-strain | Smooth muscle contraction + fatigue | Cystometry, pressure-flow | P_det_max × F_det × k_det |
| Esophageal peristalsis | Bolus pressure-velocity | Smooth muscle wave + fatigue | High-resolution manometry | P_per_max × tau_fatigue_per |
| Uterine contraction | Intrauterine pressure-volume | Myometrial contraction + fatigue | Tocography, EMG | P_uter_max × k_uter × L |
