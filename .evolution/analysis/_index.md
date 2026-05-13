# analysis/ — Evolution Analysis Artifacts

Stores analysis outputs from the evolution engine: quality reports, trend data,
benchmark results, absorption evaluations, and any derived analytics.

## Purpose

- Keep analysis artifacts separate from active state
- Enable historical trend analysis across cycles
- Store detailed evaluation reports too large for state.json
- Host visualization data and computed metrics

## Suggested Contents

- `trends/` — Score trends over time (structural, benchmark, overall)
- `reports/` — Per-cycle analysis reports
- `absorb/` — Absorption evaluation details
- `diagnose/` — DIAGNOSE phase outputs
