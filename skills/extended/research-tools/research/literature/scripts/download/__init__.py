#!/usr/bin/env python3
"""下载模块 — 统一导出所有下载函数。

Tier 架构:
  Tier 1: OA 直链 (arXiv, Frontiers, PLOS, CrossRef, Unpaywall, PMC)
  Tier 2: Sci-Hub (bban.top 直连)
  Tier 3: 备份 (LibGen, MedData)
  Tier 4: 出版社 (DOI2PDF, CORE, OpenURL, ScienceDirect, Springer, Wiley, IEEE, ACM)

设计决策:
  所有下载函数通过 tier 分级，按优先级排序。
  每个 Tier 失败后自动回退到下一级。
  最终验证: PDF magic number (5 bytes: %PDF-)。
"""
from .config import (
    CONNECT_TIMEOUT, READ_TIMEOUT, TOTAL_TIMEOUT, MAX_SIZE, USER_AGENT
)
from .utils import (
    safe_filename, save_pdf, verify_pdf, generate_bibkey
)
from .http import smart_download, download_via_curl, download_via_urllib, normalize_doi
from .tier1_oa import (
    download_arxiv_pdf, download_frontiers_pdf, download_plos_pdf,
    download_crossref_link, download_unpaywall, download_pubmed_central,
    search_pmc_for_pubmed
)
from .scientific_hub import download as download_scihub
from .tier3_backup import download_libgen
from .tier4_publishers import download_doi2pdf, download_core, download_springer, download_wiley
from .meddata import try_meddata
from .scheduler import run_test

__all__ = [
    "smart_download", "verify_pdf", "safe_filename", "save_pdf",
    "generate_bibkey", "normalize_doi", "download_scihub",
    "download_libgen", "try_meddata", "run_test",
    "download_arxiv_pdf", "download_frontiers_pdf", "download_plos_pdf",
    "download_crossref_link", "download_unpaywall", "download_pubmed_central",
    "search_pmc_for_pubmed",
    "download_doi2pdf", "download_core", "download_springer", "download_wiley",
]
