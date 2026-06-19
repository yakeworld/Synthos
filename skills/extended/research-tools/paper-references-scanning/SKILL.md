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
- WRONG: `r'[Dd][Oo][Ii]\s*=\s*"\{?([^}"\s]+)\}?"?'` — the `"?` around `{` is too strict; it requires the quote to match the brace style, causing zero matches.
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
Some papers list references via raw `\bibitem{}` in the `thebibliography` environment but never call them with `\cite{}` in the body. This results in D8 counting the bibitems but D10a=0% (no citations to match). These are real papers with references — the `\cite{}` may be missing, or the references may be uncited. Detect this pattern: `cited_count == 0 and bibitem_count > 0`. These papers need a `\cite{}` fix, not a new bib file.

### `\\cite` regex uses single-escape in raw strings
`re.compile(r'\\\\cite')` — two backslashes in source, regex engine interprets as one literal backslash.
- `r'\\\\\\\\cite'` → matches double-backslash → WRONG for standard tex files
- `r'\\cite'` → `\c` is invalid regex escape → SyntaxError
- Correct: `r'\\\\cite'`

### Comment detection must distinguish `%` from `\%`
`%%` and `%` at line start = comment. But `$13.9\%$` or `~\%` are NOT comments.
Check `line.lstrip().startswith('%')` only.

### ⚠️ Reference directory must be normalized before scanning (2026-06-18 实战)
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
The absolute numbers change with each scan run. For historical context, see `references/scan-results-2026-06-18.md`. **Consumers of the JSON must skip the `__metadata__` entry** and use `papers_scanned` for the true paper count.

## Steps

1. Discover paper dirs with `01-manuscript/paper.tex` (excludes `_*` and `lit-reviews`)
2. Extract cite keys from uncommented lines: `\cite{}`, `\citep{}`, `\cite[opt]{}`
3. Find ONE best bib file: `06-references/references.bib` → `{name}.bib` → `references.bib` → `enhanced_refs/enhanced.bib`
4. Also extracts `\bibitem{}` from thebibliography in tex
5. Computes D8, D10a, orphans, zombies, bbl status

## Canonical Skill

This IS the canonical scan skill. The scan script `scripts/d8d10a-scan.py` handles all resolution: inline theinlinebibliography, external .bib files, single-bib-per-paper priority, comment filtering. Run it directly.

## Support Files
- `references/ocular-blood-flow-paper-116.md` — Paper 116 ocular blood flow 2-ODE reference (R2=0.993, Cc=0.45 bifurcation)
- `references/doi-coverage-analysis.md` — How to add DOI coverage analysis to D8/D10a scans; common pitfalls; 2026-06-18 scan revealed 86.8% papers have 0% DOI coverage
- `scripts/d8d10a-scan.py` — Primary scan script. Produces JSON to stdout. Scan logic:
  1. Discovers paper dirs with `01-manuscript/paper.tex` (excludes `_*` and `lit-reviews`)
  2. Extracts uncommented `\cite{}`, `\citep{}`, `\cite[opt]{}` keys
  3. Finds ONE best bib file: 06-references/references.bib → {name}.bib → references.bib → enhanced_refs/enhanced.bib
  4. Also extracts `\bibitem{}` from thebibliography in tex
  5. Computes D8, D10a, orphans, zombies, bbl status
  6. Appends `__metadata__` entry with directory/paper count discrepancy
- `references/scan-results-2026-06-18.md` — Latest full scan: 72 papers, 66 healthy, DOI coverage crisis (86.8% with 0% DOI)
- `references/scan-results-2026-06-12.md` — Earlier scan: 153 papers, non-paper dir detection added
- `references/scan-results-2026-06-11.md` — Earlier scan: 151 papers, 3 healthy, 148 problems
- `references/scan-results-2026-06-09-v3.md` — Earlier scan: 147 papers, 45 healthy
- `references/scan-results-2026-06-08.md` — Earlier scan
- `references/non-paper-directory-taxonomy-2026-06-12.md` — Classification of non-paper directories
- `references/maturity-scanning-additional-dimensions.md` — 论文成熟度扫描的额外维度（D8/D10a之外的指标）
- `references/pima-crispdm-dir-normalization-case.md` — pima-crispdm参考目录错乱诊断与规范化实录（2026-06-18）

## 论文成熟度多维度扫描（2026-06-18 新增）
## 论文成熟度多维度扫描（2026-06-18 新增）

D8/D10a 仅衡量引用完整性，**不等于论文成熟度**。成熟论文还需：

### 7维评分体系

| 维度 | 满分 | 评分标准 |
|:-----|:----:|:---------|
| 引用完整性 (D10a) | 15 | 100%=15, 80-99%=10, 50-79%=5, <50%=0 |
| 引用质量 (D8) | 10 | ≥30=10, 20-29=7, 10-19=4, <10=0 |
| 编译PDF存在 | 15 | 存在且>500KB=15, <500KB=5, 无=0 |
| 结构完整 (01-07) | 15 | 7个目录+index+QC=15, 5-6=10, 3-4=5, <3=0 |
| 实验代码 | 15 | ≥25文件=15, 10-24=10, 5-9=5, <5=0 |
| 图表完整 | 10 | 3+张+GA=10, 2张+GA=7, 1张=3, 无=0 |
| 状态元数据 | 10 | status.json+state.json=5, status.json=3, 无=0 |

### 成熟度分级

| 等级 | 分数 | 含义 | 实例 |
|:-----|:----:|:-----|:-----|
| L5 | ≥90 | 成熟投稿级 | 3d-eyeball-iris-segmentation (D10a=100%, 75引用, 2.7MB PDF, 3图, GA) |
| L4 | 70-89 | 准投稿级 | — |
| L3 | 50-69 | 可投稿级 | pima-crispdm (D10a=100%, 78引用, 372KB, 缺QC) |
| L2 | 20-49 | 草稿级 | 有.tex可编译但引用不完整 |
| L1 | <20 | 骨架级 | 仅有目录结构 |

### PDF vs Bib 不匹配处理

**模式**：参考文献PDF数量可能远超Bib条目数。

**原因**：NotebookLM导入历史残留，后续引用变化但PDF未清理。

**处理策略**：只要D10a=100%且bib条目全部正确引用在正文中，PDF历史残留不影响论文质量。质量报告中标注"PDF历史残留: X个非bib PDF"。

**实例**：pima-crispdm — 51 PDF vs 33 Bib，多出18个PDF（Cabral2025, Chen2016等不在bib中），D10a仍为100%。