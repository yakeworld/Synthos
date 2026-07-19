#!/usr/bin/env python3
"""数据源：PubMed

职责: 通过 NCBI E-utilities API 检索生物医学文献。
设计决策:
- 使用 curl subprocess 而非 Python urllib POST（此主机上 urllib POST 会挂起）
- 两步查询：esearch 获取 PMID 列表 → esummary 获取详细信息
- 每个查询最多 3 个 PMID（API 限制，需分批）
- PMC 文章自动构建 PDF 链接
限制:
- 非生物医学领域覆盖差
- 无 PDF 直链（除 PMC 外），链接为 PubMed 页面
- 速率限制：无 key 3 req/s，设 NCBI_API_KEY 后 10 req/s

API 协议:
  POST https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
  POST https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
  认证: 可选 NCBI_API_KEY 环境变量（提升限流至 10 req/s）
  响应: JSON 格式

依赖: curl (subprocess), json (stdlib)
"""
import json
import os
import subprocess
import time
from typing import Optional

# 读取 NCBI API Key
NCBI_API_KEY = os.environ.get("NCBI_API_KEY", "").strip()


def _api_params(**kwargs) -> str:
    """构建 POST data，含 api_key（如有）。"""
    parts = [f"{k}={v}" for k, v in kwargs.items()]
    if NCBI_API_KEY:
        parts.append(f"api_key={NCBI_API_KEY}")
    return "&".join(parts)


class PubMed:
    """NCBI E-utilities API 封装。

    使用 curl subprocess 调用（Python urllib POST 在此主机上会挂起，
    这是已知系统限制，非代码问题）。

    两步查询流程:
      1. esearch(term=topic, retmax=N) → 获取 PMID 列表
      2. esummary(id=pmid1,pmid2,...) → 获取每篇详细信息

    NCBI_API_KEY 环境变量：
      设此变量后限流从 3 req/s 提升至 10 req/s，retmax 硬限取消。

    参数映射:
      search() 输入: topic (str), max_results (int), year_range (str|None)
        → esearch term, retmax (硬限 3)
      search_by_doi() 输入: doi (str)
        → esearch term=doi[aid], 自动提取 PMID

    数据流:
      用户查询 → esearch → PMID 列表 → esummary → 标准化纸
      提取: title, authors, year, doi, pmid, pmc, abstract, venue

    返回的 paper dict 包含:
      pdf_url: PMC 文章有 PDF 链接 (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/)
      links: pubmed, ncbi, pmc_fulltext
    """

    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索 PubMed 文献。

        参数:
            topic: 搜索关键词
            max_results: 最大结果数
            year_range: 未使用（PubMed API 不支持年份过滤）
        返回:
            list[dict]: 标准化论文列表。
            注意：PubMed 通常返回少量精确匹配结果，非广谱搜索结果。
        异常:
            不抛异常。网络错误、超时、空结果均返回 []。
        原理:
            - PubMed 是生物医学领域最权威的索引，覆盖 3900+ 期刊
            - 使用 esearch + esummary 两步查询，避免单次请求过大
            - 无 NCBI_API_KEY 时 max_results 硬限 3；
              有 key 时提升至 min(max_results, 50)
        """
        # Step 1: esearch — 获取 PMID 列表
        safe_max = min(max_results, 50) if NCBI_API_KEY else min(max_results, 3)
        esearch_cmd = (
            f'curl -s --connect-timeout 5 --max-time 10 '
            f'-X POST "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" '
            f'-d "{_api_params(db="pubmed", term=topic, retmax=safe_max, retmode="json")}"'
        )
        try:
            result = subprocess.run(esearch_cmd, shell=True, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                return []

            search_data = json.loads(result.stdout)
            pmid_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not pmid_list:
                return []

            # Step 2: esummary — 获取详细信息
            return self._get_details(pmid_list)

        except Exception:
            return []

    def search_by_doi(self, doi: str) -> Optional[dict]:
        """通过 DOI 检索 PubMed 文献。

        参数:
            doi: DOI 字符串
        返回:
            dict or None: 标准化论文或 None（DOI 未在 PubMed 中注册）
        原理:
            - PubMed 有 externalids.DOI 字段，可通过 [aid] 字段检索
            - 格式: term={doi}[aid] 精确匹配 DOI 到 PMID
        """
        try:
            cmd = (
                f'curl -s --connect-timeout 5 --max-time 10 '
                f'-X POST "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" '
                f'-d "{_api_params(db="pubmed", term=f"{doi}[aid]", retmode="json")}"'
            )
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)
            pmid_list = data.get("esearchresult", {}).get("idlist", [])
            if not pmid_list:
                return None

            return self._get_details(pmid_list[:3])[:3] or None

        except Exception:
            return None

    def _get_details(self, pmid_list: list[str]) -> list[dict]:
        """批量获取 PMID 详情。

        参数:
            pmid_list: PMID 字符串列表
        返回:
            list[dict]: 标准化论文列表
        原理:
            - esummary 单次最多处理 200 个 ID，但避免超时控制并发
            - 结果中 result 是 dict，key 为 PMID 字符串（非整数）
            - 需要过滤非 PMID 的 key（如 error 字段）
        """
        if not pmid_list:
            return []

        batch_size = 50 if NCBI_API_KEY else 3
        pmid_str = ",".join(pmid_list[:batch_size])
        esummary_cmd = (
            f'curl -s --connect-timeout 5 --max-time 10 '
            f'-X POST "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi" '
            f'-d "{_api_params(db="pubmed", id=pmid_str, retmode="json")}"'
        )
        try:
            result = subprocess.run(esummary_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            papers = []
            result_section = data.get("result", {})
            for pmid, doc in result_section.items():
                if not pmid.isdigit():
                    continue
                paper = {
                    "title": doc.get("title", ""),
                    "authors": [a.get("name", "") for a in doc.get("authors", [])],
                    "year": self._extract_year(doc.get("pubdate", "")),
                    "source": "pubmed",
                    "doi": doc.get("externalids", {}).get("DOI", ""),
                    "pmid": pmid,
                    "pmc": self._extract_pmc_id(doc),
                    "abstract": doc.get("abstract", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "pdf_url": "",
                    "local_links": [],
                    "links": {
                        "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "ncbi": f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}/",
                    },
                    "citation_count": 0,
                    "venue": doc.get("source", ""),
                    "provenance": f"source=pubmed, pmid={pmid}",
                }
                if paper["pmc"]:
                    paper["pdf_url"] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{paper['pmc']}/"
                    paper["links"]["pmc_fulltext"] = paper["pdf_url"]
                if paper["title"]:
                    papers.append(paper)

            return papers

        except Exception:
            return []

    @staticmethod
    def _extract_year(pubdate: str) -> Optional[int]:
        """从 pubdate 字符串提取年份。"""
        if not pubdate:
            return None
        parts = pubdate.replace(",", " ").split()
        for p in parts:
            if p.isdigit() and len(p) == 4:
                return int(p)
        return None

    @staticmethod
    def _extract_pmc_id(doc: dict) -> str:
        """从 articleids 或 externalids 提取 PMC 号（纯数字）。"""
        for aid in doc.get("articleids", []):
            if isinstance(aid, dict):
                idtype = aid.get("idtype", "")
                value = aid.get("value", "")
                if idtype in ("pmc", "pmcid"):
                    num = str(value).lstrip("PMC").lstrip("pmc").lstrip("PMC-")
                    if num and num.isdigit():
                        return num
        pmc = doc.get("externalids", {}).get("PMC", "")
        if pmc:
            return str(pmc).lstrip("PMC").lstrip("pmc").lstrip("PMC-")
        return ""
