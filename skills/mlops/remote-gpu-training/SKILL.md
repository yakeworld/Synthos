---
name: remote-gpu-training
description: >-
  Remote GPU training workflow — SSH into a GPU server, set up Python env,
  scp training scripts, run background training via tmux, monitor progress,
  diagnose and fix common issues (path mismatches, missing modules, 
  workspace symlinks). Use when the user asks to run or fine-tune a model 
  on a remote GPU server.
version: 1.1.0
author: Synthos Agent
license: MIT
tags: [remote, gpu, training, fine-tune, tmux, ssh, mlops]
dependencies: []
---

# Remote GPU Training Workflow

Manage ML training jobs on remote GPU servers. This skill covers the **remote execution layer** — how to get code and data to the server, run training, and monitor it — not the training recipe itself (see `experiment-recipes` for that).

## ⚡ Trigger Decision: HOST vs DOCKER

Before anything else, decide execution mode:

| If task is... | Run on... | Reason |
|:--------------|:----------|:-------|
| **ML benchmark sweep** (sklearn, XGBoost, LightGBM, CV, model zoo, 34 models) | **Docker** (`science10`) | Environment isolation, reproducibility, conda has sklearn+numpy |
| **Heavy GPU training** (PyTorch, hours-long, custom model, multi-stage pipeline) | **Host** (`vllm_env` venv) | Direct GPU access, internet needed |
| **Single quick test** (<30s, no deps) | Either — Docker preferred for cleanliness | |

> **Default to Docker for ML benchmarks.** If you start running a benchmark on the host and the user says "work1不是有这个docker环境吗？", you missed this decision.

## Server Topology (SSH Aliases)

The user has two machines accessible via SSH config aliases:

| Alias | Hostname | GPU | Role |
|-------|----------|-----|------|
| `work1` | user-NF5468-M7-A0-R0-00 | 8× RTX 4090 (24GB each) | **Training server** — GPU training on HOST (`vllm_env`), ML benchmarks in `science10` Docker |
| `work2` | yakeworld-Precision-7920-Tower | 1× Quadro RTX 4000 (8GB) | **Local workstation** — light tasks, NotebookLM CLI, Hermes gateway |

### work1 (Training Server) Details

```bash
# SSH alias: work1
# User: yakeworld (SSH key auth)
# Data: /mnt/nfs/eye_video_HD/  (NFS mount, 28T, 10.20.43.5:/volume1/nfs)
# Python envs (HOST):
#   /home/yakeworld/vllm_env/        torch (preferred for training)
#   /home/yakeworld/sglang_env/      older torch
# Training code: /mnt/nfs/eye_video_HD/code/
# Model checkpoints: /mnt/nfs/eye_video_HD/code/rn18_experiments/{exp_name}/
# Docker containers:
#   science10 (my_pytorch, port 8809→8888) — ML BENCHMARKS & experiments
#   Several vLLM containers — MUST stay Exited (see Pitfall #7)
# NFS→container mount: /mnt/nfs → /workspace (bind mount in science10)
```

> **Execution path: GPU training runs on HOST; ML benchmarks/experiments run in science10 Docker.** Decision rule: if the task is a heavy GPU training loop (hours-long, custom model, multi-stage pipeline like RN18→distillation→student→hybrid), run it on HOST via `vllm_env` venv. If the task is an ML benchmark sweep (many models, scikit-learn/XGBoost/LightGBM, cross-validation, short runs), run it inside `science10` Docker for environment isolation and reproducibility. Ask the user if unsure.

### work2 (Workstation) Details

```bash
# SSH alias: work2
# Hardware: Dell Precision 7920 Tower, 1× Quadro RTX 4000 (8GB), Intel Xeon Silver 4214R
# CUDA: Driver v12020 — too old for newer PyTorch versions
# Docker: Only proxy containers (shadowsocks, npc) — NO GPU containers
# Installed: Hermes v0.13.0, NotebookLM CLI (authenticated)
```

