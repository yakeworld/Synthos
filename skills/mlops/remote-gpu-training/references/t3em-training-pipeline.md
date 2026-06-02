# T3EM Eye Tracking — Multi-Stage Training Pipeline

## Overview

The T3EM (Temporal 3D Eye Model) training pipeline uses a **teacher→distillation→student→hybrid→fine-tune** sequence. All training happens on **work1 (user-NF5468-M7-A0-R0-00, 8×RTX 4090)**, host-level via `vllm_env` venv.

**Training code root:** `/mnt/nfs/eye_video_HD/code/`
**Experiment outputs:** `/mnt/nfs/eye_video_HD/code/rn18_experiments/{exp_name}/`
**Python environment:** `/home/yakeworld/vllm_env/bin/python3`

## Pipeline Stages

```
Stage 1: RN18 Teacher (OpenEDS supervised)
  Scripts:  run_resnet18_openeds.py (original a/b/c/d)
            run_resnet18_openeds_v2.py (e variant)
  Backbone: ResNet-18 (ImageNet pretrained, 17M params)
  Data:    OpenEDS (976 train, 976 val, labeled)
  Epochs:  50, batch=8, seq_len=16
  Variants:
    RN18-b (baseline):    seg=10, dice=0, edge=0, lcom=0
      → OE Dice=0.896, HD Dice=0.660, HD CErr=13.87px
    RN18-d (too strong):  seg=10, dice=1, edge=0.5, lcom=0.3, param_seg_dice=0.3
      → OE Dice=0.891, HD Dice=0.467 ❌ (over-constrained)
    RN18-e (moderate):    seg=10, dice=1, edge=0.2, lcom=0.1
      → OE Dice=0.891, HD Dice=0.650, HD CErr=12.34px  ✅ best for teacher
      Key: better HD CErr (-1.5px) than RN18-b, despite slightly lower OE
  Time:    ~1 min/epoch → ~50 min total

Stage 2: HD Distillation (pseudo-label → HD unlabeled)
  Script:  run_hd_distill.py (updated 2026-05-14)
  Loads:   RN18-e best_model.pth (was RN18-b)
  Key change (2026-05-14): param_seg_dice switched from Dice → BCE
    - BCE provides per-pixel gradients, edge pixels not drowned by interior
    - autocast(enabled=False) wrapper required (BCE unsafe inside autocast)
    - pred_soft.float(), target_mask.float() for type safety
  Data:    HD unlabeled (1033 train + 1033 val)
  Key:     param_seg_dice=1.0 (BCE between ellipse param mask and seg head)
  Result (prev RN18-b+Dice):  HD Dice=0.562→0.847, CErr=13.76→2.36px
  Epochs:  30

Stage 3: MBV2 Multi-Phase Training (student)
  Phase 1 — mbv2_ph1: OpenEDS supervised (stat+dyn+seg)
             → OE Dice=0.837, HD Dice=0.537
  Phase 2 — mbv2_ph2: +param_seg_dice + edge
             → HD Dice ↑ 0.537→0.751
  Phase 3 — mbv2_ph3: +HD mixed data, freeze seg head
             → HD Dice ↑ 0.751→0.862
  Phase 4 — mbv2_ph4: ❌ FAILED (pure K230 → Dice=0)
             Lesson: NEVER train on K230-only without OE anchor

Stage 4: Hybrid + Texture (K230+OE mixed)
  Script:  run_mbv2_mixed_tex.py (v1) / run_mbv2_mixed_tex_v2.py (v2)
  Loads:   rn18_experiments/mbv2_mixed_v4/best.pth
  Data:    OpenEDS (17K) + K230 (1K) mixed per-batch
  Loss (v2 changes applied to both scripts):
    OpenEDS:  seg=10, dice=1, edge=0.2, tex=1.0
    K230:     param_seg_dice=1.0 (BCE), edge=0.2, tex=1.0
              + center consistency: clamp(||pupil_center - iris_center|| - 5px, 0)
  v1→v2 deltas:
    - edge: 0.1 → 0.2 (stronger boundary supervision)
    - center threshold: 10px → 5px (tighter geometric constraint)
  Epochs:   30, lr=3e-5, batch=8
  Output:   rn18_experiments/mbv2_mixed_tex{,_v2}/best.pth
  Best (v1): K230 Dice=0.9084, OE CErr=1.86px

Stage 5: Fine-tune (low LR from best)
  Script:  run_mbv2_mixed_tex_ft.py (also updated to v2 params)
  Loads:   Stage 4 best.pth
  LR:      3e-5 → 15 epochs, batch=8
  Result:  K230 Dice peaked at 0.9231 (FT10), then overfit to 0.9135 (FT15)
  Lesson:  Stop at FT10-12 max for this LR schedule
```

