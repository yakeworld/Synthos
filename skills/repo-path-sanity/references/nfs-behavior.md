# NFS Filesystem Behavior (/mnt/nfs)

## Environment Constraint

`/mnt/nfs` is extremely slow — Python `os.walk()`, `du -sh`, and shell loops
over all entries will **timeout at 300s** after producing a single output line.

## Correct Commands

### Shallow listing (always use timeout 5-10)
```bash
timeout 5 ls /mnt/nfs/ | head -50
timeout 5 ls -la /mnt/nfs/<single-dir>/
timeout 5 du -sh /mnt/nfs/<single-dir>/
```

### Shallow tree traversal
```bash
timeout 10 find /mnt/nfs -maxdepth 2 -type d
find /mnt/nfs -maxdepth 3 -name "*.py" 2>/dev/null | head -20
```

### Single-directory du (one at a time, with timeout)
```bash
timeout 10 du -sh /mnt/nfs/<one-dir>/ 2>/dev/null
```

## What NOT to Do

| Action | Why it fails |
|--------|-------------|
| `os.walk('/mnt/nfs')` without depth limit | Timeout after 300s, single entry processed |
| `du -sh /mnt/nfs/* | sort` in bash loop | Timeout after first entry (NFS latency) |
| `glob.glob('/mnt/nfs/**/*.py', recursive=True)` | Timeout during directory traversal |
| `ls -la /mnt/nfs/ | while read ...` | Timeout mid-loop, partial output |

## Diagnosis Steps

1. `timeout 5 ls /mnt/nfs/ | head -50` — top-level only
2. `timeout 5 du -sh /mnt/nfs/<single-dir>/` — one dir at a time
3. `timeout 10 find /mnt/nfs -maxdepth 2 -type d` — shallow tree walk
4. If even `ls` hangs → NFS may be disconnected; `df -h /mnt/nfs`

## Project Anatomy (as of 2026-06-10)

`/mnt/nfs` hosts the eye-tracking training pipeline:

```
/mnt/nfs/
├── eye_video_HD/          # Video source: iris/pupil tracking
│   ├── 260401_train/      # VOR-MobileNet v1 pipeline
│   ├── 260402_train/      # HD input, OpenEDS mix
│   ├── 260420_yolo/       # YOLO detection sub-pipeline
│   └── 260604_label/      # Post-label processing
├── workspace/
│   └── training_pipeline/
│       └── labels_optimized/  # Optimized label outputs
├── ritout_params_final/   # Parkinson eye-tracking data source
├── experiments/           # Experiment records (catboost, etc.)
└── Synthos/               # Knowledge base system
```

Local copies in `~/下载/` and `~/文档/` contain training scripts with the most
recent versions:
- `train_ablation.py` (51KB) — 27-group ablation study (T3EM model)
- `train_ddpv6_gru_plus_pupil_new-Copy1.py` (39KB) — 7-GPU DDP
- `train_hybrid_480x800.py` (28KB) — Hybrid model, 480x800 letterbox

**Note:** `models/` package (T3EM_EncDec_Net, LossEngine, datasets) is imported
via `from models.dataset import ...` but was not found in `/mnt/nfs`. It resides
in the training working directory at runtime.