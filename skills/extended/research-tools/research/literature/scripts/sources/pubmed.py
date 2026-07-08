"""
数据源：PubMed
"""
import json
import subprocess
import time
from typing import Optional


class PubMed:
    """NCBI E-utilities API 封装。
    
    使用 curl subprocess 调用（Python urllib POST 在此主机上会挂起）。
    """
    
    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索 PubMed 文献。"""
        # esearch
        esearch_cmd = (
            f'curl -s --connect-timeout 5 --max-time 10 '
            f'-X POST "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" '
            f'-d "db=pubmed&term={topic}&retmax={min(max_results, 3)}&retmode=json"'
        )
        try:
            result = subprocess.run(esearch_cmd, shell=True, capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                return []
            
            search_data = json.loads(result.stdout)
            pmid_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not pmid_list:
                return []
            
            return self._get_details(pmid_list)
        
        except Exception:
            return []
    
    def search_by_doi(self, doi: str) -> Optional[dict]:
        """通过 DOI 检索 PubMed 文献。"""
        try:
            cmd = (
                f'curl -s --connect-timeout 5 --max-time 10 '
                f'-X POST "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" '
                f'-d "db=pubmed&term={doi}%5Baid%5D&retmode=json"'
            )
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            pmid_list = data.get("esearchresult", {}).get("idlist", [])
            if not pmid_list:
                return None
            
            return self._get_details(pmid_list[:3])[:3]
        
        except Exception:
            return None
    
    def _get_details(self, pmid_list: list[str]) -> list[dict]:
        """批量获取 PMID 详情。"""
        pmid_str = ",".join(pmid_list)
        esummary_cmd = (
            f'curl -s --connect-timeout 5 --max-time 10 '
            f'-X POST "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi" '
            f'-d "db=pubmed&id={pmid_str}&retmode=json"'
        )
        try:
            result = subprocess.run(esummary_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return []
            
            data = json.loads(result.stdout)
            papers = []
            result_section = data.get("result", {})
            # result is a dict with PMID as keys: result["42388699"] -> doc
            for pmid, doc in result_section.items():
                # Skip the metadata keys that aren't PMIDs
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
                    # Has PMC — build direct PMC PDF/full-text URL
                    paper["pdf_url"] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{paper['pmc']}/"
                    paper["links"]["pmc_fulltext"] = paper["pdf_url"]
                if paper["title"]:
                    papers.append(paper)
            
            return papers
        
        except Exception:
            return []
    
    def _extract_year(self, pubdate: str) -> Optional[int]:
        """从 pubdate 字符串提取年份。"""
        if not pubdate:
            return None
        parts = pubdate.replace(",", " ").split()
        for p in parts:
            if p.isdigit() and len(p) == 4:
                return int(p)
        return None

    def _extract_pmc_id(self, doc: dict) -> str:
        """从 articleids 或 externalids 提取 PMC 号（纯数字）。"""
        # Try articleids first (type='pmc' or type='pmcid')
        for aid in doc.get("articleids", []):
            if isinstance(aid, dict):
                idtype = aid.get("idtype", "")
                value = aid.get("value", "")
                if idtype in ("pmc", "pmcid"):
                    # Extract just the numeric part: "PMC4236699" -> "4236699"
                    num = str(value).lstrip("PMC").lstrip("pmc").lstrip("PMC-")
                    if num and num.isdigit():
                        return num
        # Fallback: externalids PMC
        pmc = doc.get("externalids", {}).get("PMC", "")
        if pmc:
            return str(pmc).lstrip("PMC").lstrip("pmc").lstrip("PMC-")
        return ""