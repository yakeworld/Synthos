# ICLR Competition Queries — Standardized PubMed Searches

> Canonical query strings for the 5 ICLR submission paper domains.
> Use these verbatim to prevent query drift across cycles.
> Created: 2026-06-24 (Cycle 225 — drift detected in tinnitus query)
> Updated: 2026-06-25 (Cycle 248 — added bare ODE drift trap for head-impulse-ODE query)

## Usage

Each cron cycle, copy the exact `pubmed_count()` call below into your probe script.
Do NOT broaden terms without documenting the variant — if you run a broader query,
also run the standardized one and report both counts.

## 1. head-impulse-ODE

```python
q = '("head impulse" OR "vestibulo-ocular reflex" OR "VOR" OR "gaze stability") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

**⚠️ Drift trap (Cycle 248, 2026-06-25)**: Do NOT use bare `ODE` or broad `"physics-informed"` (without `neural` qualifier) in this query. In C248, the broadened query `("head impulse" OR "head-impulse" OR "HIT" OR vHIT) AND ("ODE" OR "ordinary differential" OR "physics-informed")` returned **5 false positives** — all general PINN papers (MR fingerprinting, carbon prediction, wastewater optimization, deposition quality, dynamic prediction) with zero vHIT/head-impulse content. The domain terms `"head impulse"` + broad `ODE`/`"physics-informed"` match papers that mention both terms in completely unrelated contexts.

**Fix**: Use only the PINN/NeuralODE subfilter as shown in the standardized query. If you need to broaden, run this standardized query FIRST, then a separate exploratory query with bare `ODE` or `"computational model"`, and report both counts with labels. The standardized query is safe — it returns 0 hits consistently (68+ cycles as of C248).

**Rationale**: Narrow PINN/NeuralODE subfilter. Avoids broad "computational model" or "ODE" terms that match non-competitor physiological modeling papers. Domain terms: head impulse test, vestibulo-ocular reflex (full name + acronym), gaze stability (clinical synonym).

## 2. tinnitus-pinn-ode

```python
q = '("tinnitus") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

**⚠️ Drift trap**: DO NOT include `"auditory"`, `"cochlear"`, or `"computational model"` in this query. The term `"auditory"` alone returns 180+ false positives (general auditory periphery models, efferent gain control, rodent auditory models — all non-PINN, non-tinnitus papers). Keep the query strictly to `"tinnitus" AND PINN` terms. If you want to broaden, run this standardized query FIRST, then a separate exploratory query, and report both.

## 3. saccade-adaptation-pinn

```python
q = '("saccade" OR "saccadic adaptation") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

**Rationale**: Narrow PINN/NeuralODE subfilter. Saccade adaptation is a niche domain — broad "computational model" terms are unnecessary and add noise.

## 4. vhit-pinn-ode

```python
q = '("VHIT" OR "video head impulse") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

**⚠️ Drift trap (Cycle 245, 2026-06-24)**: Do NOT add `"deep learning"` to this query. The term alone returns 1 false positive (PMID 39422423 — `Toward Intelligent Head Impulse Test: A Goggle-Free Approach Using a Monocular Infrared Camera`), a DL/ML paper with zero PINN/NeuralODE content. This query is PINN-only by design. If you want to explore deep learning competition in vHIT, add a separate exploratory query (e.g., `("VHIT" OR "video head impulse") AND ("deep learning" OR "neural network")`) and report both counts side by side. DO NOT merge the terms into the standardized query — the next cycle will inherit the drift.

**Known false positives**: The "Computing Endolymph Hydrodynamics During Head Impulse Test" paper matches `"head impulse"` via the VOR query (not this one). This query is narrow enough to avoid that CFD paper. If a hit appears, verify it's PINN/NeuralODE — CFD papers are not competitors.

## 5. endolymph-hydropressure-ode

```python
q = '("endolymph" OR "endolymphatic hydrops" OR "Meniere") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

**🔴 CRITICAL — Never use bare `ODE` in this query**: The token `ODE` in PubMed All Fields matches "Optic Disc Edema" (ophthalmology MeSH term), not "ordinary differential equations". In Cycle 243, the broadened query `(endolymph OR hydrops) AND (ODE OR "ordinary differential" OR PINN)` returned **20 false positives** — ALL optic disc edema / papilledema papers. The standardized PINN-only query correctly returned 0.

**Mechanism**: `ODE` in All Fields retrieves papers indexed under the MeSH term "Optic Disc Edema". When combined with "hydrops" (corneal hydrops — also ophthalmology) and "endolymph" (endolymphatic hydrops via Meniere's), the query scope overlaps entirely with ophthalmology MeSH space.

**Fix**: Always use PINN-only subfilter. Never add bare `ODE` to this query. If you need a broader term, use `"ordinary differential"` (quoted phrase) or `ODE[Title/Abstract]` (field-restricted) — but prefer the PINN-only subfilter.

**Known CFD false positives**: Separately, this domain has 2 known CFD papers (endolymph hydrodynamics during HIT, BPPV Yacovino maneuver optimization) that match if you broaden to `"computational fluid dynamics"` or `"CFD"`. The standardized PINN-only query correctly avoids both. If you add CFD terms, annotate hits as NON_PINN.

## Consolidated Probe Template

For the ICLR competition check portion of the probe script:

```python
def run_iclr_competition():
    queries = {
        "head-impulse-ODE": '("head impulse" OR "vestibulo-ocular reflex" OR "VOR" OR "gaze stability") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]',
        "tinnitus-pinn-ode": '("tinnitus") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]',
        "saccade-adaptation-pinn": '("saccade" OR "saccadic adaptation") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]',
        "vhit-pinn-ode": '("VHIT" OR "video head impulse") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]',
        "endolymph-hydropressure-ode": '("endolymph" OR "endolymphatic hydrops" OR "Meniere") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]',
    }
    for name, q in queries.items():
        count, titles = pubmed_count(q, retmax=3)
        print(f"{name}: {count}")
        for t in titles: print(f"  - {t}")
```

## Version History

| Version | Date | Change |
|:--------|:-----|:-------|
| 1.3.0 | 2026-06-25 | Added ⚠️ Drift trap for head-impulse-ODE query (Cycle 248): bare `ODE` + broad `"physics-informed"` matched 5 general PINN papers (MR fingerprinting, wastewater, carbon prediction) with zero vHIT content. Agents must use PINN/NeuralODE-only subfilter. |
| 1.2.0 | 2026-06-24 | Added ⚠️ Drift trap for vhit query (Cycle 245): adding "deep learning" produces 1 false positive DL paper. Warn agents not to merge broad DL terms into the PINN-only standardized query. |
| 1.1.0 | 2026-06-24 | Added 🔴 CRITICAL warning for endolymph query: bare `ODE` matches "Optic Disc Edema" (20 false positives in Cycle 243). Split "Known false positives" into ODE-collision and CFD-staleness sections. |
| 1.0.0 | 2026-06-24 | Created from Cycle 225 drift correction. Standardized all 5 ICLR queries with pitfall notes. |
