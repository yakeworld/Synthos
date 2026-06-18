# Batch Processing Race Conditions — Real-World Cases

Observed 2026-05-15 during NotebookLM batch optimization (cron job queue monitoring).

## Case 1: S2 Temp File Vanishes Between Steps

**Symptom**: `enhance-notebook.sh` Step 2 (PDF download) succeeds — finds papers, downloads PDFs and PMC text. Step 3 (LaTeX generation) fails with:

```
Traceback (most recent call last):
  File "<stdin>", line 4, in <module>
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/s2_data_90cd3a82'
```

**Root cause**: `enhance-notebook.sh` has `set -e` and reads `/tmp/s2_data_${NOTEBOOK_ID}` in TWO independent Python heredocs (line 81 and line 149). Between them, another parallel process (also running `enhance-notebook.sh` in the same batch) exits and runs `rm -f "/tmp/s2_data_${NOTEBOOK_ID}"` on line 234 — cleaning up its OWN file. But in this case, the NOTEBOOK_ID `90cd3a82` is unique per process, so the cleanup shouldn't affect other processes.

**More likely root cause**: A second batch-runner process was running concurrently despite the global lock, because the cron job's lock check used `cat`/`test -f` on a `mkdir`-created directory lock (see Case 2). Both batch runners picked the same notebook (`90cd3a82`) from the queue. One finished Step 2 and cleaned up. The other tried Step 3 with the now-deleted file.

**Fix (planned)**: 
1. Fix cron job lock check to use `test -d`
2. In `enhance-notebook.sh`, re-fetch S2 data before Step 3 if temp file is missing
3. Better: pass parsed S2 data between Steps 2-3 via a shared Python script or inline-passed JSON

**Workaround**: Re-run the failed notebook. The S2 API is protected by mutex (`/tmp/.hermes_s2_lock`), so the data is fetched fresh.

## Case 2: Directory-Based Lock Misdetection

**Symptom**: Cron job checks `cat /tmp/.hermes_batch_lock 2>/dev/null; echo "EXIT:$?"` — gets exit code 1 — reports "no lock". But `batch-runner.sh` uses `mkdir /tmp/.hermes_batch_lock` which creates a **directory**, not a file.

**Impact**: Two batch-runner instances launch concurrently, both processing the same queue items, causing duplicate work and race conditions on temp files.

**Fix**: Always use `test -d /tmp/.hermes_batch_lock` for lock detection in monitoring scripts.

## Case 3: BATCH_LOG.md Entries Not Written

**Symptom**: Batch completes with 3 items (2 ✅, 1 ❌) but BATCH_LOG.md doesn't get the new entry.

**Root cause**: The batch-runner reads the queue at start, then launches 3 sub-processes. By the time sub-processes finish and the script writes the log, another batch-runner instance has already updated the queue. The `BATCH_NUM` counter is stale (`grep -c '^|' "$LOG" + 1`), but the actual log write may fail silently or the results string may be empty because the queue items no longer match the original pick.

**Defense**: Not critical — the QUEUE.md has the authoritative progress data. The BATCH_LOG is supplementary.

## Script Paths

- Queue: `/media/yakeworld/sda2/Synthos/outputs/papers/QUEUE.md`
- Batch log: `/media/yakeworld/sda2/Synthos/outputs/papers/BATCH_LOG.md`
- Batch runner: `/media/yakeworld/sda2/Synthos/scripts/batch-runner.sh`
- Per-notebook enhancer: `/media/yakeworld/sda2/Synthos/scripts/enhance-notebook.sh`
- Lock (directory): `/tmp/.hermes_batch_lock`
- S2 API lock: `/tmp/.hermes_s2_lock`
- NotebookLM lock: `/tmp/.hermes_notebooklm_lock`
- S2 temp data: `/tmp/s2_data_${NOTEBOOK_ID}`

## Timeline (2026-05-15)

```
14:24 — Batch 1: headmount-et-lit ✅, eye-iris-biometric-lit ✅
14:35 — Batch 2: shape-prior-lit ❌, stat-shape-model-lit ✅, iris-3d-reconstruct-lit ✅
14:31 — Batch 3 (cron): headmount ✅, eye-iris ✅, shape-prior ❌ [concurrent with Batch 2]
14:46 — Batch 3 completes; QUEUE.md shows Done: 16, Remaining: 8
```

Note: Batch 2 and Batch 3 ran concurrently due to the lock-check bug (Case 2). Shape-prior-lit was picked by both and failed in both.
