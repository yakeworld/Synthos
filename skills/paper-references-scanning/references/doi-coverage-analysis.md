# DOI Coverage Analysis Pattern

## Purpose
When running D8/D10a scans, DOI coverage is a critical quality dimension but the scan script only reports `bib_source` (not DOI fields). This pattern adds DOI coverage calculation.

## Pattern

The scan script's `find_nearest_bib()` returns the best `.bib` file path. To compute DOI coverage per paper:

1. **Find the bib file** — use the same logic as the scan script's `find_nearest_bib()`:
   ```python
   bib_file = find_nearest_bib(pdir, tex_path)
   # Priority: 06-references/references.bib → {name}.bib → references.bib → enhanced_refs/enhanced.bib
   ```

2. **Parse DOI fields from each bib entry** — split by `@` and check each entry:
   ```python
   doi_re = re.compile(r'(?:doi|DOI)\s*=\s*[\{\"]?([^}\"\s]+?)[\"}]?', re.IGNORECASE)
   entries = re.split(r'(?=@)', bib_content)
   for entry in entries:
       key_match = re.search(r'@\w+\{([^\s,;]+?),', entry)
       if key_match and doi_re.search(entry):
           doi_key_count += 1
   ```

3. **Compute coverage** — count bib entries with DOI / total bib entries:
   ```python
   total_bib_keys = paper['d8']  # from scan JSON
   coverage = round(doi_key_count / total_bib_keys * 100, 1) if total_bib_keys > 0 else 100.0
   ```

4. **Filter edge cases**:
   - `bib_source='none'` → no bib found, skip DOI check
   - `d8=0` → empty paper, coverage is meaningless
   - `bib_source='inline'` → references in tex body, no external bib to check

## Key Insight from Scan Data

In the 2026-06-18 scan:
- **86.8% of papers have 0% DOI coverage** (59/68 with d8>0)
- All ODE/PINN paper series (0xx/1xx naming) have 0% DOI — their bib files lack DOI fields entirely
- Only 4 papers achieve ≥90% DOI coverage

This means the ODE/PINN paper series are using **DOI-less references** — bibliographic data exists but is not machine-trackable. For SCI submission, DOIs are critical for G5 quality gate.

## When to Use This Pattern

- After any D8/D10a scan where you need to assess DOI completeness
- Before paper submission to verify reference traceability
- During quality gate L4/G5 evaluation
- When reviewing papers with high D8 but poor DOI coverage (e.g., D8>30, DOI<50%)

## Pitfalls

### DOI regex must be permissive
The scan script's DOI regex `r'doi\s*=\s*\{([^}]+)\}'` only matches standard BibTeX format. Real bib files use multiple formats: `doi = {value}`, `DOI = {value}`, `doi="value"`, `doi={value}`. Use the more permissive version shown above.

### Inline references have no DOI coverage
Papers with `bib_source='inline'` have references embedded in the tex body. These papers won't have an external bib file to scan. This is common for papers that use `\begin{thebibliography}` directly in the tex file.

### Empty papers (d8=0)
Papers with no references (`d8=0`, `cites=0`, `bib_source='none'`) should be excluded from DOI coverage analysis. Their coverage is meaningless.
