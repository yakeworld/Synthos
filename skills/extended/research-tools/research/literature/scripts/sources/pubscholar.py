"""
数据源：PubScholar（中文学术文献）
curl直调API — 签名算法来自 RSSHub PR #15788。
替代不稳定的 RSSHub 实例，直接对接 pubscholar.cn API。
"""
import hashlib
import json
import os
import random
import re
import string
import time
import uuid
from typing import Any, Dict, List, Optional


class PubScholar:
    """PubScholar 中文学术平台封装 — curl直调API。"""

    BASE_URL = "https://pubscholar.cn"
    SALT = os.environ.get('PUBSCHOLAR_SALT', 'YOUR_PUBSCHOLAR_SALT_HERE')

    def search(self, topic, max_results=10, year_range=None):
        """检索中文论文。

        Args:
            topic: 搜索关键词
            max_results: 最大结果数
            year_range: 年份范围（当前未用于筛选，预留）

        Returns:
            论文列表，格式符合 literature 统一数据契约。
        """
        # 生成签名
        nonce = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        ts = str(int(time.time() * 1000))
        sig = hashlib.sha1(''.join(sorted([self.SALT, ts, nonce])).encode()).hexdigest()
        xf = ''.join(format(random.randint(0, 2**32-1), '08x') for _ in range(4))
        uid = str(uuid.uuid4())

        # 构建请求头 — Cookie 使用 uid 作为实际 token
        cookie_val = "XSRF-TOKEN=" + uid
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "nonce": nonce,
            "timestamp": ts,
            "signature": sig,
            "x-finger": xf,
            "x-xsrf-token": uid,
            "Cookie": cookie_val,
            "Origin": self.BASE_URL,
            "Referer": self.BASE_URL + "/",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        body = json.dumps({
            "page": 1,
            "size": max_results,
            "order_field": "date",
            "order_direction": "desc",
            "user_id": hashlib.md5(str(int(time.time())).encode()).hexdigest(),
            "lang": "zh",
            "query": topic,
            "strategy": None,
            "orderField": "default"
        })

        try:
            import requests as req
            resp = req.post(
                self.BASE_URL + "/hky/open/resources/api/v1/articles",
                data=body.encode('utf-8'), headers=headers, timeout=15
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            if not data.get('content'):
                return []

            papers = []
            for item in data["content"][:max_results]:
                title = item.get("title", "")
                if not title or "error" in title.lower():
                    continue

                # 提取作者
                raw_authors = item.get("authors", [])
                authors = [a.get("name", "") for a in raw_authors if a.get("name")]

                # 提取 DOI
                doi_raw = item.get("doi", "")
                if isinstance(doi_raw, list):
                    doi = doi_raw[0] if doi_raw else ""
                else:
                    doi = str(doi_raw)

                # 来源期刊
                source_name = item.get("source", "")

                # 日期
                pub_date = item.get("pubDate", "")
                year = None
                if pub_date:
                    m = re.search(r'(\d{4})', str(pub_date))
                    if m:
                        year = int(m.group(1))

                # 链接
                links_raw = item.get("links", [])
                url = ""
                pdf_url = ""
                links: dict[str, str] = {}
                if isinstance(links_raw, dict):
                    u = links_raw.get("url", "") or links_raw.get("doi_url", "")
                    if u and "error" not in u.lower():
                        url = u
                        links["publisher"] = u
                    elif isinstance(links_raw, dict):
                        for lk_name, lk_url in links_raw.items():
                            if isinstance(lk_url, str) and lk_url.startswith("http") and "error" not in lk_url.lower():
                                links[lk_name] = lk_url
                elif isinstance(links_raw, list):
                    for lk in links_raw:
                        if isinstance(lk, dict):
                            u = lk.get("url", "")
                            if u and "error" not in u.lower():
                                url = u
                                links[lk.get("name", "publisher")] = u
                                break
                        elif isinstance(lk, str) and lk.startswith("http") and "error" not in lk.lower():
                            url = lk
                            links["publisher"] = url
                            break

                # 免费论文 CDN 直链
                local_links = item.get("local_links", [])
                if local_links and isinstance(local_links, list):
                    pdf_url = local_links[0]
                    for lk in local_links:
                        if isinstance(lk, str) and lk.startswith("http"):
                            links["cdn"] = lk

                paper = {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "source": "pubscholar",
                    "doi": doi,
                    "abstract": item.get("abstract", "") or "",
                    "url": url,
                    "pdf_url": pdf_url,
                    "local_links": local_links if local_links else [],
                    "links": links,
                    "citation_count": 0,
                    "venue": source_name or "PubScholar",
                    "is_free": item.get("is_free", False),
                    "provenance": "source=pubscholar, query=" + topic,
                }
                if paper["title"]:
                    papers.append(paper)
            return papers

        except Exception:
            return []

    def search_by_doi(self, doi):
        """PubScholar 不直接支持 DOI 检索。"""
        return None