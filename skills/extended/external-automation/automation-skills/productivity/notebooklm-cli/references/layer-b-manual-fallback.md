# Manual Layer B Fallback — When NotebookLM Is Unreachable

## Trigger Condition

NotebookLM CLI connects to `notebooklm.google.com` via HTTPS. In network-constrained environments (firewall, GFW, no proxy), this connection fails with `httpx.ConnectTimeout` — even though `notebooklm doctor` may report "all checks passed" (auth tokens are valid locally, but the API endpoint itself is unreachable).

**Detection**:
```
curl --connect-timeout 10 -s -o /dev/null -w "%{http_code}" https://notebooklm.google.com
# Returns 000 → Google/NotebookLM blocked
# Returns 200+ → accessible, try again with fresh notebook
```

## When to Fall Back

| NotebookLM `doctor` output | Can connect? | Action |
|---------------------------|-------------|--------|
| Auth PASS, local cookies OK | Run `list` or `ask` — if it works, use normal flow | Normal Layer B |
| Auth PASS, but `list`/`ask` hangs/throws ConnectTimeout | Google API blocked | **Manual Fallback** |
| Auth FAIL (expired cookies) | Need `notebooklm login` first | Login or fall back |

## Manual Fallback Procedure

### 1. Extract Paper Text
```
pdftotext <paper-dir>/paper.pdf - > /tmp/paper-text.txt
wc -c /tmp/paper-text.txt   # Should be > 5KB for a meaningful review
```
If text layer is empty (0 bytes), try `paper.tex` from the 01-manuscript/ directory.

### 2. Check Paper Metadata
- Read `state.json` (quality_score, gate_status, D8/D10a scan)
- Check `paper-queue.json` for the paper's entry (notes, repair history)
- Read any existing quality reports in `07-quality/`

### 3. Evaluate Five Dimensions

#### D1: Originality/Importance (weight ~25%)
- Is the ABSOLUTE WHITE claim credible? Check PubMed/OpenAlex claims against actual timing
- Is there a clear clinical motivation (prevalence, market size, unmet need)?
- Does the paper propose a genuinely new formulation (first ODE/PINN for this system)?
- **Watch for**: Gap verified too long ago → needs re-verification at submission

#### D2: Methodological Rigor (weight ~30%)
- Are the governing equations fully specified (all parameters with values and units)?
- Is the PINN/ML architecture described in sufficient detail for replication?
- Are the **right evaluation metrics used**?
  - **Regression tasks** (predicting C(t), Z(t)): R², RMSE, MAE, MAPE — NOT Accuracy, AUC
  - Accuracy and AUC are **classification metrics** — if reported for a regression PINN, flag as P0 concern
- Are ablation studies present and meaningful (≥2x factor threshold realistic)?
- Are bifurcation / sensitivity analyses appropriate for dynamical systems?
- **Watch for**: Metrics uniform across drastically different clinical conditions (suggests a problem)
- **Watch for**: No numerical solver comparison (PINN vs RK45) — standard validation gap

#### D3: Credibility/Reproducibility (weight ~20%)
- Are all parameter values published in the paper (not just "available upon request")?
- Is there a code repository link (GitHub/GitLab)?
- Are random seeds specified for training?
- Are confidence intervals / error bars reported (across random seeds, not just single run)?
- **Watch for**: Point estimates only, no uncertainty quantification

#### D4: Literature Reference Quality (weight ~15%)
- Use D8/D10a scan data if available (from `state.json` or recent scan)
- Check: Are there orphans (cited but not in bibliography) or zombies (in bib but never cited)?
- Are the references appropriate for review papers vs. primary research vs. clinical context?
- **Note**: This dimension does NOT require NotebookLM — use existing scan infrastructure

#### D5: Writing/Logical Structure (weight ~10%)
- IMRaD? Abstract → Intro → Methods → Results → Discussion → Conclusion
- Limitations section present and honest?
- Argument flow logical (gap → formulation → method → results → implication)?

### 4. Weighted Scoring

| Dimension | Weight | Score 0-1 |
|:---------|:------:|:---------:|
| D1: Originality/Importance | 25% | |
| D2: Methodological Rigor | 30% | |
| D3: Credibility/Reproducibility | 20% | |
| D4: Literature Quality | 15% | |
| D5: Writing/Structure | 10% | |
| **Weighted Total** | 100% | **0.00** |

### 5. Thresholds (same as NotebookLM Layer B)

| Score | Verdict | Action |
|:----:|:--------|:-------|
| ≥0.85 | **T1 通过** | Pipeline continues; fix P0 items before submission |
| 0.75-0.84 | **T2 临界** | Return to author for revision; re-check after fixes |
| <0.75 | **不通过** | Blocked; structural revision required |

## Recurring Paper Quality Issues (Rule of Thumb Checks)

These patterns emerged from manual Layer B reviews and should be checked in every paper:

1. **Classification metrics on regression tasks** — Papers reporting "Accuracy" or "AUC" for PINN/ODE predictions (continuous C(t), Z(t) values). These metrics are undefined for continuous regression. Always flag as P0. Correct metrics: R², RMSE, MAE, MAPE.

2. **Uniform metrics across diverse conditions** — If R² values vary by <0.01 across conditions with drastically different parameters (α ranging 0.085-1.020, γ ranging 0.248-0.42), either:
   - The model is mathematically insensitive (needs explanation), or
   - There is a train/test leakage issue

3. **Missing numerical solver baseline** — PINN papers should compare against scipy RK45/odeint for forward ODE problems. Without this, PINN accuracy cannot be assessed independently.

4. **No error bars** — Single-run point estimates without confidence intervals across random seeds. Should be at minimum 5 seeds with mean±std.

5. **Code availability claims** — Verify that any Code/Data Availability statement actually exists and points to a real repository.

## Example: 182-accommodation-ciliary-muscle-ODE Findings

For reference, the first manual Layer B review (2026-06-21) found:
- Score: 0.86 (T1 PASS) — close to borderline despite state.json qs=96
- P0 issues: Accuracy/AUC used for regression (should be RMSE/MAE), no solver comparison
- P1 issues: R² varies only 0.004 across 4 clinical conditions (unexplained), no confidence intervals
- D10a=100% (13/13, 0 orphans/zombies) — excellent reference health after repair
- True ABSOLUTE WHITE gap — core contribution is genuine
