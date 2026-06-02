---
name: training-pipeline-principles
description: Abstract principles and reusable methodologies for multi-stage model training pipelines. Extracted from practice — teacher→distillation→student→hybrid→fine-tune pattern with geometric constraints, domain adaptation via mixed data, and progressive loss scheduling.
version: 1.1.0
author: Synthos Agent
license: MIT
tags: [training, methodology, distillation, domain-adaptation, geometric-constraint, progressive-learning, loss-design]
---

# Training Pipeline Principles

## Core Philosophy

The most robust training pipelines follow a **multi-stage progressive learning** pattern. Instead of training one model to do everything at once, build a **chain of models** where each stage teaches the next. This is not just about performance — it's about **managing the complexity of knowledge transfer**: from labeled data to unlabeled, from heavy models to light, from clean domain to messy real-world.

## The 5-Stage Meta-Pattern

### Stage 1: Teacher (Labeled Source)
Train a **high-capacity model** on clean, labeled data. This establishes the upper bound of what's achievable. The teacher doesn't need to be deployable — it only needs to be **accurate**.

**General principle**: Use the heaviest model that fits your GPU budget. Don't optimize for inference yet.

**Signal**: `stat + dyn + seg` — direct supervised learning with all available labels.

### Stage 2: Distillation (Unlabeled Target)
Use the teacher to generate **pseudo-labels** on unlabeled target domain data. The key insight is **not what the teacher predicts, but how its predictions relate to its internal representations**.

**General principle**: The bridge between domains should be a **geometric or structural invariant**, not raw pixel values. If two domains share the same underlying geometry (e.g., an ellipse is an ellipse regardless of imaging conditions), use that geometry as the transfer medium.

**Signal**: `param_seg_dice/BCE` — parameter ellipse ↔ segmentation mask overlap. This works because: (a) both domains share a common structural template, (b) the relationship between a parametric shape and its rasterized mask is domain-invariant.

**Applicability**: Any problem where:
- The source and target domains share a **common geometric or structural template**
- The target domain lacks labels but shares this structure
- The teacher can produce accurate parameters on source

### Stage 3: Student (Target-Adapted)
Train a **lightweight model** on mixed source + pseudo-labeled target data. This is where model compression happens — the student learns from both the teacher's pseudo-labels and whatever original labels remain useful.

**General principle**: Never train the student on target-only data. Always mix with source data to prevent **catastrophic forgetting**. The ratio matters: too much source → poor adaptation, too much target → knowledge collapse.

**Progressive loss schedule**: Start with the simplest losses (segmentation, direct parameters), then gradually add **constraint losses** (edge, texture, consistency) as training progresses. Each new loss should capture a **different aspect** of what makes a good prediction:
- **Segmentation loss** → "what pixels belong to which class"
- **Edge loss** → "where are the boundaries"
- **Texture loss** → "what does the region look like inside"
- **Consistency loss** → "do my predictions violate known physics/geometry"

### Stage 4: Hybrid (Real-World + Source)
Add **real-world target domain data** to the training mix. This is the stage where the model learns to handle the actual deployment conditions. The critical discovery: **texture consistency loss** is more effective than pixel-level losses for cross-domain adaptation, because texture is more domain-invariant than raw pixel intensities.

**General principle**: For domain adaptation, prefer **feature-level constraints** (texture, edge, shape) over **pixel-level constraints** (MSE, L1). Feature-level constraints transfer better across imaging conditions.

### Stage 5: Fine-tune (Low-LR Polish)
Take the best checkpoint from Stage 4 and fine-tune with **lower learning rate** (typically 1/3 to 1/10 of the original). Stop early — fine-tuning gains peak quickly then overfit.

**General principle**: Fine-tuning with geometric constraints should respect a **threshold margin**. Don't penalize small deviations (they're natural variation). Only penalize large violations. The `clamp(x - threshold, 0)` pattern is broadly applicable.

---

## The 8 Abstract Principles

### 1. Progressive Capacity Cascade
```
Large Teacher (labeled) → Student (labeled+pseudo) → Compact Model (mixed) → Deploy (fine-tuned)
```
Each stage reduces model capacity but increases domain coverage. Never skip stages.

### 2. Geometric Invariant as Transfer Bridge
The most effective knowledge transfer mechanism between domains is a **shared geometric invariant** — something that both domains agree on regardless of imaging conditions. For eye tracking, it's the ellipse parameter↔segmentation mask relationship. Find your domain's geometric invariant.

### 3. Mixed Data as Forgetting Shield
When adding new domain data, **always mix with old domain data**. Pure target-only training on a pre-trained model causes catastrophic forgetting. The minimum safe ratio is ~10-20% source data in each batch.