> work2 is for lightweight tasks (NotebookLM maintenance, Hermes gateway) — not suitable for training.

## Workflow

### 1. Write the Training Script Locally

Write the Python training script on the local machine (under `/tmp/` or the project directory). Save with a `.py` extension.

**Key patterns to get right:**
- **Use absolute paths** — the script will run on the remote server. No relative paths unless you `cd` to the right directory first.
- **sys.path.insert** — add the code directory at the top so custom module imports work:
  ```python
  sys.path.insert(0, '/mnt/nfs/eye_video_HD/code')
  ```
- **Data paths** — use `/mnt/nfs/eye_video_HD/` NOT `/workspace/eye_video_HD/`. The `/workspace/` symlink only exists for root, not for yakeworld.
- **Save checkpoints** — save to `rn18_experiments/{exp_name}/` subdirectories.

### 2. Transfer to Remote Server

```bash
scp /tmp/your_script.py yakeworld@work1:/mnt/nfs/eye_video_HD/code/your_script.py
```

### 3. Verify Dependencies

Before running, test the script directly to catch missing packages:

```bash
ssh yakeworld@work1 \
  '/home/yakeworld/vllm_env/bin/python /mnt/nfs/eye_video_HD/code/your_script.py 1 2>&1 | head -30'
```

If you get `ModuleNotFoundError`, install the missing package:

```bash
ssh yakeworld@work1 \
  '/home/yakeworld/vllm_env/bin/pip install <package> -q'
```

### 4. Launch via tmux (Persistence)

