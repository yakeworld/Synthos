# Paper Project Optimization Cycle

> A 6-phase procedure for taking a completed paper draft through to submission-ready.
> Emerged from SCC Mathematical Morphology paper optimization (2026-05-30).

## When to Run

After a paper draft compiles cleanly (0 errors) and before formal submission. Run the full cycle even if the paper already passed a quality gate — the cycle catches organizational debt, submission-package drift, and research-gap opportunities that a pure QC pass misses.

## The 6-Phase Cycle

```
Phase 1: Quality Assessment (Layer A + Layer B)
    ↓
Phase 2: Auto-fix (D10a zombies, bibkey mismatches, over-citation)
    ↓
Phase 3: Submission Package Sync (bring submission/ to latest version)
    ↓
Phase 4: Directory Standardization (09-subdirectory structure)
    ↓
Phase 5: Process Documentation (CHANGE_LOG + TODO)
    ↓
Phase 6: Research Gaps & Hypotheses (RESEARCH_GAPS.md)
```

## Phase 1: Quality Assessment

### Layer A (local, seconds)
```bash
# D8: reference count
grep -c '\\bibitem' paper.tex
# or for BibTeX mode:
grep -c '^@' references.bib

# D10a: citation coverage
grep -oP '\\cite\{[^}]+\}' paper.tex | sed 's/\\cite{//;s/}//' | tr ',' '\n' | sed 's/^ *//' | sort -u > /tmp/cites.txt
grep -oP '\\bibitem\{[^}]+\}' paper.tex | sed 's/\\bibitem{//;s/}//' | sort -u > /tmp/bibs.txt
echo "Orphans: $(comm -23 /tmp/cites.txt /tmp/bibs.txt | wc -l)"   # zero tolerance
echo "Zombies: $(comm -13 /tmp/cites.txt /tmp/bibs.txt | wc -l)"

# Compilation errors
grep -c '^!' paper.log
```

### Layer B (NotebookLM Gemini, minutes)
1. Upload paper PDF to the paper's NotebookLM project (use unique naming: `{dir}-v{N}.pdf`)
2. Or upload as clean text: `notebooklm source add "$(cat /tmp/paper-text.txt)" --type text --title "Paper_v{N}_text"`
3. Ask for 7-dim SCI review with calibration

**D1-D7 review prompt template:**
```
请对刚上传的论文 [title] 进行7维SCI质量评审。目标期刊：[journal]。

D1 科学贡献(Scientific Contribution)
D2 方法学严谨性(Methodological Rigor)
D3 结果可信度(Results Credibility)
D4 完整性(Completeness)
D5 清晰性(Clarity)
D6 新颖性(Novelty)
D7 引用质量(Citation Quality)

逐维给出评分(0-1)、评价摘要、改进建议。
最终平均分 + 期刊就绪判断 + 关键改进项优先级排序。
```

### Calibration
- NotebookLM scores tend to run 0.05-0.15 above strict human review
- Apply calibration factor: `calibrated = raw - 0.01` (minor suggestion check)
- T1 threshold: ≥0.85, T2: ≥0.80, T3: ≥0.75

## Phase 2: Auto-fix

Run the standard triple-fix sequence from `dual-quality-check-v2`:
1. Activate zombie references (insert `\cite{}` at natural positions)
2. Fix Table I bibkey-author mismatches
3. Detect and replace over-cited single keys (>50% of total `\cite` groups)
4. Recompile and verify D10a = 100%, 0 errors

## Phase 3: Submission Package Sync

The `submission/` directory frequently falls behind the working `paper.tex`:

```bash
# Check drift
wc -l paper.tex submission/manuscript.tex
diff paper.tex submission/manuscript.tex | head

# Sync
cp paper.tex submission/manuscript-v{N}.tex
cp paper.pdf submission/manuscript-v{N}.pdf
```

Also update:
- `checklist.md` — note what changed in the new version
- `cover-letter.tex` — reflect new contributions in the letter text
- Recompile cover-letter.pdf

## Phase 4: Directory Standardization

Restructure the raw paper directory into the 09-subdirectory standard:

