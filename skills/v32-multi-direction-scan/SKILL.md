---

name: v32-multi-direction-scan
description: Standardized v32 multi-direction PubMed+OpenAlex scan protocol for autonomous-core-researcher cron runs.
category: research
---

# v32 Multi-Direction Scan Protocol

## When to Use
Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.

## Resilience
- PubMed API instability: NCBI eUtils endpoints (eFetch, esummary) are intermittently unreliable. See `references/pubmed-api-resilience.md` for working patterns. Use the utility script at `scripts/pubmed_utils.py` for resilient PubMed/OpenAlex queries.

## Protocol Steps

### Step 1: Rotation Scan (5 directions)
For each direction, execute PubMed targeted query + OpenAlex broad/cited:
1. Periodic Alternating Nystagmus PINN
2. Nystagmus Neutral Deviation PINN
3. Smooth Pursuit PINN
4. Vestibular Compensation ODE
5. Cupula Deflection PINN

### Step 2: New Exploration (5 directions)
1. VOR-OKR Coupling PINN
2. OKR Adaptation PINN
3. Caloric Test Response ODE
4. Vestibular Collic Reflex PINN
5. Pupillary Light Reflex PINN

### Step 2b: v33 New Candidate Scan (add if rotation confirms all white)
1. Vestibular Evoked Myogenic Potential ODE (VEP-ODE) — PubMed=0, TRUE WHITE
2. Gaze Stability ODE (GazeStability-ODE) — PubMed=0, TRUE WHITE
3. Motion Sickness PINN — PubMed=5 (classical models only), 0 PINN, WHITE for PINN

### Step 3: Scoring Matrix
| Score Range | Action |
|-------------|--------|
| ≥24 with feasibility≥3 | START — create gap analysis |
| ≥24 with feasibility<3 | CANDIDATE — gap analysis with lower priority |
| 18-23 | CANDIDATE |
| <18 | POSTPONE |

### Step 4: Update State
- Update agent-tracker.json with results
- Append to agent-log.md: `|[Cron] <date> | direction= | action= | result=`

