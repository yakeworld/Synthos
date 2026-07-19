"""
LibGen (Library Genesis) — 学术文献/书籍的影子图书馆。

原理:
  搜索 → 条目详情页 → 获取 MD5 + 下载镜像 → 下载 PDF

域名 (2026-07-18 实测):
  - libgen.bz — 主站, HTTP 200, 完整页面, Playwright 必需

流程:
  1. GET index.php?req=...&objects[]=e&curtab=e → 结果列表
  2. 点击条目链接 → edition.php?id=N → 文件详情
  3. 从详情页获取 MD5 和下载镜像 URL
  4. 尝试各镜像下载 PDF

依赖: playwright (sync_api)
"""
import re
import requests
from typing import Optional, List, Dict
from urllib.parse import quote

BASE = "https://libgen.bz"

# 下载镜像（按优先级）
MIRRORS = [
    "https://randombook.org/book/{md5}",
    "https://en.annas-archive.gl/md5/{md5}",
    "https://libgen.pw/book/{md5}",
]

# 模块级 Playwright 实例
_pw = None
_browser = None


def _get_page():
    global _pw, _browser
    if _browser is None:
        from playwright.sync_api import sync_playwright
        _pw = sync_playwright().start()
        _browser = _pw.chromium.launch(headless=True,
            args=["--disable-blink-features=AutomationControlled"])
    page = _browser.new_page()
    return page


def _cleanup():
    global _pw, _browser
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _pw:
        try:
            _pw.stop()
        except Exception:
            pass
        _pw = None


