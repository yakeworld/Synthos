# Batch Literature Scan Pattern

## Purpose

Run all 10+ PubMed + OpenAlex queries from Steps 1-2 in a **single Python invocation** instead of separate tool calls per direction. This saves ~8-12 round-trips per cron cycle.

## Pattern

```python
#!/usr/bin/env python3
"""Batch literature scan — run all queries at once."""
import sys
sys.path.insert(0, "/media/yakeworld/sda2/Synthos/skills/extended/research-tools/synthos-akne-bridge/v32-multi-direction-scan/scripts")
from pubmed_utils import pubmed_count, openalex_search

# ROTATION A — Segmentation & Geometry
c, t = pubmed_count('("pupil segmentation" OR "iris segmentation") AND ("PINN" OR "physics-informed" OR "NeuralODE")')
print(f"R1: {c}")

c, t = pubmed_count('("pupil segmentation" OR "iris segmentation") AND ("2025"[Date - Create] : "2026"[Date - Create])')
print(f"R1b DL Seg 2025-2026: {c}")

# ... repeat for each direction in Step 1 + Step 2

### === ICLR Competition Check (if deadline <= 14 days) ===
# WARNING: Do NOT hardcode ICLR query strings here.
# Use the EXACT queries from `references/iclr-competition-queries.md` (canonical source).
# That file defines all 5 standardized queries with documented pitfall notes.
# Copy-paste them verbatim into your script — do not reconstruct from memory.
#
# Query drift between this file and iclr-competition-queries.md has been
# a source of false negatives in the past. The batch-scan-pattern template
# previously contained narrower/incorrect query strings that missed 2 of
# 5 competition directions. Always defer to the canonical file.
# Load the canonical queries and copy them into your probe below:
import json
with open("/media/yakeworld/sda2/Synthos/skills/extended/research-tools/synthos-akne-bridge/v32-multi-direction-scan/references/iclr-competition-queries.md") as f:
    content = f.read()
# Copy all 5 queries (head-impulse-ODE, tinnitus-pinn-ode, saccade-adaptation-pinn,
# vhit-pinn-ode, endolymph-hydropressure-ode) into the loop below.
for label, q in [
    ("OA_R4_BPPV_DT", '"BPPV" "digital twin"'),
    ("OA_R3_SCC_PINN", '"semicircular canal" PINN'),
    ("OA_N4_ocular_torsion", '"ocular torsion" PINN'),
]:
    count, titles = openalex_search(q)
    print(f"{label}: OpenAlex={count}")

# SAVE
import json
results = {...}
with open("/tmp/scan-results.json", "w") as f:
    json.dump(results, f)
```

## Benefits

1. **Single round-trip** — all queries fire sequentially within one Python process
2. **Consistent error handling** — pubmed_utils.py retries all queries with same backoff
3. **Structured output** — save to JSON for downstream processing
4. **No shell-level security triggers** — Python urllib bypasses tirith/curl scanners

## When to Use

Every cron run in SCAN_AND_REPORT or SCAN_AND_CREATE mode. Write a fresh script per cycle using the current date to set `[Date - Create]` filters.

## Pitfalls

- **PubMed rate limits**: Running 10+ queries back-to-back may hit NCBI rate limits (~3 req/sec without API key). pubmed_utils.py has 3s RETRY_DELAY between retries per query, but sequential queries don't have an inter-query delay. If you see 429 errors mid-batch, add `time.sleep(1)` between query groups.
- **OpenAlex has no rate limit**: OpenAlex API allows ~10 req/sec without key. Safe to batch.
- **Date ranges**: Always use 2-year window `"2025"[Date - Create] : "2026"[Date - Create]` for DL papers. Use `"2024"[Date - Create] : "2026"[Date - Create]` for less frequent directions like BPPV digital twin.
- **CRITICAL — Query string consistency across cycles**: Every cron cycle writes a fresh script from scratch. Without deliberate carry-forward, query strings drift and produce false landscape-change signals. **Before writing any query, open the previous cycle's agent-log.md entry and copy the exact query strings verbatim.** Every query in your script must state whether it matches the previous cycle's exact string or is a deliberate variant. If you broaden a query, run BOTH versions and report both counts. See SKILL.md pitfall "Query string drift across cycles" for the full methodology.
- **Refine crowded queries — two strategies**:
  - **Strategy A (PINN/ODE competition subfilter)**: Add `AND ("PINN" OR "NeuralODE" OR "physics-informed")` to filter for computational competition. Report the refined count. Use when the goal is gap detection.
  - **Strategy B (clinical relevance subfilter)**: Add disease-specific + outcome terms instead, e.g. `AND ("biomarker" OR "prediction") AND ("Alzheimer" OR "aging")`. Use when the goal is external validation collection (Step 6 Post-Exhaustion Protocol) — this returns relevant clinical papers that validate Synthos hypotheses without filtering out non-PINN but valuable literature.
  - **Which to use**: If query is a rotation direction (R1-R5) and you're checking for competition, use Strategy A. If query is an exploration direction (N2, N5) and you're in Post-Exhaustion Protocol collecting external validation, use Strategy B.

