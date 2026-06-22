---

name: paper-references-scanning
description: "Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate),   orphans, zombies. Class of tasks: LaTeX reference integrity auditing."
author: Synthos
license: MIT
version: 1.0.0
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: "Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate), orphans, zombies."
    signature: |
      paper_dir: str -> scan_result: dict | scan_result: dict (d8, d10a, orphans, zombies, bib_health_report)
    related_skills: [knowledge-extraction, knowledge-acquisition, paper-cron-scan, paper-pipeline]



---



## IO_CONTRACT

- **input**: `paper_dir: str, scan_type: str` — 用户请求描述、上下文信息
- **output**: `result: dict — D8, D10a, orphans, zombies`

> 对应原则：P2（机械原子暴露输入输出规范）




# Paper References Scanning (D8/D10a)

## Scope
Scanning LaTeX paper directories for reference integrity metrics.

## Pitfalls

### DOI regex is case-insensitive and handles multiple formats
Bib DOI fields appear as `doi = {value}`, `DOI = {value}`, or `doi="value"`.
- WRONG: `r'[Dd][Oo][Ii]\s*=\s*"\\{?([^}"\s]+)\}?"?'` — the `"?` around `{` is too strict; it requires the quote to match the brace style, causing zero matches.
- CORRECT: `r'(?:doi|DOI)\s*=\s*(?:["{]?([^}"\s]+?)["}]?)'` — matches all common DOI formats regardless of quote/brace nesting.
- Even simpler: `r'doi\s*=\s*\{([^}]+)\}'` for standard BibTeX format.

### Bib files exist in multiple locations beyond the canonical search path
The canonical skill searches `06-references/references.bib → {name}.bib → references.bib → enhanced_refs/enhanced.bib`. In practice, bib files are also found:
- At paper root level (e.g., `<paper>/references.bib`)
- In `09-manuscript/<paper>/references.bib` subdirectories
- In any `.bib` file directly under the paper directory
- In deeply nested directories like `01-manuscript/<paper>/references.bib`

When scanning, expand to: first check `06-references/references.bib`, then `<paper>/references.bib`, then any `.bib` in `<paper>/`, then fall back to `01-manuscript/<paper>/` and `09-manuscript/<paper>/`.

### Papers with \bibitem{} in thebibliography but zero \cite{} calls

Some papers list references via raw `\bibitem{}` in the `thebibliography` environment but never call them with `\cite{}` in the body. This results in D8 counting the bibitems but D10a=0% (no citations to match). These are real papers with references — the `\cite{}` may be missing, or the references may be uncited. Detect this pattern: `cited_count == 0 and bibitem_count > 0`.

**Repair**: Previously labeled "Cannot auto-repair" — but a systematic mapping from bibitem keys to prose mentions works when the prose already names the referenced authors/findings. See `references/zero-citation-auto-repair.md` for the full 5-step methodology (proven on 182-accommodation-ciliary-muscle-ODE: 0% → 100%, 13/13).

### `\\cite` regex uses single-escape in raw strings
`re.compile(r'\\\\cite')` — two backslashes in source, regex engine interprets as one literal backslash.
- `r'\\\\\\\\cite'` → matches double-backslash → WRONG for standard tex files
- `r'\\cite'` → `\c` is invalid regex escape → SyntaxError
- Correct: `r'\\\\cite'`

### Comment detection must distinguish `%` from `\%`
`%%` and `%` at line start = comment. But `$13.9\%$` or `~\%` are NOT comments.
Check `line.lstrip().startswith('%')` only.

### ⚠️ Scan Script Discrepancy: v3 vs v7 Produce Different Metrics (2026-06-20)

Two scan scripts exist with **different algorithms**, producing non-comparable results:

| Script | D8 Definition | D10a Definition | When no-cites |
|--------|--------------|-----------------|---------------|
| `paper-d8-d10a-scan/scripts/scan.py` (v3) | `1 - orphans/cites` (match rate) | `1 - zombies/bib` (consistency) | Not applicable (separate status) |
| `paper-references-scanning/scripts/d8d10a-scan.py` (v7) | Raw bib entry count | `matched/total_cites` | Auto=100% |

**Key difference**: v7 with no-cites auto-sets D10a=100% (self-referenced), producing 91/93 papers at D10a=100%. v3 produces only 12/94 PASS (D8=1.0 AND D10a=1.0). These are measuring different things.

