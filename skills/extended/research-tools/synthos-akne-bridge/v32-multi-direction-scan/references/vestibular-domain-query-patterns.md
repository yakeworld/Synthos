# Vestibular Domain Query Patterns

## Covering: Vestibular Compensation ODE, Cupula Deflection PINN, Vestibular Collic Reflex PINN, VOR-OKR Coupling PINN

Domain-specific false-positive and query patterns observed during multi-direction rotation scans.

---

## Pattern 1: "Vestibular" Abbreviation Collision in OpenAlex

**Problem:** OpenAlex queries with "vestibular" AND "PINN" return false positives from gynecological/pain literature. "Vestibular" in anatomical/medical context also refers to the **vaginal vestibule** (vulvodynia, provoked vestibulodynia, neurofibromatosis).

**Detection:**
- Query `"vestibular" PINN model` → 5 OpenAlex hits
- Top titles include: "Medical and physical predictors of localized provoked vulvodynia", "Reliability and Convergent Validity of the Algometer for Vestibular Pain Assessment"

**Fix:** Add NOT clause: `"vestibular" PINN NOT vulvodynia NOT vestibulodynia`, or always inspect top-3 titles. PubMed does NOT suffer from this collision because PubMed has separate MeSH terms for vestibular system vs vestibule (vaginal).

**Rule of thumb:** If OpenAlex returns 3-5 results and the titles mention pain/vulvodynia/neurofibromatosis, the entire result set is a false positive.

---

## Pattern 2: Vestibular Compensation Broad Queries Return ONLY Clinical/Animal Studies

**Problem:** Unlike PAN (where broad queries found one classical velocity-storage model) or Smooth Pursuit (where broad queries found cerebellar models), vestibular compensation broad queries return exclusively clinical and animal studies — no computational models at all.

**Evidence from 12-query scan:**
| Query | Count | Content |
|-------|:-----:|:--------|
| `"vestibular compensation" AND "differential equation"` | 0 | — |
| `"vestibular compensation" AND ODE` | 0 | — |
| `"vestibular compensation" AND "computational model"` | 0 | — |
| `"vestibular compensation" AND simulation` | 11 | Compensatory saccade in monkey, VR rehab, eye-head gaze modeling (all behavioral, not ODE) |
| `"vestibular compensation" AND "VOR" AND model` | 15 | PROBIT recovery model, KORA FF4 symptoms, GVS effects (all clinical stats) |
| `"vestibular compensation" AND cerebellum AND model` | 15 | Thalamic lesion study, EGb 761 rat, eye-head gaze (all animal/clinical) |

**Diagnostic rule:** If ALL broad queries return only clinical study designs (observational, RCT, animal-model, rehabilitation) and 0 papers with "model" in a computational sense (ODE, state-space, dynamical system), the space is **genuinely devoid of computational models**. This is a stronger white-space signal than domains with classical models — there's no prior-art competition at all, not even from different methodological traditions.

**Implication:** Vestibular compensation, despite being a major clinical topic (unilateral vestibular loss, bilateral vestibulopathy, aging-related decline), has never had a computational ODE/PINN formulation. This is likely because: (a) the compensation process operates over days/weeks (clinical timescale, not lab recording timescale), (b) classical modelers focused on steady-state VOR rather than recovery dynamics, (c) patient-specific parameter inference requires clinical VOG data that was hard to obtain before vHIT became routine.

---

## Pattern 3: Vestibular Compensation vs Vestibular Adaptation — Query Strategy

**Problem:** "Vestibular compensation" and "vestibular adaptation" refer to related but distinct processes. Compensation = recovery after acute unilateral loss; adaptation = long-term gain changes (dual VOR, frequency tuning). Queries must be specific.

**Recommended query tiers for vestibular compensation:**

| Tier | Query Pattern | Expected Count | Purpose |
|:-----|:--------------|:--------------:|:--------|
| Narrow PINN | `"vestibular compensation" AND ("PINN" OR "NeuralODE" OR "physics-informed")` | 0 | Primary white-space test |
| Narrow ODE | `"vestibular compensation" AND ("differential equation" OR "ODE" OR "state-space")` | 0 | Confirm no computational model of compensation itself |
| Broad clinical | `"vestibular compensation" AND model` | 10-20 | Check for non-PINN/ODE computational models |
| Companion | `"unilateral vestibular loss" AND ("computational" OR "model" OR "ODE")` | 0 | Alternative clinical search |
| Cerebellar | `"vestibular compensation" AND cerebellum AND model` | 10-20 | Check for cerebellar adaptation computational models |
| Simulation | `"vestibular compensation" AND simulation` | 5-15 | Catch-all for any modeling work |

**Key insight:** Unlike oculomotor domains where the physiology is well-modeled (VOR, OKR, saccades), vestibular compensation has essentially **zero** computational literature. The clinical literature is rich (1000+ papers) but every single one is observational, animal-model, or clinical trial — never a dynamical system model of the recovery process.

---

## Pattern 4: "VOR" Abbreviation Collision (Immunology)

**Problem:** "VOR" in PubMed broadly matches immunology papers where VOR = "Vestibular-Ocular Reflex" is not the intended context. The abbreviation "VOR" can also match other biomedical abbreviations.

**Evidence:** Query `"vestibular compensation" AND "VOR" AND model` returns 15 hits, all clinical/animal. However, a broader `VOR compensation model` (without quotes) returns 9342+ hits, most from immunology (CAR T-cell VOR contexts). Already documented in `pinn-false-positives.md` as "Abbreviation collisions."

**Fix:** Always quote the full term: `"vestibular compensation"` not just `vestibular`. Quote `"VOR"` or use `"vestibulo-ocular reflex"` for precision.

---

## Created

2026-06-22, cycle-117 (VestibularCompensation-ODE literature_scan)
