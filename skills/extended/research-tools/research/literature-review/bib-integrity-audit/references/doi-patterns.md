# DOI Pattern Matching Guide

## Publisher DOI Patterns

| Publisher | Pattern | Example | Notes |
|-----------|---------|---------|-------|
| IEEE | `10.1109/XXXXX.YYYYYYY` | `10.1109/TPAMI.2008.183` | Letters in first part, numbers in second |
| Elsevier | `10.1016/j.xxxx.yyyy.zz` | `10.1016/j.patcog.2019.04.010` | Journal abbreviation in first part |
| Springer | `10.1007/xxxx-yyyyyyy` | `10.1007/978-3-031-37660-38` | Book/series ISBN-like pattern |
| ACM | `10.1145/XXXXX.XXXXXX` | `10.1145/3204493.3204525` | Conference proceedings |
| arXiv | `10.48550/arXiv.XXXXX` | `10.48550/arXiv.2408.17231` | Valid but NOT in Crossref |
| MDPI | `10.3390/journal-volume-number-page` | `10.3390/s21144769` | Open access journals |
| Springer LNCS | `10.1007/978-3-031-37660-3_8` | Book chapter | Contains underscore separator |
| PMC/PubMed | `10.1186/s12911-020-01193-5` | `10.1186/s12911-020-01193-5` | BMC journals |
| Hindawi | `10.1155/2021/1234567` | `10.1155/2021/1234567` | Year-based pattern |

## Common DOI Issues

### 1. Escaped underscores in LaTeX
- **Problem**: `10.1007/978-3-031-37660-3_8` (LaTeX escaped as `\_`)
- **Fix**: Replace `\\_` with `_` before Crossref lookup
- **Crossref URL**: `https://api.crossref.org/works/10.1007/978-3-031-37660-38`

### 2. arXiv DOIs not in Crossref
- **Problem**: `10.48550/arXiv.2408.17231` returns 404 from Crossref
- **Cause**: arXiv DOIs are valid DOIs but NOT indexed by Crossref
- **Fix**: Keep arXiv DOI in `.bib` file; do NOT delete or replace
- **Verification**: DOI is valid but Crossref is not the right source

### 3. Springer LNCS digit errors
- **Problem**: `10.1007/978-3-031-37660-38` returns 404
- **Cause**: Missing/incorrect last digit in ISBN-13 suffix
- **Fix**: Check if it should be `10.1007/978-3-031-37660-8` or `10.1007/978-3-031-37660-48`
- **Strategy**: Search Semantic Scholar first to find correct DOI

### 4. Conference proceedings without DOIs
- **Problem**: Older conference papers (pre-2010) may not have DOIs
- **Cause**: DOI system started in 2000; many conferences adopted late
- **Fix**: If truly no DOI exists, leave without DOI but note "pre-DOI era"
- **Detection**: Check publication year — before 2010, verify carefully

### 5. Publisher rebranding/migration
- **Problem**: DOI works but publisher name changed
- **Cause**: Springer merged with Nature, IEEE Xplore moved, etc.
- **Fix**: DOI remains valid even if publisher changed
- **Detection**: DOI redirects correctly even if URL structure changed

## DOI Verification Priority

For entries with complete metadata but no DOI:

1. **Semantic Scholar first** — Most reliable for modern papers
2. **Crossref** — For established journal/book entries
3. **PubMed** — For medical/clinical papers
4. **Google Scholar** (manual) — Fallback for stubborn entries
5. **Publisher website** — Manual check on journal/conference site

## Classification Logic

```python
def classify_for_doi_lookup(entry):
    """Determine if an entry should have a DOI and how to find it."""
    if entry['doi']:
        return 'has_doi'  # Already has DOI, just verify
    
    journal = str(entry.get('journal', '')).lower()
    title = str(entry.get('title', '')).lower()
    venue = str(entry.get('booktitle', '') + ' ' + journal).lower()
    publisher = str(entry.get('publisher', '')).lower()
    year = entry.get('year', '')
    
    # arXiv preprints
    if 'arxiv' in journal or 'arxiv' in title:
        return 'arxiv_preprint'  # No DOI expected
    
    # Datasets
    if any(x in venue or x in publisher for x in [
        'dataset', 'database', 'kaggle', 'casia', 'ubiris', 'openeds'
    ]):
        return 'dataset'  # No DOI expected
    
    # Preprints (not arXiv)
    if 'preprint' in journal:
        return 'preprint'  # No DOI expected
    
    # Conference proceedings
    if 'conference' in venue or 'proceedings' in venue or 'iccv' in venue or 'cvpr' in venue:
        return 'conference'  # Should have DOI, search Crossref
    
    # Book chapters
    if 'booktitle' in entry or 'handbook' in venue or 'lecture' in venue:
        return 'book_chapter'  # Should have DOI, search Crossref
    
    # Journal articles
    if journal:
        return 'journal'  # Should have DOI, search Crossref
    
    # Default
    return 'unknown'  # Need manual verification
```