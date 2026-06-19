# Tor + OpenAlex 搜索场景记录（v1 — 2026-06-19）

## 场景

通过 Tor 访问 OpenAlex 或 arXiv 搜索论文。需要处理代理、URL 编码、DNS 等问题。

## Tor 搜索方法

### 方法 1: arXiv via Tor（推荐，稳定）
```bash
curl -sL --socks5-hostname 127.0.0.1:9050 "https://export.arxiv.org/api/query?search_query=all:3D+eye+tracking"
```
- 稳定可靠，TLS 指纹自然
- 适合 3D 眼动等预印本丰富的领域

### 方法 2: OpenAlex via Tor
```python
# 通过 proxy.py 访问（curl 方式会被 strip 掉 headers）
# 必须使用 urllib 而非 curl
from urllib.parse import quote_plus
url = f"https://api.openalex.org/works?search={query}&per_page=10"
```
- ⚠️ 通过 `proxy.py`（Tor 代理）时 curl 会被 strip 掉 headers
- ⚠️ Python 3.12 urllib 要求 `quote_plus(query, safe=' ')`
- ⚠️ 某些查询串太长会导致 400 错误，需拆分

### 方法 3: PubMed via Tor
```bash
curl -s --socks5-hostname 127.0.0.1:9050 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders&retmax=10&retmode=json"
```

## 已知问题

1. **DNS 间歇性超时** — Tor 节点偶尔无法解析域名，重试即可
2. **OpenAlex 400 错误** — 某些关键词组合导致 400，需简化查询
3. **arXiv AND 搜索** — arXiv 的 AND 语法可能把关键词拆成 OR，需用精确短语搜索

## 成功用例

2026-06-19 通过 Tor + arXiv 搜索到 3D 眼动/虹膜分割相关论文 20+ 篇，成功补充到 3d-eyeball-iris-segmentation 论文的参考文献。
