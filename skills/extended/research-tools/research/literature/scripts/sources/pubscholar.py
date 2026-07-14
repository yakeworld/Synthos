#!/usr/bin/env python3
"""
PubScholar 中文学术文献检索 — 直调 pubscholar.cn API

签名算法来自 RSSHub pubscholar/utils.ts 完整实现。
"""
import hashlib
import json
import os
import random
import re
import string
import time
import uuid
from html import unescape as _unescape_html
from typing import Any, Dict, List, Optional


def _clean_html(text):
    """移除 HTML 标签并解码 HTML 实体。"""
    if not text or not isinstance(text, str):
        return text
    cleaned = re.sub(r'<[^>]+>', '', text)
    cleaned = _unescape_html(cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def _generate_nonce(length=6):
    """生成 nonce — 等价于 JS: Math.random().toString(36).slice(2).toUpperCase()
    
    JS 行为：Math.random() 返回 [0, 1) 的 double，
    toString(36) 转为 base-36 字符串，slice(2) 去掉 "0." 前缀，
    toUpperCase() 转大写 → 结果包含 [0-9A-Z] 字符。
    循环追加直到长度 >= target，然后截取。
    """
    chars = string.ascii_uppercase + string.digits
    nonce = ''
    while len(nonce) < length:
        # 用 random.random() 模拟 JS Math.random()，生成 base-36 字符
        rand_val = random.random()
        # 转为 base-36 表示（类似 JS toString(36)）
        # 由于 Python 没有直接的 toString(36)，我们用一个近似方法
        # 取 random.random() 的十进制部分转 base-36
        s = format(int(rand_val * (10**15)), 'x').upper()
        nonce += s
    return nonce[:length]


def _generate_xfinger():
    """生成 x-finger — 等价于 JS:
    Math.floor(Math.random() * Number.MAX_SAFE_INTEGER)
      .toString(16)
      .slice(-len)
      .padStart(len, '0')
    
    每个 hex32(8) 是 32 位随机数转 8 位 hex。4 个拼接 = 32 字符。
    """
    hex32 = (lambda length:
        format(int(random.random() * (2**52)), 'x').upper()[-length:].zfill(length))
    return f"{hex32(8)}{hex32(8)}{hex32(8)}{hex32(8)}"


def _get_headers(query=""):
    """生成签名请求头。"""
    salt = os.environ.get('PUBSCHOLAR_SALT', 'YOUR_PUBSCHOLAR_SALT_HERE')
    nonce = _generate_nonce(6)
    ts = str(int(time.time() * 1000))
    
    # JS: sha1([salt, timestamp, nonce].toSorted().join(''))
    # .toSorted() = lexicographic sort (Python sorted() does the same for ASCII)
    sorted_vals = sorted([salt, ts, nonce])
    sig = hashlib.sha1("".join(sorted_vals).encode()).hexdigest()
    
    xf = _generate_xfinger()
    uid = str(uuid.uuid4())
    cookie_val = uid  # Pure UUID — matches x-xsrf-token
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://pubscholar.cn",
        "Referer": "https://pubscholar.cn/",
        "Cookie": cookie_val,
        "nonce": nonce,
        "timestamp": ts,
        "signature": sig,
        "x-finger": xf,
        "x-xsrf-token": uid,
    }
    return headers


def _get_proxies():
    """获取请求代理。优先直连，失败时自动切换 Tor 代理。"""
    tor_proxy = os.environ.get("TOR_PROXY", "")
    if tor_proxy:
        return {"http": tor_proxy, "https": tor_proxy}
    return None


class PubScholar:
    """PubScholar 中文学术平台封装 — 直调 API。"""
    
    BASE_URL = "https://pubscholar.cn"

    def search(self, topic, max_results=10, year_range=None):
        """检索中文论文。

        注意：PubScholar 已改为第三方应用认证模式（2026-07），
        开放 API 调用返回 {"cause":"第三方应用独立请求时，无此操作权限","failure":true}。
        除非有 APP_ID/APP_SECRET 凭证，否则此源返回空列表。

        Args:
            topic: 搜索关键词
            max_results: 最大结果数
            year_range: 年份范围（当前未用于筛选，预留）

        Returns:
            论文列表，格式符合 literature 统一数据契约。
        """
        # Check if credentials are available
        app_id = os.environ.get('PUBSCHOLAR_APP_ID', '')
        app_secret = os.environ.get('PUBSCHOLAR_APP_SECRET', '')
        if not app_id or not app_secret:
            # API requires authentication — silently return empty
            # (matching existing behavior of not crashing the pipeline)
            return []

        headers = _get_headers(topic)
        proxies = _get_proxies()

        try:
            import requests as req
            
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

            resp_kwargs = {
                'data': body.encode('utf-8'),
                'headers': headers,
                'timeout': 15,
            }
            if proxies:
                resp_kwargs['proxies'] = proxies
            
            resp = req.post(
                self.BASE_URL + "/hky/open/resources/api/v1/articles",
                **resp_kwargs
            )
            if resp.status_code != 200:
                return []
            
            data = resp.json()
            if not data.get('content'):
                return []

            papers = []
            for item in data["content"][:max_results]:
                title = _clean_html(item.get("title", ""))
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
                links = {}
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
                    "abstract": _clean_html(item.get("abstract", "")) or "",
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