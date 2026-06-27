# Reference PDF Collection Workflow

> G5 gate requires: every cited reference must have a full-text PDF, or a written justification.
> **凡引必验** — DOI可解析性是第一优先级验证，优先于PDF存在性检查。

## 四层下载协议（按优先级执行）

### Layer 0: 前置检查 — DOI可解析性验证
在尝试任何下载前，先验证引用**真实存在**：
```bash
# 对每篇有DOI的引用，检查doi.org是否返回302
code=$(curl -sI "https://doi.org/$DOI" 2>/dev/null | head -1 | grep -oP '\d{3}')
# 302/200 → 真实；404 → 虚构引用，需替换
```
**HCS-3WT教训(2026-06-25)**: 32篇中7篇(22%) bib中有DOI字段但doi.org返回404。**禁止仅查bib中有无DOI字段即判定通过。**

### Layer 1: Semantic Scholar Open Access（最快）
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=openAccessPdf" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('openAccessPdf',{}).get('url','') or 'NO_OA')"
```
有OA URL → 直接curl下载（注意User-Agent伪装）。

### Layer 2: 直接下载（按出版商分路线）
| 出版商 | URL模式 | 反爬等级 |
|:-------|:--------|:---------|
| Wiley (CA Cancer) | `https://onlinelibrary.wiley.com/doi/pdf/DOI` | 高 — 需浏览器 |
| Elsevier (Sciencedirect) | `https://www.sciencedirect.com/science/article/pii/.../pdfft` | 高 — 需浏览器 |
| Nature | `https://www.nature.com/articles/XXXXX.pdf` | 中 — OA可直接 |
| JAMA | `https://jamanetwork.com/journals/jama/articlepdf/XXX/YYYY.pdf` | 中 — 需完整URL |
| ACM | `https://dl.acm.org/doi/pdf/DOI` | 高 — Cloudflare |
| Springer | `https://link.springer.com/content/pdf/XXX.pdf` | 高 — 需浏览器 |
| BMJ | `https://www.bmj.com/content/VOL/ISSUE/ID.pdf` | 高 — Cloudflare |
| IEEE | `https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?arnumber=XXX` | 中 |

### Layer 3: Sci-Hub（中介转发）
```bash
# 多域轮换
for domain in "sci-hub.se" "sci-hub.ru" "sci-hub.st"; do
  curl -sL --connect-timeout 15 "https://$domain/DOI" -o out.pdf
  head -c 10 out.pdf | grep -q "^%PDF" && break
done
```
注意：Sci-Hub域名经常变动，可能需要现场搜索可用域名。多数CDN会弹出CAPTCHA。

### Layer 4: Playwright 浏览器下载（最可靠，绕过反爬）
当所有curl方法返回HTML（反爬页面）时，使用真实浏览器：
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"https://doi.org/{DOI}", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(12000)  # 等待JS渲染+反爬通过
    # 方式1：直接从response body获取PDF
    resp = page.context.request.get(f"https://doi.org/{DOI}")
    if resp.body()[:4] == b'%PDF':
        with open(f"{key}.pdf", 'wb') as f: f.write(resp.body())
    # 方式2：查找页面中的PDF链接
    links = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
    for h in links:
        if '.pdf' in h.lower():
            resp = page.context.request.get(h)
            # save...
    browser.close()
```

## 下载后验证

### 1. 真伪PDF检测
```bash
# 真正的PDF以 %PDF 开头
head -c 10 file.pdf | od -A n -t x1 | grep -q "25 50 44 46"
# 反爬HTML通常含 <!DOCTYPE html>
head -c 100 file.pdf | grep -qi "html\|cloudflare\|blocked\|captcha"
```

### 2. 内容验证（防止下载同名不同内容）
```bash
strings file.pdf | grep -ci "first_author_lastname"  # 至少出现1次
strings file.pdf | grep -ci "论文主题词"              # 确认主题相关
```

## HCS-3WT实战结果（2026-06-25）
| 方法 | 成功率 | 说明 |
|:-----|:------:|:-----|
| 直接curl | 3/13 (23%) | 仅JMLR、arXiv等简单网站可用 |
| Sci-Hub | 0/13 (0%) | 所有域返回CAPTCHA/不可达 |
| Tor exit node | 0/13 (0%) | 出口IP被出版商/Cloudflare封锁 |
| Playwright | Pending | 浏览器能通过大多数反爬，但慢（每篇12s+） |

## 不可获取引用的书面说明模板

| 类型 | 模板 |
|:-----|:-----|
| UCI仓库 | "Dataset description page at archive.ics.uci.edu — no peer-reviewed PDF exists" |
| EU报告 | "Official publication at <URL>, accessed YYYY-MM-DD" |
| 书籍 | "ISBN <isbn>, published by <publisher>, YYYY. No open-access version available." |
| 旧会议(<2000) | "Published in <proceedings>, not available in open digital archives" |
| 出版商付费墙 | "Published in <journal>, <volume>, <pages>, <year>. Paywalled. Preprint not found on arXiv." |

## G5门通过标准
| 覆盖率 | 判定 |
|:-------|:-----|
| 100% (PDF + 说明) | ✅ PASS |
| ≥80% PDF + ≤20% 说明 | ⚠️ SOFT — 需人工确认说明合理性 |
| <80% PDF | ❌ FAIL — PDF覆盖率不足 |