### 4. Progressive Loss Assembly
Add losses in order of **semantic complexity**:
1. Direct supervision (CE, MSE)
2. Structural constraint (Dice, IoU)
3. Boundary constraint (Edge gradient)
4. Internal consistency (Texture, Center alignment)
5. Domain adaptation (Pseudo-label distillation)

Each new loss addresses a failure mode of the previous layer.

### 5. Teacher/Student Capacity Asymmetry
High-capacity models (17M+ params) saturate with simple losses — they don't need extra constraints. **Edge/consistency losses benefit only low-capacity models** (3-5M params). The teacher's job is to be accurate; the student's job is to be efficient under constraints. Don't add the same constraints to both.

### 6. Threshold-Aware Constraints
Add constraints as `clamp(metric - threshold, 0)` rather than `metric` directly. This creates a **dead zone** where small natural variations are tolerated. The threshold should be calibrated from the teacher's performance on validation data.

### 7. Stop Before Overfitting
Multi-stage pipelines have a **peak-and-decay pattern** at each stage. The peak occurs early in fine-tuning (typically epoch 10-12 out of 15 for low-LR). Track a geometric mean of performance across domains, not just one metric. Stop when the mean plateaus or drops.

### 8. BCE > Dice for Edge-Sensitive Parametric Supervision (NEW v1.1)
**Dice is a region metric** — it measures area overlap. For parametric shape supervision (ellipse parameters→mask), Dice is dominated by large interior areas; edge displacement of 3-5px only changes Dice by ~2-3%, producing weak gradients for boundary refinement.

**BCE is a pixel metric** — each pixel contributes independently to the gradient. Edge pixels (~6% of total area for a typical pupil) contribute proportionally to their count, not drowned out by the interior.

**EllSeg finding**: The EllSeg paper uses `α·SurfaceLoss + (1-α)·GDice + wCE`, explicitly acknowledging that GDice alone is insufficient for boundary precision. They use an alpha curriculum: α=0 (pure GDice) at epoch 0 → α=1 (pure SurfaceLoss) at epoch 40.

**Recommendation**: For `param_seg_dice` (parameter↔segmentation consistency), prefer **BCE** over Dice. The gradient signal is denser and more edge-sensitive. Keep Dice for direct label supervision (where interior accuracy matters more than boundary precision).

---

## Decision Trees

### When to use Teacher→Distillation→Student?
Ask three questions:
1. Do you have labeled data for one domain and unlabeled for another? → Yes → Use this pattern
2. Do both domains share a common geometric structure? → Yes → Distill via that structure
3. Is the target model much smaller than the teacher? → Yes → Progressive capacity cascade

### Which losses to add?
```
simple labels available? → seg CE / MSE
need shape accuracy? → +Dice / +IoU  
need boundary precision? → +Edge gradient OR BCE(distillation)
  Edge gradient: use when you trust image gradients (good lighting, no artifacts)
  BCE(distillation): use when image gradients are unreliable (speckle, glare)
need internal consistency? → +Texture / +Center consistency
need domain transfer? → +Pseudo-label distillation
```

### When to use BCE vs Dice for distillation?
```
Teacher is accurate AND boundary precision matters → BCE
Teacher is noisy → Dice (more robust to outlier pixels)
Target domain has small features (few pixels) → BCE (less diluted)
Need fast convergence on overlap → Dice
Need edge refinement in later stages → BCE
```

### How to set learning rate?
- **Teacher training**: standard LR (1e-4 for AdamW)
- **Distillation**: standard or slightly lower
- **Student**: standard
- **Hybrid mixed**: standard
- **Fine-tune**: 1/3 to 1/10 of standard (3e-5 from 1e-4)

---

## Applicability Beyond Eye Tracking

These principles generalize to any problem where:
1. You have **labeled source data** + **unlabeled target data**
2. Both domains share a **common geometric/structural pattern**
3. The target requires a **smaller/faster model**
4. The deployment environment has **different conditions** from training

Examples that fit this pattern:
- Medical image segmentation (labeled public datasets → unlabeled hospital data)
- Autonomous driving (day → night, clear → rain)
- Industrial inspection (lab → factory floor)
- Any edge-AI deployment (cloud GPU → embedded NPU)

## References
- `remote-gpu-training` — operational execution layer
- `references/t3em-training-pipeline.md` — concrete application of these principles to eye tracking
- `references/ellseg-loss-comparison.md` — full comparative analysis of EllSeg vs our loss architecture (SurfaceLoss, GDice, BCE, alpha curriculum, self-consistency)
