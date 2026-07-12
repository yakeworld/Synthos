#!/usr/bin/env python3
"""
Tier 3: 备份下载 — 纯引用层，实际实现来自 sources 模块。

设计决策:
  不再在此文件中实现下载逻辑，所有实现统一归口到 sources/ 模块。
"""
from typing import Optional, Dict, Any

def download_libgen(doi: str = None, title: str = None) -> Optional[bytes]:
    """从 LibGen 下载（通过 sources.libgen）。"""
    try:
        from ..sources.libgen import LibGen
        libgen = LibGen()
        if doi:
            result = libgen.search_by_doi(doi)
        elif title:
            result = libgen.search(title[:100])
        else:
            return None
        
        if result and isinstance(result, dict):
            pdf_url = result.get('pdf_url', result.get('download_link'))
            if pdf_url and isinstance(pdf_url, str):
                import requests
                r = requests.get(pdf_url, timeout=30)
                if r.content[:4] == b'%PDF' and len(r.content) > 100:
                    return r.content
        return None
    except Exception:
        return None

def try_meddata(doi: str = None, output_path: str = None, pmid: str = None, extra: Dict = None) -> Optional[Dict]:
    """从 MedData 下载（正确实现：SSO + full_look + viewtext）。"""
    from .meddata import try_meddata as _try_meddata
    return _try_meddata(doi=doi, output_path=output_path, pmid=pmid, extra=extra)
