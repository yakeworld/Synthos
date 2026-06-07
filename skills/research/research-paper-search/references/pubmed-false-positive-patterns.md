# PubMed False Positive Patterns — v76 (2026-06-07)

## Caloric = False Positive (v76)

**Root cause**: PubMed expands "caloric" to match "caloric restriction" (diet/nutrition) papers.
Query: `caloric+testing+differential+equation` → 1 result, but it's about Meniere's clinical audiologic function, NOT a caloric nystagmus ODE model.

**Detection**: After any PubMed search, always read the first abstract. If it mentions "caloric restriction" or "diet" or "nutrition" → FALSE POSITIVE, not caloric nystagmus.

**Workaround**: Use tighter queries: `caloric+nystagmus+differential` (not just "caloric") or `thermal+stimulation+cupula+ODE`.

## Related: "PINN" False Positives

PubMed expands "PINN" to match:
1. CD19/CD22 CAR-T cell biology (PINN = protein name) — e.g. "VOR-cancellation-PINN" returns 9342 CAR-T results
2. Physics-informed neural network papers (genuine, but not vestibular)
3. Chemical kinetics (PINN = physics-informed neural network for chemistry)

**Detection**: Read abstracts. If the paper is about CAR-T, cancer, chemistry, or power systems → FALSE POSITIVE.

## Detection Pattern

After any PubMed search, always ask:
1. Does the term have alternative expansions (caloric=restriction, PINN=protein)?
2. Read the top-3 abstracts — are they about vestibular/eye/vestibular/inner ear?
3. If abstracts are about unrelated domains → FALSE POSITIVE, not a valid candidate.