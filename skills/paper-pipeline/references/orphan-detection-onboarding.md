# Orphan Detection & Batch Onboarding

> **发现日期**: 2026-06-18  
> **触发场景**: Paper Repair Agent cron 运行时发现 9 篇论文有 paper.tex + state.json 但不在 paper-queue.json 中  
> **根因**: 论文通过 Track B→Track A 晋升或其他渠道产生 paper.tex，但队列从未同步

## 检测脚本

```python
# orphan_detect.py — 找出有 paper.tex 但不在 paper-queue.json 中的论文
import os, json

PAPERS_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers'
QUEUE_PATH = os.path.join(PAPERS_DIR, 'paper-queue.json')

with open(QUEUE_PATH) as f:
    queue = json.load(f)

queue_ids = {p['paper_id'] for p in queue['papers']}

unregistered = []
for d in sorted(os.listdir(PAPERS_DIR)):
    if d.startswith('_') or d.startswith('.'):
        continue
    full = os.path.join(PAPERS_DIR, d)
    if not os.path.isdir(full):
        continue
    
    tex_files = []
    for root, dirs, files in os.walk(full):
        for f in files:
            if f == 'paper.tex':
                tex_files.append(os.path.relpath(os.path.join(root, f), full))
    
    if tex_files and d not in queue_ids:
        unregistered.append((d, tex_files))

print(f'Papers in queue: {len(queue_ids)}')
print(f'Unregistered (with paper.tex): {len(unregistered)}')
for name, texs in unregistered:
    print(f'  {name}: {texs}')
```

## 快速状态扫描

```bash
# 检查每篇未注册论文是否有 state.json 和 bib
cd /media/yakeworld/sda2/Synthos/outputs/papers
for d in <orphan-list>; do
  has_state=""
  [ -f "$d/state.json" ] && has_state="state.json" || has_state="NO_STATE"
  tex_count=$(find "$d" -name "paper.tex" | wc -l)
  bib_count=$(find "$d" -name "*.bib" | wc -l)
  echo "$d | state=$has_state | tex=$tex_count | bib=$bib_count"
done
```

## 批量加入 paper-queue.json

```python
# orphan_onboard.py — 最多 N 篇一批，生成符合格式的 queue entry
import json, os
from datetime import datetime, timezone

PAPERS_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers'
QUEUE_PATH = os.path.join(PAPERS_DIR, 'paper-queue.json')
MAX_PER_RUN = 5  # cron 单次上限

with open(QUEUE_PATH) as f:
    queue = json.load(f)

existing_ids = {p['paper_id'] for p in queue['papers']}
ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
onboarded = []

# candidates 来自 orphan_detect.py 的输出，按需填入
candidates = [...]
count = 0

for paper_id in candidates:
    if count >= MAX_PER_RUN:
        break
    
    state_path = os.path.join(PAPERS_DIR, paper_id, 'state.json')
    if not os.path.exists(state_path):
        print(f"SKIP {paper_id}: no state.json")
        continue
    
    with open(state_path) as f:
        state = json.load(f)
    
    qs = state.get('quality_score', 60)
    gate = state.get('gate_status', 'PENDING')
    steps = state.get('steps_completed', [])
    d10a = '?'
    d10a_scan = state.get('d8_d10a_scan')
    if isinstance(d10a_scan, dict):
        d10a = d10a_scan.get('d10a', '?')
    
    entry = {
        "paper_id": paper_id,
        "status": "completed",
        "reason": "orphan_onboarded",
        "current_step": state.get('current_step', 'publication'),
        "quality_score": qs,
        "gate_status": gate,
        "steps_completed": steps[:10],
        "last_updated": ts,
        "notes": {
            f"orphan_onboarding_{ts[:10]}": f"Orphan onboarded from disk. qs={qs}, gate={gate}, D10a={d10a}, steps={len(steps)}."
        }
    }
    
    queue['papers'].append(entry)
    onboarded.append(paper_id)
    count += 1

with open(QUEUE_PATH, 'w') as f:
    json.dump(queue, f, indent=2, ensure_ascii=False)

print(f"Onboarded: {len(onboarded)}/{len(candidates)}")
print(f"Queue size: {len(queue['papers'])}")
```

## 幽灵条目检测

幽灵条目 = paper-queue.json 中有记录但实际目录不存在（仅在 `_knowledge_only/` 中有残留）

```python
import os, json

PAPERS_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers'
QUEUE_PATH = os.path.join(PAPERS_DIR, 'paper-queue.json')

with open(QUEUE_PATH) as f:
    queue = json.load(f)

ghosts = []
for p in queue['papers']:
    pid = p['paper_id']
    dir_path = os.path.join(PAPERS_DIR, pid)
    if not os.path.isdir(dir_path):
        ghosts.append(pid)

print(f"Ghost entries: {len(ghosts)}/{len(queue['papers'])}")
# 大多数幽灵在 _knowledge_only/ 中有残留目录，需批量 mv 或确认
```

## 2026-06-18 实战发现

| 指标 | 数值 |
|:-----|:-----|
| 未注册论文（有 paper.tex 不在 queue） | 9 |
| 本轮入职 | 5 (达到上限) |
| 剩余待入职 | 4 |
| 幽灵条目（queue 有但目录不在 papers/） | 60 |
| 幽灵根因 | _knowledge_only/ 晋升后目录未移动 |

**剩余待入职**: off-axis-iris-normalization-correction, optic-nerve-head-deformation-ODE, pan-PINN, vestibular-adaptation-ODE
