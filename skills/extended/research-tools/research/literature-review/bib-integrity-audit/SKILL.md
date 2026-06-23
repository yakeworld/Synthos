---
name: bib-integrity-audit
description: "Audit `.bib` reference files across a paper library for:"
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

- **input**: `bib_file: str` — 用户请求描述、上下文信息
- **output**: `audit_report: dict — Bib完整性审计`


> 对应原则：P2（机械原子暴露输入输出规范）
# Bib Integrity Audit

## Scope

Audit `.bib` reference files across a paper library for:
- **DOI completeness**: percentage of entries with DOI fields
- **Suspicious entries**: malformed @misc, Kaggle publishers, URL-as-year, arXiv preprints without IDs
- **Cross-file dedup**: same entry key appearing in multiple bib files with inconsistent metadata
- **Known-DOI completion**: entries with complete metadata (title, author, year, journal) but missing DOI

## Step-by-Step Workflow

### 1. Discover all `.bib` files

```bash
find <paper-root> -name '*.bib' -type f
```

- Include ALL `.bib` files, not just `06-references/references.bib`
- The Synthos papers use varied locations: `reference4.bib`, `referencefinal.bib`, `reference3.bib`, `ref.bib`, `ref_orig.bib`

### 2. For each bib file, compute metrics

- **Entry count**: `grep -c '^@[A-Za-z]' file`
- **DOI count**: count entries with `doi = {...}` field
- **DOI coverage**: DOI count / entry count × 100%

### 3. Detect suspicious entries (mark, do NOT delete)

Check each entry against these signals:

| Signal | Pattern | Example |
|--------|---------|---------|
| `@misc` with auto-generated key | `auto\d{4}` in key | `@misc{auto2024...}` |
| Kaggle publisher | `publisher = {...kaggle...}` | `publisher={Kaggle}` |
| URL as year field | `year = {https?://...}` | `year={http://biometrics.idealtest.org/}` |
| arXiv preprint without arXiv ID | `journal = {arXiv preprint` but no `arXiv:XXXX` | `journal={arXiv preprint}` without ID |
| Incomplete `@misc` | missing `author` or `title` | dataset citations without proper fields |
| No author field | no `author = {` in entry | orphan entries |
| No title/booktitle field | no `title = {` or `booktitle = {` in entry | |
| Empty DOI | `doi = {}` | |
| Duplicate key across files | same key in multiple .bib files | `swirski2013fully` in 3+ files |

### 4. Cross-file deduplication

For each unique entry key across ALL bib files:
- Check if the same key appears in multiple files
- For duplicates: check consistency of title, author, year, journal, DOI
- Flag entries with inconsistent metadata across files

### 5. Known-DOI completion

For entries with complete metadata but missing DOI, use known DOI database:

| Key | Known DOI | Source Type |
|-----|-----------|-------------|
| `daugman2009iris` | `10.1016/b978-0-12-374457-9.00025-1` | Springer chapter |
| `proencca2009ubiris` | `10.1109/TPAMI.2009.66` | IEEE TPAMI |
| `lu2022neural` | `10.1109/ISMAR55827.2022.00053` | IEEE ISMAR |
| `dierkes2018novel` | `10.1145/3281417.3281423` | ACM ETRA |
| `tsukada2011illumination` | `10.1109/ICCVW.2011.6139507` | IEEE ICCVW |

For entries with complete metadata but unknown DOI, use **OpenAlex API** for DOI lookup:
```
https://api.openalex.org/works?search={title}&select=title,doi,author_institutions,institutions
```

### 6. Output report

Generate a markdown report with:
- Summary table: paper | entries | DOIs | DOI coverage | suspicious count
- Suspicious items detail: file | key | type | issue
- Known DOI completions: paper | key | title | suggested DOI
- DOI gaps requiring API lookup: entries with complete metadata
- Cross-file duplicates: key | locations | inconsistency
- Priority recommendations: P0/P1/P2 action items

## Pitfalls

### Paper-level reference file duplication
- Papers often carry multiple versions of the same reference list (e.g. `ref.bib` vs `ref_orig.bib`, `referencefinal.bib` vs `reference4.bib`). These share the same entry keys — the audit will flag them as "cross-file duplicates" but they are **not inconsistent**, they are redundant copies. Treat the version with fewer entries as the likely cleaned copy; the longer one is usually the raw export. Recommend consolidating to a single source of truth per paper.

### `find -name '*.bib'` may miss files in non-standard paths
- Synthos papers store .bib files in varied subdirectories (e.g., `投稿文件final/`, `latexnew/`)
- Use explicit `find` with path walk, don't assume `06-references/` structure
- **Unicode path trap**: Directories with non-ASCII characters (Chinese, curly apostrophes `'`) cause `cd`, glob expansion (`*.bib`), and `ls *.bib` to silently fail. When shell commands fail on a known directory, switch to Python `os.listdir()` for traversal. Avoid `cd` into unicode-named dirs entirely; always use absolute paths from Python or `find -print | while read` patterns.

