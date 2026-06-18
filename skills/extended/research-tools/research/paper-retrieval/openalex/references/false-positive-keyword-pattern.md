# OpenAlex Keyword False Positive Patterns

## Overview

In the vestibular/oculomotor PINN/ODE search domain, common terms like "neural network", "differential equation", "neural interface", and "model" trigger massive irrelevant results due to keyword collision with unrelated domains. This file catalogs confirmed false positive patterns.

## Confirmed False Positive Patterns

### "Neural Network" / "Neural Interface"
- **Pattern**: Any query containing "neural network" or "neural" returns results from materials science, electronics, prosthetics, and computer vision — NOT computational neuroscience
- **Examples**: "vestibular-spinal neural network" → top hit: "Next Generation Neural Interface Electronics"; "vestibular-efferent neural network" → vibrotactile prosthetics; "vestibular-computation neural network" → neural interface electronics
- **Root cause**: OpenAlex's "neural network" keyword is dominated by materials/electronics papers, not computational models
- **Rule**: Never use "neural network" as a standalone search term. Always combine with specific methodology terms (PINN, ODE, PDE, differential equation, computational model) to filter

### "Differential Equation" / "ODE" / "Model"
- **Pattern**: Queries with "differential equation" often return unrelated physics/engineering papers
- **Examples**: "smooth pursuit neural ODE" → thermal dynamics rectangular fin model, Hirschsprung disease, traffic forecasting
- **Rule**: Combine with domain-specific terms (vestibular, saccade, nystagmus) AND methodology (PINN, neural ODE, ordinary differential equation)

### "Fixation"
- **Pattern**: "fixation PINN" returns molecular transport, botany, protein evolution, fishing studies
- **Examples**: "fixation stability PINN" → extracellular space molecular transport, bacterial decomposition, protein evolution
- **Root cause**: "Fixation" in chemistry/materials context dominates
- **Rule**: Must use "fixation stability" OR "eye fixation" AND PINN/ODE to filter

### "Cochlear" / "Vestibular" Alone
- **Pattern**: Broad anatomical terms return music therapy, animal behavior, speech processing papers
- **Examples**: "cochlear vestibular coupling" → neural interface electronics, music therapy, primate vision
- **Rule**: Always combine with methodology (PINN, ODE, computational, dynamics model)

### "Eye" + "Head" + "Coordination" / "Coordination"
- **Pattern**: "eye head coordination" returns drug-induced bodily awareness, autonomous vehicle architecture, pentecostal spirituality
- **Examples**: v91 scan — "eye head coordination computational model PINN" → OA=10, top-3: (1) Drug-induced alterations of bodily awareness, (2) Savvy autonomous vehicle architecture, (3) Pentecostal spirituality vs Chinese religious thought
- **Root cause**: "coordination" in non-ocular contexts (vehicle safety coordination, spiritual coordination) dominates
- **Rule**: PubMed=0 + OA>5 → almost certainly false positive. Must verify by reading titles/abstracts.

## Verification Protocol

When OpenAlex returns results for a PINN/ODE query:

1. Read the **title** of the top-3 results
2. If any top-3 result is about materials, electronics, music, animal behavior, speech, or climate → **ALL LIKELY FALSE POSITIVES**
3. Check abstract_inverted_index to confirm the methodology term appears in the actual abstract, not just the title or keywords
4. If top-3 are irrelevant, the search term is producing false positives → try more specific methodology terms or accept as white space

## PubMed Cross-Check

Always cross-check with PubMed. If PubMed returns 0 for the same query, OpenAlex high counts are almost certainly false positives from non-biological domains.
