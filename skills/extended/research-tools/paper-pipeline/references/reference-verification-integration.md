# Paper Pipeline Integration with Reference Verification

## Overview

The `reference-verification` skill provides automated DOI verification and missing DOI search capabilities for papers in the paper pipeline.

## Integration Points

### 1. P0 Pre-Audit Gate

Before running the P0 pre-audit gate (D10a zombie/orphan detection), the paper pipeline should:

1. Load the `reference-verification` skill
2. Run `scripts/verify-references.py` on the paper's `references.bib` file
3. Process the verification report:
   - Add any found DOIs to the bib file
   - Investigate failed verifications
   - Search for missing DOIs

### 2. Pipeline Stage Integration

| Pipeline Stage | Reference Verification Action |
|----------------|-------------------------------|
| P0 (Pre-Audit) | Run automated DOI verification |
| P4 (Quality Check) | Review verification report for quality score impact |
| P7 (Final Review) | Ensure all DOIs are verified and present |

## Example Workflow

```bash
# 1. Run verification on a paper's references
python3 /home/yakeworld/.hermes/skills/reference-verification/scripts/verify-references.py \
    /media/yakeworld/sda2/Synthos/outputs/papers/3d-eyeball-iris-segmentation/06-references/references.bib

# 2. Process the JSON report
# - Add found DOIs to references.bib
# - Investigate failed verifications
# - Search for missing DOIs

# 3. Update the bib file with new DOIs
# 4. Re-run P0 pre-audit to check D10a improvements
```

## Output Format

The verification script outputs a JSON report with:
- `total_entries`: Total number of references
- `with_doi`: Number of entries with DOI
- `doi_coverage`: Percentage of entries with DOI
- `verified_via_crossref`: Number of successfully verified DOIs
- `failed_verification`: Number of failed verifications
- `missing_dois`: List of entries needing DOI search
- `results`: Detailed verification results for each entry

## Quality Impact

The reference verification directly impacts the paper's quality score:

| Metric | Impact on Quality Score |
|--------|------------------------|
| DOI Coverage ≥90% | +0.1 to D10a score |
| DOI Coverage 80-89% | +0.05 to D10a score |
| DOI Coverage <80% | -0.1 to D10a score |
| Crossref Verification ≥95% | +0.05 to D10a score |
| Crossref Verification <90% | -0.05 to D10a score |

## Reference Files

- `../../reference-verification/SKILL.md` - Main reference verification skill
- `../../reference-verification/scripts/verify-references.py` - Automated verification script