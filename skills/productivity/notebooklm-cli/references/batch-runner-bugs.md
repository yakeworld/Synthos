# batch-runner.sh & enhance-notebook.sh — Known Bugs

Verified 2026-05-15 during cycle 4 batch run (shape-prior-lit).

## Bug 1: Double `papers/papers/` in PDF Check Path

**File**: `/media/yakeworld/sda2/Synthos/scripts/batch-runner.sh`
**Line**: ~63

```bash
OUTDIR="/media/yakeworld/sda2/Synthos/outputs/papers"
# ...
PDF="$OUTDIR/papers/$PROJ/paper.pdf"
#    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    resolves to: .../outputs/papers/papers/shape-prior-lit/paper.pdf
#    should be:   .../outputs/papers/shape-prior-lit/paper.pdf
```

The variable `OUTDIR` already ends with `/papers`, so appending `/papers/` doubles it.

**Fix**: Change to `PDF="$OUTDIR/$PROJ/paper.pdf"`

**Impact**: Every run reports ❌ in BATCH_LOG.md with Fail=1, even when paper.pdf was successfully generated. Metrics show zero successful runs, which is misleading.

## Bug 2: QUEUE.md Not Updated After Completion

**File**: `/media/yakeworld/sda2/Synthos/scripts/batch-runner.sh`

The script header claims "完成后更新队列和日志", but only BATCH_LOG.md is written. The QUEUE.md table rows are never modified.

**Impact**: Same item gets picked on every cron cycle. Queue stagnates until manually updated. The 2026-05-15 session had to do a manual patch (patch QUEUE.md via file editing).

**Fix**: Add a Python heredoc after the result check that:
1. Reads QUEUE.md
2. Removes the processed item's row from Queue table
3. Adds a Done bullet: `- ✅ `<notebook_id>` <title> → <project-name>`
4. Increments Done counter, decrements Remaining counter
5. Writes back to QUEUE.md

## Bug 3: enhance-notebook.sh Uploads Unsupported Formats

**File**: `/media/yakeworld/sda2/Synthos/scripts/enhance-notebook.sh`
**Lines**: 225-229

```bash
for f in "$OUTDIR/paper.tex" "$OUTDIR/references.bib" "$OUTDIR/paper.pdf"; do
```

The .tex and .bib uploads always fail:
- `.bib` → HTTP 400 (NotebookLM doesn't accept BibTeX format)
- `.tex` → HTTP 400 (NotebookLM doesn't accept LaTeX source)

Only `.pdf` and `.md` files are accepted.

**Fix**: Change the loop to only upload paper.pdf:
```bash
for f in "$OUTDIR/paper.pdf"; do
```
Or add a glob for .md files if they exist:
```bash
for f in "$OUTDIR/paper.pdf" "$OUTDIR/paper.md"; do
    # ...
done
```

## Bug 4: `set -e` + Subprocess Exit Code Interaction

**File**: `/media/yakeworld/sda2/Synthos/scripts/batch-runner.sh`, line 9

```bash
set -e
# ...
bash "$SCRIPT" "$NID" "$QUERY" "$PROJ"
RC=$?
```

When `bash "$SCRIPT" ...` returns non-zero, `set -e` in the parent script can cause unpredictable behavior depending on bash version. Some versions abort immediately (before the PDF check and log write), others let it slide.

**Fix**: Guard the call:
```bash
bash "$SCRIPT" "$NID" "$QUERY" "$PROJ" || true
RC=$?
```
Or remove `set -e` and use explicit error handling.

## Reproduction

```bash
# Verify Bug 1:
/usr/bin/test -f /media/yakeworld/sda2/Synthos/outputs/papers/papers/shape-prior-lit/paper.pdf
echo $?  # 1 — not found (wrong path)
/usr/bin/test -f /media/yakeworld/sda2/Synthos/outputs/papers/shape-prior-lit/paper.pdf
echo $?  # 0 — found (correct path)

# Verify Bug 3:
notebooklm source add /media/yakeworld/sda2/Synthos/outputs/papers/shape-prior-lit/paper.tex
# → HTTP 400
notebooklm source add /media/yakeworld/sda2/Synthos/outputs/papers/shape-prior-lit/references.bib
# → HTTP 400
notebooklm source add /media/yakeworld/sda2/Synthos/outputs/papers/shape-prior-lit/paper.pdf
# → ✅ Uploaded
```
