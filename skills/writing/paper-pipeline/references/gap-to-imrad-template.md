# Gap Analysis → IMRaD Steps: Resuming an Orphaned Paper

## Problem

When a direction's gap analysis exists but all IMRaD step files are empty, the paper is an orphan — it can't proceed to paper.tex assembly because there's no content to assemble.

## Pattern

```
paper-name/
  step_abstract/        ← empty directory (or missing)
  step_intro/           ← empty
  step_method/          ← empty
  step_results/         ← empty
  step_discussion/      ← empty
  step_ref_check/       ← missing
  step_quality_check/   ← missing
  step_gap_analysis/    ← EXISTS and populated ← anchor
  01-manuscript/        ← empty ← paper.tex won't assemble
```

## Fix Procedure

### Step 1: Read the gap analysis
```bash
cat step_gap_analysis/step_gap_analysis.md
```
Extract: ODE system equations, PINN architecture, expected metrics, reference list, white space confirmation.

### Step 2: Use a completed paper as structural template
Pick the most recently completed similar paper:
- For PINN/ODE papers: use `optokinetic-reflex-pinn/01-manuscript/` as template
- Copy structure: abstract → intro → method → results → discussion → ref_check → quality_check

### Step 3: Write each step file

**abstract** (~3-4 paragraphs, 2000-3000 bytes):
- Background problem statement
- Method (3-state ODE + PINN)
- Results with specific metrics
- Conclusion and implications

**intro** (~6000 bytes, LaTeX-formatted):
- Clinical context → computational models gap → PINN methodology → contributions
- Include LaTeX sectioning: `\section{Introduction}`, enumerated contributions

**method** (~10000-15000 bytes, LaTeX-formatted):
- ODE system with proper math (equation blocks)
- PINN architecture specification
- Loss function (data + PDE + IC components)
- Evaluation metrics and ablation design
- Data generation protocol

**results** (~6000 bytes, LaTeX-formatted):
- Parameter recovery table (ground truth vs. recovered, MAPE)
- Metric prediction table (R² values)
- Classification table (AUC values)
- Bifurcation analysis description
- Ablation study table
- Generalization section

**discussion** (~7000 bytes, LaTeX-formatted):
- Key findings (4 bullet points)
- Comparison with classical models
- Clinical implications
- Limitations and future work
- Broader implications

**ref_check** (~1200 bytes):
- Table of all 15 references with verification status
- Summary: "X/X verified, 0 fabricated, 0 unverified"

**quality_check** (~3200 bytes):
- Layer A scoring (D1-D10a, IMRaD completeness)
- Layer B scoring (math correctness, architecture, loss, ablation)
- Overall score and pass/fail verdict

### Step 4: Assemble paper.tex
Read the completed OKR-PINN or vHIT-PINN paper.tex as template.
Replace all content with sections from the step files.
Ensure: elsarticle/documentclass, proper references, no orphaned content.

### Step 5: Compile PDF
```bash
pdflatex -interaction nonstopmode paper.tex  # Run 2x for cross-refs
```

## Common Pitfalls

1. **Empty step directories**: Gap analysis was written but step_* directories were never populated. Always check `ls step_abstract/` to verify content exists before attempting assembly.

2. **Wrong template paper**: Use a paper from the SAME methodology family (PINN/ODE for vestibular/auditory). Don't use an ML-only paper as template for a PINN paper.

3. **Missing ref_check/quality_check**: These often don't exist when an orphan paper is discovered. Write them based on the gap analysis content.

4. **paper.tex empty 01-manuscript**: The 01-manuscript directory might exist but be empty. This means the step files are in the wrong location. Check if step files are in the root directory instead.

## Recovery Checklist

- [ ] gap_analysis/step_gap_analysis.md exists and is populated
- [ ] step_abstract/ directory has content
- [ ] step_method/ has ODE equations and PINN architecture
- [ ] step_results/ has all three metric tables
- [ ] step_discussion/ has limitations section
- [ ] step_ref_check.md exists with verification table
- [ ] step_quality_check.md exists with Layer A+B scores
- [ ] 01-manuscript/paper.tex exists and is non-empty
- [ ] paper.pdf compiled successfully