**Method A — One-liner (for scripts that don't need stdin):**
```bash
ssh yakeworld@work1 \
  'tmux new-session -d -s <session_name> \
    "cd /mnt/nfs/eye_video_HD/code && \
     /home/yakeworld/vllm_env/bin/python your_script.py <gpu_id> \
     2>&1 | tee rn18_experiments/<exp_name>/train.log"'
```

**Method B — Two-step (for complex commands or multi-line arguments):**
```bash
ssh yakeworld@work1 \
  'tmux new-session -d -s <session_name>'
ssh yakeworld@work1 \
  'tmux send-keys -t <session_name> \
    "cd /mnt/nfs/eye_video_HD/code && \
     /home/yakeworld/vllm_env/bin/python your_script.py --arg value --gpu 1" Enter'
```

> Prefer **Method B** for scripts with complex CLI flags (spaces, special chars) — the one-liner in Method A can misinterpret quote nesting and cause silent failures.

**tmux flag meanings:**
- `new-session -d`: create detached (doesn't need a terminal)
- `-s <name>`: session name for later reference
- `send-keys -t <name>`: type text into the session's first window
- `Enter` (literal word, sent to tmux): press enter after the command
- `tee`: log to file AND show in tmux buffer

### 5. Monitor Training

```bash
# Quick process check
ssh yakeworld@work1 'ps aux | grep your_script | grep -v grep'

# View tmux output
ssh yakeworld@work1 'tmux capture-pane -t <session_name> -p -S -10'

# Tail the log file
ssh yakeworld@work1 'tail -5 /mnt/nfs/eye_video_HD/code/rn18_experiments/<exp_name>/train.log'

# Advanced: Find GPU-consuming processes (host-level, NOT Docker)
ssh yakeworld@work1 'fuser -v /dev/nvidia0 /dev/nvidia1 /dev/nvidia2 /dev/nvidia3 2>&1'
# This shows PIDs, owners, and whether training runs on HOST vs IN Docker

# Full GPU process breakdown
ssh yakeworld@<server> 'nvidia-smi --query-compute-apps=pid,used_memory,name --format=csv,noheader'
```

**Pro tip for multi-server environments**: Always check BOTH host-level and Docker-level processes:
```bash
ssh <server> '
  echo "=== HOST processes ==="
  ps aux | grep python | grep -v grep | grep -v docker
  echo "=== Docker processes ==="
  docker exec <container> ps aux 2>/dev/null | grep python | grep -v grep | grep -v jupyter
  echo "=== tmux sessions (host) ==="
  tmux list-sessions 2>/dev/null
  echo "=== GPU PIDs ==="
  fuser -v /dev/nvidia* 2>&1 | grep -v "nvidiactl\|nvidia-modeset\|nvidia-uvm"
'

### 4b. Docker Execution Path (ML Benchmarks only)

For ML benchmark sweeps (many models, sklearn/xgboost/lightgbm, cross-validation), use the `science10` Docker container:

**Step 1: Copy data & script to NFS mount**
```bash
# Create dirs on work1
ssh work1 "mkdir -p /mnt/nfs/synthos_data /mnt/nfs/experiments"

# SCP data and script from LOCAL machine
scp local_data.csv work1:/mnt/nfs/synthos_data/
scp script.py work1:/mnt/nfs/experiments/

# OR copy between host paths on work1 (if data already exists on host)
ssh work1 "cp ~/synthos_data/dataset.csv /mnt/nfs/synthos_data/"
```

**Step 2: Ensure paths match container mount**
- NFS `/mnt/nfs` → container `/workspace`
- Script should read from `/workspace/synthos_data/` (not host paths like `/home/yakeworld/...` or `/root/...`)
- Output should write to `/workspace/experiments/` (not `/home/yakeworld/...`)
- **Always patch the script's data-loading functions before copying**, or create a `_docker.py` variant

**Step 3: Verify ALL dependencies at once (critical — prevent 3+ retries)**

Run a single import check for ALL packages the script needs before starting:

```bash
ssh work1 'docker exec science10 /opt/conda/bin/python3 -c \
python3 -c \"import sklearn, xgboost, lightgbm, imblearn, numpy, pandas, scipy; print('ALL OK')\"'
# If ModuleNotFoundError: install ALL missing packages in one command
ssh work1 'docker exec science10 /opt/conda/bin/pip install <pkg1> <pkg2> -i https://pypi.tuna.tsinghua.edu.cn/simple'

> **Why this matters:** Running the script and discovering missing packages one-by-one wastes 3+ round trips. A single dependency check at the start eliminates this.
>
> Container uses **conda Python** at `/opt/conda/bin/python3` — NOT system `/usr/bin/python3`. Container **has no internet access** — all data must be pre-downloaded to NFS.

**Step 4: Run inside Docker**
```bash
# Simple run (visible output)
ssh work1 "docker exec -w /workspace/experiments science10 /opt/conda/bin/python3 script.py"

# Background run (via Hermes terminal tool)
terminal(command="ssh work1 'docker exec -w /workspace/experiments science10 /opt/conda/bin/python3 script.py'", background=true, notify_on_complete=true)
```

**Step 5: Retrieve results**
```bash
# Results written to /workspace/experiments/ → available at /mnt/nfs/experiments/
ssh work1 "cat /mnt/nfs/experiments/results.json"
# Or copy back locally
scp work1:/mnt/nfs/experiments/results.json .
```

**Key differences from HOST execution:**
| Aspect | HOST (vllm_env) | Docker (science10) |
|--------|-----------------|-------------------|
| Python | `/home/yakeworld/vllm_env/bin/python` | `/opt/conda/bin/python3` |
| GPU | Full 8× RTX 4090 | Limited/indirect |
| Internet | Yes (via Tailscale exit node) | **No** — preload data |
| Data path | `/mnt/nfs/...` | `/workspace/...` (=`/mnt/nfs/...`) |
| Use for | Heavy GPU training (hours) | ML benchmarks, CV sweeps, sklearn/XGBoost |

**Pitfall: don't hardcode host paths in scripts meant for Docker.** If the script was written for host execution (e.g. `/home/yakeworld/synthos_data/...`), patch the paths to use `/workspace/synthos_data/` before copying, or create a separate Docker variant.

### 6. Diagnose and Fix Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'X'` | Missing package in Python env | `pip install X` in the used environment |
| K230 dataset has 0 samples | Wrong glob path (uses `/workspace/` instead of `/mnt/nfs/`) | Change glob to `/mnt/nfs/eye_video_HD/...` |
| `No such file or directory` for code import | `sys.path.insert` not set or wrong path | Add `sys.path.insert(0, '/mnt/nfs/eye_video_HD/code')` |
| Training exits immediately, no log | Script crashed before writing | Run interactively first to see traceback |
| GPU 0% utilization after launch | Process died silently | Check `ps aux \| grep python` |
| `bash: python: command not found` | Environment not activated | Use full path: `/home/yakeworld/vllm_env/bin/python` |

### 7. Kill a Running Job

```bash
ssh yakeworld@work1 'pkill -f your_script.py'
ssh yakeworld@work1 'tmux kill-session -t <session_name>'
```

## Pitfalls

1. **Always use full Python path** — the yakeworld user doesn't have `python` in PATH for conda environments. Use `/home/yakeworld/vllm_env/bin/python` explicitly.
2. **No `/workspace/` for yakeworld on HOST** — the `/workspace/` -> `/mnt/nfs/` symlink only exists for root on the host. If you create it as yakeworld, it may fail silently. **However**, inside the `science10` Docker container, `/workspace/` IS the correct path (bind-mounted from `/mnt/nfs`). Context matters: host scripts use `/mnt/nfs/...`, Docker scripts use `/workspace/...`.
3. **tmux sessions persist after job ends** — the tmux window stays until you explicitly kill it.
4. **Remote logs are inaccessible locally** — if you need the log locally, scp it back after the job finishes.
5. **`ssh -t` interferes with backgrounding** — don't use `-t` flag if running via `terminal(background=true)`. Use plain `ssh`.
6. **`pkill` kills the SSH connection too** — if you `pkill -f` a script that the SSH session itself is running, it kills the pipe. Kill from a *separate* connection, or kill via tmux.
7. **NEVER start vLLM containers on work1 without explicit user approval.** The user has been burned by this — vLLM consumes 4× GPUs (TP=4) during training. The `vllm-qwen3-nvfp4` containers exist but MUST stay `Exited` unless the user explicitly asks. This is a hard rule: if the user hasn't mentioned vLLM, don't mention it either. Check `docker ps -a | grep vllm` to confirm status; do NOT offer to start them.
8. **Training runs on HOST; ML benchmarks run in Docker** — heavy GPU training (RN18→distillation→student→fine-tune) runs on the host `vllm_env` venv. ML benchmarks (sklearn, XGBoost, cross-validation sweeps, model zoo) run inside `science10` Docker. Check host processes with `ps aux` and `fuser -v /dev/nvidia*`; check Docker processes with `docker exec science10 ps aux`. When running a benchmark, the user's expectation is Docker first — default to Docker unless the task is clearly a GPU training job.
9. **Zombie (defunct) python processes from GPU training** — after training completes, zombie python processes ([python] <defunct>) may accumulate from PyTorch data workers. These are harmless but clutter `ps aux`. They're cleaned on next reboot or can be manually reaped by killing their parent processes.
10. **tmux capture on running training** — `tmux capture-pane -t <session> -p -S -50` captures the last 50 lines of scrollback. But if the training script writes progress bars with `\\\\r` (carriage return), the captured output shows the final state only, not the full log. Use the tee'd log file instead for reliable history.
11. **tmux one-liner (Method A) fails silently for complex commands** — if the script has multi-line arguments, quotes embedded in strings, or `heredoc` in the tmux command, the shell nesting causes silent failures (no session created, no log). Always fall back to **Method B (send-keys)** for anything beyond the simplest `python script.py N` pattern. Verify the session exists with `tmux list-sessions` after creation.
12. **cv2 (OpenCV) is only available in vllm_env** — the default `/usr/bin/python3` lacks `cv2`. Always use `/home/yakeworld/vllm_env/bin/python` for training scripts. Verify: `ls /home/yakeworld/vllm_env/bin/python3`.
13. **Run the full pipeline top-down** — don't skip the teacher (RN18) training and jump straight to distillation or student training. The user expects the complete pipeline: RN18 → hd_distill → MBV2 multi-phase → hybrid + texture → fine-tune. Always ask: "has the teacher been trained yet?" before running student training.
14. **Experiment config modifications**: When adding a new experiment variant to an existing script (e.g., adding `RN18-e` to `run_resnet18_openeds.py`), use a Python fix script on the remote, NOT `sed`. `sed` with inline Python heredocs via SSH breaks on quote/backslash nesting. Workflow:
    - Copy the original: `cp script.py script_v2.py`
    - Write a Python fix script to `/tmp/fix_script.py` on remote
    - Execute: `ssh work1 "python3 /tmp/fix_script.py"`
    - Verify: `ssh work1 "python3 -m py_compile /path/to/modified.py && echo OK"`
    - **Critical: verify the argparse `choices` list matches new experiment names** — sed replacements that match partial strings (e.g. replacing 'RN18-d' in the experiments dict also hit it in `choices=[...]`) can create malformed choices.
17. **`docker exec` via SSH produces benign ioctl warnings** — running `docker exec ...` from an SSH command produces `bash: 无法设定终端进程组 (-1): 对设备不适当的 ioctl 操作` and `bash: 此 shell 中无任务控制`. These are NON-FATAL — ignore them. The script runs correctly.
18. **Always use `-w /workspace/experiments` with `docker exec`** — the working directory inside the container defaults to `/` if not specified with `-w`. Always set it to the directory where your scripts live, e.g. `docker exec -w /workspace/experiments science10 /opt/conda/bin/python3 script.py`.
19. **Conda Python path required** — the container's system Python (`/usr/bin/python3`) lacks all ML packages. Always use `/opt/conda/bin/python3` for execution and `/opt/conda/bin/pip` for package management.
20. **Docker container has no internet** — the `science10` container cannot reach GitHub/PyPI/UCI. All data must be pre-downloaded to `/mnt/nfs/synthos_data/` from the host (which has internet via Tailscale exit node). Use `curl` or `wget` on the host, then SCP or copy to NFS mount. PIDD/Early Diabetes/CDC datasets should be pre-cached.
21. **Path mismatch between host and container** — scripts written for host execution use paths like `/home/yakeworld/synthos_data/` or `/root/synthos_data/`. When running in Docker, paths must start with `/workspace/synthos_data/`. Always patch the script's data-loading functions before transferring, or create a `_docker.py` variant. Verify with `head -5` before running.

### 9. Modify Multiple Scripts on Remote (safely)

When you need to edit Python files on the remote server (e.g., updating hyperparameters across scripts):

**Simple single-file replacements** (works for unique strings):
```bash
ssh yakeworld@work1 "sed -i 's/old_string/new_string/g' /path/to/file.py"
```

**Multi-file same change:**
```bash
ssh yakeworld@work1 "sed -i 's/old_string/new_string/g' /path/to/file1.py /path/to/file2.py"
```

**Complex multi-line edits** (adding new experiment configs, restructuring code):
- Write a Python fix script to `/tmp/fix_script.py` on the remote
- Execute it: `ssh yakeworld@work1 "python3 /tmp/fix_script.py"`
- Always verify with `python3 -m py_compile /path/to/modified_file.py`

**Critical: verify syntax after edits:**
```bash
ssh yakeworld@work1 "python3 -m py_compile /path/to/modified_file.py && echo 'Syntax OK'"
```

> **Pitfall**: `sed` with inline Python heredocs via SSH can easily break due to quote/backslash escaping. For multi-line Python edits, write a `.py` fix script to `/tmp/` on the remote and execute it there. This avoids all SSH escaping issues.

## See Also

- `experiment-recipes` — ML training recipes (architecture selection, optimizer config, debugging checklist, etc.)
- `references/t3em-training-pipeline.md` — T3EM eye tracking multi-stage training pipeline (teacher→distillation→student→hybrid→fine-tune) for context on how training scripts connect