### arXiv preprint format varies
- Some use `journal = {arXiv preprint arXiv:XXXX}` (has ID, no DOI)
- Some use `eprint = {XXXX}` + `archivePrefix = {arXiv}` (proper BibTeX format)
- Some use `doi = {10.48550/arXiv.XXXXX}` (has DOI already)
- The "arXiv preprint without ID" check should only flag entries where journal says "arXiv preprint" but NO arXiv:ID appears anywhere in the entry body

### Dataset citations are often malformed
- CASIA, MMU, Kaggle dataset references frequently use `@misc` with URL-as-year or missing author/title
- These are COMMON and should be flagged but not auto-removed
- Recommended fix: use `@dataset` entry type or properly formatted `@misc` with URL and accessed date

### `@Comment{jabref-meta:...}` entries
- JabRef adds a trailing comment entry — must be skipped during analysis

### Entry type classification for DOI sourcing

| Entry type | DOI expected | Verification source |
|-----------|-------------|---------------------|
| Journal articles (IEEE, Elsevier, Springer) | Yes — always | Crossref API (high success rate) |
| Conference proceedings (ACM ETRA, IEEE, Springer LNCS) | Yes — always | Semantic Scholar → Crossref fallback |
| arXiv preprints | No DOI until published | Keep arXiv ID in `eprint` or `journal` field |
| Datasets (CASIA, UBIRIS, OpenEDS, Kaggle) | No DOI | Keep as `@misc` with URL, no DOI expected |
| Book chapters | Yes | Crossref API (may require full book ISBN for lookup) |
| Technical reports | Sometimes | Crossref, but not always indexed |

### API-based DOI verification workflow

For entries with complete metadata but missing DOI, use a tiered approach:

1. **Semantic Scholar first** (most reliable for modern papers):
   ```
   GET https://api.semanticscholar.org/graph/v1/paper/search
   ?query={title}&limit=3&fields=title,authors,year,externalIds
   Header: User-Agent: synthos-audit/1.0 (yakeworld@wmu.edu.cn)
   ```
   - Returns `externalIds.DOI` and `externalIds.SEMANTIC_SCHOLAR`
   - S2 ID can be used as fallback identifier when DOI is absent
   - Best for: arXiv papers, recent conference papers, preprints

2. **Crossref API** (for journal articles and book chapters):
   ```
   GET https://api.crossref.org/works
   ?query.title={title}&rows=3&mailto=yakeworld@wmu.edu.cn
   ```
   - High success rate for IEEE, Elsevier, Springer journal articles
   - DOI format: `doi = {10.xxxx/yyyy}` — clean `\\_` to `_` before lookup
   - Rate limit: add `mailto:` header, 5 req/sec max

3. **PubMed** (for medical/clinical papers):
   ```
   GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
   ?db=pubmed&term={title}&retmax=5
   ```
   - Use when Semantic Scholar returns no results for medical papers
   - Then efetch for full details including DOI

4. **Fallback**: If no API source returns a match, the entry may be:
   - Too old (pre-DOI era, before 2000)
   - Very niche conference without online indexing
   - Non-English venue not in major databases
   - In this case, flag as "DOI not found — manual verification required"

### Known DOI pitfalls

- **arXiv DOIs** (e.g., `10.48550/arXiv.2408.17231`) are VALID DOIs but NOT in Crossref database. Crossref returns 404. Keep them as-is in the `.bib` file.
- **Springer LNCS DOIs** (e.g., `10.1007/978-3-031-37660-38`) may return 404 if the book/chapter is not yet indexed or if there's a digit error. Verify by searching Semantic Scholar or Google Scholar first.
- **ACM ETRA DOIs** follow pattern `10.1145/XXXXX.XXXXXX` — always start with 10.1145
- **IEEE DOIs** follow pattern `10.1109/XXXXX.YYYYYYY` or `10.1109/ACCESS.XXXXXXX`
- **Elsevier DOIs** follow pattern `10.1016/j.xxxx.yyyy.zz`
- **Crossref 404 is not always wrong** — may be due to: new publication not yet indexed, wrong last digit in DOI, publisher moved/rebranded, or the paper truly doesn't have a DOI in Crossref

### DOI field whitespace varies
- Entries use variable whitespace: `doi     = {value}` (multiple spaces) vs `doi = {value}` (single space). A naive `doi = {` regex will miss entries with 2+ spaces. Use `doi\s*=\s*\{` or `grep -c 'doi'` for counting instead.

### Cross-file references may use different keys for the same paper
- e.g., `lu2022neural` vs `Lu2022Neural3G` for the same ISMAR paper
- Check by title match, not just key match
- **Unicode title trap**: When parsing entries from bib files with unicode characters (Chinese directories, LaTeX escapes like `{\\c{c}}`), entry titles may parse as N/A or garbled in simple grep-based parsers. Use Python for robust multi-file dedup comparison — shell `awk`/`grep` can silently drop or corrupt unicode content in titles.

