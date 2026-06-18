# Sci-Hub PDF Download via curl_cffi

> 2026-05-27 发现并验证。比Playwright浏览器自动化快4倍（4s vs 15s）。

## 问题

Sci-Hub 所有镜像被 DDoS-Guard 保护，返回 JS 挑战页。标准 HTTP 库（requests/aiohttp）无法绕过——Content-Type 返回 `text/html` 而非 `application/pdf`。

## 解决方案：curl_cffi TLS 指纹模拟

`curl_cffi` 库模拟 Chrome 120 的 TLS 握手指纹。DDoS-Guard 识别为真实浏览器，放行请求。

```python
from curl_cffi import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (...)"}

# Step 1: 获取落地页
r = requests.get(f"https://sci-hub.ru/{doi}", headers=headers, 
                 impersonate="chrome120", timeout=30)

# Step 2: 提取PDF URL
soup = BeautifulSoup(r.text, 'html.parser')
pdf_rel = None

# 方式A: 下载按钮
for a in soup.find_all('a'):
    href = a.get('href', '')
    if 'download' in a.text.lower() or ('.pdf' in href and 'storage' in href):
        pdf_rel = href; break

# 方式B: iframe
if not pdf_rel:
    iframe = soup.find('iframe', id='pdf')
    if iframe and iframe.get('src'):
        pdf_rel = iframe['src']

# 拼完整URL
pdf_url = pdf_rel if pdf_rel.startswith('http') else f"https://sci-hub.ru{pdf_rel}"

# Step 3: 下载PDF（用同样impersonate保持session连贯）
r2 = requests.get(pdf_url, headers=headers, impersonate="chrome120", timeout=60)
assert r2.content[:4] == b'%PDF'  # 验证
```

## 可用镜像（2026-05-27 实测11个）

`sci-hub.ru`, `sci-hub.ee`, `sci-hub.shop`, `sci-hub.ren`, `sci-hub.red`,
`sci-hub.al`, `sci-hub.vg`, `sci-hub.wf`, `sci-hub.es`, `sci-hub.box`, `sci-hub.yt`

## 已知限制

- 论文不在数据库中返回"статья отсутствует в базе"（俄语"文章不存在"）
- 需 `curl_cffi >= 0.15`（impersonate 参数）
- 首次安装：`pip install curl_cffi`

## 集成到 Research Paper Manager

代码在 `src/downloader/scihub_download.py`。被 `PDFDownloader._try_scihub_playwright()` 调用。

调用链：search → download_pdf → _try_sci_hub_download → 检测DDoS-Guard → _try_scihub_playwright → scihub_download.py（子进程）

方法名 `_try_scihub_playwright` 保留历史命名，实际使用 curl_cffi。Playwright 版本已弃用。
