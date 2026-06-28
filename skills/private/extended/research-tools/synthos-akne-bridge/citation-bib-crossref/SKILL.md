---
name: citation-bib-crossref
description: 'Scan paper directories for mismatches between `\\cite{key}` calls in `.tex` files and `@type{key}` entries in `.bib` files. Produces D8 (bib count) and D10a (match percentage) metrics, plus orphan/zombie classification.'
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

- **input**: `paper_list: list[dict]` — 任务描述、参数配置
- **output**: `citation_report: dict — 执行结果`

> 对应原则：P2（机械原子暴露输入输出规范）

## Scope

Scan paper directories for mismatches between `\cite{key}` calls in `.tex` files and `@type{key}` entries in `.bib` files. Produces D8 (bib count) and D10a (match percentage) metrics, plus orphan/zombie classification.

## Key Definitions

| Metric | Meaning |
|--------|---------|
| **D8** | Count of unique bib entries in the .bib file |
| **D10a** | Percentage of `\cite{}` keys found in the .bib file |
| **孤儿** (orphan) | `\cite{key}` exists in .tex but no matching `@type{key}` in .bib |
| **僵尸** (zombie) | `@type{key}` exists in .bib but no `\cite{key}` references it |

## Step-by-Step Workflow

### 1. Discover paper directories

```bash
find /path/to/papers/ -maxdepth 1 -type d
```

Each directory represents one paper project. Skip non-paper directories:
- `_docs`, `_todo`, `lit-reviews` — auxiliary folders, not paper projects
- Directories without any `.tex` file containing `\cite{}` patterns

### 2. For each paper directory, find citation files and bib files

**Citation source** (priority order):
1. `01-manuscript/paper.tex` — the canonical manuscript
2. Any `*.tex` file anywhere in the directory with `\cite{}` patterns
3. Prefer `paper.tex` files over other `.tex` names

**Bib source** (priority order):
1. `06-references/references.bib` — canonical location
2. `references.bib` at the paper directory root (common: often a symlink)
3. Any `*.bib` file in subdirectories (last resort — warn if found far from root)

### 3. Extract citation keys from .tex

```python
import re

def extract_cite_keys(tex_path):
    with open(tex_path) as f:
        content = f.read()
    patterns = [
        r'\\cite(?:p|t|author|year|yearpar|inline)?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}',
        r'\\fullcite\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}',
        r'\\nocite\s*\{([^}]+)\}',
    ]
    keys = set()
    for pat in patterns:
        for m in re.finditer(pat, content):
            for k in m.group(1).split(','):
                k = k.strip()
                if k:
                    keys.add(k)
    return keys
```

**Note**: Handle `\cite[pg.5]{key}` and `\cite{key1,key2}` (multiple keys per call). Also handle `\fullcite{}` and `\nocite{}`.

### 4. Extract bib keys from .bib

```python
def extract_bib_keys(bib_path):
    with open(bib_path) as f:
        content = f.read()
    keys = set()
    for m in re.finditer(r'@(?:[a-zA-Z]+)\{([^,}]+),', content):
        k = m.group(1).strip()
        if k and not k.startswith('%') and not k.startswith('@'):
            keys.add(k)
    return keys
```

### 5. Compute metrics

```python
cite_keys = extract_cite_keys(tex_path)
bib_keys = extract_bib_keys(bib_path)

d8 = len(bib_keys)
orphans = cite_keys - bib_keys       # cited but no bib entry
zombies = bib_keys - cite_keys       # bib entry but not cited
matched = cite_keys & bib_keys

d10a_pct = round(100.0 * matched / len(cite_keys), 1) if cite_keys else 100.0
```

### 6. Check compiled artifacts

```python
# Check for .bbl file (compiled bibliography)
def check_bbl(paper_dir):
    for dirpath, _, filenames in os.walk(paper_dir):
        for f in filenames:
            if f.endswith('.bbl'):
                return True
    return False
```

### 7. Produce report

```
论文                   D8   D10a   孤儿   僵尸   编译
--------------------------------------------------
pima-crispdm           33   100%    0     0    ✅
3d-iris-normalization  30   93.8%   2     0    ✅
bppv-pc-repositioning  44   75.0%   3    35    ❌
```

### 8. Classify problem papers

| Category | Criteria |
|----------|----------|
| **严重** | D8=0 (no bib file or empty) — paper has \cite{} but no \bib{} |
| **中等** | D10a<100% but D8≥30 — bib exists but mismatched |
| **低** | D8<30 but D10a=100% — small but complete bib |
| **混合** | Significant orphans AND zombies (>5 each) |