**Rule**: G1-G7 pipeline gates use **v3 metrics** (paper-d8-d10a-scan). Use v7 only for raw inventory and structural audit. When reporting scan results, always state which script was used and what its D8/D10a definitions are.

### Reference directory must be normalized before scanning (2026-06-18 实战)
pima-crispdm管线中`06-references/`根目录包含7个旧管线遗留PDF（不属于当前Bib），pdfs子目录有44个PDF。这种目录结构错乱会导致D10a扫描结果不可靠——PDF数量与Bib条目数完全不匹配。

**修复流程（在扫描前执行）**：
1. 读取当前Bib的bib keys
2. 删除根目录中不属于当前Bib的所有文件（包括PDF、元数据文件）
3. 从子目录（pdfs/）中提取与当前Bib匹配的PDF到根目录
4. 对名称不匹配的Bib key创建符号链接
5. 确认根目录保持扁平：PDF + .bib（空子目录可选）
6. 然后再运行D8/D10a扫描

**参考**: paper-pipeline Skill.md Trap #35-#36（参考文献目录标准化模式）。

### Bib files exist in multiple locations beyond the canonical search path

### Bib keys can contain hyphens
Use `[^\s,;]+?` instead of `\w+` for bib key capture (`Norgeot2020MI-CLAIM` has `-`).

### Bib key prefix stripping
`bib_key_re` captures `@EntryType{key,` including the prefix. The script strips it by finding `{`, taking after it, then finding `,` and taking before it. Without this, `@Article{Ahmad2020,` won't match cite key `Ahmad2020`, causing false orphans and zombies.

### Commented `\\\\bibitem{}` must be excluded from D8
Only count uncommented `\\bibitem{}` for D8.

### External .bib papers: bibitems live in .bbl, NOT in .tex (2026-06-23)

Papers using `\bibliography{references.bib}` compile via bibtex, which generates a `.bbl` file containing the real `\bibitem{}` entries. The `.tex` file may contain only **template placeholder bibitems** like `\bibitem{label}` and `\bibitem{lamport94}` — these are NOT the actual references.

**Trap**: Grepping the `.tex` file for `\bibitem{}` on an external-bib paper finds only 2 template entries while the paper has 30+ real references. D10a appears to be 0% when it's actually 100%.

**Fix**: Always check for `.bbl` file first. If `.bbl` exists, extract bibitems from it. Only fall back to inline thebibliography in `.tex` when no `.bbl` is found. The `scripts/d8d10a-scan.py` handles this automatically — do NOT use ad-hoc shell grep.

**Detection heuristic**: If `grep -c '\\bibitem' paper.tex` returns ≤3 but `grep -c '\\cite' paper.tex` returns >10, the paper almost certainly uses external .bib → look for .bbl.

### Stale .bbl from older tex revision (2026-06-22)

When a paper undergoes multiple revisions, the .bbl filename may not match the .tex filename (e.g., `revision20241117.bbl` but tex is `revision20241118v3.tex`). The scan script finds the stale .bbl (alphabetically first or same basename guess) and reports D10a < 100% even though all orphan keys exist in the .bib file.

**Symptom**: D10a 65-85% with 5-20 orphans, all of which ARE found in the .bib file. The .bbl filename differs from the .tex filename.

**Fix**: Delete the stale .bbl. Recompile. The new .bbl will have the correct basename and all entries.

### Empty .bbl (0 bytes) from tex without \bibliography command (2026-06-22)

A degenerate sub-case of stale .bbl: papers using inline `\begin{thebibliography}` + `\bibitem{}` (no external `.bib`) can still have a `.bbl` file if someone ran bibtex on them. Since the `.tex` has no `\bibliography{}` command, bibtex produces an **empty .bbl** (0 bytes, "I found no \bibdata command" in `.blg`). The scan script prioritizes `.bbl` over tex thebibliography → finds 0 bibitems → D10a=0% despite perfectly matched thebibliography entries.

**Symptom**: D10a=0.0%, source=bbl, `.blg` says "I found no \bibdata command" + "I found no \bibstyle command", `.bbl` is 0 bytes. All orphan keys ARE found as `\bibitem{}` entries in the tex's thebibliography.

