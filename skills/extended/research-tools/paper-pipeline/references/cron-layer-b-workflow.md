# Cron-Based Manual Layer B Review Workflow

> Headless cron workflow for SCI-quality Layer B assessment when NotebookLM auth has expired.
> Created: 2026-06-24 (Cycle B-2, vhit-pinn-ode review)
> Applies to: paper-layer-b-review cron job

## Trigger Condition

NotebookLM browser profiles expire after ~7-14 days. In a headless cron job:

```bash
notebooklm list 2>&1 | grep -q "Not authenticated"
# -> auth is dead, fall back to manual
```

**Detection matrix**:

| `notebooklm list` | `curl` to Google | Diagnosis | Action |
|:-----------------|:-----------------|:----------|:-------|
| Success | 302 | Full access | Use normal flow |
| "Not authenticated" | 302 | Auth expired, service reachable | **Manual Fallback** |
| Timeout/error | 000 | Network blocked | **Manual Fallback** |

## Priority Selection

When multiple papers need Layer B, prioritize by:
1. **ICLR submission deadline** -> papers closest to deadline first
2. **Pipeline qs** -> higher qs papers (more likely to be submitted soon)
3. **Existing review status** -> papers with only gap-verification (step_layer_b.md) but no 07-quality/layer-b-report.md

## Workflow Steps

### Step 1: Check Existing Reviews

```bash
# Check if paper already has a comprehensive Layer B
ls paper-dir/07-quality/layer-b-report.md 2>/dev/null && echo "HAS_LAYER_B"
ls paper-dir/01-manuscript/step_layer_b.md 2>/dev/null && echo "HAS_GAP_LAYER_B"
```

Papers with only gap-verification (step_layer_b.md from G2/G6 gate) need the full SCI-quality review.

### Step 2: Read Paper Content

- For LaTeX papers (preferred — preserves structure, equations, tables): `read_file paper-dir/01-manuscript/paper.tex`
- For PDF-only papers: `pdftotext paper-dir/paper.pdf - > /tmp/paper-text.txt`

Prefer paper.tex when available — PDF text extraction loses LaTeX math, table structures, and may introduce encoding artifacts.

### Step 3: Check Paper Metadata

- `read_file paper-dir/state.json` — quality_score, gate_status, D8/D10a scan, notes
- `read_file paper-dir/07-quality/quality-report.md` — existing quality gate reports

Cross-reference pipeline qs (paper-queue.json) vs state.json qs — look for discrepancies suggesting auto-gate false positives.

### Step 4: Manual 5-Dimension Scoring

Score each dimension 0-1, then compute weighted total:

| Dimension | Weight | Evaluation Criteria |
|:----------|:------:|:-------------------|
| D1: Originality/Importance | 25% | ABSOLUTE WHITE claim credible? Clear clinical motivation? Genuinely new formulation? Watch for: Gap verified long ago -> needs re-verification. |
| D2: Methodological Rigor | 30% | Governing equations fully specified (parameters + values + units)? PINN/ML architecture replicable? Right evaluation metrics for task type? Ablation studies meaningful? Bifurcation/sensitivity analyses for dynamical systems? Watch for: Classification metrics on regression tasks (AUC on ODE predictions). Uniform metrics across drastically different conditions. No numerical solver baseline (PINN vs RK45). |
| D3: Credibility/Reproducibility | 20% | Parameter values published in paper? Code repository link (verified)? Random seeds specified? Confidence intervals across seeds (not single-run point estimates)? Watch for: Claimed repo but no code artifacts in paper directory. |
| D4: Literature Quality | 15% | D8/D10a scan data (verify inline vs .bib). Orphans (cited but not in bib) and zombies (bib but never cited). Appropriate references for paper type. Watch for: D10a=0% false negative when paper uses inline thebibliography — scan script may be .bib-only. |
| D5: Writing/Logical Structure | 10% | IMRaD structure? Limitations section present and honest? Argument flow logical (gap -> formulation -> method -> results -> implication)? |

**Weighted formula**: `total = D1*0.25 + D2*0.30 + D3*0.20 + D4*0.15 + D5*0.10`

### Step 5: Apply Thresholds

| Score | Verdict | Action |
|:-----:|:--------|:-------|
| >=0.85 | **T1 PASS** | Pipeline continues; fix P0 items before submission |
| 0.75-0.84 | **T2 PASS** (borderline) | Return to author for revision; re-check after fixes |
| <0.75 | **FAIL** | Blocked; structural revision required |

