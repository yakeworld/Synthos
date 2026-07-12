#!/usr/bin/env python3
"""数据源：Sci-Hub（bban.top CDN 直连）

职责: 通过 bban.top CDN 直连下载 PDF（无需 HTML 中转）。
原理: https://sci.bban.top/pdf/{DOI}.pdf → 直接返回 PDF 字节。
限制: 
- 仅对有 DOI 的论文有效
- 2025+ 新论文可能未被收录
- 预印本平台（SSRN/Cassyni 等）不收录
"""
import subprocess
import os
import re
from typing import Optional, Dict, Any

SCIHUB_CDN = "https://sci.bban.top/pdf/%s.pdf"

class SciHub:
    """Sci-Hub 数据源 — bban.top CDN 直连下载"""
    
    NAME = "scihub"
    
    def __init__(self):
        pass
    
    def search(self, query: str, max_results: int = 10) -> list:
        """搜索不支持（bban.top 需要 DOI）。返回空列表。"""
        return []
    
    def search_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """通过 DOI 尝试从 bban.top 下载 PDF。"""
        if not doi:
            return None
        
        url = SCHI_HUB_CDN % doi
        result = subprocess.run(
            ['curl', '-s', '-o', '/tmp/scihub_doi.pdf', '-m', '60', '-L', url],
            capture_output=True, text=True, timeout=65
        )
        
        if os.path.exists('/tmp/scihub_doi.pdf') and os.path.getsize('/tmp/scihub_doi.pdf') > 100:
            with open('/tmp/scihub_doi.pdf', 'rb') as f:
                header = f.read(5)
            if header == b'%PDF-':
                size = os.path.getsize('/tmp/scihub_doi.pdf')
                return {
                    'doi': doi,
                    'pdf_url': url,
                    'pdf_local': '/tmp/scihub_doi.pdf',
                    'source': 'scihub',
                    'size': size,
                }
        
        return None
