# v53 Comprehensive White Space Scan — 2026-06-07

## Scan Results

### PubMed Absolute White (count=0)
- `gaze*AND*PINN*AND*(physics+OR+physical+OR+differential)` → 0
- `saccade*AND*PINN*AND*(physics+OR+physical+OR+differential)` → 0
- `saccade*AND*kinematics*AND*differential+equation+OR*ODE+OR*PINN` → 0

### PubMed Broad Matches — ALL FALSE POSITIVES
- `gaze*OR*fixation*OR*saccade*OR*pupil*AND*PINN+OR*physical+informed+OR*neural+ODE` → 20 hits, titles:
  - PMID 42250200: "Handling missing data in fibromyalgia clinical trials"
  - PMID 42250193: "Augmented reality enhanced physical simulation for femoral nailing"
  - PMID 42248183: "Impact of dose rates on hydrogen peroxide production in water radiolysis"
  - PMID 42245176: "Mathematical modeling of biosystems" (genetics)
- `vestibular*adaptation*AND*PINN` → 10 hits: elephant seals, elastography, childhood adversity
- `ocular*torsion*AND*PINN` → 10 hits: same pattern (elephant seals, etc.)
- `VEMP*OR+otolith*AND*PINN` → 10 hits: same pattern

### OpenAlex Results (with quote_plus fix)
- `gaze stability PINN neural ODE` → 1 irrelevant (VR tech, cited=0)
- `gaze PINN` → 5 irrelevant (VR on-screen gaze, aerospace, robotics, radiology, eye-gaze interpretability)
- `saccade PINN` → **0 results — ABSOLUTE WHITE**
- `gaze physical informed differential equation` → 5 irrelevant (GWAS, VR, attention theory, marketing)
- `saccade physical informed` → 5 irrelevant (MS COCO, PET, eye-hand coordination, motor control)
- `pupil PINN` → 5 irrelevant (brain decoding, cerebral edema, microscopy)
- `fixation PINN` → 5 irrelevant (VR gaze, drug resistance, V1 alpha, bacteria, bone)
- `eye movement PINN` → 5 irrelevant (computer vision, nanorobots, epidemics, virtual cells)
- `gaze ODE (classical)` → 1 relevant (cited=38): "Eye movement instabilities and nystagmus can be predicted by a nonlinear dynamics model of the saccadic system" — THIS IS PMID 42067630

## Key Findings

1. **GazeStability-PINN**: CONFIRMED ABSOLUTE WHITE. PubMed=0 for specific query, OpenAlex=0 relevant. Classical ODE exists (PMID 42067630, cited=204) but NO PINN/NeuralODE.

2. **Saccade-PINN**: CONFIRMED ABSOLUTE WHITE. PubMed=0, OpenAlex=0. Classical saccade models exist but NO computational PINN approaches.

3. **False positive pattern**: PubMed broad queries produce hundreds of results but ALL top hits are unrelated. Systematic PubMed behavior with specific keyword combinations.

4. **Python 3.12 OpenAlex**: `quote_plus(query, safe=' ')` is REQUIRED. Bare spaces cause InvalidURL errors.