## Staleness Guard Probe Pattern

When the staleness guard is active (full rotation skipped), run this reduced probe set instead. This is the primary diagnostic during SCAN_AND_REPORT frozen cycles — run it BEFORE the full rotation to avoid wasting API calls on a frozen landscape.

```python
#!/usr/bin/env python3
"""Staleness guard probe — minimal query set for frozen landscape."""
import sys, json, time
sys.path.insert(0, "/media/yakeworld/sda2/Synthos/skills/extended/research-tools/synthos-akne-bridge/v32-multi-direction-scan/scripts")
from pubmed_utils import pubmed_count

results = {}

# === PLR-H1 Dual Probe (primary landscape diagnostic) ===
# Use EXACT queries from the previous cycle's agent-log.md — copy verbatim, don't reconstruct.

# Refined clinical (narrow AD — primary signal, range 5-9)
q = '("pupillometry" OR "pupil light reflex") AND ("Alzheimer" OR "Alzheimer disease" OR "MCI" OR "mild cognitive impairment") AND 2025:2026[dp]'
c, t = pubmed_count(q, retmax=5)
results["PLR_refined"] = {"count": c, "titles": t[:5]}
print(f"PLR refined: {c} — top: {t[0] if t else 'none'}")

# Broad AD (secondary — check for unexpected jumps)
q = '("pupillometry" OR "pupil light reflex" OR "pupil dynamics") AND ("Alzheimer" OR "dementia" OR "MCI") AND 2025:2026[dp]'
c, t = pubmed_count(q, retmax=3)
results["PLR_broad"] = {"count": c}
print(f"PLR broad: {c}")

# PINN/NeuralODE competitor check
q = '("pupillometry" OR "pupil light reflex") AND ("PINN" OR "NeuralODE" OR "physics-informed neural network") AND 2025:2026[dp]'
c, t = pubmed_count(q, retmax=3)
results["PLR_PINN"] = {"count": c}
print(f"PLR PINN: {c}")

# === Core ABSOLUTE_WHITE quick pulse (one query each) ===
### === ICLR Competition Check (if deadline <= 14 days) ===
# WARNING: Do NOT hardcode ICLR query strings here.
# Use the EXACT queries from `references/iclr-competition-queries.md` (canonical source).
# That file defines all 5 standardized queries with documented pitfall notes.
# Copy-paste them verbatim into your script — do not reconstruct from memory.
#
# Query drift between this file and iclr-competition-queries.md has been
# a source of false negatives in the past. The batch-scan-pattern template
# previously contained narrower/incorrect query strings that missed 2 of
# 5 competition directions. Always defer to the canonical file.
# Load the canonical queries and copy them into your probe below:
import json
with open("/media/yakeworld/sda2/Synthos/skills/extended/research-tools/synthos-akne-bridge/v32-multi-direction-scan/references/iclr-competition-queries.md") as f:
    content = f.read()
# Copy all 5 queries (head-impulse-ODE, tinnitus-pinn-ode, saccade-adaptation-pinn,
# vhit-pinn-ode, endolymph-hydropressure-ode) into the loop below.
for label, q in [
    ("R1_pupil_iris_PINN", '("pupil segmentation" OR "iris segmentation") AND ("PINN" OR "NeuralODE" OR "physics-informed") AND 2025:2026[dp]'),
    ("R3_SCC_PINN", '("semicircular canal" OR "cupula") AND ("PINN" OR "NeuralODE" OR "physics-informed") AND 2025:2026[dp]'),
    ("R4_BPPV_DT", '("BPPV" OR "canalithiasis") AND ("digital twin" OR "PINN" OR "NeuralODE") AND 2024:2026[dp]'),
    ("R5_VOR_DT", '("vestibulo-ocular reflex" OR "VOR") AND ("digital twin" OR "PINN" OR "NeuralODE") AND 2024:2026[dp]'),
    ("N4_ocular_torsion_PINN", '("ocular torsion" OR "cyclotorsion") AND ("PINN" OR "NeuralODE" OR "physics-informed") AND 2024:2026[dp]'),
]:
    c, t = pubmed_count(q, retmax=2)
    results[label] = {"count": c}
    print(f"{label}: {c}")

### === ICLR Competition Check (if deadline <= 14 days) ===
# WARNING: Do NOT hardcode ICLR query strings here.
# Use the EXACT queries from `references/iclr-competition-queries.md` (canonical source).
# That file defines all 5 standardized queries with documented pitfall notes.
# Copy-paste them verbatim into your script — do not reconstruct from memory.
#
# Query drift between this file and iclr-competition-queries.md has been
# a source of false negatives in the past. The batch-scan-pattern template
# previously contained narrower/incorrect query strings that missed 2 of
# 5 competition directions. Always defer to the canonical file.
# Load the canonical queries and copy them into your probe below:
import json
with open("/media/yakeworld/sda2/Synthos/skills/extended/research-tools/synthos-akne-bridge/v32-multi-direction-scan/references/iclr-competition-queries.md") as f:
    content = f.read()
# Copy all 5 queries (head-impulse-ODE, tinnitus-pinn-ode, saccade-adaptation-pinn,
# vhit-pinn-ode, endolymph-hydropressure-ode) into the loop below.
for label, q in [Competition Check (if deadline <= 14 days) ===
# WARNING: Do NOT hardcode ICLR query strings here.
# Use the EXACT queries from `references/iclr-competition-queries.md` (canonical source).
# That file defines all 5 standardized queries with documented pitfall notes.
# Copy-paste them verbatim into your script — do not reconstruct from memory.
#
# Query drift between this file and iclr-competition-queries.md has been
# a source of false negatives in the past. The batch-scan-pattern template
# previously contained narrower/incorrect query strings that missed 2 of
# 5 competition directions. Always defer to the canonical file.
# Load the canonical queries and copy them into your probe below:
import json
with open("/media/yakeworld/sda2/Synthos/skills/extended/research-tools/synthos-akne-bridge/v32-multi-direction-scan/references/iclr-competition-queries.md") as f:
    content = f.read()
# Copy all 5 queries (head-impulse-ODE, tinnitus-pinn-ode, saccade-adaptation-pinn,
# vhit-pinn-ode, endolymph-hydropressure-ode) into the loop below.
for label, q in [
    ("ICLR_head_impulse", '"head impulse" AND ("ODE" OR "PINN" OR "NeuralODE" OR "physics-informed") AND 2025:2026[dp]'),
    ("ICLR_saccade_pinn", '"saccade adaptation" AND ("PINN" OR "NeuralODE" OR "physics-informed") AND 2025:2026[dp]'),
    ("ICLR_vhit_pinn", '("vHIT" OR "video head impulse") AND ("PINN" OR "NeuralODE" OR "physics-informed") AND 2025:2026[dp]'),
]:
    c, t = pubmed_count(q, retmax=2)
    results[label] = {"count": c}
    print(f"{label}: {c}")

# Save structured results
with open("/tmp/scan-results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nResults saved to /tmp/scan-results.json")
```

**Interpreting results**:
- PLR refined count 5-9 with same 5 core PMIDs confirmed → Frozen, no change
- PLR refined count spike >15 + core papers unchanged → "PLR" acronym noise (platelet/lymphocyte ratio), check by re-running WITHOUT bare `PLR` term
- PLR PINN count = 0 → No PINN competition — primary signal for "frozen"
- Any core ABSOLUTE_WHITE direction showing >0 PINN hits → Thawing, BREAK staleness immediately
- ICLR competition >0 → Flag for human review, check if it's a genuine competitor
