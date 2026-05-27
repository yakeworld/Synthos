---
name: pdf-download-racing
description: "并行竞速PDF下载引擎 — curl_cffi TLS指纹绕过 + Sci-Hub域轮换 + LibGen + 域健康探测。从scansci-pdf吸收的技术：Parallel racing、Domain probing、curl_cffi bypass。依赖 src/downloader/ 和 src/sources/ 下的代码。"
version: 1.0.0
author: Synthos (absorbed from scansci-pdf)
tags: [download, pdf, sci-hub, libgen, racing, curl-cffi]
---

# PDF Download Racing Engine

> 多源并行，首个成功即止。域健康探测，失败自动冷却。

## 架构

```
搜索论文DOI
  ↓
① OpenAccess / arXiv ───── aiohttp → 失败 → curl_cffi (TLS指纹+brotli+403绕过)
  ↓ 无
② Parallel Racing Engine
   ├── Tier 1 (15s): Sci-Hub (curl_cffi + 域轮换)
   │   ├── 域健康探测 (SQLite, 4h TTL)
   │   ├── curl_cffi impersonate chrome120
   │   └── 冷却机制 (fail_streak≥3跳过)
   └── Tier 2 (20s): LibGen (5镜像轮换)
  ↓ 都不行
③ 记录DOI到缺失清单
```

## 依赖

| 包 | 用途 | 安装 |
|:---|:-----|:------|
| `curl_cffi>=0.15` | TLS指纹模拟，绕过Cloudflare/DDoS-Guard | `pip install curl_cffi` |
| `beautifulsoup4>=4.12` | HTML解析提取PDF URL | `pip install beautifulsoup4` |
| `requests>=2.31` | 最后保底下载 | 已内置 |

## 代码位置

```
outputs/code/src/
├── downloader/
│   ├── base_downloader.py    ← curl_cffi fallback (brotli/403修复)
│   └── pdf_downloader.py     ← _download_racing() 入口
├── racing_engine.py          ← 并行竞速引擎 (ThreadPoolExecutor)
├── domain_db.py              ← 域健康SQLite数据库
└── sources/
    ├── scihub_racing.py       ← Sci-Hub: curl_cffi + 域轮换 + 探测
    └── libgen.py              ← LibGen: 5镜像轮换
```

## 工作流

### 单篇下载

```python
# 不通过搜索，直接给DOI下载
from src.downloader.pdf_downloader import PDFDownloader
from src.core.config import Config

dl = PDFDownloader(Config())
await dl.create_session()
success = await dl._download_racing("10.1145/3065386", "/path/to/save.pdf")
await dl.close_session()
# success = True/False
```

### 搜索+下载（完整流程）

```bash
cd /media/yakeworld/sda2/Synthos/outputs/code
python3 main.py search "论文标题" --limit 3
# → research/results.csv + research/pdfs/*.pdf + research/references.bib
```

### 域健康维护（自动）

域健康探测每4小时自动执行一次，11个Sci-Hub域并行探测。状态存到 `.domain_cache/domain_stats.db`。

```bash
# 手动触发探测
python3 -c "from src.domain_db import set_probe_timestamp; set_probe_timestamp()"
# 查看域状态
python3 -c "
from src.domain_db import load_stats
for d, s in load_stats().items():
    rate = s['success']/max(s['success']+s['fail'],1)*100
    print(f'{d:30s} rate={rate:.0f}% latency={s[\"avg_latency\"]:.0f}ms fail_streak={s[\"fail_streak\"]}')
"
```

## 关键原理

### curl_cffi TLS 指纹模拟

```python
from curl_cffi import requests as cffi
# impersonate="chrome120" 模拟Chrome 120的TLS握手
# 可绕过Cloudflare / DDoS-Guard / Cloudflare Challenge
r = cffi.get(url, impersonate="chrome120", timeout=120, allow_redirects=True)
```

### 并行竞速

```python
with ThreadPoolExecutor(max_workers=N) as pool:
    futures = {pool.submit(try_source, doi, path): label for fn, label in sources}
    for future in as_completed(futures, timeout=timeout):
        if future.result().get('success'):
            cancel_others(futures)  # 首个成功即停
            return result
```

### 域健康数据库

```sql
CREATE TABLE domain_stats (
    domain TEXT PRIMARY KEY,
    success INTEGER, fail INTEGER, fail_streak INTEGER,
    avg_latency REAL, reachable INTEGER, updated_at REAL
);
```

## Sci-Hub 域列表 (2026-05-27 可用11个)

```
https://sci-hub.ru  https://sci-hub.ee  https://sci-hub.shop
https://sci-hub.ren https://sci-hub.red https://sci-hub.al
https://sci-hub.vg  https://sci-hub.wf  https://sci-hub.es
https://sci-hub.box https://sci-hub.yt
```

## LibGen 镜像

```
https://libgen.li  https://libgen.bz  https://libgen.gs
https://libgen.rs  https://libgen.st
```

## 陷阱

1. **Sci-Hub 2023年后论文覆盖不全** — 近年来新论文可能不在Sci-Hub。2025年论文成功率低。
2. **curl_cffi 超时** — 大PDF (>5MB) 可能需要120s+。代码默认超时120s。
3. **aiohttp 不支持 brotli** — `base_downloader.py` 的 fallback 已用 curl_cffi 修复。
4. **域冷却** — 连续3次失败的域自动跳过，24h后重置。
5. **PDF验证** — 下载后检查 `%PDF-` 头部 + `%%EOF` 尾部 + 最小1000字节。
