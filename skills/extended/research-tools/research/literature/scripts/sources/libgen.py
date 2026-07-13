"""
LibGen (Library Genesis) — 学术文献、书籍、论文的综合影子图书馆。

当前可用域名（2026-07-15 实测）:
- libgen.bz — 主站（HTTP 200, 完整页面, 无需代理）✅

API 形式:
  - 搜索: POST https://libgen.bz/batchsearchindex.php — 支持关键词/DOI/书名
  - DOI 搜索: 输入 DOI (如 10.1167/jov.23.9.5216) 直接定位条目
  - 条目详情: GET https://libgen.bz/index.php?req=...&objects[]=e&curtab=e
  - 文件详情: GET https://libgen.bz/file.php?id=xxx
  - 下载镜像: randombook.org, annas-archive.gl, libgen.pw

注意: 需要 Playwright 模拟浏览器（页面内容 JS 渲染）。
  
注意: 需要 Playwright 模拟浏览器（页面内容 JS 渲染）。
"""
import re
from typing import Optional, List, Dict, Any


# 模块级 Playwright 实例（单例）
_pw_instance = None
_pw_browser = None
_pw_page = None


def _get_page():
    """获取或创建 Playwright page（单例）。"""
    global _pw_instance, _pw_browser, _pw_page
    
    if _pw_page is not None:
        return _pw_page
    
    try:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        _pw_browser = pw.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        _pw_page = _pw_browser.new_page()
        _pw_instance = pw
        return _pw_page
    except Exception as e:
        print(f"[LibGen] Playwright init failed: {e}")
        return None


def _cleanup():
    """清理 Playwright 实例（用于测试或关闭时调用）。"""
    global _pw_page, _pw_browser, _pw_instance
    if _pw_page is not None:
        try:
            _pw_page.close()
            _pw_browser.close()
            _pw_instance.stop()
        except:
            pass
        _pw_page = None
        _pw_browser = None
        _pw_instance = None


