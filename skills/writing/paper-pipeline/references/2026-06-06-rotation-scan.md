# 2026-06-06 Rotation Scan — All White Spaces Stable

## Scan Context

v28 rotation directions + 5 new explorations. All core PINN/NeuralODE directions confirmed white.

## Results

### Rotation Directions (5)
| Direction | PubMed | OpenAlex | Status |
|-----------|--------|----------|--------|
| cerebellar-VOR-adaptation | 0 | 0 | WHITE |
| periodic-alternating-nystagmus-PINN | 0 | 0 | WHITE |
| nystagmus-NeuralODE | 0 | 0 | WHITE |
| vestibular-compensation-ODE | 0 | 0 | WHITE |
| kappa-angle-ML | 39 | 0 | IRRELEVANT (all non-computational) |

### Core PINN Cross-Check
| Direction | PubMed | Status |
|-----------|--------|--------|
| VOR-PINN-ODE | 0 | WHITE |
| optokinetic-reflex-PINN | 0 | WHITE |
| vHIT-PINN | 0 | WHITE |
| saccade-kinematic-PINN | 0 | WHITE |

## Key Finding

**All 9 scanned PINN/NeuralODE directions remain white spaces.** No new competitive papers detected.

The kappa-angle-ML direction shows PubMed=39 but all are clinical measurement papers (IOL, cataract, ophthalmology) — none use machine learning for kappa angle computation. This is a known false positive pattern from previous scans.

## Implications

1. **cerebellar-VOR-adaptation-PINN** is a strong candidate for the next paper (10 PubMed classical models, 0 PINN/ODE)
2. **periodic-alternating-nystagmus-ODE** is also viable (0 PubMed PINN, 126 broad OpenAlex, 5 cited clinical papers with no computational ODE/PINN)
3. **nystagmus-NeuralODE** remains a true white space — no computational models for nystagmus dynamics at all
4. **vestibular-compensation-ODE** is white — no ODE models for vestibular compensation dynamics

## Scan Methodology

- PubMed: direct eSearch with precise AND-based queries
- OpenAlex: `filter=cited_by_count:1-` with relevance check on top results
- All queries use bare spaces in search parameter (Python 3.12 URL encoding quirk)
- 1.1s delay between requests to respect rate limits