```
{paper-dir}/
├── 01-manuscript/      论文手稿各版本 (*v1.tex, *v2.tex, v{N}.tex + .pdf)
├── 02-submission/      投稿材料 (cover-letter, declarations, checklist, manuscript)
├── 03-code/            分析代码 (Python/R/Matlab scripts)
├── 04-data/            实验数据 (CSV, JSON, HDF5, etc.)
├── 05-figures/         图表文件 (PDF, PNG, SVG)
├── 06-references/      参考文献PDF (pdfs/ subdir)
├── 07-quality/         质量报告 (v2-report, v4-check, gemini-review)
├── 08-records/         过程记录 (CHANGE_LOG, TODO, RESEARCH_GAPS, tmp archive)
└── 09-background/      前期资料 (article_todo sync, related work, sub-papers)
```

**Cleanup actions:**
- Move all files from root into appropriate subdirectories
- Archive `tmp/` → `08-records/` (don't delete — process trace)
- Sync external copies (article_todo versions) → `09-background/`
- Remove LaTeX build artifacts (.aux, .log, .out, .spl, .synctex.gz, .bbl, .blg)

## Phase 5: Process Documentation

Write three files under `08-records/optimization-logs/`:

### CHANGE_LOG.md
Track what was done in the optimization cycle. Sections:
- Phase 1: Quality Assessment (Layer A + B scores)
- Phase 2: Auto-fix (what was fixed)
- Phase 3: Submission Package Sync (drift detected and resolved)
- Phase 4: Directory Standardization (structure before/after)
- Phase 5: Generated files (CHANGE_LOG, TODO, RESEARCH_GAPS)
- Quality score history (table: version → date → Layer A → Layer B → calibrated → T1 pass?)

### TODO.md
Task list organized by priority and phase:
```
## 投稿前
- [ ] P0: task description
- [ ] P1: task description

## 子论文
- [ ] ... 

## 后续研究
- [ ] ...
```

### RESEARCH_GAPS.md
Systematic gap→hypothesis mapping. Structure:

```
## 一、已解决的核心问题
(what the paper accomplished)

## 二、研究空白（Gap Analysis）
### Gap N: [Name]
| Current | Ideal | Gap |
|---------|-------|-----|
| ...     | ...   | ... |

**→ Hypothesis H{N}a**: [testable claim with effect size]
**→ Hypothesis H{N}b**: [alternative formulation]

## 三、下一步工作计划
### 短期（投稿前冲刺）
### 中期（投稿后同步推进）
### 长期（新课题方向）

## 四、与关联项目的交叉
(how this paper's findings feed into other active projects)
```

## Phase 6: Research Gaps & Hypotheses

Derive gaps from three sources:

1. **Paper's own Limitations section** — these are the author-acknowledged gaps
2. **Gemini review improvement suggestions** — D1-D7 gaps the reviewer spotted
3. **Cross-project connections** — how findings map to other active work (competition, companion papers)

For each gap, formulate explicit hypotheses:
- Use **H1a, H1b** numbering for alternative formulations of the same gap
- Include **effect size estimate** where possible (e.g., "Cohen d > 0.5")
- State what **evidence would falsify** the hypothesis

## Known Pitfalls

1. **membranous vs bony file fragmentation** — Check for split annotation files (`*mem* + *mem2*`) when analyzing paired structures. If arc ratio (memb/bony) < 1.0, files may need merging.
2. **Duplicate bibliography** — After multi-session editing, `\bibliography{}` may appear twice (once in appendix, once before `\end{document}`). Check with `grep -c '\\bibliography{' paper.tex`.
3. **Submission package stale** — Always check `wc -l` of submission manuscript vs working manuscript. The submission package is rarely updated alongside the working draft.
4. **NotebookLM text source** — When uploading large LaTeX papers as text, the `$(cat ...)` approach may fail with arrow characters (→, U+2192) causing SyntaxError in Python f-strings. First strip or replace non-ASCII symbols. Better: upload the PDF directly if it has a text layer (>100 chars from `pdftotext`).
