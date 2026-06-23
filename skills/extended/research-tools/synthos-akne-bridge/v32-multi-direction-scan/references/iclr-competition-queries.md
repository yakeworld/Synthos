# ICLR Competition Queries — Standardized PubMed Searches

> Canonical query strings for the 5 ICLR submission paper domains.
> Use these verbatim to prevent query drift across cycles.
> Created: 2026-06-24 (Cycle 225 — drift detected in tinnitus query)

## Usage

Each cron cycle, copy the exact `pubmed_count()` call below into your probe script.
Do NOT broaden terms without documenting the variant — if you run a broader query,
also run the standardized one and report both counts.

## 1. head-impulse-ODE

```python
q = '("head impulse" OR "vestibulo-ocular reflex" OR "VOR" OR "gaze stability") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

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

**Known false positives**: The "Computing Endolymph Hydrodynamics During Head Impulse Test" paper matches `"head impulse"` via the VOR query (not this one). This query is narrow enough to avoid that CFD paper. If a hit appears, verify it's PINN/NeuralODE — CFD papers are not competitors.

## 5. endolymph-hydropressure-ode

```python
q = '("endolymph" OR "endolymphatic hydrops" OR "Meniere") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]'
```

**Known false positives**: This domain has 2 known CFD papers (endolymph hydrodynamics during HIT, BPPV Yacovino maneuver optimization) that match if you broaden to `"computational fluid dynamics"` or `"CFD"`. The standardized PINN-only query correctly returns 0. If you add CFD terms, annotate hits as NON_PINN.

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
| 1.0.0 | 2026-06-24 | Created from Cycle 225 drift correction. Standardized all 5 ICLR queries with pitfall notes. |
