# PMCFullTextDownloader — PMCID Extraction & Dependencies

## PMCID Extraction from UnifiedPaper

`UnifiedPaper` does NOT have a `pubmed_id` attribute. PMID is stored in `external_ids`:

    pmid = p.external_ids.get('PMID', '')

- PMCID may be absent, the string "N/A", or a string without the "PMC" prefix.
- Always strip "PMC" prefix from the raw PMCID string before passing to download_and_extract().
- Pass the clean PMCID (without "PMC" prefix) to download_and_extract(pmcid, save_dir).

## Dependency

Requires pdfminer.six installed. If not present, PMCIDFullTextDownloader will fail on import.

    pip install pdfminer.six --break-system-packages

Without it, you can still search and retrieve metadata, but cannot download full-text XML/PDF from PMC.

## ResearchPaperManager.search_and_download max_results

main.py passes max_results as keyword argument to search_and_download(). The method signature must include max_results: int = 20 parameter.

The search_papers() call within should use limit=min(max_results, 100) to respect the S2 API limit-100 cap.

If the method signature does not have max_results, main.py search will crash with:

    ResearchPaperManager.search_and_download() got an unexpected keyword argument 'max_results'
