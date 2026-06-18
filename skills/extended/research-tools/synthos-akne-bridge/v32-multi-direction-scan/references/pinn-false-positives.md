# PubMed False Positive Patterns for PINN/ODE Directions

## Pattern: PINN keyword in unrelated contexts (v82)

**Problem:** PubMed queries for "PINN" return very high counts (50-200+) from papers that do NOT use Physics-Informed Neural Networks. The word "PINN" or "physics-informed" appears in the abstract/text of papers in entirely different fields.

**v82 VOR-PINN example:** Query "vestibulo-ocular reflex PINN OR neural ODE modeling" → 186 PubMed hits. Top 3:
- PMID 42244590: "Learning dynamical systems with biochemically informed neural ordinary differential equations" → biochemically-informed NeuralODE, NOT VOR. Domain: computational chemistry.
- PMID 42232895: "Deep learning guided propofol ketamine dosing and inflammation trajectories in elderly burns" → neural network for drug dosing. Domain: anesthesiology.
- PMID 42177291: "Moving from table to graph in physics-informed spatio-temporal symbolic regression" → symbolic regression with physics-informed constraints. Domain: applied mathematics.

**Diagnostic rule:** If all top-3 titles are from non-ocular/vestibular domains, the actual relevant count is 0 regardless of PubMed count.

## Pattern: "learning" in robotics/ML contexts (v82)

**Problem:** Queries with "learning" match robotics, path planning, UAV, control theory papers that are NOT about the biological/clinical domain.

**Example:** "eye head coordination PINN model" → OA=3 but top-3 are additive manufacturing, AI roadmap, UAV path planning. 0 relevant.

## Pattern: Abbreviation collisions (v82)

**Problem:** Broad PubMed expansion picks up papers where an abbreviation relevant to your domain appears as a secondary abbreviation in an unrelated paper.

**Example:** VOR-cancellation PINN → 9342 results. All top hits are CAR T-cell therapy (CD19 CAR T → CD19 is also VOR abbreviation in some immunology papers). 0 relevant to vestibular ODE modeling.

**Rule:** Any query returning >100 PubMed hits for niche PINN/ODE topics should be immediately suspicious. Check top-3. If >2 are irrelevant, the effective count is 0.

## Anti-pattern: Broad PubMed queries for PINN/ODE topics

**Problem:** Broad PubMed queries like "PUPIL PINN" or "EYE MOVEMENT ODE" return thousands of irrelevant results due to PubMed auto-expansion and AND/OR semantics.

**Fix:** Always use precise AND-clause queries. If count > 500, the query is too broad. Narrow with domain-specific AND clauses: "eye AND (pinning OR pinning model) AND (PDE OR differential equation)" etc.
