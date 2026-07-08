#!/usr/bin/env python3
"""
下载模块 — 统一导出所有下载函数。
原子函数，按功能分类导入。
"""
from .utils import (
    safe_filename,
    save_pdf,
    verify_pdf,
    generate_bibkey,
)
from .tier4_publishers import (
    normalize_doi,
    extract_doi_from_text,
    extract_arxiv_id,
    extract_pmcs_id,
    extract_pmid,
)
from .http import (
    download_http,
    download_http_tor,
    download_via_subprocess,
    smart_download,
)
from .tier1_oa import (
    download_arxiv_pdf,
    download_frontiers_pdf,
    download_plos_pdf,
    download_crossref_link,
    download_unpaywall,
    download_pubmed_central,
    search_pmc_for_pubmed,
)
from .tier2_scihub import (
    download_scihub_direct,
    download_scihub_via_tor,
)
from .tier3_backup import (
    download_libgen,
    download_meddata,
)
from .tier4_publishers import (
    download_s2_pdf,
    download_biorxiv_pdf,
    download_core,
    download_doi2pdf,
    download_via_openurl,
    download_sciencedirect,
    download_springer,
    download_wiley,
    download_ieee,
    download_acm,
)
from .scheduler import (
    race_downloads,
    batch_download,
    run_test,
)

__all__ = [
    # Utils
    "safe_filename", "save_pdf", "verify_pdf", "generate_bibkey",
    "normalize_doi", "extract_doi_from_text", "extract_arxiv_id",
    "extract_pmcs_id", "extract_pmid",
    # HTTP
    "download_http", "download_http_tor", "download_via_subprocess", "smart_download",
    # Tier 1: OA
    "download_arxiv_pdf", "download_frontiers_pdf", "download_plos_pdf",
    "download_crossref_link", "download_unpaywall", "download_pubmed_central",
    "search_pmc_for_pubmed",
    # Tier 2: Sci-Hub
    "download_scihub_direct", "download_scihub_via_tor",
    # Tier 3: Backup
    "download_libgen", "download_meddata",
    # Tier 4: Publishers
    "download_s2_pdf", "download_biorxiv_pdf", "download_core",
    "download_doi2pdf", "download_via_openurl", "download_sciencedirect",
    "download_springer", "download_wiley", "download_ieee", "download_acm",
    # Scheduler
    "race_downloads", "batch_download", "run_test",
]