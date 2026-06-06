# Caloric Nystagmus — Computational Modeling Reference

## Domain Overview

Caloric nystagmus is induced by temperature-driven endolymph convection in the horizontal semicircular canal. It is one of the oldest and most widely used clinical vestibular tests (since Brandt 1882).

## Physical Mechanism

1. **Heat diffusion**: Irrigation (30°C cold or 44°C warm) heats/cools the temporal bone
2. **Endolymph convection**: Temperature gradient creates density-driven flow in horizontal canal
3. **Cupula deflection**: Convective flow bends the cupula, stimulating hair cells
4. **Nystagmus response**: Slow-phase nystagmus in the direction of endolymph flow

**Key property**: Warm irrigation → endolymph rises toward ampulla → ampullofugal flow → nystagmus with fast phase AWAY from irrigated ear. Cold irrigation → opposite.

## Classical ODE Model (Azzi 1964)

The classical model is a chain of 3 coupled linear ODEs:

**Equation 1 — Heat diffusion in canal wall:**
dT/dt = -α·(T - T_room) + β·I(t)

where T = canal wall temperature, α = heat transfer coefficient, β = irrigation strength, I(t) = irrigation input (step function).

**Equation 2 — Endolymph convection:**
dv/dt = γ·(T - T_ref) - δ·v

where v = endolymph velocity, γ = convection coefficient, δ = viscous damping, T_ref = reference temperature.

**Equation 3 — Cupula displacement:**
dx/dt = ε·v - ζ·x

where x = cupula displacement, ε = coupling coefficient, ζ = cupula stiffness.

## Clinical Interpretation

- **Canal paresis**: (max_SPV - min_SPV)/(max_SPV + min_SPV) × 100%
- **Directional preponderance**: (right - left)/(right + left) × 100%
- **Normal**: peak velocity 10-40°/s, decay τ 10-30s
- **VHI**: peak velocity 5-20°/s, decay τ 15-45s
- **Bifurcation**: τ < 12s → VHI likely; τ > 20s → healthy

## White Space Validation (v45)

- PubMed: 9 papers on caloric nystagmus with computational models — ALL classical (Azzi 1964, Oesterle 1996, MacIver 2014)
- 0 PINN/NeuralODE/physics-informed papers
- OpenAlex: 0 relevant PINN/ODE papers
- **Status**: CONFIRMED WHITE SPACE for PINN/ODE approach
- Reference: Paper 70 (caloric-nystagmus-ODE) gap analysis D1-D10a

## Reference Papers

- Azzi 1964 — Heat diffusion and endolymph convection model
- Oesterle 1996 — Caloric-induced VOR physiology
- MacIver 2014 — Caloric testing clinical guidelines
- Guedry 1993 — Caloric nystagmus clinical protocols
- Soto 2015 — Caloric nystagmus as VOR biomarker
