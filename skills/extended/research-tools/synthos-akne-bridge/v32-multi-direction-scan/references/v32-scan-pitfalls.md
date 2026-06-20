# v32 Scan Pitfalls & Lessons

## Pitfall: completed_papers_count drift

**Problem:** The `completed_papers_count` in agent-tracker.json can drift from the actual `completed_papers` list length. Each scan cycle that updates the tracker needs to verify this match.

**Fix:** After any tracker mutation, verify `len(completed_papers) == completed_papers_count`. If mismatch, set count = len(list).

## Pitfall: new_directions accumulator not cleaned

**Problem:** `new_directions` accumulates entries for papers that have been completed. Completed entries (status containing "COMPLETE") should be either: (a) removed from new_directions, or (b) marked as complete but not acted upon. Leaving them creates false positives for "pending" candidates.

**Fix:** Before every scan, filter new_directions to remove entries where status contains "COMPLETE" (or explicitly move them to a `completed_directions` key).

## Pitfall: OpenAlex cited_filter false positives

**Problem:** OpenAlex broad searches can return very high counts (500+) for niche topics due to irrelevant matches. Top-3 titles must always be checked for relevance before declaring a space white.

**Example:** `saccade-kinematic-ODE` has OpenAlex count=506 but all top-3 are free-energy formulation papers (general physics/philosophy), not computational saccade models.

**Fix:** Always inspect top-3 titles from OpenAlex. If they match a "broad keyword but irrelevant domain" pattern, the actual count is effectively 0.

## Pitfall: PubMed broad expansion masks true count

**Problem:** PubMed auto-expands queries (AND/OR semantics). Queries like `saccade AND "physics-informed neural"` may return 0, but a broader `saccade PINN` query can return thousands of irrelevant results.

**Fix:** Use precise AND-clause queries for PINN/ODE directions. If count > 1000, immediately check top-3 titles.

## Pitfall: Classical ODE ≠ PINN competition

**Problem:** A classical ODE paper does NOT eliminate a PINN white space. Per trap7, classical computational models and PINN/NeuralODE approaches are distinct. Only direct PINN/ODE/PINN competition eliminates the space.

**Example:** PMID 42067630 (Scientific Reports 2026) is a damped harmonic oscillator for gaze stability — classical ODE. But gaze-stability-PINN is still white because no PINN paper exists.

## Pitfall: Meniere/clinical papers masquerading as computational

**Problem:** A clinical paper on Meniere's disease (e.g., "Meniere disease AND machine learning" = 41 hits) may be clinical diagnosis AI, not computational ODE/PINN. The clinical domain is crowded but the computational modeling space remains white.

**Fix:** Check if the ML papers are clinical classification/diagnosis (NOT computational ODE/PINN). If clinical, the computational space is still white for ODE/PINN approaches.

## Pitfall: VCR abbreviation collision & domain name ambiguity (v133, 2026-06-21)

**Problem:** "VCR" is heavily abbreviation-ambiguous. PubMed queries with bare "VCR" match viral clearance rate (CAR T-cell therapy), voluntary control ratio (psychophysics), and vaccine coverage rate (epidemiology). Query "VCR" AND "vestibular" returns animal studies (mouse VOG, chinchilla VCR). The VCR goes by at least 4 names: "vestibular collic reflex", "ocular counter-roll", "torsional VOR", "otolith-ocular reflex".

**Fix:** Never use bare "VCR" — always use full terms. Scan ALL 4 names for completeness. Narrow PINN queries on all 4 return 0 hits consistently. The VCR clinical literature (>500 hits) is all diagnostic/animal — zero PINN/ODE computational models, mirroring the cupula pattern.

**Animal model dominance pattern**: Broad queries on any VCR-related term return mostly animal studies (mouse VOG, chinchilla VCR) or clinical diagnostic studies. This is a genuine avoidance signal — the host species of most VCR literature is non-human. The computational VCR modeling space remains white because no PINN/ODE formulation exists for ANY species.

## Pitfall: Parent research-queue.json "completed marked as in_progress" variant (v133, 2026-06-21)

**Problem:** A new staleness variant was discovered where `outputs/papers/research-queue.json` shows a candidate as `status: in_progress` with fewer `steps_completed` than the candidate's own `_knowledge_only/<id>/state.json`, which shows `status: completed` with all 4 steps listed. This is the INVERSE of the previously documented variant (where the candidate's own state lags behind the parent queue).

**Diagnosis:** The prior cron run completed the pipeline step (wrote output file, updated candidate's own state.json, updated evolution-state.json) but skipped the parent queue sync.

**Detection:** Before trusting `outputs/papers/research-queue.json`'s `next_candidate` and `next_step`:
1. Read the candidate's own `_knowledge_only/<id>/state.json`
2. Compare `steps_completed.length` between the two
3. If the candidate's state has MORE steps_completed entries, the parent queue is stale

**Fix:** Sync the parent queue's `steps_completed`, `current_step`, `status`, and `knowledge_score` from the candidate's own state.json. Also check `completed_candidates` — if the candidate shows `status: completed` but is absent from `completed_candidates`, append it.

**Prevention:** The knowledge_entry post-write checklist must include the parent queue sync:
- Update `outputs/papers/research-queue.json` entry: status=completed, steps_completed includes all 4, knowledge_score set
- Update `_knowledge_only/research-queue.json`: same sync (two separate files)
