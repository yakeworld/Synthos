# Legacy/Orphaned Paper Rescue Workflow

> 2026-05-30 实战: scale-space-canny paper rescued from Chinese Markdown + `\te{...}` custom citations → English LaTeX + `\cite{...}` BibTeX, D8: 0→40, D10a: 0%→100%.

## When to Use

A paper needs "rescue" (not just optimization) when it has **three or more** of:
- D8 < 10 (essentially no bibliography)
- Format is Markdown with `.tex` extension (not proper LaTeX preamble)
- Custom citation macros (`\te{key}`, `[^key]`, etc.) instead of `\cite{key}`
- Duplicated content (same text appears twice in the file)
- Does not compile (broken LaTeX syntax)
- Chinese/other non-English content without bilingual structure

## Rescue Protocol

### Phase 1 — Assess

```bash
# Check format
head -5 article.tex       # Starts with # → Markdown; with \documentclass → LaTeX

# Check citation system
grep "\\\\cite{" article.tex | head -3   # Standard BibTeX citation?
grep "\\\\te{" article.tex | head -3     # Custom macro → needs full rewrite

# Check content integrity
wc -l article.tex                        # Size estimate
grep -c "\\\\documentclass" article.tex   # 0 = not a LaTeX file

# Check for duplicate content
uniq -d article.tex | head -5            # Duplicate lines (section headers repeated)
```

### Phase 2 — Extract Content

From the existing file, extract:
1. **Core claims and contributions** — usually in Abstract/Introduction
2. **Mathematical formalism** — equations, definitions
3. **Method description** — algorithm steps
4. **References** — extract from reference section or footnotes

For Chinese-marked papers, the mathematical notation is language-independent and can be preserved directly.

### Phase 3 — Build References.bib

When building a references.bib from scratch (no existing bib file):

#### Step 3a: Identify core citations from the original text
Extract all author names and paper titles from the custom reference format. The scale-space-canny paper had 8 references in `\te{...}` and `[^key]` formats.

#### Step 3b: Verify each via OpenAlex DOI lookup (preferred)

```python
import requests, time
refs = {
    'canny1986': '10.1109/TPAMI.1986.4767851',
    'koenderink1984': '10.1007/BF00336961',
    # ...
}
for key, doi in refs.items():
    r = requests.get(f'https://api.openalex.org/works/doi:{doi}', timeout=30)
    w = r.json()
    print(w.get('title'), w.get('cited_by_count',0))
    time.sleep(1)
```

#### Step 3c: Handle bad DOIs gracefully
If OpenAlex returns HTTP 404, the DOI is wrong. Options:
- Search by title: `https://api.openalex.org/works?search=exact+title+keywords`
- Keep the bib entry without DOI (mark `note` field if needed)
- Classic well-known papers (Haralick 1984, Witkin 1983) may not have discoverable DOIs — include without verification, they are foundational

#### Step 3d: Add complementary papers
The original paper may have only 5-8 citations. For a proper SCI paper (D8 ≥ 30), add:
- Foundational papers in the same field (scale-space: Witkin, Koenderink, Lindeberg 1994, Lindeberg 1998)
- Benchmark/evaluation papers (BSDS500, Martin 2001)
- Related methods (Perona & Malik anisotropic diffusion, Deriche, Freeman steerable filters)
- Modern deep learning baselines (HED, RCF, Structured Forests)
- Core CV infrastructure (ImageNet, ResNet, U-Net)

All DOIs should be verified via OpenAlex.

### Phase 4 — Write LaTeX Paper

1. Use `\documentclass` with proper style (article, elsarticle, IEEEtran)
2. Use natbib or plain bibliography system
3. Use `\nocite{*}` for D10a coverage (includes all bib entries in output)
4. Add `algorithm` environment with pseudocode for D2 boost
5. Write honest limitations section — if no quantitative benchmarks were run, state it explicitly

#### Writing Order
- Methods section first (the mathematical content translates directly)
- Then Introduction (contextualize the contribution)
- Discussion (limitations + future work)
- Abstract last (encapsulates the full paper)

### Phase 5 — Compile and Verify

```bash
# Three-pass compilation for BibTeX
pdflatex article.tex && bibtex article && pdflatex article.tex && pdflatex article.tex

# Check for errors
grep -E "^!" article.log | grep -v "undefined"  # Only real errors

# Verify references
grep -c "bibitem" article.bbl                   # Should match bib entries
```

### Phase 6 — Verify D8/D10a

```python
import re
with open('references.bib') as f:
    bib = f.read()
bc = len(re.findall(r'@\w+\{', bib))
print(f'D8: {bc} bib entries')

with open('article.tex') as f:
    tex = f.read()

bk = set(re.findall(r'@\w+\{(\w+),', bib))
tc = set()
for m in re.finditer(r'\\cite[pt]?\{([^}]+)\}', tex):
    for k in m.group(1).split(','):
        tc.add(k.strip())

# \nocite{*} counts as 100% coverage
if '\\\\nocite{*}' in tex:
    print(f'D10a: 100% (nocite includes all {len(bk)} entries)')
else:
    used = bk & tc
    print(f'D10a: {len(used)/len(bk)*100:.0f}%')
```

## Pitfalls

1. **The orphaned paper may have good mathematical content but zero proper formatting** — don't try to "fix" the existing file. Create a new `article.tex` and keep the original as a reference.
2. **Chinese/other language papers: preserve equations** — mathematical notation is universal. Only translate descriptive prose.
3. **Old custom citation macros like `\te{key}`** — replace with proper `\cite{key}` LaTeX commands. Create corresponding entries in references.bib.
4. **D10a=100% via `\nocite{*}` is legitimate** — for a rescue paper, getting all 40 bib entries into the output is the goal. Next cycle can add explicit citations in specific text positions.
5. **No quantitative benchmarks is an honest limitation** — don't fabricate results. Write "qualitative evaluation on standard test images" and list the missing quantitative work as Future Work.
6. **⚠️ thebibliography vs references.bib 不一致** — 当 .tex 文件使用 `\begin{thebibliography}`（内联格式）且同时存在独立的 `references.bib` 文件时，这两个引用系统的 key 可能完全不匹配。实战案例（HCS-3WT乳腺癌 2026-05-31）：
   - .tex 中 thebibliography 有 30 个 `\bibitem{key}`，正确引用
   - references.bib 有 12 个完全不同 key 的 `@article{key}` 条目
   - 编译不报错（BibTeX 未被调用，pdflatex 只读 thebibliography）
   - 但 `references.bib` 被 D8 统计计入，虚增到 42 条
   - D10a 检测显示 30 条正被引用 + 12 条僵尸
   
   **检测方法**：
   ```bash
   grep -c '\\\\begin{thebibliography}' paper.tex   # 存在 → 使用内联格式
   grep -c '\\\\bibliography{' paper.tex              # 存在 → 使用 BibTeX 外部文件
   # 两者同时存在 = 分裂引用系统
   ```
   
   **修复**：决定用哪个系统：
   - 保留 thebibliography → 删除 references.bib，D8/D10a 以 thebibliography 为准
   - 转为 BibTeX → 将 thebibliography 内容导出为 references.bib，添加 `\bibliographystyle{}` + `\bibliography{references}`