### BibTeX entry-block regex trap — non-greedy `(.+?)` fails across braces
- **The broken pattern**: `r'^@([A-Za-z]+)\s*\{\s*([^,]+?),\s*(.*?)(?=\n@[A-Za-z]+\s*\{|$)'`
  - `\s*` after `,\s*` consumes newlines, so `(.+?)` starts from the first field.
  - `.*?` is non-greedy — the `}` inside `title={...}` can satisfy the lookahead prematurely. The body is truncated after the first field.
  - **Symptom**: DOI coverage reads as 0%, many false "no title" errors. All entries appear malformed.
- **The fix**: `r'^@([A-Za-z]+)\s*\{\s*([^,]+?),\s*([\s\S]*?)(?=\n\s*\}\s*\n|\n\s*\}\s*$)'`
  - `[\s\S]*?` matches ANY character including newlines.
  - Lookahead matches `}` on its own line (BibTeX entry terminator), not `@`.
  - Correctly captures full body: multi-line author fields, DOIs, bare-value fields.
- **Field parsing caveat**: The field regex `r'(\w+)\s*=\s*(?:\{([^}]*)\}|"[^"]*")'` without `re.DOTALL` misses multi-line `author={Name and Name}`. Use line-by-line parsing with `re.DOTALL`, or add bare-value third alternative `(.+)`.

### Empty bib file detection
- A bib file that parses to 0 entries indicates either: (a) the file is truly empty/contains only comments, (b) the parser regex didn't match (e.g., non-standard format), or (c) Unicode corruption in the file. Always surface 0-entry files in the report as a P0 issue — they represent papers with no references at all, which is a complete D8 failure.

### Codex timeout trap in shell scripts
- **Never** call `codex -p hermes exec` from within a `.sh` script that has `set -euo pipefail`. Codex is non-blocking (background process), but the shell script waits for it to exit, causing silent 120s+ timeouts on cron jobs.
- **Fix**: Write standalone Python scripts (see `scripts/scan_bib_integrity.py`) for all long-running work. Shell scripts should only `python3 <script.py>`.
- **Symptom**: Cron job reports "Script timed out after 120s" with no other output. See `references/session-report-2026-06-23.md` for the full case study.

## Output Format

```
🧹 Bib标准化报告 (YYYY-MM-DD)

| 论文 | 条目数 | DOI覆盖率 | 可疑条目 | 已补DOI |
|:-----|:------:|:--------:|:--------:|:-------:|
| pima-crispdm | 33 | 94% | 0 | 0 |

可疑条目明细:
- paper-xyz: Key2024 (journal: arXiv preprint 无ID)

已补DOI明细:
- paper-abc: Key2020 → 10.XXXX/...
```

## Anti-patterns (what NOT to do)

- **DO NOT auto-delete suspicious entries** — always report and let the user confirm
- **DO NOT assume all papers use `06-references/references.bib`** — audit finds what exists
- **DO NOT skip entries just because they're conference proceedings or tech reports** — these still need DOI tracking
- **DO NOT treat arXiv preprints as having DOIs** unless `10.48550/arXiv` DOI is explicitly present

## Support Files

- `references/bib-suspicious-patterns.md` — Detailed catalog of suspicious entry patterns with examples
- `references/session-report-2026-06-06.md` — Session report for cross-file dedup workflow
- `references/session-report-2026-06-12.md` — Session report for DOI completion workflow
- `references/synthos-known-dois.md` — Pre-verified DOI mappings for known Synthos paper references (updated with new DOIs and entry type classification)
- `references/api-lookup-workflow.md` — Complete API workflow for DOI lookup: Semantic Scholar, Crossref, PubMed endpoints, parameters, error handling, DOI patterns
- `references/doi-patterns.md` — DOI pattern reference guide: publisher patterns, common issues (escaped underscores, arXiv in Crossref, Springer digit errors), classification logic
- `scripts/bib-audit-v2.py` — Automated audit script: scans .bib files, computes DOI coverage, detects suspicious entries, cross-file deduplicates, OpenAlex DOI lookup, markdown report output
- `scripts/bib-audit.py` — Original audit script (legacy)
- `scripts/bib-verify.py` — DOI verification script: verifies existing DOIs via Crossref, classifies entries by type (journal/conference/dataset/preprint), generates verification report
- `scripts/scan_bib_integrity.py` — Standalone runner with no Codex dependency; directly scans a paper root and outputs JSON. Replaced broken `codex`-based unified scan. See references/session-report-2026-06-23.md for the case study.

## When to Use

- Before paper submission (LaTeX compilation ready check)
- After adding new references to a paper
- Periodic integrity audit of a growing paper library
- When merging references from multiple papers (collaborative work)
- Prior to running quality-gate on a paper's references section