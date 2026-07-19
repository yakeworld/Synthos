#!/usr/bin/env python3
"""
Tier 3: 备份下载 — LibGen + MedData。

LibGen: 通过 Playwright 搜索 libgen.bz → MD5 → 镜像下载
MedData: 通过 SSO + full_look + viewtext 下载
"""
from typing import Optional, Dict

def download_libgen(doi: str = None, title: str = None) -> Optional[bytes]:
    """从 LibGen 下载（通过 sources.libgen）。"""
    try:
        from ..sources.libgen import LibGen
        lg = LibGen()
        if doi:
            result = lg.search(doi, max_results=3)
            if result:
                return lg.download(result[0]["edition_id"])
        if title:
            result = lg.search(title[:100], max_results=3)
            if result:
                return lg.download(result[0]["edition_id"])
        return None
    except Exception:
        return None

def try_meddata(doi: str = None, output_path: str = None, pmid: str = None, extra: Dict = None) -> Optional[Dict]:
    """从 MedData 下载（正确实现：SSO + full_look + viewtext）。"""
    from .meddata import try_meddata as _try_meddata
    return _try_meddata(doi=doi, output_path=output_path, pmid=pmid, extra=extra)
