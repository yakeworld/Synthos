# Inline Bib Scan Blind Spot

**Date**: 2026-06-27
**Source**: unified-scan-2026-06-27 quality gate check

## Discovery

`unified-paper-scan.sh` only scans `*.bib` files via glob. Papers using inline `thebibliography` (no .bib file) are **completely invisible** to the scan.

**Impact**: 68+ pipeline papers skipped. These papers' references are never audited, G5 gate is never checked, and they receive false-positive PASS status.

## Quantified Impact

- **94 pipeline papers** have state.json
- **38** have external .bib files → scanned
- **68+** use inline thebibliography → **NOT scanned**
- **Scan coverage**: 25 unique papers (only ~27% of pipeline)

## 38 Papers with state.json AND inline bib (no .bib)

02-corneal-tension-ODE, 086-endolymph-perilymph-coupling-ode, 092-dissociated-ocular-torsion-PINN, 093-saccade-target-shift-PINN, 102-vestibular-efferent-PINN, 103-fixation-stability-PINN, 104-perilymph-fistula-ODE, 105-lacrimal-drainage-ODE, 109-vestibular-tremor-PINN, 110-tear-film-dynamics-ODE, 112-presbyopia-lens-stiffening-ODE, 114-auditory-vestibular-crosstalk-ODE, 121-blink-dynamics-ODE, 124-vitreous-humor-ODE, 137-ciliary-body-ODE, 142-meibomian-gland-secretion-ODE, 146-vitreous-cortex-structural-ODE, 147-lens-capsule-biomechanics-ODE, 148-corneal-epithelial-wound-healing-ODE, 150-scleral-remodeling-ODE, 151-ocular-torsion-dynamics-ODE, 152-intraocular-pressure-rhythm-ODE, 153-choroidal-blood-flow-ODE, 182-accommodation-ciliary-muscle-ODE, 187-scleral-remodeling-ODE, binaural-vestibular-PINN, bppv-nystagmus-pinn, cerebellar-VOR-adaptation-PINN, cochlear-vestibular-coupling-PINN, concussion-oculomotor-PINN, corneoscleral-shell-ODE, crispdm-heart, data-leakage-breast-cancer-critical-audit, gaze-stability-PINN, head-impulse-ODE, nystagmus-computational-ODE, ocular-blood-flow-ODE-paper-116, ocular-torsion-ODE, ocular-torsion-PINN, off-axis-iris-normalization-correction, optic-nerve-head-deformation-ODE, optokinetic-reflex-pinn, pan-PINN, Paper_100_fixation-vernier-PINN, Paper_101_optokinetic-reflex-PINN, paper-91-fixation-stability-PINN, paper-95-nystagmus-PINN, pupillary-light-reflex-ODE, retinal-neural-ODE, saccade-adaptation-pinn, saccade-burst-neuron-neuralode, saccade-kinematic-ODE, saccadic-velocity-storage-ODE, schlemm-canal-dynamics-ODE, stroke-prediction, tinnitus-pinn-ode, tonic-VOR-PINN, torsional-VOR-PINN, vergence-accommodation-coupling-PINN, vestibular-adaptation-ODE, vestibular-adaptation-PINN, vestibular-computation-PINN, vhit-pinn-ode, vor-pinn-ode-gap-analysis

## Why This Matters

This is not a "gap" — it's a **structural blind spot**. The scan script's glob `*.bib` means:
- Papers with no .bib file → 0 entries in scan results → zero suspicious → no red flags
- These papers appear "perfect" because nothing was checked
- Per quality-gate inline bibliography audit trap: "假阳性通过" (false positive pass)

## Fix Required

The scan script must implement the inline bibliography detection from quality-gate:
1. For each paper directory, check if `*.bib` exists
2. If NOT, check if `*.tex` contains `thebibliography`
3. If inline: extract `\cite{}` keys and `\bibitem{}` keys from tex
4. Compute D10a from cite↔bibitem match
5. Validate DOI on each cited entry

## Detection Pattern

```bash
for dir in /path/to/papers/*/; do
    if ! ls "$dir"*/**/*.bib >/dev/null 2>&1; then
        if grep -rl 'thebibliography' "$dir" --include='*.tex' >/dev/null 2>&1; then
            echo "INLINE_BIB_UNSCANNED: $dir"
        fi
    fi
done
```
