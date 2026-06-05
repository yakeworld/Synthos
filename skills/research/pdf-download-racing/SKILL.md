---
name: pdf-download-racing
description: 并行竞速PDF下载引擎 — curl_cffi TLS指纹绕过 + Sci-Hub域轮换 + LibGen + MedData。依赖 tools/paper-manager/src/。
metadata:
  synthos:
    version: 1.7.0
    author: Synthos
    signature: 'doi: str -> pdf_path: str'
    related_skills:
    - paper-pipeline
    absorbed_skills:
    - meddata-access
---

# PDF Download Racing

## 三级竞速

```
Tier 1 (15s): Sci-Hub (11域轮换 + curl_cffi TLS绕过)
Tier 2 (20s): LibGen (5镜像)
Tier 3 (20s): MedData (中国医学平台, 需MEDDATA_USERNAME/PASSWORD)
  └─ 降级: paper-manager download_one.py
```

## 使用

```bash
# 直接下载
python3 /path/to/paper-manager/download_one.py <DOI> <output.pdf>

# 或通过paper-pipeline
# 在paper-pipeline的参考文献补充流程中自动触发
```

## Sci-Hub域列表

```python
SCI_HUB_DOMAINS = [
    "https://sci-hub.ru", "https://sci-hub.ee", "https://sci-hub.shop",
    "https://sci-hub.ren", "https://sci-hub.red", "https://sci-hub.al",
    "https://sci-hub.vg", "https://sci-hub.wf", "https://sci-hub.es",
    "https://sci-hub.box", "https://sci-hub.yt",
]
```

## MedData (中国医学数据平台)

需设置环境变量：
```bash
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="..."
```

下载原理：`fileName = doi.replace('/', '')`，viewtext API直接返PDF。
`pmid` 参数可任意，`doi` 参数传真实DOI。
详见 `references/meddata-api-details.md`。

## 智能 Cloudflare 绕过

`tools/paper-manager/src/smart_download.py` 提供两层下载策略：
1. 先用 `requests.get()` 尝试
2. 检测到 Cloudflare（403/503/429 + cf标识）→ 自动重试 `curl_cffi (impersonate="chrome")`

```python
import sys; sys.path.insert(0, 'tools/paper-manager/src')
from smart_download import smart_download
result = smart_download(url, timeout=30)
if result['ok'] and result['content'][:4] == b'%PDF':
    # 下载成功
```

## 参考文件

- `references/cloudflare-smart-download.md` — 智能Cloudflare绕过
- `references/meddata-access-absorbed.md` — MedData下载(旧)
- `references/meddata-api-details.md` — MedData API参数详解(2026-06-04实战)
- `references/paper-manager-fallback.md` — paper-manager降级

## 脚本

- `scripts/smart_download.py` — 自动Cloudflare检测+curl_cffi降级
- `scripts/batch_references_all.sh` — 批量下载脚本
- `scripts/download_and_upload.py` — 下载+上传管线
