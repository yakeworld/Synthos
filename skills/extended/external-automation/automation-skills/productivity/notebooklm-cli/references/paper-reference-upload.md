# Paper Reference Upload Workflow — Uploading a Full Reference List to NotebookLM

## When to Use

A paper has been written (or is being analyzed) and its 10-15 references need to be uploaded as NotebookLM sources so the user can ask cross-reference questions. References are a mix of:
- arXiv/PMC PDFs (academic papers)
- GitHub READMEs (software repos cited as [1], [3], etc.)
- API documentation pages
- Internal project documents (evolution logs, constitutions)

## Precondition

The Synthos Paper + figures are already in the notebook (5+ existing sources). You're adding the reference layer.

## Workflow

### 1. Inventory References

From the paper's `## References` section (usually lines 270-310 in the SKILL.md paper), identify:

| Category | Examples | Upload Action |
|----------|----------|--------------|
| arXiv paper | `[6] arXiv:2408.06292` | Download PDF: `curl -L "https://arxiv.org/pdf/XXXX.XXXXX.pdf" -o ref_06.pdf` |
| GitHub repo | `[1] GPT-Researcher` | Download README: `curl -L "https://raw.githubusercontent.com/owner/repo/main/README.md" -o ref_01.md` |
| API docs | `[2] Semantic Scholar API` | Download page: `curl -L "https://api.semanticscholar.org/" -o ref_02.html` |
| Internal doc | `[14] Evolution Log` | Copy local file: `cp path/to/file ref_14.md` |

### 2. File Preparation Pitfalls

#### HTML files are NOT accepted by NotebookLM
`notebooklm source add file.html` fails silently or returns UnknownType. Convert to text first:
```bash
pandoc ref_02.html -o ref_02.txt
```
If pandoc not available, strip HTML tags:
```bash
sed 's/<[^>]*>//g' input.html > output.txt
```

#### Markdown files with HTML tags fail
Some GitHub READMEs contain inline HTML (`<h1>`, `<img>`, `<br>`, `<p>`) that causes NotebookLM to show status=UNKNOWN or error.
**Fix**: Strip HTML tags before upload:
```bash
sed 's/<[^>]*>//g' input.md > clean.md
```

#### PDF upload 400 error (resumable upload failure)
Occurs when the path contains special characters, is too deep, or has symlink issues.
**Fix**: Copy the PDF to `/tmp/` before uploading:
```bash
cp ref_07.pdf /tmp/ref_07.pdf
notebooklm source add /tmp/ref_07.pdf
```

### 3. Upload Sequence

```bash
notebooklm use <notebook_id_prefix>

# Upload each prepared file
notebooklm source add ref_01.md        # GPT-Researcher README
notebooklm source add ref_02.txt       # Converted API docs
notebooklm source add ref_06.pdf       # arXiv paper PDF
# ...repeat for all 10-12 sources
```

Wait ~1 second between uploads to let the API settle.

### 4. Verify Uploads

```bash
notebooklm source list
```

Check the Status column — all should say `ready`. Sources showing `preparing` or `UNKNOWN` need re-upload with cleaned file.

### 5. Rename Sources (Critical)

After upload, sources have filenames like `content.md` or `ref_01.md` as titles. Rename to human-readable reference titles:

**UUID Prefix Method** (required for Chinese/Unicode titles):

1. Get UUIDs from `notebooklm source list` — each source has a UUID like `bb354b74-ce14-4f62-b1f0-2d9d70067345`
2. Use the **first 12 characters** as the identifier
3. Rename each:
```bash
notebooklm source rename "bb354b74" "[01] GPT-Researcher (assafelovic) ⭐27K"
notebooklm source rename "c293c004" "[06] AI-Scientist arXiv Paper (2408.06292)"
```

**Naming convention**: `[ref_num] Project Name (Owner) ⭐Stars` for GitHub repos, `[ref_num] Paper Title (arXiv ID)` for papers.

**Known pitfall**: `notebooklm source rename` fails on Unicode/mixed-language titles if using partial title matching. Always use the **UUID prefix (first 12 chars)**. The `source list` UUID column shows these — copy the first segment before the first `-`.

### 6. Clean Up Duplicates

If uploads were retried, duplicate entries may remain. Delete them:
```bash
echo "y" | notebooklm source delete "duplicate-uuid-prefix"
```

### 7. Final Verification

```
notebooklm source list
```
Expected: 15-18 total sources (5 original + 10-12 references). All `ready`.

Then test with a cross-reference question:
```bash
notebooklm ask "What does reference [6] (AI Scientist) contribute that differs from reference [4] (SakanaAI GitHub)?"
```

## Concrete Execution Trace (2026-05-15)

Target: Synthos paper (15 references, 10 uploaded)
Notebook: `b54348f4` ("Synthos：自主进化科研教学认知操作系统")

**Uploads attempted**: 14 files (incl. retries)
**Successful uploads**: 10 sources (2 PDFs + 7 Markdown + 1 TXT)
**Failed/Kept for retry**: HTML file (converted to TXT), HTML-in-MD file (stripped tags), PDF (copied to /tmp/)
**Rename jobs**: 10/10 successful
**Final count**: 15 sources (5 original + 10 references)

**End state**: Paper + all available citations queryable in NotebookLM.

## When to Skip a Reference

| Condition | Action |
|-----------|--------|
| Repo returns 404 (deleted/private) | Skip, note in status |
| Internal benchmark without standalone file | Skip, note as unavailable |
| Duplicate of another reference (e.g., arXiv paper + GitHub repo for same project) | Upload PDF only, skip README |
| Source already absorbed into Synthos as a skill | Upload the absorption report instead of the original source |
| Paywalled journal with no accessible PDF | Upload PubMed abstract as .txt if available, otherwise skip |
