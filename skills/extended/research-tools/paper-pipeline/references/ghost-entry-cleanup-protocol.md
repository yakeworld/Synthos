# Paper Repair Agent — Ghost Entry Cleanup Protocol

> Added 2026-06-19. Captures the pattern for detecting and cleaning up paper-queue.json entries whose directories have been moved to `_archive/` or `_drafts_archive/`.

## Trigger

Paper Repair Agent cron run discovers queue entries with low QS or FAIL gate, but the corresponding directory does not exist under `papers/`.

## Detection Script

```python
import os, json

BASE = "/media/yakeworld/sda2/Synthos/outputs/papers"

with open(f"{BASE}/paper-queue.json") as f:
    q = json.load(f)

ghosts = []

for p in q['papers']:
    pid = p['paper_id']
    dp = os.path.join(BASE, pid)
    
    if os.path.isdir(dp):
        continue  # directory exists, not a ghost
    
    # Search archive locations
    location = None
    for d in ['_archive', '_drafts_archive', '_knowledge_only']:
        archive_path = os.path.join(BASE, d, pid)
        if os.path.isdir(archive_path):
            location = d
            break
    
    if not location:
        location = 'missing'
    
    ghosts.append({
        'paper_id': pid,
        'location': location,
        'old_status': p.get('status'),
        'old_qs': p.get('quality_score'),
        'old_gate': p.get('gate_status'),
    })

# Update queue entries
for p in q['papers']:
    if p['paper_id'] in [g['paper_id'] for g in ghosts]:
        g = next(g for g in ghosts if g['paper_id'] == p['paper_id'])
        p['status'] = 'archived'
        p['reason'] = f'ghost_entry_cleanup: directory in {g["location"]}'
        if 'notes' not in p:
            p['notes'] = {}
        p['notes']['ghost_cleanup_2026-06-19'] = (
            f"Directory in {g['location']}. Marked archived. "
            f"Old status: {g['old_status']}, qs={g['old_qs']}, gate={g['old_gate']}"
        )
        p['last_updated'] = '2026-06-19T20:30:00Z'
```

## 2026-06-19 Run Data

| Paper ID | Location | Old QS | Old Gate | Action |
|:----------|:---------|:------:|:---------|:-------|
| 3d-pupil-localization | _archive/ | 55 | PASS | → archived |
| 3wd-framework-trustworthy-clinical-ai | _archive/ | 25 | FAIL | → archived |
| intraocular-pressure-ODE | _archive/ | 75 | HARD_FAIL | → archived |
| eye-tracking-4d | _drafts_archive/ | 68 | CONDITIONAL | → archived |
| cuteye-model | _drafts_archive/ | 78 | CONDITIONAL | → archived |
| automated-label-production-pipeline-for-eye-tracking | missing | 0 | PASS | → archived |

## Related

- Trap #28: 未注册孤儿（disk→queue，纸在盘不在队）
- Trap #41: 幽灵条目逆方向（queue→disk，队在盘不在）
