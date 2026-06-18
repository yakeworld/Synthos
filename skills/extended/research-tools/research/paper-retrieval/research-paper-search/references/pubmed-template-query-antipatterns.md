# PubMed Template Query Anti-Patterns — v22

## Problem

`scripts/pubmed_scan_template.py` `DEFAULT_QUERIES` use OR-heavy queries that produce massive false positives.

## v22 Evidence

| Query Template | PubMed Count | Relevant Hits |
|----------------|:------------:|---------------|
| 3D Eye Tracking (OR-heavy) | 88 | 0/3 |
| Kappa Angle ML | 261,272 | 0/3 |
| VOR Digital Twin | 15,468 | 0/3 |
| BPPV ML | 117,342 | 0/3 |
| PD Saccade ML | 1,379,528 | 0/3 |

## Fix

Replace ALL OR-heavy queries with AND-composed queries. Example:

```python
# WRONG — produces false positives
"Kappa Angle": '"angle kappa" OR "pupillary axis" OR "visual axis"',

# CORRECT — precise AND composition
"Kappa Angle": '("angle kappa" OR "pupillary axis" OR "visual axis") AND "machine learning"',
```

## General Rule

Every query must have at least one AND operator to narrow the search. OR-only queries match ANY keyword appearing anywhere in ANY context.
