---
name: academic-paper-completion
description: Complete academic paper lifecycle — from human-in-the-loop writing and iterative quality optimization through LaTeX compilation, citation management, journal selection, and submission readiness. Covers elsarticle compilation, citation key synchronization, paper verification, framework-based writing workflows, SCI-level quality scoring loops, and medical AI journal selection.
version: 1.2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [latex, elsarticle, paper, journal, compilation, citations, bibtex]
    category: research
---

# Academic Paper Completion

## 原理层 · 文言

| 概念 | 文言 | 义 |
|:-----|:-----|:---|
| 从手稿到终稿 | **草成者续之，断者连之，误者正之** | 接手已有草稿→修补结构错误→同步引文→编译验证→投递准备 |
| 引用即承诺 | **引必可溯，数必有源** | 每条引用必须能在bib中找到，每个数值必须有项目数据/DOI可追溯 |
| 增量优化 | **不够则循，停滞则止** | 分数量化→自动迭代→连续改良<3点或两次停滞才停 |
| 期刊匹配 | **文质相当，刊者自选** | 根据论文质量选择T1-T4期刊，不妄投顶刊也不浪费底稿 |

## Overview

Complete and finalize an existing LaTeX manuscript for journal submission. Covers structure analysis, citation validation, LaTeX error resolution, and compilation verification. Focus on **Elsevier elsarticle** class but applicable to any academic LaTeX paper.

## When to Use

- User asks to "analyze" or "complete" a paper in a directory
- Paper needs final compilation and submission-readiness check
- LaTeX compilation fails with citation or structure errors
- Citation keys are mismatched between `.tex` and `.bib`
- User asks to write an academic paper — you MUST use LaTeX + BibTeX (Markdown-only is unacceptable for final output)
- A Markdown paper draft needs conversion to LaTeX for journal submission

## Workflow

### Phase 1: Directory Analysis

1. Read `AGENTS.md` if present — it contains file architecture and conventions
2. Identify the primary `.tex` file and `.bib` file
3. Check for figures, supplementary materials, and auxiliary files
4. Read the full `.tex` to understand section structure

### Phase 2: Structural Issues

Check for these common problems:

- **Duplicate sections**: grep for repeated `\section{` titles. Common when merging drafts.
- **Duplicate paragraphs**: look for repeated text blocks after `\end{enumerate}` or `\end{itemize}` — a sign of copy-paste errors during revision.
- **Missing `\end{enumerate}` / `\end{itemize}`**: verify every `\begin` has a matching `\end`.
- **Nested list environments**: elsarticle `highlights` environment already provides a list structure — do NOT wrap with `\begin{itemize}`.

### Phase 2.5: Converting Full Markdown Paper to LaTeX

When the paper exists only as a Markdown file (`.md`) with standard Markdown formatting — NOT LaTeX body content. This is the common case when AI agents draft papers. The .md uses `# Section`, `**bold**`, pipe tables, and narrative citations like `(Author et al., 2024)`.

**Step 1: Identify document class and template.** For clinical/medical journals, use `elsarticle`. For general journals, use `article`. Check if the target journal has a specific template.

**Step 2: Create .tex wrapper with frontmatter.** Always include:
```latex
\documentclass[review]{elsarticle}
\usepackage{amsmath,amssymb}
\usepackage{graphicx,booktabs,hyperref}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\onehalfspacing
```
**CRITICAL:** Do NOT add `\usepackage{natbib}` — elsarticle loads it internally (causes Option clash).

**Step 3: Convert Markdown formatting systematically:**

| Markdown | LaTeX |
|----------|-------|
| `# Section Title` | `\section{Section Title}` |
| `## Subsection` | `\subsection{Subsection}` |
| `### Sub-subsection` | `\subsubsection{Sub-subsection}` |
| `**bold**` | `\textbf{bold}` |
| `*italic*` | `\textit{italic}` |
| `` `code` `` | `\texttt{code}` |
| `$$ formula $$` | `\[ formula \]` |
| `$ inline $` | `\( inline \)` |
| `- item` or `* item` | `\item item` (inside itemize) |
| Pipe tables (`\| A \| B \|`) | `\begin{tabular}` with `\toprule`/`\midrule`/`\bottomrule` |
| Horizontal rule `---` | `\medskip` or omit |
| `[1]`, `[2,3]` citations | `\cite{refkey1}`, `\cite{refkey2,refkey3}` |
| Narrative `(Author et al., Year)` | Map to BibTeX key and use `\cite{refkey}` |

