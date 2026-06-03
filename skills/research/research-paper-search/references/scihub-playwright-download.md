# Sci-Hub Playwright 浏览器自动化下载

> DDoS-Guard 拦截了所有 Sci-Hub 镜像的 HTTP 请求（返回 HTML 挑战页而非 PDF）。  
> Playwright 提供真实浏览器环境，自动执行 JS 挑战，绕过拦截。

## 原理

```
requests/session → DDoS-Guard (blocked) → HTML challenge page
                         ↓
Playwright Chromium headless → 加载页面 → JS challenge 自动通过 → cookies 设置
                         ↓
提取 PDF iframe URL → 带 cookies 重新 requests 下载
```

## 依赖

Playwright + Chromium 引擎（已安装，NotebookLM CLI 浏览器 cookies 登录依赖它）：
```bash
pip install playwright
playwright install chromium   # 如果未安装
```

## 核心代码

路径：`/media/yakeworld/sda2/Synthos/outputs/code/src/downloader/scihub_download.py`

```python
from playwright.async_api import async_playwright

async def download_via_scihub(doi, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0...")
        page = await context.new_page()
        
        for mirror in SCI_HUB_MIRRORS:  # 11个镜像依次尝试
            await page.goto(f"{mirror}{doi}", wait_until="networkidle", timeout=30000)
            
            # 提取PDF URL: iframe/embed/下载链接/script内容
            pdf_url = await page.evaluate("""...""")
            
            if pdf_url:
                cookies = {c['name']: c['value'] for c in await context.cookies()}
                import requests
                r = requests.get(pdf_url, cookies=cookies, timeout=60)
                if r.content[:4] == b'%PDF':
                    with open(output_path, 'wb') as f:
                        f.write(r.content)
                    return True
        return False
```

## 集成到 PDFDownloader

在 `pdf_downloader.py` 中，`_try_sci_hub_download` 方法：

1. 先用 requests 快速检测第一个镜像的 Content-Type
2. 如果是 `text/html`（DDoS-Guard 特征），立即调用 `_try_scihub_playwright(doi, save_path)`
3. `_try_scihub_playwright` 以子进程方式运行 `scihub_download.py`

## PDF URL 提取策略

Sci-Hub 页面可能有多种方式提供 PDF：

| 方法 | 选择器 | 优先级 |
|:-----|:--------|:------:|
| iframe#pdf | `document.querySelector('iframe#pdf').src` | 最高 |
| embed[type="application/pdf"] | `document.querySelector('embed').src` | 次高 |
| 下载链接 | `a[href*="sci-hub"].href` 或含"Download"文本 | 备用 |
| script 内容 | 从 `textContent` 中 regex 匹配 `.pdf` URL | 末选 |

## 已知局限

1. **论文不在 Sci-Hub 数据库**：返回 "статья отсутствует в базе"（article not in database）。无法绕过。
2. **每篇 ~15 秒**：Playwright 启动（~3s）+ 页面加载（~5s）+ JS 执行 + PDF 下载
3. **新论文（2025+）可能未收录**：Sci-Hub 主要收录 2023 年及之前的论文

## 可用镜像（2026-05-27）

```
ee, shop, ren, ru, red, al, vg, wf, es, box, yt
```