### Step 6: G7 Cross-Check (Mandatory)

After scoring, cross-check against existing quality reviews:

1. Read `07-quality/step_quality_review.md` (if exists) — compare G7 score vs Layer B score
2. Read `paper-queue.json` entry — check if "auto-gate fix" or "auto_gate_fix" appears in notes
3. If G7 review found SOFT_FAILs but queue says "auto-gate -> PASS" AND issues aren't resolved -> **flag as auto-gate false positive**
4. Compute Delta = (pipeline qs * 100) - (Layer B score * 100). Delta >= 10 -> auto-gate inflation suspected.
5. Document discrepancy in the Layer B report

**Real case (2026-06-22)**: head-impulse-ODE had G7 review ~54/100 with 4 SOFT_FAILs. Queue showed "auto-gate fix -> PASS, qs 65->85." Layer B found 0.57 — zero underlying issues were fixed.

### Step 7: Create Layer B Report

Write to `paper-dir/07-quality/layer-b-report.md`. Include:
- Header with timestamp and mode (NotebookLM vs Manual Fallback)
- 5-dimension table with scores and key findings
- Weighted total score and verdict
- G7 cross-check results (Delta computation)
- P0 issues (must fix) and P1 issues (should fix)
- ICLR readiness table (if applicable)

### Step 8: Update state.json

Add a note to `publication_notes`:

```json
"layer_b_YYYY-MM-DD": "Cycle X comprehensive SCI-quality Layer B review: weighted score=0.XX (T2 PASS). Key findings: ..."
```

**PITFALL: Use write_file for state.json, not patch**
The patch tool's fuzzy matching can corrupt JSON when inserting new key-value pairs — it may insert literal escaped newline sequences instead of actual line breaks. This corrupts the JSON and forces a full rewrite. Always use write_file for the complete state.json when adding a new entry to a nested JSON object with multiple existing entries. The small overhead of rewriting the whole file is trivial; repairing corrupted JSON from patch is not.

For simple single-line edits at the top level of a flat file, patch is fine. For complex nested JSON objects (like publication_notes with multiple existing entries), use write_file with the complete corrected object.

### Step 9: Append to agent-log.md

Use **patch**, not write_file (append-only protocol):

```python
# Read last few lines
read_file("agent-log.md", offset=-5)
# Append after last line
patch(path="agent-log.md",
      old_string="<last line of existing content>",
      new_string="<last line>\n\n## Cycle B-N | TIMESTAMP\n...")
```

**CRITICAL**: agent-log.md is maintained by multiple cron jobs (autonomous-core-researcher, paper-repair, paper-layer-b-review, literature-monitor). NEVER use write_file on it.

## Recurring Issues Checklist

Check these in EVERY paper:

1. **Classification metrics on regression tasks** — AUC/Accuracy reported for ODE/PINN predictions (continuous C(t), Z(t) values). Correct metrics: R2, RMSE, MAE, MAPE. Note exception: when AUC is computed on a downstream classifier (SVM on inferred parameters) it IS valid — distinguish carefully.

2. **Uniform metrics across diverse conditions** — If R2 varies by <0.03 across conditions with drastically different parameters, either the model is mathematically insensitive or there's leakage.

3. **Missing numerical solver baseline** — PINN papers MUST compare against scipy RK45/odeint for forward ODE. Without this, PINN accuracy cannot be independently assessed.

4. **No error bars** — Single-run point estimates without confidence intervals across random seeds. Minimum 5 seeds with mean+std.

5. **Code availability claims** — Verify that any Code/Data Availability statement points to a real repository with actual artifacts.

6. **"Bifurcation" claims without eigenvalue analysis** — Dynamical systems claiming bifurcation must provide eigenvalue analysis, bifurcation diagram, or mathematical derivation. Loose use of "bifurcation" to mean "clinical threshold" is a writing flaw.

7. **Synthetic-only validation** — Papers trained only on simulated data with "pending IRB" clinical data are not ready for competitive submission. AUC/accuracy drops from simulated to clinical should be reported and explained.

## Files Created/Updated Per Cycle

| Artifact | Path | Purpose |
|:---------|:-----|:--------|
| Layer B report | paper-dir/07-quality/layer-b-report.md | Comprehensive SCI-quality assessment |
| state.json update | paper-dir/state.json | Add layer_b note to publication_notes |
| agent-log.md | outputs/papers/agent-log.md | Append Cycle B-N entry |