class LibGen:
    """LibGen 搜索与下载。

    用法:
        lg = LibGen()
        results = lg.search('deep learning', max_results=5)
        pdf = lg.download(results[0]['edition_id'])
    """

    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict]:
        """搜索 LibGen 条目。

        返回列表，每项含:
            edition_id, title, author, publisher, year,
            pages, language, size, ext, md5, mirrors
        """
        page = _get_page()
        try:
            url = (f"{BASE}/index.php"
                   f"?req={quote(query)}"
                   f"&columns%5B%5D=t&columns%5B%5D=a&columns%5B%5D=s"
                   f"&columns%5B%5D=y&columns%5B%5D=p&columns%5B%5D=i"
                   f"&objects%5B%5D=e&topics%5B%5D=l&curtab=e&res=25")
            page.goto(url, timeout=15000)
            page.wait_for_timeout(2000)

            # 跳过前4行（导航/表头/分页），取数据行
            rows = page.query_selector_all("tr")[4:]
            results = []

            for tr in rows[:max_results]:
                cells = tr.query_selector_all("td")
                if len(cells) < 7:
                    continue

                # 第1个td: 标题+链接
                title_link = cells[1].query_selector("a")
                if not title_link:
                    continue
                title = title_link.inner_text().strip()
                edition_url = title_link.get_attribute("href") or ""
                edition_id = ""
                if edition_url:
                    m = re.search(r'id=(\d+)', edition_url)
                    if m:
                        edition_id = m.group(1)

                author = cells[2].inner_text().strip() if len(cells) > 2 else ""
                publisher = cells[3].inner_text().strip() if len(cells) > 3 else ""
                year = cells[4].inner_text().strip() if len(cells) > 4 else ""

                # 结果只包含基础信息，详情在 download 时惰性获取
                results.append({
                    "edition_id": edition_id,
                    "title": title,
                    "author": author,
                    "publisher": publisher,
                    "year": year,
                    "ext": "",
                    "size": "",
                    "md5": "",
                })

            return results

        finally:
            page.close()

    @staticmethod
    def search_by_doi(doi: str) -> Optional[Dict]:
        """通过 DOI 搜索（fallback: 直接用 DOI 做关键词搜索）。"""
        results = LibGen.search(doi, max_results=3)
        # LibGen 搜索结果可能包含 DOI 在标题/描述中
        for r in results:
            if doi in r.get("title", "").lower():
                return r
        return results[0] if results else None

    @staticmethod
    def _get_edition_info(edition_id: str) -> Dict:
        """获取条目详情（MD5/ext/size/mirrors）。"""
        info = {"ext": "", "size": "", "md5": "", "mirrors": []}
        if not edition_id:
            return info

        page = _get_page()
        try:
            page.goto(f"{BASE}/edition.php?id={edition_id}", timeout=15000)
            page.wait_for_timeout(2000)
            text = page.evaluate("document.body.innerText")
            html = page.content()

            # 提取 MD5（优先从下载链接 get.php?md5=...，兜底全HTML hex）
            m = re.search(r'get\.php\?md5=([a-f0-9]{32})', html)
            if not m:
                m = re.search(r'ads\.php\?md5=([a-f0-9]{32})', html)
            if not m:
                m = re.search(r'([a-f0-9]{32})', html)
            if m:
                info["md5"] = m.group(1)

            # 从纯文本提取大小和扩展名
            m = re.search(r'Size:\s*([\d.]+\s*(?:MB|GB|KB|kB))', text)
            if m:
                info["size"] = m.group(1).strip()
            m = re.search(r'Extension:\s*(\w+)', text)
            if m:
                info["ext"] = m.group(1).lower()

            # 提取所有下载链接
            info["mirrors"] = []
            for mirror_url in [tmpl.format(md5=info["md5"]) for tmpl in MIRRORS]:
                if mirror_url:
                    info["mirrors"].append(mirror_url)

            # 也提取备用链接（文件名称构成的直接URL）
            for a in page.query_selector_all("a[href]"):
                href = a.get_attribute("href") or ""
                # 匹配 libgen.lol / libgen.li / library.lol 等直接下载
                if re.search(r'(libgen\.(lol|li)|library\.lol)', href) and href.endswith(".pdf"):
                    if href not in info["mirrors"]:
                        info["mirrors"].append(href)

            return info
        except Exception:
            return info
        finally:
            page.close()

    @staticmethod
    def download(query: str, ext: str = "pdf", timeout: int = 60) -> Optional[bytes]:
        """搜索并下载第一个匹配的 PDF。

        参数:
            query: 搜索关键词 或 edition_id（纯数字）
            ext: 文件格式（默认 pdf）
            timeout: 下载超时

        返回:
            bytes 或 None
        """
        # 1. 获取条目
        if query.isdigit():
            info = LibGen._get_edition_info(query)
            title = "unknown"
        else:
            results = LibGen.search(query, max_results=5)
            if not results:
                return None
            # 找第一个匹配 ext 的
            target = None
            for r in results:
                if r.get("ext") == ext:
                    target = r
                    break
            if not target:
                target = results[0]
            info = target
            title = target.get("title", "unknown")

        mirrors = info.get("mirrors", [])
        md5 = info.get("md5", "")
        edition_id = query if query.isdigit() else info.get("edition_id", "")

        # 2. 尝试各镜像下载
        for url in mirrors[:5]:
            try:
                r = requests.get(url, timeout=timeout, allow_redirects=True,
                                 headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200 and len(r.content) > 1000:
                    data = r.content
                    if data[:4] == b"%PDF":
                        return data
                    if data[:4] == b"PK\x03\x04":  # EPUB (ZIP)
                        if ext == "epub":
                            return data
                    # 如果返回 HTML，可能是中间页，找重定向链接
                    if b"<html" in data[:500].lower():
                        dl_links = re.findall(
                            r'href="([^"]+\.(?:pdf|epub))"',
                            data.decode("utf-8", errors="ignore"), re.I
                        )
                        for dl in dl_links:
                            if dl.startswith("//"):
                                dl = "https:" + dl
                            elif dl.startswith("/"):
                                dl = BASE + dl
                            r2 = requests.get(dl, timeout=timeout,
                                              headers={"User-Agent": "Mozilla/5.0"})
                            if r2.status_code == 200 and r2.content[:4] == b"%PDF":
                                return r2.content
            except Exception:
                continue

        # 3. 最终尝试：Playwright 打开 randombook 页面点击下载
        if md5:
            try:
                _page = _get_page()
                _page.goto(f"https://randombook.org/book/{md5}", timeout=15000)
                _page.wait_for_timeout(2000)
                _html = _page.content()
                _page.close()
                # 找所有 PDF 链接
                for m in re.finditer(r'href="([^"]+\.pdf)"', _html, re.I):
                    dl = m.group(1)
                    if dl.startswith("//"):
                        dl = "https:" + dl
                    elif dl.startswith("/"):
                        dl = "https://randombook.org" + dl
                    if not dl.startswith("http"):
                        continue
                    r3 = requests.get(dl, timeout=timeout,
                                      headers={"User-Agent": "Mozilla/5.0"})
                    if r3.status_code == 200 and r3.content[:4] == b"%PDF":
                        return r3.content
            except Exception:
                pass

        return None

    @staticmethod
    def cleanup():
        _cleanup()
