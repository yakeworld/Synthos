---
name: citation-integrity-fix
description: "```python"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---




## IO_CONTRACT

- **input**: `bib_file: str, citation_check: str` — 用户请求描述、上下文信息
- **output**: `integrity_report: dict — 引文完整性报告`

> 对应原则：P2（机械原子暴露输入输出规范）


# Citation Integrity Fix

> Fix papers where \begin{thebibliography} has entries but ZERO \cite{} commands in the text body. A common LLM generation failure mode.

## Detection

```python
import re
with open('paper.tex') as f: tex = f.read()
cites = re.findall(r'\\cite\{([^}]+)\}', tex)
```

**D10a 计算规则**：
- 对 `.tex` 文件：用 `\\bibitem\{` 提取条目（编译后的 `.bbl` 文件中存在）
- 对 `.bib` 文件：用 `@(\w+)\{([^,\s]+)` 提取条目 key（`\\bibitem` 在 `.bib` 中不存在）

```python
# .bib 文件提取
with open('references.bib') as f: bib_content = f.read()
bib_entries = re.findall(r'@(\w+)\{([^,\s]+)', bib_content)
unique_bib = set([entry[1] for entry in bib_entries])
```

**Thresholds**:
| D10a | Status | Action |
|:-----|:-------|:-------|
| 0% | **Critical** — no citations at all | Add \cite{} commands |
| 0–50% | Poor — mostly uncited | Add \cite{} commands |
| 50–80% | Partial | Add missing citations |
| 80–99% | Healthy | No action needed |
| 100% | Perfect | All entries cited |

**注意**：D10a=100% 不是必须的。5-10% 的 unused bib entries 是正常的（背景引用、延伸阅读等）。重点确保所有在正文中出现的 cite 都有对应的 bib entry。

## Fix Protocol

### Step 1: Identify claims that need citations
Map every claim in the text to a bib entry:
- Historical claims (author, date) → primary source
- Formula claims → original paper
- Clinical data (ranges, percentages) → source paper
- Model comparisons → baseline paper
- Mechanism descriptions → foundational paper

### Step 2: Add \cite{} commands
```latex
% Before:
Helmholtz mechanism, universally accepted.

% After:
Helmholtz mechanism~\cite{hirsch1937accommodation,navarro1985}, widely accepted.
```

### Step 3: Verify D10a ≥ 80%
```python
unused = set(bib) - unique_keys
assert len(unused) <= max(1, len(bib) * 0.2), f"{len(unused)} unused entries"
```

## Known Pitfalls

### Unescaped `$` in Text Mode
- **Symptom**: `Command \end{abstract} invalid in math mode`
- **Root cause**: `$15 billion` enters math mode, breaks abstract
- **Fix**: Escape currency: `\$15 billion`
- **Detect**: `grep -n '\$[0-9]' paper.tex`

### Double-Backslash from Patch Tool
- **Symptom**: `\\cite` appears in file (2 backslashes instead of 1)
- **Fix**: Python `content.replace('\\\\cite', '\\cite')`

### Zero-Count Cite Before Text Edit
When editing text in the bib section area, `\cite` commands added to the bibliography section itself (not the text body). Ensure `\cite{}` is in the main text, not in the `\begin{thebibliography}...\end{thebibliography}` block.

## Verification

1. `pdflatex paper.tex` → First pass (citation warnings expected)
2. `pdflatex paper.tex` → Second pass (no undefined references)
3. Check `paper.log` for `Error` → Should be 0
4. Check D10a → Should be ≥ 80%
5. Check unused entries → Should be ≤ 2

## Reference

- `paper-pipeline/references/thebibliography-citation-integrity.md` — Full protocol with case study
- `paper-improvement/references/latex-compilation-workflow.md` — 5-round compilation workflow
- `citation-integrity-fix/references/d10a-calculation.md` — D10a calculation guide with .bib vs .tex distinction