# Bib Integrity Audit — Session Report 2026-06-22

## Scope
Full scan of all .bib files in Synthos paper library.

## Results

### Statistics
- **125 .bib files** across the paper library
- **2,842 total entries**
- **2,082 DOIs** (73.3% coverage across all files)
- **239 suspicious entries** (mostly @misc without proper fields)
- **201 cross-file duplicates** (mostly consistent, expected)

### Key Findings

#### 1. DOI Coverage by Paper
**100% DOI (excellent):**
- 146-vitreous-cortex-structural-ODE (16 entries)
- bppv-canalith-relocation-ode (13 entries)
- orthokeratology-corneal-remodeling-ODE-paper-117 (17 entries)
- vog-vestibular-review (33 entries)
- 113-nystagmus-compensatory-ODE (16 entries)
- pd-dysphagia-2026 (48+ entries, multiple files)

**<50% DOI (needs work):**
- 3d-eyeball-iris-segmentation: 43.1% (58 entries, 4 duplicates)
- dual-ellipse-fitting: 50.0% (30 entries, 2 duplicates)

**0% DOI but valid BibTeX (needs DOI supplementation):**
- 162-corneal-hydration-dynamics-ODE (26 entries, 3 duplicates)
- corneal-biomechanics-ODE (12 entries)
- 150-scleral-remodeling-ODE (20 entries)
- 189-vem-pinn (29 entries, 3 duplicates)

#### 2. Entry Type Case Inconsistency
Found `@article` vs `@Article` vs `@ARTICLE` — should be normalized to lowercase `@article`.

#### 3. Cross-file Duplicates
201 entries appear in multiple files. Most are consistent (same paper referenced by multiple projects). Key clusters:
- pima-crispdm ↔ submissions: 27 shared entries (consistent)
- 3d-eyeball-iris-segmentation ↔ _archive: 80+ shared entries
- off-axis-iris-normalization-correction ↔ _archive: 20+ shared entries

#### 4. Suspicious Entries (239 total)
- @misc without author/title: dataset citations
- Kaggle publisher entries
- @misc with DOI (unusual)

### Action Items

1. **P0**: Add DOIs to 0% papers (162-corneal-hydration, corneal-biomechanics, 150-scleral, 189-vem-pinn)
2. **P1**: Supplement DOIs for papers <90% coverage (dual-ellipse-fitting, 3d-eyeball-iris, 3d-iris-normalization)
3. **P2**: Normalize entry type case (@Article → @article, etc.)
4. **P3**: Clean up suspicious @misc entries (add proper author/title fields)
5. **P4**: Consider consolidating duplicate .bib files (same entry in multiple locations)

### Reports
- JSON: `outputs/researchaudit/bib-integrity-2026-06-22.json`
- Unified scan: `outputs/researchaudit/unified-scan-2026-06-22.json`
- Summary: `outputs/researchaudit/unified-scan-report-2026-06-22.md`