## Model Architecture

```
T3EM_EncDec_Net (MobileNetV2 backbone, 3.5M trained / 35M total)
├── Encoder: MobileNetV2.features (1ch adapted from RGB)
├── Decoder (UNet): 5 stages (1280→256→128→64→32→16ch)
├── seg_head → 3ch (bg/iris/pupil)
└── K230_Regression_Head
    ├── head_static → 4 params: (ecx, ecy, r_eye, r_iris)
    └── head_dynamic → 8 params: (pcx, pcy, pa, pb, angle, _, icx, icy)
```

**Parameter semantics:**
- `d_pred[:, 0:2]` — pupil center (cx, cy)
- `d_pred[:, 2:5]` — pupil ellipse (a, b, angle) — a,b are diameters
- `d_pred[:, 6:8]` — iris center (icx, icy) — same coordinate space
- `s_pred[:, 0:4]` — eye center + radii → combined with d_pred[:,6:8] → iris ellipse
- **Center consistency** = `clamp(||d_pred[:,0:2] - d_pred[:,6:8]|| - 5px, 0)`

## Loss Functions

| Loss | Type | Source | Purpose |
|------|------|:-------|---------|
| `seg` (CE) | Cross-entropy | seg_head logits | Pixel segmentation (bg/iris/pupil) |
| `dice` | Dice | seg_head vs GT | Segmentation mask overlap |
| `param_seg_dice` | **BCE** ⬅️ changed 2026-05-14 | param mask vs seg head | Per-pixel gradient — edge pixels not drowned. See `training-pipeline-principles` principle #8 |
| `edge` | PupilEdgeGradientLoss | d_pred[:,0:5] + get_geometry | Radial gradient: pupil+iris dual path |
| `tex` | TextureLoss | seg_head + decoder features | Warp-pooled iris texture consistency |
| center_dist | Clamped L2 `clamp(d-5,0)` | d_pred[:,0:2] vs d_pred[:,6:8] | Custom: pupil vs iris center alignment |

## Key Design Decisions & Lessons

1. **Mixed data prevents catastrophic forgetting** — K230-only → Dice=0. OE+K230 mixed → stable.
2. **Edge loss helps students, not teachers** — RN18 (17M) doesn't benefit; MBV2 (3.5M) needs it. Confirmed by RN18-d (edge=0.5 → HD Dice collapsed to 0.467).
3. **BCE > Dice for edge-sensitive distillation** — Dice is region-dominant; BCE gives per-pixel gradients. But: BCE requires `autocast(enabled=False)` wrapper, slower initial convergence.
4. **Texture loss is the secret weapon** — K230 Dice jumped 0.889→0.908 when tex=1.0 added.
5. **Center threshold of 5px** — 10px too loose, <5px over-constrains (anatomical variation is 3-5px).
6. **Segmentation distillation is the foundation** — Without it, all downstream work fails.
7. **Center consistency is custom, not LCOM** — LCOM needs GT seg masks (unavailable for K230). Custom constraint compares pupil/iris centers from dynamic head directly.

## Current Experimental Results (2026-05-14)

| Experiment | Status | Key Metric |
|:-----------|:-------|:-----------|
| RN18-e (edge=0.2, lcom=0.1) | 🟢 Completed ✅ | OE Dice=0.891, HD Dice=0.650, HD CErr=12.34px |
| HD Distill (RN18-e teacher + BCE) | 🟢 Running | Ep3/30, Loss=0.373 (BCE scale) |
| MBV2 v2 (edge=0.2, center=5px) | ⏳ Queued | After HD distill completes |

## Quick Commands

```bash
# View running training
ssh work1 'tmux capture-pane -t <session> -p -S -5'

# Check GPU
ssh work1 'nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader'

# Tail training log
ssh work1 'tail -5 /mnt/nfs/eye_video_HD/code/rn18_experiments/<exp>/train.log'

# Kill and restart
ssh work1 'tmux kill-session -t <session>'
ssh work1 'tmux new-session -d -s <session>'
ssh work1 'tmux send-keys -t <session> "cd /mnt/nfs/eye_video_HD/code && /home/yakeworld/vllm_env/bin/python script.py --gpu 1" Enter'
```
