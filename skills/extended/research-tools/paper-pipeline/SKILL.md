---
name: paper-pipeline
description: "Complete paper pipeline: retrieval, extraction, quality review, analysis, and publication."
version: 1.0.1
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: composite
    priority: P0
    signature: "paper_path: str -> analysis_report: dict"
    related_skills: []

---

# Paper Pipeline

## Purpose

Composite skill that merges 35 paper-related skills into a unified pipeline.

## Members (36)

- **adhd-eye-tracking-review**: Directory index for adhd-eye-tracking-review: adhd-eye-tracking-review
- **arxiv**: arXiv论文搜索 — 按关键词/作者/类别/ID检索。支持Tor SOCKS代理访问。
- **bib-integrity-audit**: Audit `.bib` reference files across a paper library for:
- **biorxiv**: Directory index for biorxiv: biorxiv
- **citation-bib-crossref**: Scan paper directories for mismatches between `\\cite{key}` calls in `.tex` files and `@type{key}` entries in `.bib` files. Produces D8 (bib count) and D10a (match percentage) metrics, plus orphan/zombie classification.
- **citation-integrity-fix**: ```python
- **emerging-field-landscape-scan**: Skill: emerging-field-landscape-scan
- **gif-search**: Search and download GIFs directly via the Tenor API using curl. No extra tools needed.
- **knowledge-base-audit**: Audit and maintain personal knowledge management systems (AKNE, NotebookLM,
- **latex-output**: Directory index for latex-output: latex-output
- **nano-pdf**: Edit PDFs using natural-language instructions. Point it at a page and describe what to change.
- **nature-paper2ppt**: Nature-style Chinese PPTX from academic papers — argument-driven slide
- **nsfc-grant-audit**: Directory index for nsfc-grant-audit: nsfc-grant-audit
- **openalex**: Directory index for openalex: openalex
- **paper-citation-health**: Scan all papers in `outputs/papers/` for citation bibliographic health metrics D8 (bib entries) and D10a (cite-to-bib match %).
- **paper-cron-scan**: 路由到 `v32-multi-direction-scan` — 所有旋转扫描和白空间验证由此技能执行。独立 paper-cron-scan 技能已合并入 v32。
- **paper-pipeline**: 主skill | SCI论文全流程编排器。v3.18.10新增Trap#42跨项目参考文献污染检测（Synthos Paper ID后缀/占位符键名/空条目/Prose提及无cite）。v3.18.9新增Trap#41 paper-queue.json幽灵条目逆方向。v3.18.5-8: D10a批量扫描+natbib盲区+注释过滤+路由修复。v3.18: Track A晋升协议。v3.16: 队列自愈+ABSOLUTE WHITE独立验证。v3.15: 轨道B四步工作流。
- **paper-quality-deep-review**: 论文质量深度审查引擎 — 从文献下载→内容分析→研究空白验证→科学假设评估→解决方法评估→文献引用质量评分→综合评分。
- **paper-queue-audit**: Directory index for paper-queue-audit: paper-queue-audit
- **research-queue-audit**: Research queue audit and management — read/validate research-queue.json, check candidate state consistency, detect stale entries, sync state layers. Implementation lives in `v32-multi-direction-scan` (Steps 5-6 + pitfalls). This is a routing stub — the actual queue lifecycle protocol is in the v32 scan skill.
- **paper-references-scanning**: Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate),   orphans, zombies. Class of tasks: LaTeX reference integrity auditing.
- **pdf-download-racing**: 并行竞速PDF下载引擎 — 外文期刊。**中文文献（CNKI/知网）见 `references/cnki-chinese-literature-access.md`**。
- **pdf-to-md-notebooklm**: PDF→Markdown→NotebookLM 全流程管线。支持批量上传、自动类型检测、大文件处理。
- **pubmed**: Deep PubMed/MEDLINE search via NCBI E-utilities — query construction, MeSH terms, batch retrieval, clinical query refinement.
- **quality**: 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。
- **quality-score-assignment**: Paper satisfies `current_step in steps_completed` AND `len(steps_completed) >= 8`.
- **research**: 直接调用子类别/技能名称即可。例如：`arxiv`、`bib-integrity-audit`、`research-ideation`。
- **research-ideation**: 研究创意发散与认知引擎（RIF+CCF）。三层架构：Layer 1（10操作框架）→ 产出研究方向候选； Layer 2（8认知引擎）→
- **research-paper-search**: 主skill | 多源论文检索+全文下载编排器。入口：Semantic Scholar (API Key), PubMed, OpenAlex, arXiv (Tor), Crossref。调用子skill: arxiv, pubmed, openalex。
- **research-skill-audit**: Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities.
- **literature-analysis-table-workflow**: 文献对比表（Table 1）构建工作流 — 从原始PDF读取→提取指标→分析预处理泄露→建表。用于方法论审计/系统性综述论文。参见 `references/literature-analysis-table-workflow.md`。
- **researcher-portrait**: Directory index for researcher-portrait: researcher-portrait
- **sci-paper-quality-review**: Directory index for sci-paper-quality-review: sci-paper-quality-review
- **sci-paper-standard-structure**: Directory index for sci-paper-standard-structure: sci-paper-standard-structure
- **skill-integrity-audit**: | 概念 | 文言 | 义 |
- **systematic-review**: 系统综述与Meta分析工作流助手 — PRISMA流程、搜索策略设计、研究选择、质量评估、数据提取和综合支持。
- **v32-multi-direction-scan**: Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.

## 🔴 研究方向约束（2026-06-22）

> 此约束同时作用于 autonomous-core-researcher、paper-repair、paper-quality-review、paper-layer-b-review、literature-monitor 等所有 cron 任务。

### ✅ 核心方向（全流程：论文生成→修复→评审→投稿）

1. **瞳孔/虹膜分割** — 3d-eyeball-iris-segmentation, dual-ellipse 系列
2. **眼球三维模型建模** — 3D pupil localization, Kappa角校准系列
3. **半规管空间姿态** — SCC reconstruction, cupula deflection
4. **BPPV虚拟仿真** — canalithiasis, Epley simulation 系列
5. **VOR数字孪生** — VOR cancellation, digital twin, sparse modular
6. **三维眼动算法组件** — 边缘检测、特征点提取、校准方法
7. **公开眼动数据集分析/方法论审计** — PIMA/WDBC/Heart 等数据完整性审计
8. **Synthos科研辅助系统** — 系统自身开发与进化
9. **AI辅助教学** — 教学应用论文

### 🔴 外围方向（仅提取研究空白和科学假设，不推进论文）

角膜/晶状体/玻璃体生物力学、泪膜/睑板腺、耳鸣/脑震荡/脑干/吞咽障碍等非眼动非数据集驱动的生物学建模方向。

### 管线执行决策矩阵

| 场景 | 行为 |
|:-----|:------|
| 自动扫描发现核心方向 gap | ✅ 全流程：hypothesis → paper |
| 自动扫描发现外围方向 gap | ⛔ 只记录 gap + hypothesis，不进 paper queue |
| paper-repair 遇到外围论文 | ⛔ 跳过，不修复不报告 |
| quality-review 遇到外围论文 | ⛔ 跳过 |
| literature-monitor 发现外围文献 | ✅ 可记录至附录，不进主报告 |

## ⚡ Filesystem Layout (Dual-Filesystem Awareness)

Papers and pipeline state are spread across **three locations**. All cron agents MUST know all three:

| Location | Contents | Purpose |
|:---------|:---------|:--------|
| `~/outputs/papers/` | Queue files (processed_papers.txt, low_score_papers.txt, no_state_papers.txt), bib-standards reports (`bib-standards-report-YYYY-MM-DD.md`) | Cron output reports, queue tracking |
| `~/桌面/article_todo/` | Actively developed papers (7 core direction papers — iris, pupil, SCC, BPPV — with submission materials) | Writing workspace. See `references/article-todo-inventory.md` |
| `/media/yakeworld/sda2/Synthos/outputs/papers/` | **Main pipeline** — 132 paper directories, `paper-queue.json`, `research-queue.json`, `_knowledge_only/` (21 research candidates), `state.json`, `submissions/` | Full paper pipeline + knowledge pipeline + evolution tracking |

**Critical distinction**: Two separate queue files with different semantics:
- `paper-queue.json` (132 papers) — full paper pipeline with quality scores, gate status, notes
- `_knowledge_only/research-queue.json` (21 research candidates) — Track B knowledge pipeline (literature_scan → gap_analysis → hypothesis_generation → knowledge_entry)

**Evolution tracking**: Main evolution state at `/media/yakeworld/sda2/Synthos/evolution-state.json` (cycle 174+, EXCELLENT 0.9696 as of 2026-06-23). Legacy at `/media/yakeworld/sda2/Synthos/outputs/evolution/evolution-state.json` (cycle 64).

**Agent log**: `/media/yakeworld/sda2/Synthos/outputs/papers/agent-log.md` (cron execution history).

> ⚠️ **Pitfall**: Home `~/outputs/papers/` queue files (`processed_papers.txt`, etc.) reflect a subset and may be stale. Always read `/media/yakeworld/sda2/Synthos/outputs/papers/paper-queue.json` for authoritative state.

> ⚠️ **Agent-Log Append-Only Protocol**: `agent-log.md` is written by multiple cron jobs (autonomous-core-researcher, paper-repair, paper-layer-b-review, literature-monitor, etc.). **NEVER overwrite it with write_file**. Always use patch to append new entries after the last line. If accidentally overwritten, reconstruct from session_search (all pipeline cron sessions are stored in the session DB) and rewrite the combined file.

## ⚠️ D10a Verification Pitfalls

When verifying D10a (cite-to-bibitem match rate), these traps cause false positives/negatives:

| Trap | Symptom | Fix |
|:-----|:--------|:----|
| **External .bib/.bbl** | Grepping tex for `\bibitem` finds only template placeholders (`{label}`, `{lamport94}`) | Papers with `\bibliography{references}` use external bib → bibtex generates `.bbl` with real bibitems. **Must grep the .bbl, not the .tex.** |
| **LaTeX comments** | Template instructions like `%% Example citation, See \cite{lamport94}.` count as orphans | Skip all lines starting with `%` before extracting cites |
| **Template markers** | `<label>` in `\cite{<label>}` flags as orphan | Filter keys containing `<` or `>` |
| **Stale reference_health** | state.json `reference_health.D10a` disagrees with `d8_d10a_scan.d10a` | `d8_d10a_scan` is authoritative (updated by batch scan). `reference_health` may be stale pre-repair snapshot. |
| **Stale .bbl from different bib source** | D10a=0% despite inline thebibliography having correct keys. .bbl exists but was generated from a different .bib file with incompatible key naming (e.g., short keys in bbl vs long keys in tex cite commands). Script uses bbl (priority 1) → 0 matches. | Delete all stale `.bbl` files in the paper directory. Script will fall back to inline thebibliography or a fresh bibtex run. **Always check**: does the bbl's bibitem keys match the tex citation style? If key naming conventions differ, the bbl is from a different compilation era. |
| **Missing .bib masquerading as .txt** | `\bibliography{reference4}` causes BibTeX "I didn't find a database entry" for ALL cites, but `reference4.txt` exists with full content. The `.bib` extension is missing — BibTeX only reads `.bib` files. | Search for files with the same basename but `.txt` extension (e.g., `reference4.txt`, `06-references/reference4.txt`). Copy to `.bib` extension. **Check**: does the `.txt` file cover all cited keys? It may be from a different draft version and missing newer citations. After copying, run bibtex to identify remaining gaps. |
| **Stale .bbl from older tex revision** | D10a < 100% even though bib entries exist in the .bib file. The .bbl filename doesn't match the .tex filename (e.g., `revision20241117.bbl` but tex is `revision20241118v3.tex`). The old bbl predates newer citations added to the tex. | Delete the stale .bbl. Recompile: `pdflatex → bibtex → pdflatex×2`. Verify the new .bbl filename matches the tex basename. |
| **Wrong .tex file selected** (multi-tex directories) | D10a=0% or nonsensical results (e.g., 3 cites R1/R2/R3 with 30 bibitems). Scan may pick up a LaTeX template file (e.g., `Sage_LaTeX_Guidelines.tex`) before the real manuscript (`articlev2.tex` or `paper.tex`). **Self-perpetuating trap**: if `paper.tex` stays as the template, every cron cycle re-flags it at 0.0% regardless of prior fixes. | **Diagnose**: Check which tex was scanned with `grep -l '\\begin{document}' *.tex`. Look for realistic citation keys (not R1/R2/R3 or `<label>`). Prefer tex with the most real cites and `\begin{document}`. **Fix**: Copy/link the real manuscript to `paper.tex` so future batch scans pick it up correctly. Delete/rename template files if they shadow the real manuscript. Then clean aux and recompile to produce `paper.bbl`. |
| **article_todo workspace scanning** | The main `d10a-batch-scan.py` targets `/media/yakeworld/sda2/Synthos/outputs/papers/` only. Papers in `~/桌面/article_todo/` need separate D10a checks. | Run a targeted scan on `~/桌面/article_todo/` using the same methodology: extract cites, find bib/bbl, compute D10a. The article_todo papers typically use .bbl-based references; stale .bbl is the #1 D10a issue here. See `references/article-todo-d10a-repair.md`. |
| **NEEDS_VERIFICATION bib notes** | Bib entries with `note = {NEEDS_VERIFICATION: ...}` contain underscores, colons, and single quotes that LaTeX can't handle — producing `Missing $ inserted` and `Extra }` errors (45+ per compile). The compile errors prevent bibtex from generating a complete .bbl. | Remove all `note` lines containing `NEEDS_VERIFICATION` from the .bib file. These are annotation markers for human reviewers, not bibliographic data. After removal, recompile pdflatex→bibtex→pdflatex×2 and verify D10a reaches 100%. |
| **G7 review vs queue staleness** | paper-queue.json reports D10a=100% with "no_repair_needed", but the most recent G7 deep review (`07-quality/step_quality_review.md`) found D10a=87.9% or 93.3%. The queue was updated by an earlier repair run; the G7 review ran later with fresh compilation and found new issues. | **Always cross-check the most recent G7 review before trusting the queue.** Read `07-quality/step_quality_review.md` for each paper flagged by the scan. If the G7 review's D10a assessment disagrees with the queue, the G7 review is authoritative (fresher data). Fix per the G7 review's findings, then update both queue and state.json. |
| **natbib `\citep`/`\citet` blind spot** (RP-6, 2026-06-24) | `d10a-batch-scan.py` D10a=0% with 58 orphans. Paper uses `\citep{}` (natbib) instead of `\cite{}`. Script regex `\cite{` misses natbib variants entirely — finds 0 cites, but the .bbl has 28 matching bibitems. | **Run targeted Python scan** that matches `\\(?:cite|citep|citet)\{` pattern. See `scripts/d10a-targeted-scan.py`. This is common in Elsevier `elsarticle-num` papers which load `natbib`. |
| **.bbl patch double-escaping** (RP-6, 2026-06-24) | Using `patch` tool to add `\bibitem{...}` to a .bbl file produces `\\bibitem{...}` (double backslash). LaTeX interprets `\\` as line break, breaking the bibliography. | After patching .bbl, run `python3 -c "content = open('file.bbl').read(); content = content.replace('\\\\\\\\bibitem', '\\\\bibitem').replace('\\\\\\\\newblock', '\\\\newblock').replace('\\\\\\\\href', '\\\\href').replace('{\\\\\\\\path', '{\\\\path'); open('file.bbl','w').write(content)"`. Always verify with grep `'\\bibitem'` that single backslashes are present. |\n| **Missing .bbl file entirely** (RP-7, 2026-06-24) | D10a=0% with batch scan reporting `source=inline`. Paper uses `\bibliography{references}` (external bib) but the .bbl file is absent — aux files were cleaned (`rm -f *.aux *.bbl *.blg`) without recompiling. Scanner falls back to grepping .tex for `\bibitem{}`, finds nothing (or only template placeholders `{label}`, `{lamport94}`), and misreports "source=inline". | Recompile: `pdflatex → bibtex → pdflatex×2`. **Diagnostic**: when `source=inline` + `orphan count > 10` + paper has `\bibliography{}` command → .bbl is missing, not an actual inline bibliography. Confirm by checking if `paper.bbl` exists. After recompile, verify D10a with independent Python script (not just batch scan). |\n| **"source=inline" misdiagnosis when .bbl missing** (RP-7, 2026-06-24) | d10a-batch-scan.py reports `source=inline` for a paper that uses external `\bibliography{references}`. The scanner falls through: no .bbl → tries .tex `\bibitem{}` regex → finds zero real bibitems → reports 0 matches. This is NOT an inline-thebibliography paper. | The `source=inline` label from the batch scan is unreliable when D10a=0% and orphan count > 10. Always check: does `paper.bbl` exist? If not, the paper was never properly compiled. Recompile first, then re-scan. |

| **Multi-tex version drift** (HCS-3WT, 2026-06-26) | A paper directory contains **two or more .tex versions** with different cite keys. The queue record (e.g., D10a=100%) was computed on one version, but a quality review scans a different version. New cite keys in the scanned version have no bib entries → D10a drops (e.g., 79.3%) despite queue saying 100%. | **Step 1**: List all .tex files in the paper's 01-manuscript/ directory. **Step 2**: Extract cite keys from each .tex version. **Step 3**: Compare key sets across versions — any key in one version but not the other reveals a citation swap. **Step 4**: For the version being reviewed, check if new keys (not in bib) were swapped in from an older version. **Step 5**: Cross-check the queue record's D10a note — does it mention a specific tex filename or compile timestamp? If the note says "D10a=100% (30/30)" but current tex has 29 keys, the queue record is based on a different version. **Rule**: Always verify which .tex version produced the recorded D10a before trusting the queue. The `paper.tex` (canonical) may be a different file from the one actually compiled. |

**Trusted methodology**: Use `scripts/d10a-batch-scan.py` for all D10a verification on the main pipeline. For papers using natbib (`\\citep`/`\\citet`), the batch scan produces false D10a=0% — cross-check with `scripts/d10a-targeted-scan.py` which handles all citation command variants. For article_todo workspace papers, use `scripts/d10a-targeted-scan.py --dir ~/桌面/article_todo/`.

**Multi-tex scan pattern** (for directories with >1 .tex): Before computing D10a, run `grep -l '\\\\begin{document}' *.tex` to identify the canonical tex, then `diff` cite keys across all versions. If any version has keys not in bib, flag for review. This catches the "version drift" trap before it produces false quality scores.
1. **Pre-scan**: Read `agent-log.md` for the most recent G7 Deep Review (not SCAN_AND_REPORT — look for "G7 Deep Review" or "G7 deep quick review"). Note any papers flagged with D10a < 95%.
2. `python3 scripts/d10a-batch-scan.py --all --threshold 95 --base-dir /media/yakeworld/sda2/Synthos/outputs/papers`
3. **Cross-check**: For each paper below threshold, also read `07-quality/step_quality_review.md` if it exists. If the G7 review found D10a issues that the queue doesn't reflect, the G7 review is authoritative.
4. For each paper below threshold: **First check if `paper.tex` is the real manuscript or a template** — when D10a=0.0% with `source=inline` and orphans >10, 90% of the time `paper.tex` is the elsarticle/Sage template. `grep -c '\\citep{' paper.tex` tells you instantly (template = 0, real manuscript = 20+ for natbib papers). If template → copy the real tex to `paper.tex`, recompile, re-scan. Then identify orphan cause (comment? template? missing bibitem? missing .bbl? wrong bib source? stale bbl? missing .bib extension? NEEDS_VERIFICATION notes? natbib `\citep` blind spot?)
5. Fix and re-verify (delete stale bbls first if present; check for `.txt` siblings of missing `.bib` files; fill missing entries; remove NEEDS_VERIFICATION note lines; recompile pdflatex→bibtex→pdflatex×2)
6. **Post-fix**: run bibtex separately to catch entries missing from the `.bib` that were previously in the `.bbl` (old bbl may have had bibitems not in current bib file). BibTeX warnings reveal these silently-matched-before entries.
7. **article_todo check**: After pipeline scan, run a targeted D10a scan on `~/桌面/article_todo/`. The most common issue in article_todo is stale .bbl from older revision. Fix: delete old .bbl, recompile. See `paper-references-scanning/references/article-todo-d10a-check.md` for the full targeted scan methodology (created 2026-06-22).
8. **Direction filter**: Skip peripheral-direction papers (corneal, lens, vitreous, tear film, tinnitus, brainstem, dysphagia, etc.). Only repair core-direction papers (pupil/iris, 3D eyeball, SCC, BPPV, VOR, algorithm components, dataset audits, Synthos system, AI teaching).

## Manual Layer B (NotebookLM Cron Fallback)

When NotebookLM auth has expired in a headless cron, use `references/cron-layer-b-workflow.md` for the complete manual Layer B workflow:

1. Check NotebookLM auth status (expired? -> manual fallback)
2. Priority-select papers (ICLR deadline first, then highest qs)
3. Read paper.tex / paper.pdf for content
4. Score 5 dimensions (D1-D5) with weighted formula
5. Compute verdict (T1/T2/FAIL thresholds)
6. G7 cross-check for auto-gate false positives
7. Create `07-quality/layer-b-report.md`
8. Update `state.json` publication_notes (use write_file, NOT patch — see pitfall)
9. Append to agent-log.md (use patch, NOT write_file — append-only protocol)

**Known pitfalls**: D10a false negative when paper uses inline thebibliography (scan is .bib-only); state.json patching corrupts nested JSON with escaped newlines; all 5 ICLR papers showed 13-15pt discrepancies between pipeline qs and Layer B scores, indicating auto-gate inflation.

## IO_CONTRACT

- **input**: `paper_path: str, analysis_type: str` — Paper path and analysis type
- **output**: `analysis_report: dict` — Complete analysis report


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）