**Fix**: Delete the empty `.bbl`. The scan script falls back to extracting bibitems from the `thebibliography` in the tex. No recompilation needed (thebibliography papers don't use bibtex).

**Detection**: `ls -la paper.bbl` → 0 bytes. `grep 'bibdata' paper.blg` → "I found no \bibdata command". Cites extracted from tex all match thebibliography bibitems when checked with manual Python regex.

**Real case**: `093-saccade-target-shift-PINN` (14 cites, 14 bibitems, 0% D10a → 100% after deleting 0-byte .bbl). `endolymph-hydropressure-ode` (15/15, same pattern).

### Wrong .tex file selected in multi-tex directories (2026-06-22)

When a paper directory contains multiple `.tex` files (e.g., a LaTeX template + the real manuscript), `get_main_tex()` may pick the wrong one. Templates like `Sage_LaTeX_Guidelines.tex` or `elsarticle-template-num.tex` may have placeholder cites (`R1`, `R2`, `R3` or `lamport94`) and no substantive content, causing D10a=0% (3 cites R1/R2/R3 vs 30 bibitems).

**Detection**: D10a=0% or nonsensical results (tiny cite count with huge bibitem count). Cite keys are template placeholders.

**Fix**: Prefer the .tex with the most `\cite{}` calls AND `\begin{document}`. If multiple candidates exist, check for realistic citation keys (author-year format, not R1/R2/R3). The `scripts/d8d10a-scan.py` uses a scoring heuristic — if it consistently picks the wrong tex, force the correct one by naming it `paper.tex` or moving templates to a subdirectory.

### ⚠️ Multi-tex version scoring bias: older heavy tex beats newer lean tex (2026-06-23)

A sub-trap of multi-tex selection: when a paper has versioned tex files (e.g., `articlev1.tex` and `articlev2.tex`), the `cite-count + has-document` heuristic can pick the **older, template-heavier version**. The older draft may have more `\cite{}` calls (33 vs 18) simply because it bundles more background citations or legacy content — not because it's the canonical version.

**Symptom**: Scan picks `articlev1.tex` (33 cites, older) over `articlev2.tex` (18 cites, newer by 2 months). D10a reports 93.8% because bbl is `articlev2.bbl` (24 zombie bibitems from v2's bib, but v1's cites don't all match). However `articlev2.tex` + `articlev2.bbl` = 100% D10a.

**Detection**: When multiple tex files have valid `\begin{document}`, check file modification times. If a newer file exists whose basename matches the `.bbl` filename, prefer it regardless of cite count.

**Fix**: Add a **version bonus** to the scoring: `+500` for any tex whose basename contains a higher version number suffix (`v2`, `v3`, etc. over `v1`). Or simply prefer the tex with the **matching bbl basename** (if `articlev2.bbl` exists, prefer `articlev2.tex` over `articlev1.tex`). The `scripts/article-todo-d10a-scan.py` implements both heuristics.

**Real case**: `~/桌面/article_todo/SCC 3D Reconstruction` — `articlev1.tex` (33 cites, Mar 2025) outscored `articlev2.tex` (18 cites, May 2025). Fix: deleted stale `articlev1.bbl`, scan picked `articlev2.tex` (100%).

### ⚠️ Queue-vs-scan D10a divergence: paper-queue.json claims 100% but scan finds 0% (2026-06-23)

A subtle trap: the paper-queue.json notes may claim D10a was fixed to 100% on a prior date, but a fresh scan finds D10a=0% with `bib_source=none`. This is NOT a scan script bug — it means the filesystem state has diverged from the metadata.

**Root causes** (in order of likelihood):
1. **Bib source moved/deleted after fix**: The .bib file that was present during the fix was later removed or renamed. The scan script can't find any bib source → `bib_source=none` → D10a=0%.
2. **Fix applied to wrong tex**: The prior repair edited a tex file that the scan script doesn't select (e.g., a versioned copy), leaving the canonical tex with its original 0% state.
3. **state.json manually set without verification**: state.json was updated to claim D10a=100% but the actual bib/tex were never fixed.
4. **Queue notes describe an intent, not an outcome**: The note "D10a 0%→100%" records what was attempted, not what was verified post-repair.

**Detection**: Queue notes say D10a fixed, but scan shows `bib_source=none` or D10a=0%. Check: does the paper directory contain ANY .bib file? Does the tex have `\bibliography{...}` or `\begin{thebibliography}`?

**Fix workflow**:
1. Search for .bib files: `find <paper_dir> -name '*.bib'`
2. Check the tex for bibliography command: `grep 'bibliography\|thebibliography' <paper>.tex`
3. If `bib_source=none` but queue claims fix → the fix was ephemeral (bib file lost). Treat as fresh repair.
4. After any fix, run the scan AGAIN to verify — don't trust queue metadata alone.

**Real case**: `orthokeratology-corneal-remodeling-ODE-paper-117` — queue note dated 2026-06-15 says "D10a 0%→100%. qs → 60. gate FAIL→CONDITIONAL", but 2026-06-23 scan shows D10a=0%, bib_source=none. The fix evaporated — likely the bib file was deleted or the fix targeted a non-canonical tex.

### Directory count ≠ Paper count (ephemeral snapshot)
The `/media/yakeworld/sda2/Synthos/outputs/papers/` directory accumulates non-paper subdirectories over time (ML projects, old papers, scripts, templates, `_archive_*`, `_docs`, etc.). The `get_main_tex()` function silently filters these out by looking for a valid `.tex` file. **Never assume total_directories == papers_scanned** — always use the `__metadata__` entry from the scan JSON:
```
meta = [x for x in data if x.get('__metadata__')][0]
true_paper_count = meta['papers_scanned']  # NOT len(data) - 1
non_paper_count = meta['non_paper_count']
```
The absolute numbers change with each scan run. For historical context, see `references/scan-results-2026-06-20.md`. **Consumers of the JSON must skip the `__metadata__` entry** and use `papers_scanned` for the true paper count.

## Steps

1. Discover paper dirs with `01-manuscript/paper.tex` (excludes `_*` and `lit-reviews`)
2. Extract cite keys from uncommented lines: `\cite{}`, `\citep{}`, `\cite[opt]{}`
3. Find ONE best bib file: 06-references/references.bib → {name}.bib → references.bib → enhanced_refs/enhanced.bib
4. Also extracts `\bibitem{}` from thebibliography in tex
5. Computes D8, D10a, orphans, zombies, bbl status

## Canonical Skill

This IS the canonical scan skill. The scan script `scripts/d8d10a-scan.py` handles all resolution: inline theinlinebibliography, external .bib files, single-bib-per-paper priority, comment filtering. Run it directly.

## Support Files
- `scripts/d8d10a-scan.py` — Canonical pipeline D8/D10a scan (132 papers, `/media/yakeworld/sda2/Synthos/outputs/papers/`).
- `scripts/article-todo-d10a-scan.py` — **2026-06-23**: Targeted D10a scan for `~/桌面/article_todo/` writing workspace. Handles multi-tex version scoring bias (v2 bonus), template filtering, stale .bbl detection. Proven on 11 papers (2 fixes: 64.7%→100%, 93.8%→100%).
- `references/zero-citation-auto-repair.md` — **2026-06-20**: Proven 5-step method to repair papers with complete thebibliography but zero \\cite{} commands. Maps bibitem keys to prose mentions systematically. Tested on 182-accommodation-ciliary-muscle-ODE (13/13, 0%→100%).
- `references/article-todo-d10a-check.md` — **2026-06-22**: Targeted D10a check methodology for `~/桌面/article_todo/` workspace papers. Covers multi-tex selection, template artifact filtering (`<label>`, `lamport94`), stale .bbl detection, and wrong-tex-selection pitfalls specific to the writing workspace.
- `references/ocular-blood-flow-paper-116.md` — Paper 116 ocular blood flow 2-ODE reference (R2=0.993, Cc=0.45 bifurcation)
- `references/scan-script-discrepancy-v3-vs-v7.md` — **CRITICAL**: Two scan scripts produce incompatible D8/D10a metrics. Always state which script is used. Includes metric cross-mapping table.
- `references/scan-results-2026-06-21.md` — Latest cross-validated scan results (v3+v7), updated 2026-06-21
- `references/scan-results-2026-06-20.md` — Latest scan results (two-script cross-validation)
- `references/paper-repair-cron-workflow.md` — **2026-06-23**: Standard paper-repair cron workflow: two-scan approach (pipeline + article_todo), direction constraint filtering, common fix patterns, cron-specific pitfalls.