## Key Lessons from v32/v33
1. PubMed count >1000 → check top 3 titles immediately
2. 

  io_contract: input: ['scan_directions: list[str] -> scan_results: list[Paper]', 'output: ['scan_results: list[Paper] (title, doi, source, relevance, abstract)']


# v32 Multi-Direction Scan Protocol

## When to Use
Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.

## Resilience
- PubMed API instability: NCBI eUtils endpoints (eFetch, esummary) are intermittently unreliable. See `references/pubmed-api-resilience.md` for working patterns. Use the utility script at `scripts/pubmed_utils.py` for resilient PubMed/OpenAlex queries.

## Protocol Steps

### Step 1: Rotation Scan (5 directions)
For each direction, execute PubMed targeted query + OpenAlex broad/cited:
1. Periodic Alternating Nystagmus PINN
2. Nystagmus Neutral Deviation PINN
3. Smooth Pursuit PINN
4. Vestibular Compensation ODE
5. Cupula Deflection PINN

### Step 2: New Exploration (5 directions)
1. VOR-OKR Coupling PINN
2. OKR Adaptation PINN
3. Caloric Test Response ODE
4. Vestibular Collic Reflex PINN
5. Pupillary Light Reflex PINN

### Step 2b: v33 New Candidate Scan (add if rotation confirms all white)
1. Vestibular Evoked Myogenic Potential ODE (VEP-ODE) — PubMed=0, TRUE WHITE
2. Gaze Stability ODE (GazeStability-ODE) — PubMed=0, TRUE WHITE
3. Motion Sickness PINN — PubMed=5 (classical models only), 0 PINN, WHITE for PINN

### Step 3: Scoring Matrix
| Score Range | Action |
|-------------|--------|
| ≥24 with feasibility≥3 | START — create gap analysis |
| ≥24 with feasibility<3 | CANDIDATE — gap analysis with lower priority |
| 18-23 | CANDIDATE |
| <18 | POSTPONE |

### Step 4: Update State
- Update agent-tracker.json with results
- Append to agent-log.md: `|[Cron] <date> | direction= | action= | result=`

## Key Lessons from v32/v33
1. PubMed count >1000 → check top 3 titles immediately
2. 
metadata:
  synthos:
    priority: P2
    atom_type: tool
    description: Standardized v32 multi-direction PubMed+OpenAlex scan protocol for autonomous-core-researcher cron runs.
    signature: 'scan_directions: list[str] -> scan_results: list[Paper]'
    related_skills: [knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification]
---



# v32 Multi-Direction Scan Protocol

## When to Use
Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.

## Resilience
- PubMed API instability: NCBI eUtils endpoints (eFetch, esummary) are intermittently unreliable. See `references/pubmed-api-resilience.md` for working patterns. Use the utility script at `scripts/pubmed_utils.py` for resilient PubMed/OpenAlex queries.

## Protocol Steps

### Step 1: Rotation Scan (5 directions)
For each direction, execute PubMed targeted query + OpenAlex broad/cited:
1. Periodic Alternating Nystagmus PINN
2. Nystagmus Neutral Deviation PINN
3. Smooth Pursuit PINN
4. Vestibular Compensation ODE
5. Cupula Deflection PINN

### Step 2: New Exploration (5 directions)
1. VOR-OKR Coupling PINN
2. OKR Adaptation PINN
3. Caloric Test Response ODE
4. Vestibular Collic Reflex PINN
5. Pupillary Light Reflex PINN

### Step 2b: v33 New Candidate Scan (add if rotation confirms all white)
1. Vestibular Evoked Myogenic Potential ODE (VEP-ODE) — PubMed=0, TRUE WHITE
2. Gaze Stability ODE (GazeStability-ODE) — PubMed=0, TRUE WHITE
3. Motion Sickness PINN — PubMed=5 (classical models only), 0 PINN, WHITE for PINN

### Step 3: Scoring Matrix
| Score Range | Action |
|-------------|--------|
| ≥24 with feasibility≥3 | START — create gap analysis |
| ≥24 with feasibility<3 | CANDIDATE — gap analysis with lower priority |
| 18-23 | CANDIDATE |
| <18 | POSTPONE |

### Step 4: Update State
- Update agent-tracker.json with results
- Append to agent-log.md: `|[Cron] <date> | direction= | action= | result=`

## Key Lessons from v32/v33
1. PubMed count >1000 → check top 3 titles immediately
2. "adaptation" in query matches clinical rehab, not just computational adaptation
3. "dynamics" matches physics/robotics, not just oculomotor
4. Caloric test PubMed count=77 but OA broad=2727 (all microbiota papers) → FALSE POSITIVE pattern
5. Cupula PubMed=277 but ALL clinical/zFish, 0 computational → still white for PINN
6. OKR Adaptation: PubMed=0 for (OKR adaptation + PINN/NeuralODE) → ABSOLUTE WHITE SPACE
7. Always use retmode=xml for eFetch (v31 fix)
8. Always use lowercase `idlist` in PubMed eSearch (v4 fix)
9. v33: Classical computational models ≠ PINN competition — motion sickness has 5 PubMed hits (Oman 1990, Oman 2001, Allred 2024) but 0 PINN/NeuralODE → still WHITE for PINN approach
10. v33: Three NEW confirmed white spaces added: VEP-ODE, GazeStability-ODE, MotionSickness-PINN
11. v33: Dizziness-ML has 21 clinical papers, 0 computational models → NOT suitable for PINN pipeline (wrong paradigm)

## Pitfalls
- PubMed AND/OR semantics: count > 5000 → almost certainly false positive
- **PINN keyword false positive pattern (v82):** PubMed broad queries for "PINN" return large counts (50-200+) from non-PINN papers. Top-3 patterns: (a) "physics-informed" in unrelated contexts (biochemically-informed NeuralODE, phonon Boltzmann, symbolic regression), (b) "neural network" in unrelated biomedical contexts (propofol dosing, inflammation), (c) "learning" in unrelated ML contexts (robotics, path planning, UAV). Always read top-3 titles — do NOT trust PubMed count alone. If top-3 are all non-domain-PINN, the actual relevant count is 0.
- **BPPV false positive pattern:** BPPV returns hundreds of clinical papers, but many have "BPPV" in methodology/clinical section of completely different papers. Only count papers where BPPV is the PRIMARY topic.
- **Caloric false positive pattern:** "Caloric" matches heat transfer, microbiota, restriction/metabolism papers. caloric-ODE=26396 PubMed all false positive (caloric restriction). Top-3 must be checked.
- **VOR-cancellation false positive pattern:** "VOR cancellation" returns 9342 results but all are CAR T-cell therapy (CD19 CAR T → CD19 is also VOR abbreviation in immunology). 0 relevant. Pattern: broad PubMed auto-expansion picks up unrelated abbreviations.
- OA broad count can be very high even for niche topics due to irrelevant matches
- Always check top-3 titles for relevance before declaring a space white
- For PINN/ODE directions: PubMed count of classical papers ≠ competition. Only 0 PINN/ODE = white space.
- See `references/v32-scan-pitfalls.md` for accumulated pitfalls: completed_papers_count drift, new_directions accumulator not cleaned, OpenAlex false positives, classical ODE ≠ PINN competition, clinical ML ≠ computational competition.
- See `references/v32-scan-pitfalls-v2.md` for enhanced tracker reconciliation procedures and prevention tips for the v87 pagination truncation bug.
- See `references/pinn-false-positives.md` for detailed PubMed false positive patterns specific to PINN/ODE queries (keyword collisions, abbreviation collisions, domain-mismatch false positives).
- See `references/pubmed-api-resilience.md` for NCBI API instability patterns and resilient query patterns (eFetch JSON errors, HTTP 502/503/504, esummary structure variance).
- Use `scripts/pubmed_utils.py` — reusable PubMed/OpenAlex query functions with automatic retry, BOM stripping, and JSON resilience.