# OpenAlex count=-1 semantics (v195, 2026-06-11)

## Problem
OpenAlex API sometimes returns `count=-1` instead of `count=0` or `count=N`. This doesn't mean "one result" — it means the count field is **not provided**. The `results` array is the actual data source.

## Pattern Observed
All 14 extended candidates for Papers 161+ returned:
- `count: -1`
- 3 results in `results` array
- All results are keyword-matching noise (not ODE computational dynamics papers)

Examples of keyword-noise:
- "hemodynamic stress" in retinal context → actual paper about aortic remodeling, not retinal
- "axonal" in optic nerve context → actual paper about white matter scaling
- "pupil dilation" → actual paper about cognitive effort/psychology
- "corneal" → actual paper is a cross-linking review

## ABSOLUTE_WHITE Determination
| count | results | ODE-relevant? | Status |
|-------|---------|---------------|--------|
| 0 | any | N/A | ABSOLUTE_WHITE |
| -1 | empty | N/A | ABSOLUTE_WHITE |
| -1 | keyword-noise only | no | ABSOLUTE_WHITE |
| -1 | contains ODE papers | yes | NOT ABSOLUTE_WHITE |
| N>0 | contains ODE papers | yes | NOT ABSOLUTE_WHITE |

## Noise Identification Checklist
A result is **not** ODE competition if:
1. It's a review, survey, or clinical features paper
2. It's an MRI/EEG/biometric study
3. It mentions "deep learning", "machine learning", "neural network"
4. No mention of "differential equation", "ODE", "ordinary differential", "computational model", or "mathematical model" in a dynamics context
5. The paper is about clinical guidelines, not computational dynamics

## Refined Query Approach
Use domain-specific ODE queries to filter noise:
- `+differential+equation` → filters to papers with "differential equation"
- `+mathematical+model` → filters to papers with "mathematical model"
- `+computational+model` → filters to papers with "computational model"
- `+ordinary+` → filters for "ordinary differential equations"

Generic queries (e.g., `retinal+blood+flow`) return broad keyword matches.
Refined queries (e.g., `retinal+blood+flow+differential+equation`) return noise-free results.

When count=-1 with refined queries shows no results = strong ABSOLUTE_WHITE signal.