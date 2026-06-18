# MedData Coverage Limits & 2026-06-18 Download Failures

## Empirical Results (8 papers tested)

### Successful (1/8)

| Paper | DOI | Result | Size | MD5 |
|-------|-----|--------|------|-----|
| Ling2020Barany | 10.3389/fneur.2020.00602 | REAL PDF (Frontiers Neurology) | 663417 B | c42bfb3cdb3a9751f99dd7d8dea5bb50 |

### Placeholder/No Coverage (7/8)

All returned status=2 and identical placeholder PDF:

| Paper | DOI | Journal | Publisher |
|-------|-----|---------|-----------|
| Saeedi2019 | 10.1016/j.diabres.2019.107843 | Diabetes Research | Elsevier |
| Zheng2018 | 10.1038/nrendo.2017.151 | Nature Reviews Endocrinology | Nature/Springer |
| Riley2020SampleSize | 10.1136/bmj.m441 | BMJ | BMJ Publishing |
| Vollmer2020Machine | 10.1136/bmj.l6927 | BMJ | BMJ Publishing |
| Wu2024BRFSS | 10.1002/eng2.13080 | Engineering Reports | Wiley |
| Stekhoven2012missForest | 10.1093/bioinformatics/btr597 | Bioinformatics | Oxford |
| Mehta2024 | 10.1007/s41666-024-00189-8 | Journal of Healthcare Informatics | Springer |
| Stiglic2012Missing | 10.1007/s10916-012-9822-z | Journal of Medical Systems | Springer |

All returned: status=2, fileUrl=null, doiUrl=null, placeholder MD5=fd469bd7cd29446f2800f099e3b71457 (606841 bytes)

## Key Patterns

1. MedData does NOT cover Western/Elsevier/Springer/Nature/BMJ/Oxford journals
2. Only Frontiers papers (at least some) are accessible
3. All placeholder PDFs are identical regardless of DOI (606KB fake doc, title "PII: 0006-2944(75)90147-7", 2003-old paper)

## Workaround Attempts (All Failed)

### OA Direct Download
- Frontiers format: 404 for Tonin2025 (DOI not found on platform)
- PLOS ONE format: 404 for Amri2025

### PubMed Central (PMC)
- reCAPTCHA challenge blocks automated PDF access

### Sci-Hub
- All 11 domains blocked by DDoS-Guard/Cloudflare JavaScript challenge (2026-06-18)

## Recommendation

For Western journal papers not in MedData:
1. Manual browser download (user has reported browser works on MedData)
2. Institution library proxy (WMU library)
3. Remove invalid references from Bib if unobtainable (Chang2024, Deepalakshmi2025, Wen2024Leakage are DOI-invalid)
