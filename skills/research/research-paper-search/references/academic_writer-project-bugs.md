# Known bugs and fixes in the academic_writer project

## Location
`/media/yakeworld/sda2/academic_writer/work/`

## Bug: `callback` used in `multi_database_search` without being declared
**File**: `src/manager/paper_manager.py` L153-L162
**Symptom**: Method body references `callback` variable but the method signature (L130-L137) does not include it as a parameter.
**Impact**: `NameError: name 'callback' is not defined` at runtime when `multi_database_search` is called.
**Fix**: Add `callback: Optional[Callable[[int, int, str], None]] = None` to the method signature (L137). Also update the docstring to document the parameter.

## Bug: `_fetch_semantic_scholar_data_sync` is an empty stub
**File**: `src/manager/paper_manager.py` L340-L342
**Symptom**: The method does `return entry` — it does not actually call Semantic Scholar API.
**Impact**: BibTeX enhancement does not enrich entries with S2 metadata (abstract, citation count, references, etc.).
**Note**: Non-blocking — it works but returns no enrichment data.

## Bug: `main.py` `expand --bib` not implemented
**File**: `main.py` L176
**Symptom**: Prints "BibTeX output not yet implemented" when `--bib` flag is used.
**Impact**: Cannot save expanded papers as BibTeX via CLI.

## Bug: Hardcoded Semantic Scholar API Key in two places
**Files**: `src/core/config.py` L9, `codev10.py` L259
**Fix**: Replace both with `os.environ.get('SEMANTIC_SCHOLAR_API_KEY', '')`.

## Bug: Hardcoded GitHub Token in `github_maintenance.py`
**File**: `github_maintenance.py` L36-L37
**Fix**: Replace with `os.environ.get('GITHUB_TOKEN', '')`.

## Bug: `.git-credentials` committed to repo
**File**: `.git-credentials` (committed), `.git/credentials` (untracked)
**Fix**: `git rm --cached .git-credentials`, add to `.gitignore`, delete from disk.

## Bug: HTML file with triplicated content
**File**: `Markdown_academic.html` (was 159KB, now 53KB)
**Symptom**: The file contained 3 complete copies of the same HTML page concatenated. Each copy had the same `id` attributes, causing 28 duplicate IDs and 6 script blocks.
**Detection**: Count `<body>`, `<html>`, `</html>` tags — if >1, content is duplicated.
**Fix**: Keep only the first complete copy (from start to first `</html>`).

## Bug: Duplicate `journal.json` file
**File**: `journal.json` (6.3MB duplicate of `journals.json`)
**Fix**: Delete `journal.json`.

## Bug: Code execution vs system Python mismatch
**Environment**: Sandbox runs Python 3.12.3 (uv-managed), system runs different binary.
**Symptom**: `pip3 install` says "already satisfied" but `python3 -c "import MODULE"` fails, or vice versa.
**Fix**: Always verify imports in the actual sandbox Python, not the shell Python. Check: `python3 -c "import sys; print(sys.executable, sys.version)"` to see which Python is running.
