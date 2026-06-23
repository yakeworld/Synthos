# Paper Repair Cron — Two-Scan Workflow

**Created**: 2026-06-23 | **Proven on**: Cycle RP-1 (deepseek-v4-pro)

## Purpose

Document the standard paper-repair cron workflow: scan both the main pipeline AND the article_todo writing workspace for D10a issues, apply repairs to core-direction papers only, skip peripheral.

## Two-Scan Architecture

| Scan | Script | Target | Papers |
|:-----|:-------|:-------|:-------|
| Pipeline | `scripts/d8d10a-scan.py --all --base-dir /media/yakeworld/sda2/Synthos/outputs/papers` | Main pipeline (132 papers) | All papers with valid tex |
| Article_todo | `scripts/article-todo-d10a-scan.py` | Writing workspace (`~/桌面/article_todo/`) | Core direction papers with compiled PDFs |

## Direction Constraint Matrix

**Repair**: ✅ Core direction only
**Skip**: 🔴 Peripheral direction — do not repair, do not report details

Core = pupil/iris seg, 3D eyeball, SCC, BPPV, VOR, algorithm components, dataset audits, Synthos, AI teaching.
Peripheral = corneal, lens, vitreous, tear film, tinnitus, concussion, cochlear, etc.

## Standard Execution Flow

```
1. Run pipeline D10a scan → filter core-direction papers below 95%
2. Run article_todo D10a scan → filter core-direction papers below 95%
3. For each core paper below threshold:
   a. Identify orphan/zombie cause (missing bib entry, stale .bbl, wrong tex selected, etc.)
   b. Apply fix
   c. Recompile: pdflatex → bibtex → pdflatex×2 (for external .bib papers)
   d. Re-run scan to verify D10a=100%
4. Append results to agent-log.md via patch (NEVER write_file)
5. If no core-direction issues found AND no fixes applied → response is "[SILENT]"
```

## Common Fix Patterns (by symptom)

| Symptom | Most Likely Cause | Fix |
|:--------|:------------------|:----|
| 1-3 orphans, all in bib file | bib entry exists but bbl is stale | Recompile (pdflatex→bibtex→pdflatex×2) |
| 1 orphan, NOT in bib file | Missing bib entry | Add entry to .bib, recompile |
| D10a=0%, bib_source=none | No bib source found | Search for .bib, check tex for \bibliography |
| D10a=0%, bib_source=bbl, 0-byte .bbl | Empty .bbl from wrong compile | Delete .bbl, scan falls back to thebibliography |
| D10a ~65-85%, all orphans in .bib | Stale .bbl (wrong filename) | Delete stale .bbl, recompile |

## Pitfalls Specific to Cron Context

1. **Queue claims fix but scan disagrees**: paper-queue.json notes say D10a=100% from prior fix, but fresh scan shows 0%. The fix was ephemeral — likely bib file deleted after the fix date. Treat as fresh repair.

2. **Peripheral papers with D10a issues**: The scan may report peripheral papers below threshold. Do NOT fix them — skip silently. The direction constraint is absolute.

3. **Dual-Ellipse as canonical example**: Article_todo papers often have versioned tex files (v1-v6). The article-todo scan script handles version selection automatically — trust its tex choice.

4. **agent-log.md append-only**: Multiple cron jobs write to this file. Always use `patch` to append, never `write_file` which would overwrite other agents' entries.

## Example: Cycle RP-1 (2026-06-23)

- Pipeline: 93 scanned, 1 below threshold (orthokeratology, peripheral → skipped)
- Article_todo: 3 compiled, Dual-Ellipse at 95% with 1 orphan (mathot2018pupillometry)
- Fix: Added bib entry + recompile → 100% D10a
- Result: 0 core-direction issues remaining
