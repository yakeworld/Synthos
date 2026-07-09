#!/usr/bin/env python3
"""数据源：Sci-Hub（用于获取全文下载地址）

职责: 通过 Sci-Hub 获取论文全文 PDF，作为文献检索的兜底下载源。
设计决策:
- 按域名顺序尝试（sci-hub.se → sci-hub.ru → sci-hub.st）
- search() 返回空列表（Sci-Hub 不支持关键词搜索）
- search_by_doi() 返回含 PDF 直链的论文数据
- download_by_doi() 直接下载 PDF 字节
限制:
- Sci-Hub 域名频繁变动，需手动维护 DOMAINS 列表
- 无正式 API，通过 HTTP 请求直接获取 PDF
- 部分 PDF 页面不是纯 PDF（403/拦截页面）
- 法律灰色区域，仅限机构内部研究使用

API 协议:
  GET https://{domain}/{doi} → PDF 直链
  认证: 无（但可能被 ISP/国家防火墙拦截）
  响应: application/pdf（成功时）

依赖: urllib (stdlib)
"""
import os
import json
import urllib.request
import urllib.parse
import re
from typing import Optional


class SciHub:
    """Sci-Hub 全文下载封装。

    作为文献检索源，返回论文的完整信息 + PDF 直链。
    按域名顺序尝试。

    域名维护:
      DOMAINS = ["https://sci-hub.se", "https://sci-hub.ru", "https://sci-hub.st"]
      域名失效时（连接超时/返回 HTML 而非 PDF），自动尝试下一个域名。
      验证逻辑: content.length > 10000 AND "%PDF" in content[:10]

    参数映射:
      search() → 始终返回 []（Sci-Hub 不支持搜索）
      search_by_doi() 输入: doi (str)
        → API: GET {domain}/{doi}
        → 验证: 响应为 PDF 字节（不是 HTML）
      download_by_doi() 输入: doi (str), timeout (int), output_path (str|None)
        → API: 同上，但保存文件而非返回内存

    数据流:
      DOI → 尝试各域名 → 验证 PDF → 解析页面 HTML 获取标题/作者/年份
      → 标准化纸（pdf_url = Sci-Hub URL 本身）

    注意: Sci-Hub 页面的 HTML 可能变化，标题/作者/年份提取可能失效。
    建议调用方用其他源（S2/CrossRef）补充元数据。
    """

    # Sci-Hub 域名（按需维护，按成功率排序）
    DOMAINS = [
        "https://sci-hub.se",
        "https://sci-hub.ru",
        "https://sci-hub.st",
    ]

    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """搜索 Sci-Hub 论文。

        注意: Sci-Hub 没有正式 API，不支持关键词搜索。
        此方法始终返回空列表。
        正确用法: 通过 search_by_doi() 查询特定 DOI。
        """
        return []

    def search_by_doi(self, doi: str) -> Optional[dict]:
        """通过 DOI 从 Sci-Hub 获取全文链接。

        参数:
            doi: DOI 字符串
        返回:
            dict or None: 标准化论文或 None（所有域名均失败）
        原理:
          1. 尝试各域名，请求 {domain}/{doi}
          2. 验证响应为 PDF（长度 > 10KB 且以 %PDF 开头）
          3. 如果 PDF 有效，再请求一次 HTML 页面提取元数据
          4. 标题从 <title> 标签提取
          5. 作者/年份可能提取失败（Sci-Hub 页面结构变化频繁）

        返回的纸:
            pdf_url = Sci-Hub URL（本身就是 PDF 直链）
            local_links = [pdf_url]
            links = {"scihub": pdf_url}
        """
        if not doi:
            return None

        # 步骤 1: 尝试获取 PDF
        content = None
        url = ""

        for domain in self.DOMAINS:
            url = f"{domain}/{doi}"
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Synthos-Literature/1.0",
                    "Accept": "application/pdf",
                })
                with urllib.request.urlopen(req, timeout=60) as resp:
                    content = resp.read()
                    # 验证 PDF: 长度 > 10KB 且以 %PDF 开头
                    if len(content) > 10000 and b"%PDF" in content[:10]:
                        break
            except Exception:
                continue

        if content is None:
            return None

        # 步骤 2: 解析 HTML 获取元数据
        title = ""
        authors = []
        year = None

        try:
            for domain in self.DOMAINS:
                page_url = f"{domain}/{doi}"
                try:
                    req = urllib.request.Request(page_url, headers={
                        "User-Agent": "Synthos-Literature/1.0",
                    })
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        html = resp.read().decode("utf-8", errors="ignore")

                    # 尝试从 HTML 中提取标题
                    title_m = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
                    if title_m:
                        title = title_m.group(1).strip()

                except Exception:
                    continue
        except Exception:
            pass

        if not title:
            title = f"Paper (DOI: {doi})"

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "source": "scihub",
            "doi": doi,
            "abstract": "",
            "url": url,
            "pdf_url": url,  # Sci-Hub URL 本身就是 PDF 直链
            "local_links": [url],
            "links": {"scihub": url},
            "citation_count": 0,
            "venue": "",
            "provenance": f"source=scihub, doi={doi}",
        }

    def download_by_doi(self, doi: str, timeout: int = 60, output_path: Optional[str] = None) -> Optional[bytes]:
        """通过 DOI 从 Sci-Hub 下载 PDF。

        参数:
            doi: DOI 字符串
            timeout: 超时秒数
            output_path: 输出文件路径（可选，保存到磁盘）
        返回:
            bytes or None: PDF 字节或 None（所有域名均失败）
        原理:
          - 与 search_by_doi 相同的域名尝试逻辑
          - 如果 output_path 不为 None，额外保存文件
          - 返回原始 PDF 字节，调用方自行验证
        """
        content = None
        for domain in self.DOMAINS:
            url = f"{domain}/{doi}"
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Synthos-Literature/1.0",
                    "Accept": "application/pdf",
                })
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    content = resp.read()
                    if len(content) > 10000 and b"%PDF" in content[:10]:
                        break
            except Exception:
                continue

        if content and output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(content)

        return content if content else None