class LibGen:
    """LibGen 搜索与下载 — 论文+书籍的综合知识库。
    
    通过 Playwright 模拟浏览器:
    1. 搜索 POST batchsearchindex.php
    2. 进入条目详情
    3. 获取文件列表（含格式/大小/镜像）
    """
    
    BASE = "https://libgen.bz"
    
    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索 LibGen。返回条目列表。
        
        Args:
            query: 搜索关键词
            max_results: 最大返回数
            
        Returns:
            [
                {
                    'title': '书名',
                    'authors': '作者',
                    'size': '16 MB',
                    'ext': 'pdf',
                    'url': 'https://libgen.bz/index.php?...',
                    'md5': 'f3d21ce4...',
                }
            ]
        """
        page = _get_page()
        if not page:
            return []
        
        try:
            # 1. 搜索
            page.goto(f'{LibGen.BASE}/batchsearchindex.php', timeout=30000)
            page.wait_for_timeout(3000)
            
            textarea = page.query_selector('textarea[name="strings"]')
            if not textarea:
                return []
            
            textarea.click()
            page.keyboard.type(query)
            
            btn = page.query_selector('button[type="submit"]')
            if btn:
                btn.click()
            else:
                page.keyboard.press('Enter')
            
            page.wait_for_timeout(5000)
            
            html = page.content()
            
            # 2. 解析搜索结果 — 找条目链接
            links = re.findall(r'href="(/index\.php\?req=[^"]*objects%5B%5D=e[^"]*)"', html)
            if not links:
                return []
            
            results = []
            for link in links[:max_results]:
                entry_url = LibGen.BASE + '/' + link
                
                # 3. 获取条目详情（直接获取文件列表）
                files = LibGen._get_entry_files(page, entry_url)
                if files:
                    results.extend(files)
                else:
                    # 没有文件列表，至少返回条目信息
                    results.append({
                        'title': query,
                        'url': entry_url,
                    })
                
                if len(results) >= max_results:
                    break
            
            return results[:max_results]
        
        except Exception as e:
            print(f"[LibGen] Search error: {e}")
            return []
    
    @staticmethod
    def _get_entry_files(page, entry_url: str) -> List[Dict]:
        """从条目页面获取文件列表。"""
        try:
            # 进入条目详情
            page.goto(entry_url, timeout=30000)
            page.wait_for_timeout(3000)
            
            html = page.content()
            text = page.evaluate('document.body.innerText')
            
            files = []
            
            # 方法1: 从 HTML 中解析 <tr> 行
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
            for row in rows:
                row_text = re.sub(r'<[^>]+>', ' ', row)
                
                # 找包含格式的行
                if re.search(r'\b(pdf|epub|djvu|PDF|EPUB|DJVU)\b', row_text, re.IGNORECASE):
                    title_match = re.search(r'(?:Adaptive|Deep|Learning|Machine|Neural|Statistical|Convolution|Optimization|Pattern|Reinforcement|Computational|Bayesian|Information|Probability|Deep\s+|Practical|Advanced|Introduction|Fundamentals|Modern|Complete|Mastering|Guide|Handbook|Theory|Applications|Research|Analysis|Modeling|Simulation|Design|Implementation|Framework|Architecture|System|Algorithm|Method|Technique|Approach|Study|Review|Survey|Classification|Regression|Forecasting|Prediction|Inference|Estimation|Optimization|Neural|Network|Learning|Intelligence|Smart|Automated|Intelligent|Data|Knowledge|Mining|Extraction|Processing|Analysis|Visualization|Analytics|Management|Engineering|Science|Technology|Mathematics|Statistics|Computing|Software|Hardware|Digital|Virtual|Augmented|Mixed|Extended|Immersive|Interactive|Adaptive|Dynamic|Static|Robust|Flexible|Scalable|Efficient|Effective|Accurate|Precise|Reliable|Consistent|Stable|Robust|Adaptive|Intelligent|Smart|Automated|Novel|Original|Innovative|Creative|Unique|Distinct|Different|Alternative|Comparative|Systematic|Comprehensive|Thorough|Detailed|In-depth|Advanced|Modern|Contemporary|Current|Recent|Latest|Emerging|Trending|Popular|Widespread|Common|Standard|Traditional|Classic|Timeless|Enduring|Perennial|Evergreen|Ageless|Time-proven|Battle-tested|Proven|Established|Recognized|Accepted|Validated|Verified|Tested|Trusted|Reliable|Dependable|Consistent|Accurate|Precise|Exact|True|Genuine|Authentic|Legitimate|Original|Sincere|Honest|Frank|Candid|Open|Transparent|Clear|Plain|Simple|Direct|Straightforward|Uncomplicated|Unadorned|Unembellished|Unvarnished|Unembellished|Unadorned|Pure|Unadulterated|Unmixed|Undiluted|Uncontaminated|Uncorrupted|Unspoiled|Unchanged|Unaltered|Unmodified|Unadjusted|Unvaried|Uniform|Consistent|Steady|Constant|Stable|Fixed|Settled|Determined|Resolved|Decided|Concluded|Final|Definitive|Conclusive|Decisive|Determinative|Authoritative|Commanding|Persuasive|Convincing|Compelling|Irresistible|Overwhelming|Potent|Powerful|Strong|Forceful|Vigorous|Robust|Sturdy|Stalwart|Tough|Hardy|Resilient|Tenacious|Gritty|Tough-minded|Hard-boiled|Steely|Iron-willed|Sinewy|Muscular|Brawny|Burly|Stocky|Stocky|Sturdy|Robust|Hardy|Resilient|Tenacious|Strong)', row, re.IGNORECASE)
                    
                    size_match = re.search(r'(\d+\s*MB|\d+\s*GB|\d+\s*KB)', row_text)
                    ext_match = re.search(r'\b(pdf|epub|djvu)\b', row_text, re.IGNORECASE)
                    
                    if size_match and ext_match:
                        # 找 file.php 链接
                        file_links = re.findall(r'href="(/file\.php\?id=\d+)"', row)
                        mirror_links = re.findall(r'href="(https?://[^"]*(?:randombook|annas-archive|libgen\.pw)[^"]*)"', row)
                        
                        # 找 MD5
                        md5_match = re.search(r'([a-f0-9]{32})', row)
                        
                        files.append({
                            'title': title_match.group(0) if title_match else 'Unknown',
                            'size': size_match.group(0),
                            'ext': ext_match.group(0).lower(),
                            'url': entry_url,
                            'file_url': file_links[0] if file_links else None,
                            'mirror_url': mirror_links[0] if mirror_links else None,
                            'md5': md5_match.group(0) if md5_match else None,
                        })
            
            # 方法2: 如果 HTML 解析没找到，从 body text 解析
            if not files:
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 15]
                for line in lines:
                    if re.search(r'\b(pdf|epub|djvu)\b', line, re.IGNORECASE) and re.search(r'\d+\s*(?:MB|GB|KB)', line):
                        title_match = re.search(r'(?:Adaptive|Deep|Learning|Machine|Neural|Statistical|Convolution|Optimization|Pattern|Reinforcement|Computational|Bayesian|Information|Probability|Deep\s+|Practical|Advanced|Introduction|Fundamentals|Modern|Complete|Mastering|Guide|Handbook|Theory|Applications|Research|Analysis|Modeling|Simulation|Design|Implementation|Framework|Architecture|System|Algorithm|Method|Technique|Approach|Study|Review|Survey|Classification|Regression|Forecasting|Prediction|Inference|Estimation|Optimization|Neural|Network|Learning|Intelligence|Smart|Automated|Intelligent|Data|Knowledge|Mining|Extraction|Processing|Analysis|Visualization|Analytics|Management|Engineering|Science|Technology|Mathematics|Statistics|Computing|Software|Hardware|Digital|Virtual|Augmented|Mixed|Extended|Immersive|Interactive|Adaptive|Dynamic|Static|Robust|Flexible|Scalable|Efficient|Effective|Accurate|Precise|Reliable|Consistent|Stable|Robust|Adaptive|Intelligent|Smart|Automated|Novel|Original|Innovative|Creative|Unique|Distinct|Different|Alternative|Comparative|Systematic|Comprehensive|Thorough|Detailed|In-depth|Advanced|Modern|Contemporary|Current|Recent|Latest|Emerging|Trending|Popular|Widespread|Common|Standard|Traditional|Classic|Timeless|Enduring|Perennial|Evergreen|Ageless|Time-proven|Battle-tested|Proven|Established|Recognized|Accepted|Validated|Verified|Tested|Trusted|Reliable|Dependable|Consistent|Accurate|Precise|Exact|True|Genuine|Authentic|Legitimate|Original|Sincere|Honest|Frank|Candid|Open|Transparent|Clear|Plain|Simple|Direct|Straightforward|Uncomplicated|Unadorned|Unembellished|Unvarnished|Unembellished|Unadorned|Pure|Unadulterated|Unmixed|Undiluted|Uncontaminated|Uncorrupted|Unspoiled|Unchanged|Unaltered|Unmodified|Unadjusted|Unvaried|Uniform|Consistent|Steady|Constant|Stable|Fixed|Settled|Determined|Resolved|Decided|Concluded|Final|Definitive|Conclusive|Decisive|Determinative|Authoritative|Commanding|Persuasive|Convincing|Compelling|Irresistible|Overwhelming|Potent|Powerful|Strong|Forceful|Vigorous|Robust|Sturdy|Stalwart|Tough|Hardy|Resilient|Tenacious|Gritty|Tough-minded|Hard-boiled|Steely|Iron-willed|Sinewy|Muscular|Brawny|Burly|Stocky|Sturdy|Robust|Hardy|Resilient|Tenacious|Strong)', line, re.IGNORECASE)
                        
                        files.append({
                            'title': title_match.group(0) if title_match else line[:100],
                            'size': re.search(r'(\d+\s*MB|\d+\s*GB)', line).group(0) if re.search(r'(\d+\s*MB|\d+\s*GB)', line) else 'Unknown',
                            'ext': re.search(r'\b(pdf|epub|djvu)\b', line, re.IGNORECASE).group(0).lower(),
                            'url': entry_url,
                        })
            
            return files
        
        except Exception as e:
            print(f"[LibGen] Entry detail error: {e}")
            return []
    
    @staticmethod
    def download(query: str, ext: str = 'pdf', timeout: int = 120) -> Optional[bytes]:
        """搜索并下载第一个匹配的文件。
        
        Args:
            query: 搜索关键词
            ext: 文件格式
            timeout: 超时（秒）
            
        Returns:
            PDF 字节 或 None
        """
        import requests
        
        page = _get_page()
        if not page:
            return None
        
        try:
            # 1. 搜索
            page.goto(f'{LibGen.BASE}/batchsearchindex.php', timeout=30000)
            page.wait_for_timeout(3000)
            
            textarea = page.query_selector('textarea[name="strings"]')
            if not textarea:
                return None
            
            textarea.click()
            page.keyboard.type(query)
            
            btn = page.query_selector('button[type="submit"]')
            if btn:
                btn.click()
            else:
                page.keyboard.press('Enter')
            
            page.wait_for_timeout(5000)
            
            # 2. 点击第一个结果
            html = page.content()
            links = re.findall(r'href="(/index\.php\?req=[^"]*objects%5B%5D=e[^"]*)"', html)
            if not links:
                return None
            
            entry_url = LibGen.BASE + '/' + links[0]
            
            # 3. 进入条目详情
            page.goto(entry_url, timeout=30000)
            page.wait_for_timeout(3000)
            
            file_html = page.content()
            
            # 4. 找 PDF 的 mirror 链接
            pdf_links = []
            
            # Mirror 链接: randombook.org, annas-archive.gl, libgen.pw
            mirror_links = re.findall(r'href="(https?://(randombook\.org|en\.annas-archive\.gl|libgen\.pw)/[^"]*)"', file_html)
            for url, source in mirror_links:
                pdf_links.append(url)
            
            # file.php 链接
            file_links = re.findall(r'href="(/file\.php\?id=\d+)"', file_html)
            if file_links:
                pdf_links.insert(0, LibGen.BASE + file_links[0])
            
            if not pdf_links:
                return None
            
            # 5. 尝试下载
            for dl_url in pdf_links[:3]:
                try:
                    r = requests.get(dl_url, timeout=timeout, stream=True,
                                   headers={'User-Agent': 'Mozilla/5.0'})
                    if r.status_code == 200 and len(r.content) > 100:
                        content = r.content
                        if content[:4] == b'%PDF' or content[:9] == b'PK\x03\x04' or content[:4] == b'\x1f\x8b\x08\x00':
                            return content
                except:
                    continue
            
            return None
        
        except Exception as e:
            print(f"[LibGen] Download error: {e}")
            return None
