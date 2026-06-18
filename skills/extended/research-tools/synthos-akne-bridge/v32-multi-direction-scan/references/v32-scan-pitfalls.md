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
