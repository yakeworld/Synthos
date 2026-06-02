# BibTeX Source Renaming for NotebookLM

When sources (especially PDFs) are added to a NotebookLM notebook, they retain their original filenames — which are often long, contain special characters, or have inconsistent formats. For clean academic reference management, rename them to BibTeX-style keys.

## Simpler Convention: {bibkey}.pdf (2026-05-26)

The `AuthorYear_Keyword` convention above has been superseded by the simpler `{bibkey}.pdf` format for new work:

Format: `{bibkey}.pdf` where bibkey = `{author}{year}{keyword}` (fully lowercase)

Examples:
- `lala2025paperqa.pdf`
- `bai2022constitutional.pdf`
- `lu2024ai.pdf`

Rules:
- Filename = BibTeX key + .pdf (exact match)
- All lowercase, no hyphens/underscores/spaces
- The bibkey appears in the .tex file's `\bibitem{...}` and `\cite{...}` commands
- No `.pdf` suffix in NotebookLM --title (use `--title "{bibkey}"`)

Examples:
- `Munoz2003_VisualFixationSaccadicADHD`
- `Kothari2021_EllSeg_EyeTracking`
- `Chawla2002_SMOTE`
- `Gong1988_CWISC`

Rules:
- Use only ASCII letters, digits, underscores. No spaces, hyphens, or Unicode.
- Author surname + year + 2-4 word keyword is the standard.
- For Chinese-language sources, transliterate author name (pinyin) + year + keyword.
- For no clear author, use first significant word + year.

## The Rename Problem

**Critical: `notebooklm source rename` uses partial ID matching on the SOURCE_ID argument, but partial matching BREAKS on:**
- Unicode characters (Chinese, Cyrillic, etc.)
- Mixed-language titles
- Titles with special characters (tildes, parentheses)
- Titles with accented characters

**Result:** Most rename attempts fail with `Error: No source found starting with '...'`

## The Fix: Use UUID Prefixes

Every source in NotebookLM has a UUID. The first 12 characters are unique across sources. Use them as the reliable identifier:

```bash
# Step 1: Get UUID prefixes
notebooklm source list    # or notebooklm metadata
# Output shows: │ eaeb5784-b058-4… │ A review on eye… │ 📄 PDF │

# Step 2: Map each UUID prefix to its desired BibTeX key
# eaeb5784 -> Ayyagari2006_ReviewEyeMovementChildhoodPsychiatry

# Step 3: Rename using UUID prefix (works reliably for ALL sources)
notebooklm source rename "eaeb5784" "Ayyagari2006_ReviewEyeMovementChildhoodPsychiatry"
```

## Bulk Rename Script

```python
import subprocess

mappings = [
    ("eaeb5784", "Ayyagari2006_ReviewEyeMovementChildhoodPsychiatry"),
    ("fc830e3f", "Soyiri2013_EpidemiologyADHD"),
    ("e734ebfa", "Altun2022_AutomaticDiagnosisADHD"),
    # ... add all sources
]

for uuid_prefix, new_title in mappings:
    cmd = f'notebooklm source rename "{uuid_prefix}" "{new_title}" 2>&1'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
    status = "OK" if r.returncode == 0 else f"FAIL: {r.stdout.strip()[:80]}"
    print(f"[{status}] {uuid_prefix} -> {new_title}")
```

## Verification

After renaming, confirm all sources:

```bash
notebooklm source list  # Check all titles are now BibTeX keys
notebooklm metadata     # Verify metadata also shows new names
```

## Tips

1. **Validate prefix uniqueness:** Before bulk renaming, test one prefix to ensure it only matches one source.
2. **Handle non-PDF sources:** Markdown files, DOCX files, and other formats should also be renamed if they serve as references (e.g., `project_review_comments`, `project_application_reconstructed`).
3. **Preserve original names in notes:** When creating notes referencing sources, use the new BibTeX key names for consistency.
4. **Don't rename during active workflow:** Rename sources only when the notebook is stable — after all additions are complete.