## Pitfalls

### Non-standard directory layouts

Not all papers follow the `01-manuscript/paper.tex` + `06-references/references.bib` pattern:
- Some have `paper.tex` directly in the root directory
- Some have named manuscript files: `hcs3wt-breast-cancer.tex` instead of `paper.tex`
- Some have different reference directory names: `06-lit-review/`, `05-refs/`
- **Always fall back to recursive `.tex`/`.bib` search**

### Papers with enumerate references (no BibTeX)

Some papers use `\begin{enumerate}` for references instead of `\bibliography{}`:
- These will have `\cite{}` in text but NO `.bib` files
- The script correctly identifies them as "D8=0, all orphans"
- These are **not errors** — they use manual reference lists
- Flag them but don't treat as failed integrity

### Symlinked bib files

Common pattern: `references.bib -> 06-references/references.bib`
- Python's `os.path.isfile()` follows symlinks by default
- But relative paths in the `.bib` file (e.g., `\bibliography{refs}`) won't resolve through the symlink
- Handle carefully: read from the actual file location

### `\label{}` inside cite patterns

Some papers use `\label{}` for cross-references within the same document:
- Pattern: `\label{fig:main}` — should NOT be treated as a bib key
- BibTeX keys typically follow `[a-z]+[0-9]*` or `[A-Za-z]+[0-9]*` patterns
- Labels like `<label>` or `fig:...`, `tab:...`, `sec:...` are NOT bibliographic keys

### Case sensitivity

- BibTeX keys are **case-insensitive** for matching purposes
- `\cite{Bachmann2017}` matches `@article{bachmann2017}`
- The script should normalize to lowercase for comparison

### Multi-file bib structures

Some papers split references across multiple `.bib` files (e.g., `main.bib`, `refs.bib`, `data.bib`):
- **Aggregate all bib keys** from all `.bib` files in the paper directory
- Count orphans/zombies against the union of all keys

### Empty or whitespace-only bib files

- Some `.bib` files are created but empty (0 bytes or just whitespace)
- `extract_bib_keys()` returns empty set → D8=0, all orphans
- These represent **failed bib setup**, not just mismatch

### Directories that aren't papers

- `_docs`, `_todo`, `lit-reviews` — contain notes, TODOs, and reference collections but are not paper projects
- Filter these out before scanning
- Look for directories with `paper.tex` or `.bib` + `.tex` with cites

### `@Comment{jabref-meta:...}` entries

- JabRef adds comment entries at the end of `.bib` files
- Skip entries where the key starts with `Comment` or `jabref-meta`

## Output Format

### Table

```
论文                   D8   D10a   孤儿   僵尸   编译
--------------------------------------------------
pima-crispdm           33   100%    0     0    ✅
```

### Problem detail

```
严重问题 (D8=0):
- 3d-eye-bppv-diagnosis: D10a=0.0% (孤儿: Aw2013, Balatsouras2012, ...62 total)
  无 .bib 文件 / .bib 为空

中等问题 (D10a<100%):
- 3d-iris-normalization: D10a=93.8% (孤儿: <label>, lamport94)
  bib 文件存在但 2 个引用未匹配

低问题 (D8<30):
- bppv-epley-semont: D8=26, D10a=100%
  bib 完整但条目不足 30

混合问题 (孤儿+僵尸 均 >5):
- bppv-pc-repositioning: D10a=75% (孤儿: Baloh2003, Chang2004, Kim2012)
  僵尸: Anagnostou2018, Beyea2012, ...35 total)
```

### Summary

```
总计: 65篇, 健康: 16篇, 问题: 49篇
```

## When to Use

- Periodic integrity audit of a growing paper library
- Before batch compilation of multiple papers
- After bulk citation changes across papers
- When investigating "why did compilation fail on paper X?"
- Prior to quality-gate reviews (D8/D10a is L0.5 data honesty gate)

## Related Skills

- `bib-integrity-audit` — DOI completeness and suspicious entries within .bib files (complementary: this skill checks \cite↔\bib matching, that checks \bib entry quality)
- `paper-pipeline` → `citation-completeness-verification` — same-concept check for in-text \bibitem{} (within a single .tex file, not cross-file)
- `quality-gate` — D8/D10a metrics feed into L0.5 gate evaluation

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
