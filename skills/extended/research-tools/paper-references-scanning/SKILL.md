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

### Commented `\\bibitem{}` must be excluded from D8
Only count uncommented `\bibitem{}` for D8.

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
- `references/zero-citation-auto-repair.md` — **2026-06-20**: Proven 5-step method to repair papers with complete thebibliography but zero \\cite{} commands. Maps bibitem keys to prose mentions systematically. Tested on 182-accommodation-ciliary-muscle-ODE (13/13, 0%→100%).
- `references/ocular-blood-flow-paper-116.md` — Paper 116 ocular blood flow 2-ODE reference (R2=0.993, Cc=0.45 bifurcation)
- `references/scan-script-discrepancy-v3-vs-v7.md` — **CRITICAL**: Two scan scripts produce incompatible D8/D10a metrics. Always state which script is used. Includes metric cross-mapping table.
- `references/scan-results-2026-06-21.md` — Latest cross-validated scan results (v3+v7), updated 2026-06-21
- `references/scan-results-2026-06-20.md` — Latest scan results (two-script cross-validation)