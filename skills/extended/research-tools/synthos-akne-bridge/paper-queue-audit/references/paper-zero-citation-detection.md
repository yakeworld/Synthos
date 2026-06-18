# Paper Zero-Citation Trap — Pipeline Anomaly Detection

> Cron audit pattern: papers with thebibliography/bib entries but zero \cite{} in body text.
> First detected: 2026-06-13, Paper 189 (VEMP-PINN).

## Detection in Queue Audit

When running paper-queue-audit scan, flag papers where:

1. state.json has current_step at or past compile
2. Paper has thebibliography or references.bib entries > 0
3. grep -c cite paper.tex returns 0
4. quality_score < 80 (consistent with D10a=0%)

## Typical Signature

| Field | Value |
|-------|-------|
| current_step | publication / compile / g1g7_gate_check |
| quality_score | 0-55 (very low) |
| gate_status | CONDITIONAL |
| D10a | 0% |
| D8 | 10-20 (exists but not cited) |
| state | publication but never compiled |

## Queue-Wide Impact

From Paper 189 audit: 95 papers in queue, 76 with quality_score < 80.
Hypothesis: A significant fraction of these have the zero-citation trap.
Action: Run zero-citation detection on all low-score papers.

## Fix Priority

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 | Paper at compile/publication, D10a=0% | Add citations, recompile, re-QC |
| P1 | Paper at early stage, no citations yet | Fix during content generation |
| P2 | Paper already QC-passed | Likely fine (D10a checked during QC) |