**Step 4: Create the abstract and frontmatter.** The elsarticle frontmatter goes before `\begin{document}`:
```latex
\begin{frontmatter}
\title{Paper Title}
\author[1]{Author Name}
\affiliation[1]{organization={...}, ...}
\begin{abstract}
...abstract text...
\end{abstract}
\begin{keyword}
keyword1 \sep keyword2
\end{keyword}
\end{frontmatter}
```

**CRITICAL — Abstract section markers:** The `\begin{abstract}` environment goes INSIDE `\begin{frontmatter}` and BEFORE `\begin{document}`. Do NOT put abstract text outside frontmatter — it will cause compilation errors.

**Step 5: Create the BibTeX file.** Every citation in the .tex needs a matching `@article{key, ...}` entry in `.bib`. When converting from narrative citations like `(Collins et al., 2024)`:
- Use the first author's last name + year as the key: `collins2024tripod`
- Create complete BibTeX entries: title, author list, journal, year, volume, pages, DOI
- Every key in `\cite{}` must exist in `.bib` — verify with the diff command (see Phase 3)

**Step 6: Handle tables.** Markdown pipe tables need the most manual conversion:
```latex
% For wide tables, wrap with resizebox:
\begin{table}[htbp]
\centering
\caption{Descriptive caption.}
\label{tab:name}
\resizebox{\textwidth}{!}{%
\begin{tabular}{p{2cm}p{3cm}p{4cm}}
\toprule
\textbf{Header1} & \textbf{Header2} & \textbf{Header3} \\
\midrule
Cell1 & Cell2 & Cell3 \\
\bottomrule
\end{tabular}
}
\end{table}
```

**Step 7: Compile and verify.** Run the compilation sequence:
```bash
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
```

**Step 8 (optional): Convert back to Markdown.** After successful PDF compilation:
```bash
pandoc paper.tex -f latex -t markdown --citeproc --bibliography=references.bib -o paper.md
```

**Common pitfalls:**
- **Narrative citations in .md are NOT valid LaTeX citations.** Every `(Author, Year)` must become `\cite{key}` — there is no automatic conversion. You must create a mapping.
- **elsarticle frontmatter must be inside `\begin{frontmatter}...\end{frontmatter}`** and before `\begin{document}`. Putting abstract or keywords elsewhere breaks compilation.
- **Pipe tables lose formatting.** Restore bold headers with `\textbf{}` and ensure all columns align.
- **`\begin{keyword}` uses `\sep`, not commas.**
   - Target: zero overfull boxes; accept <= 1 trivial (< 15pt) as cosmetic

### Phase 3: Citation Key Synchronization

**CRITICAL**: `.tex` citation keys must match `.bib` entry keys exactly.

```python
import re

# Extract all \\cite{...} keys from .tex
with open('paper.tex') as f:
    tex = f.read()
tex_keys = set()
for c in re.findall(r'\\\\cite\\{([^}]+)\\}', tex):
    for key in c.split(','):
        tex_keys.add(key.strip())

# Extract all @entry{key, from .bib
with open('paper.bib') as f:
    bib = f.read()
bib_keys = set(re.findall(r'@\\w+\\{([^,]+),', bib))

# Find mismatches
missing = tex_keys - bib_keys
```

**Common mismatches and their fixes:**
- `Author2020Paper` in .tex vs `Author2020PaperOP` in .bib (suffix variants)
- `Author2020Short` vs `Author2020FullTitle` (abbreviated vs full keys)
- Missing entries entirely → search enhanced BibTeX files or append from complete database

**Batch replacement — CRITICAL PITFALL**: When replacing citation keys in batch, beware of **substring collision**. Example:

```python
# DANGER: This will double-replace!
replacements = [
    ('Gupta2021Comparative', 'Gupta2021ComparativePA'),
]
# Gupta2021ComparativePA already existed in .tex as a correct key.
# After replacement: Gupta2021ComparativePA → Gupta2021ComparativePAPA
```

**Safe batch replacement workflow**:

```python
# 1. Apply replacements
for old, new in [('Author2020Short', 'Author2020Full'), ...]:
    content = content.replace(old, new)

# 2. VERIFY no double-replacements:
for bib_key in bib_keys:
    for _, corrected in replacements:
        if corrected != bib_key and corrected in bib_key:
            print(f"WARNING double-replace: {bib_key} contains {corrected}")
            content = content.replace(bib_key, corrected)
```

Always verify with a check script after any batch rename operation. The double-replace leaves keys like `MarieSainte2019CurrentTFTF` which break compilation silently (BibTeX just won't find them).

### Phase 3.5: Three-File Sync (.tex + .md + .bib)

When a project maintains BOTH `.tex` AND `.md` versions of the same paper (common in academic_writer workflow):

1. **Edit both in parallel** — they diverge silently if only one is updated.
2. **Citation format differs**: `.tex` uses `\\cite{key1, key2}`; `.md` uses `[@key1; @key2]` or `[^N]` footnotes.
3. **Table format differs**: `.tex` uses `\\begin{tabular}`; `.md` uses pipe tables.
4. **Sync checklist after any edit**:
   - [ ] `.tex` section count matches `.md` section count
   - [ ] `.tex` citation keys all resolve in `.bib` (grep + diff)
   - [ ] `.md` `[@key]` references also resolved in `.bib` (separate check)
   - [ ] New `.md` footnotes (`[^N]`) appended at file bottom
   - [ ] New BibTeX entries added to BOTH working `reference.bib` AND master `enhanced-bibtex-*.bib`

### Phase 3.6: Literature Table Expansion

When the paper includes a systematic comparison table (e.g., Table 1) that lists prior work:

- Newly found papers with inflated metrics need entries in BOTH the .tex longtable AND the .md pipe table
- Each new paper gets a new `\\midrule` row in .tex longtable and a new `||` row in .md pipe table
- Footnotes for the .md version get `[^N]` references appended at the file bottom

### Phase 4: elsarticle-Specific Pitfalls

#### `highlights` Environment

The elsarticle class `highlights` environment is already a list. Do NOT nest `\begin{itemize}`:

```latex
% CORRECT:
\begin{highlights}
    \item First highlight point
    \item Second highlight point
\end{highlights}

% WRONG — causes "Something's wrong--perhaps a missing \item":
\begin{highlights}
    \begin{itemize}
        \item[highlight-1] First highlight point
    \end{itemize}
\end{highlights}
```

#### Reference style

elsarticle uses `elsarticle-num.bst` — numbered bibliography. Do not change citation style (journal requirement).

### Phase 5: Paper Enhancement with Systematic Literature Evidence

When the paper's thesis is "inflated metrics arise from methodological flaws (data leakage), not algorithmic superiority," the argument is strengthened by expanding the systematic review table with recently published papers that exhibit the same pattern.

#### Workflow

1. **Mine existing literature cache**: Search project's `literature/results.csv` for papers with accuracy/F1 claims in abstracts. Use regex to extract numeric metrics. Filter for papers claiming accuracy above the paper's benchmark (e.g., > 88%).

2. **Classify methodological flaws**: For each high-claim paper, check abstract for: global vs within-fold SMOTE, presence/absence of cross-validation, train-test split mention, class imbalance handling, zero-value correction.

3. **Search for additional papers**: Use OpenAlex (best rate limits) or S2 API to find recent (2024-2026) PIDD papers with high accuracy claims.

4. **Create BibTeX entries**: Add new entries to BOTH `reference.bib` (working copy) and the authoritative `enhanced-bibtex-*.bib` (master).

5. **Integrate into paper at three insertion points**:
   - **Related Work → Credibility Gap paragraph**: Add sentence citing new papers
   - **Table 1 (Comparative Analysis)**: Add 4-6 most illustrative new rows
   - **Discussion → Debunking Inflated Metrics**: Reference expanded table as systematic evidence

6. **Recompile**: Delete `.aux` and `.bbl`, then `pdflatex → bibtex → pdflatex × 2`.

Full methodology: `references/inflated-metrics-detection.md`. Concrete worked example: `references/pidd-inflated-metrics-table.md` (PIDD-specific table, BibTeX entries, flaw classification, and core argument statement).

### Phase 5.5: Paper Comparison / Gap Analysis Against State-of-the-Art

Before final compilation, systematically identify improvement areas by benchmarking the paper against top-cited competitors in the same domain.

#### Workflow

1. **Identify target paper's domain and contributions**: Read the paper's abstract, contribution list, and comparison table to understand its claimed positioning.

2. **Discover top competitor papers** — multi-source search with fallbacks:
   - **arXiv API** (primary): `https://export.arxiv.org/api/query?search_query=...&max_results=10` (be careful with special characters — URL-encode queries)
   - **Semantic Scholar API** (secondary): `https://api.semanticscholar.org/graph/v1/paper/search?query=...&fields=title,authors,year,citationCount,externalIds,abstract` (with API key header `x-api-key`)
   - **Direct arxiv.org/abs/ID page** (fallback): parse the HTML for title, authors, abstract via regex on `<span class="descriptor">`
   - **pdftotext on existing PDFs** (local cache): `pdftotext -raw /path/to/paper.pdf - | head -80`
   - **Rate limit handling**: arXiv returns "Rate exceeded" — wait and retry with backoff. S2 returns 429/403 — fall back to direct arxiv pages or local PDFs.

3. **Extract key data from each competitor**:
   - Paper identity: full title, authors, year, venue, DOI/arXiv ID
   - Abstract (first 300-500 chars)
   - Page count (from `pdfinfo paper.pdf | grep Pages`)
   - Key claims/contributions (skim abstract + introduction)
   - Methodology approach (monolithic, pipeline, modular, RAG, etc.)
   - Evaluation method (human review, benchmark, self-report, etc.)
   - Any unique capabilities relevant to the comparison

4. **Handle corrupted/inaccessible PDFs gracefully**:
   - `pdftotext` returns "Couldn't find trailer dictionary" or "Couldn't read xref table" → corrupt PDF
   - Fallback: fetch abstract from arXiv HTML (`curl -sL https://arxiv.org/abs/ID`), parse with `re.search(r'<span class="descriptor">Abstract:</span>(.*?)</blockquote>', html, re.DOTALL)`
   - Fallback tier: direct arXiv HTML → Semantic Scholar API → Google Scholar snippet → manual description based on known work
   - Log which fallback was used for each paper

5. **Create multi-dimension comparison matrix**:
   - Identify 6-10 comparison dimensions covering architecture, autonomy, quality assurance, unique claims
   - Rate each system per dimension (`✅` / `🟡` / `❌` or similar)
   - Include the target paper's self-assessment honestly

6. **Identify gaps** — compare target paper against top papers:

   | Priority | Type | Finding | 
   |:--------:|:----:|:--------|
   | P0 | Critical gap | Missing feature/evidence common across competitors |
   | P1 | Notable gap | Missing feature present in 2+ top competitors |
   | P2 | Enhancement | Nice-to-have improvement |

7. **Produce actionable recommendations**: For each gap, state:
   - Current state → target state
   - Effort estimate (quick fix / moderate / major addition)
   - Specific change needed ("Increase Discussion Limitations from 3 to 5 quantified items")

8. **Offer to execute immediately**: High-confidence fixes (P0 with non-controversial approach) should be offered for direct execution rather than just reported.

#### Common comparison dimensions

| Dimension | What to look for | Typical evidence |
|:----------|:-----------------|:-----------------|
| **Autonomy level** | Fully autonomous vs human-in-the-loop vs query-only | Paper's stated mode of operation |
| **Architecture style** | Monolithic, pipeline, modular, atomic, RAG | System description |
| **Self-evolution** | Does the system improve its own architecture? | Evolution cycle numbers, version history |
| **Quality assurance** | Any gates, reviews, checks, or validation? | Quality metrics, failure analysis |
| **Evaluation rigor** | Self-report, benchmark, human review, reproducible? | Evaluation section methodology |
| **Citations/references** | Number, verification method, real vs hallucinated | Reference list, PDF verification |
| **Publication venue** | Conference, journal, preprint? | Venue name, peer review status |
| **Open-source** | Code available, license, reproducibility | Code availability statement |

#### Example output structure

```
## 📊 对比矩阵
| Dimension | Our Paper | Competitor A | Competitor B | ... |

## 📖 逐篇深度对照
### Competitor A — Key strengths we lack
### Competitor B — Different approach

## 🔧 改进空间
| P0 | Missing X | Current: Y → Target: Z |

## 🎯 核心结论
Unique advantages + biggest vulnerability
```

#### References

- `references/paper-comparison-example.md` — Worked example from SynthOS vs AI Scientist/Agent Laboratory/OpenScholar/MLGym/STORM comparison

### Phase 6: Compilation

Standard elsarticle compilation sequence:

```bash
cd /path/to/paper
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex   # 2nd pass for cross-refs
```

**Check for errors after each pass:**

```bash
grep -c "Error" paper.log
grep "Warning" paper.log | sort -u
```

**Full recompilation reset**: When adding new BibTeX entries or fixing citation keys, stale `.aux` and `.bbl` files can cause "undefined citation" warnings even after correct bibtex runs. Delete them before the clean build:

```bash
cd elsarticle
rm -f paper.aux paper.bbl paper.blg
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

This forces BibTeX to fully rebuild citation databases from scratch. Without this reset, `bibtex` may silently use cached references from the old `.aux` file.

**Acceptable warnings (no action needed):**
- "Float too large for page" — cosmetic float placement, paper still correct
- "Label(s) may have changed" — resolved by re-running pdflatex

**Unacceptable (must fix):**
- "Something's wrong--perhaps a missing \item" — check list environments
- "I didn't find a database entry for" — citation key mismatch
- "Undefined control sequence" — missing package or typo

### Phase 7: Verification Checklist

After successful compilation, verify:

- [ ] Zero BibTeX warnings
- [ ] Zero LaTeX errors (cosmetic warnings OK)
- [ ] All `\ref{}` and `\cite{}` resolve (no `??` in PDF)
- [ ] All sections present: Abstract, Introduction, Methods, Results, Discussion, Conclusion
- [ ] All figures referenced in text exist as files
- [ ] No duplicate content
- [ ] `.bib` file is the authoritative version (matches `AGENTS.md` if present)

## Files

- `scripts/check_citations.py` — verify .tex citations match .bib keys
- `references/inflated-metrics-detection.md` — methodology for finding supporting literature when the paper's thesis is "inflated metrics = data leakage"
- `references/leadership-briefing-template.md` — template for leadership briefing reports (absorbed from paper-workflow)
- `references/task-templates.md` — task templates per dimension for iterative optimization (absorbed from sci-paper-loop-optimization)
- `references/pitfalls.md` — detailed bug analysis from HCS-3WT project (absorbed from sci-paper-loop-optimization)
- `references/cycle-optimization-workflow.md` — iterative optimization workflow with quality rubric (absorbed from journal-selection-medical-ai)
- `references/breast-cancer-ml-journals.md` — curated journal metrics for breast cancer ML papers (absorbed from journal-selection-medical-ai)
- `scripts/loop_optimizer.py` — reusable loop optimizer script (absorbed from sci-paper-loop-optimization)

### Authoritative BibTeX vs Working BibTeX

In projects with multiple `.bib` files (e.g., `enhanced-bibtex-*.bib` as master and `reference.bib` as working copy), check `AGENTS.md` to determine which is authoritative. When `\bibliography{reference}` points to the working copy but keys differ from the master:

1. Extract which keys are in master but missing from working copy
2. Either copy entries from master to working copy with corrected keys, or rename working copy keys to match master
3. Verify zero BibTeX warnings after sync

Pattern: `@Article{Author2020Short,` in reference.bib → `@Article{Author2020FullTitle,` in enhanced-bibtex. Rename the working copy key to match the master.

### Systematic Review Literature Support

When the paper argues that inflated metrics stem from data leakage (not algorithmic superiority), follow the methodology in `references/inflated-metrics-detection.md`. Key pattern: mine existing `literature/results.csv` for accuracy claims, classify by flaw type, search for additional papers via OpenAlex, and integrate into Table 1 and Discussion.

---

## Phase 8: Human-in-the-Loop Paper Writing Workflow

> Absorbed from: `paper-workflow` skill (archived)

When the user asks to "write a paper" from scratch (not just complete existing LaTeX), use this human-in-the-loop workflow. Generates a paper framework, presents for human confirmation, then executes full writing.

### Pipeline

**Step 1: Understand source material.** Before generating anything, identify what verified data exists:
- Project metrics from evolution-state.json, skill docs, README
- Literature from NotebookLM or paper queue
- User-stated facts from conversation context
- **Do NOT invent numbers** — say "not available" or use qualitative terms

**Step 2: Build a content framework** (leadership reports prefer this 5-point structure):
1. **Technology definition** — concept, background, significance
2. **Self-developed implementation** — what was built, key capabilities
3. **AI/software platform** — supporting technology stack
4. **Integration platform** — how everything connects
5. **Application & translation** — clinical, educational, industrial use cases

**Step 3: Generate, review, iterate.** Present output for user feedback. Common corrections:
- "所有数字必须严谨，不要虚构" — Always distinguish verified data from estimates
- "演示内容和解说没有对齐" — For video/report content, each claim must be visually verifiable

### Data Integrity Rules (CRITICAL)

This user's highest-priority constraint: **all numbers must be rigorous, never fabricated.**

| ✅ Do | ❌ Don't |
|:-----|:---------|
| Use project data: `7/7 (100%)`, `0.97/1.0`, `13轮连续健康运行` | Invent market sizes (`2000万ADHD儿童`) |
| Say "高精度" if specs unknown | Claim `0.1° accuracy` without verification |
| Say "效率显著提升" without specific factor | Claim `4-6x improvement` unless project data supports it |
| Quote literature with explicit DOIs | Cite statistics from memory |
| Mark uncertain values as "待补充" | Present estimates as facts |

**BEFORE presenting any number**, ask: Where does this number come from? Is it a fact or an estimate? Would the user be able to open a file and verify it? If no → use qualitative language.

### Template: Leadership Briefing

When writing BCI/AI reports, use this structure:
```
# Title: [领域]：[主题]
## 一、[Technology] 技术定义与战略定位
## 二、自研实现：[System Name]
## 三、AI/软件平台：[Platform Name]
## 四、体系整合
## 五、成果落地与应用范围
```

See `references/leadership-briefing-template.md` for the full template.

### Pitfalls

1. **Fabricated numbers are #1 offense** — review every number before delivering. If in doubt, remove and use qualitative language.
2. **Narration must match slides** — every spoken claim must be visually present on the corresponding slide.
3. **Efficiency metrics confusion** — distinguish literature SEARCH (minutes vs hours, 10x) from literature REVIEW writing (days vs weeks, 4-6x).
4. **User prefers qualitative over wrong-quantitative** — vague "高精度" is better than precise "0.1°" you made up.
5. **Source all claims** — every significant claim needs: project data path, DOI, or explicit "待补充标记".

---

## Phase 9: Iterative Quality Optimization

> Absorbed from: `sci-paper-loop-optimization` skill (archived)

After the initial paper draft exists (from Phase 1-8), run this 4-phase iterative optimization cycle to reach SCI submission quality (target: 92/100).

### Phase 9a: Diagnosis and Assessment

Evaluate across 5 weighted dimensions:

| Dimension | Weight | What to Measure |
|-----------|--------|----------------|
| Experiment Completeness | 25% | Dataset count, SOTA comparisons, ablation studies |
| Methodological Rigor | 20% | Pipeline encapsulation, data-leakage-free, reproducibility |
| Writing Quality | 10% | Structure, word count, terminology, tables/figures |
| Citation Integrity | 10% | All citations exist in bib, format consistency |
| Figure Completeness | 10% | Figure count, PDF+PNG format, in-text references |

Total: `weighted_score * 0.85 + base_other(75) * 0.15 = final_score`. Target: 92/100.

### Phase 9b: Planning and Strategy

Generate optimization tasks per dimension. Priority: HIGH (<50), MEDIUM (50-70), LOW (>70).

### Phase 9c: Parallel Execution

- Auto-verifiable: bib integrity check, figure count, metric consistency
- Manual/subagent: language polishing, SOTA comparison, clinical discussion, new experiments

### Phase 9d: Quality Review and Iteration Decision

- Score >= 92: STOP
- Improvement < 3 AND consecutive stagnation >= 2: STOP (local optimum)
- Improvement >= 3: CONTINUE
- Improvement < 3 but first cycle: CONTINUE with strategy adjustment

### Pitfalls

- **cross_validate import**: `from sklearn.model_selection import cross_validate` — missing import causes silent failures.
- **PowerTransformer column count**: Must match what it was fit on. Never pass full X to pipeline trained on feature-subset X.
- **@Comment lines in bib files**: Lines like `@Comment{jabref-meta: ...}` cause greedy regex consumption. Always strip before extracting bib keys.
- **Percentage double-counting**: If stats return values already as percentages, don't multiply by 100 again.
- **single-class cross_val_predict**: Requires targets with >1 class. Always pass actual y values.

---

## Phase 10: Target Journal Selection

> Absorbed from: `journal-selection-medical-ai` skill (archived)

Systematic methodology for evaluating and ranking SCI journals as publication targets for medical AI / computational health papers.

### Step 1: Assess Paper Quality

Grade the paper objectively: strengths, weaknesses, quality tier (A-/B+/B).

### Step 2: Identify Candidate Journals

1. **Search similar papers** via PubMed/OpenAlex to find where they're published
2. **Compile known journals** in the domain (medical AI: *Artificial Intelligence in Medicine*, *npj Digital Medicine*, *Computers in Biology and Medicine*, IEEE JBHI)
3. **Get journal metrics** — IF, JCR Quartile, publisher, OA status, acceptance time

### Step 3: Evaluate Fit

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Topic match | 30% | Does Aims & Scope include your topic? |
| Paper quality match | 25% | Does typical paper quality match yours? |
| Methodology preference | 20% | Does journal favor your approach? |
| Practical factors | 15% | IF tier, speed, OA cost, acceptance rate |
| Precedent | 10% | Have similar papers been published here? |

### Step 4: Rank and Tier

- **TIER 1 (Reach)**: IF >= 7.0, Q1, strong topic match
- **TIER 2 (Target)**: IF 5.0-7.0, Q1/Q2, good match
- **TIER 3 (Safety)**: IF 3.0-5.0, Q2/Q3, adequate match
- **TIER 4 (OA/Backup)**: Broad scope, lower prestige

### Step 5: Prepare Submission

- Verify recent similar papers exist in target journal
- Read 2-3 recent papers for tone/depth expectations
- Check Author Guidelines: word limits, figure limits, reference style
- Prepare supplementary material for potential reviewer requests
- Have a fallback journal pre-identified

### Pitfalls

- **Don't over-index on IF alone** — poor topic fit rejects faster than moderate IF with perfect fit
- **Verify with actual papers** — search PubMed/OpenAlex before assuming acceptance
- **Check recent issues** — scope may have shifted, look at last 6 months
- **Multi-dataset validation for Q1 journals** — single-dataset papers may be desk-rejected
- **Beware of predatory journals** — verify Scopus/WoS/DOAJ indexing
- **OA costs** — APCs ($500-$2000+), factor into decision
- **Preprint strategy** — consider arXiv/bioRxiv before submission

---

## Quick Citation Check (no Python needed)

```bash
# Extract all \cite keys from .tex
grep -oP '\\cite\{\K[^}]+' paper.tex | tr ',' '\n' | sed 's/^ *//' | sort -u

# Extract all entry keys from .bib  
grep -oP '@\w+\{\K[^,]+' reference.bib | sort -u

# Diff them
diff <(grep -oP '\\cite\{\K[^}]+' paper.tex | tr ',' '\n' | sed 's/^ *//' | sort -u) \
     <(grep -oP '@\w+\{\K[^,]+' reference.bib | sort -u)
```
