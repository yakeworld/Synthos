#!/usr/bin/env python3
"""下载模块 — 统一导出所有下载函数。

职责: 提供文献 PDF 下载的统一接口。
所有下载函数通过 tier 分级：Tier 1-4，按优先级排序。

模块级导出:
  - smart_download(url, timeout) → bytes|None  — 通用下载
  - verify_pdf(content) → bool                — PDF 验证
  - normalize_doi(doi) → str                   — DOI 标准化
  - run_test() → dict                           — 连通性测试
  - try_meddata(doi, output_path) → dict|None      — MedData 兜底下载

Tier 架构:
  Tier 1: OA 直链 (arXiv, Frontiers, PLOS, CrossRef, Unpaywall, PMC)
  Tier 2: Sci-Hub (curl_cffi 直连 + Tor 代理)
  Tier 3: 备份 (LibGen, MedData)
  Tier 4: 出版社 (DOI2PDF, CORE, OpenURL, ScienceDirect, Springer, Wiley, IEEE, ACM)

设计决策:
- smart_download() 接受 URL，不关心来源，自动按 URL 特征选择策略
- verify_pdf() 检查 %PDF magic number，避免保存 HTML 错误页面
- normalize_doi() 去除 https://doi.org/ 前缀和大小写差异

限制:
- 部分 tier（如 Tier 4）需要特定网络环境
- MedData 需要机构 IP
- 某些出版社页面需要 JavaScript 渲染
"""
from .http import smart_download, verify_pdf, safe_filename, normalize_doi
from .config import MAX_SIZE, VERIFY_PDF_HEADER_BYTES, VERIFY_PDF_HEADER
from .scheduler import sequential_download, run_test
from .meddata import try_meddata
from .tier1_oa import download_arxiv_pdf, download_frontiers_pdf, download_plos_pdf, download_crossref_link, download_unpaywall, download_pubmed_central
from .tier2_scihub import download_scihub_direct, download_scihub_via_tor
from .tier3_backup import download_libgen
from .tier4_publishers import download_doi2pdf, download_core, download_sciencedirect, download_springer, download_wiley
from .utils import generate_bibkey
from .scientific_hub import download, download_direct, download_proxy, DIRECT_DOMAINS, PROXY_DOMAINS

__all__ = [
    "smart_download",
    "verify_pdf",
    "normalize_doi",
    "safe_filename",
    "sequential_download",
    "run_test",
    "try_meddata",
    "download_libgen",
    "download_arxiv_pdf",
    "download_frontiers_pdf",
    "download_plos_pdf",
    "download_crossref_link",
    "download_unpaywall",
    "download_pubmed_central",
    "download_scihub_direct",
    "download_scihub_via_tor",
    "download_doi2pdf",
    "download_core",
    "download_sciencedirect",
    "download_springer",
    "download_wiley",
    "generate_bibkey",
    "download",
    "download_direct",
    "download_proxy",
    "DIRECT_DOMAINS",
    "PROXY_DOMAINS",
    "MAX_SIZE",
    "VERIFY_PDF_HEADER_BYTES",
    "VERIFY_PDF_HEADER",
]

def download_meddata(doi: str) -> bytes | None:
    """Download PDF from MedData. Returns PDF bytes or None."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        tmp_path = f.name
    try:
        result = try_meddata(doi, tmp_path, doi=doi)
        if result and result.get('success') and os.path.exists(tmp_path):
            with open(tmp_path, 'rb') as f:
                return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return None
