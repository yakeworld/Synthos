# Gap Analysis Template

> Template for the gap_analysis step (step 2/4 of the research pipeline).
> Follow this structure when producing `step_gap_analysis.md` for a candidate.

## Required Sections (9)

### 1. Research Gap Validation

**Table: Gap Dimensions**

| Dimension | Value |
|-----------|-------|
| Domain | Physiological system description |
| White Space Status | ABSOLUTE_WHITE / CONDITIONAL / OCCUPIED |
| Classical Models Exist? | YES/NO with key references |
| PINN/ODE Gap | What's missing — the specific gap statement |
| Clinical Need | Population sizes, current biomarker gap |

**White Space Characterization**: Describe the type (Methodological / Disease / Mechanism / Biomarker), the classical models that exist (with years), what's missing, and key distinctions (forward vs inverse PINN, DNN vs PINN, etc).

### 2. Proposed Model Architecture

**ASCII Diagram**: Box diagram showing ODE-1, ODE-2, and PINN layer with inputs/outputs/loss.

**ODE-1 Detail**: Name, purpose, reusable kernel check (structural analog check with specific prior kernel), state variables table, key parameters table (name, symbol, range, description), dynamics equations, key behavior.

**ODE-2 Detail**: Same structure as ODE-1.

**PINN Layer Detail**: Architecture table (layer, type, size, activation), inputs/outputs, loss function components, training strategy (pre-training, fine-tuning, transfer).

**Multi-Scale Temporal Dynamics Check**: Table with Detection→Assessment→Mitigation→Identifiability Impact. Check for ODE-1 vs ODE-2 timescale gaps.

**Cross-ODE Parameter Identifiability Confound Check**: Table with Detection→Assessment→Mitigation (at least one external anchor)→Residual. Identify all confounds (multiplicative, ratio, shared parameter), assess severity, propose mitigation, and accept/declare residuals.

### 3. Parameter Count Estimation

| Component | Parameters | Notes |
|-----------|-----------|-------|
| ODE-1 | N | List params |
| ODE-2 | N | List params |
| PINN | ~N | NN architecture breakdown |
| **Total** | **N** | |

**Data Requirements**: Minimal (N), Target (N), Clinical feasibility statement.

**Identifiability Analysis**: Table (parameter, ★ rating, clinical information carrier).

### 4. Clinical Impact Assessment

**Clinical Conditions Table**: (Condition, Prevalence, Domain Relevance, Current Assessment, PINN Gap)

Cover 5-8 conditions. For each: what the current assessment is, why PINN fills a gap, what a PINN-derived parameter would measure.

**Clinical Translation Pathway**: Phase 1-4 with timeline, activity, and success criterion. Phases should progress: synthetic data → retrospective clinical → prospective study → longitudinal biomarker.

**Addressable Market**: Population sizes, current standard limitations, PINN value proposition.

### 5. Feasibility Assessment

**Multi-Criterion Scoring**: Table (criterion, score 0-1, justification). Minimum dimensions: Model Complexity, Data Availability, Parameter Identifiability, Clinical Translation, Novelty. Compute overall.

**Comparison with Prior Candidates**: Table comparing this candidate vs the most recent prior candidate across same dimensions, with delta.

**Data Abundance Advantage**: Describe the data sources available for this candidate and why they're better/special.

### 6. Comparison with Existing Approaches

Table: (Approach, Type, Patient-Specific?, Param Count, Clinical Use, PINN Gap). Cover 6-10 approaches including: gold standard clinical tests, classical forward ODE models, data-driven NN methods, PINN-based but unrelated methods, and this work.

### 7. Key Challenges

Numbered list of 4-6 challenges. Each with: problem description + **Mitigation** (bold). Cover identifiability, data, equipment, model selection, clinical adoption.

### 8. Next Step: Hypothesis Generation

3 candidate hypotheses. Each formatted as:

**H{N} — Title**: Statement of what the PINN parameter predicts/discriminates, with ROC AUC threshold. Rationale paragraph with prevalence numbers.

### 9. Quality Assessment

| Dimension | Score | Criteria Met |
|-----------|:-----:|-------------|
| Gap specificity | 0.xx | Paragraph |
| Architecture soundness | 0.xx | Paragraph |
| Parameter identifiability | 0.xx | Paragraph |
| Clinical relevance | 0.xx | Paragraph |
| Data feasibility | 0.xx | Paragraph |
| Novelty | 0.xx | Paragraph |
| **Composite** | **0.xx** | **GATE** |

**Gate**: PASS (≥0.85) or CONDITIONAL (0.65-0.84).

## Quality Rubric for Gap Analysis Scoring

| Dimension | Weight | 1.0 (Excellent) | 0.7 (Good) | 0.5 (Adequate) | 0.3 (Weak) |
|-----------|:-----:|:----------------|:-----------|:---------------|:-----------|
| Gap specificity | — | Pinpointed to exact physiological mechanism, no ambiguity | Well-defined gap with clear boundaries | General gap area, needs refinement | Vague, could apply to many domains |
| Architecture soundness | — | Maps to well-characterized physiology, structural analog exists | Sound mapping, minor adaptation needed | Plausible but no direct physiological basis | Unclear or forced mapping |
| Parameter identifiability | — | All params identifiable from routine data, strong anchors | Most params identifiable, one moderate confound | Multiple confounds, partial resolution | Key params unidentifiable |
| Clinical relevance | — | 25M+ patients, zero new equipment, first biomarker | Large population, one new device needed | Niche population or expensive new equipment | Research-only, no clinical path |
| Data feasibility | — | 40K+ public datasets available | 500+ clinical recordings available | 100+ but requires new collection | Must generate synthetic-only |
| Novelty | — | ABSOLUTE_WHITE (zero competing PINN) | Zero PINN but classical alternative exists | PINN exists for different but related domain | OCCUPIED (PINN exists for same problem) |

## Examples

Reference implementations:
- `_knowledge_only/vocal-fold-phonation-PINN/step_gap_analysis.md` (K-014, 313 lines)
- `_knowledge_only/respiratory-mechanics-PINN/step_gap_analysis.md` (K-015, 325 lines)
- `_knowledge_only/cochlear-mechanics-PINN/` (K-013)
