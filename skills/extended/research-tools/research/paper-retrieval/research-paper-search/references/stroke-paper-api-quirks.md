# Stroke Paper Research API Quirks — 2026-06-06

> 本文件记录 stroke 论文管线执行中发现的 API 访问模式。

## 已验证可用的 API

### PubMed (eSearch)
```python
# 格式: term= 使用 + 编码的空格
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=stroke+prediction+machine+learning&retmax=20&retmode=json"
# 返回: {"esearchresult": {"idlist": [...]}}  ← 注意 idlist 小写，不是 IdList
```

### Crossref
```python
# 格式: query= 参数，不是 search=
url = "https://api.crossref.org/works?query=stroke+prediction&select=title,author,DOI,published-print,journal-container&rows=20&sort=citedness&order=desc"
# 返回: {"message": {"items": [...]}}
# 关键: 使用 query= 而非 search=，search= 返回 400 Bad Request
```

### OpenAlex
```python
# 格式: search= 但 Python urllib 拒绝带空格的 URL
# 正确方式:
from urllib.parse import quote_plus
url = f"https://api.openalex.org/works?search={quote_plus('stroke prediction', safe=' ')}&per_page=20"
# 但 quote_plus 仍可能返回 400 — 需要测试当前环境是否支持
# 备选: 先用 bare space 测试（Python 3.12 urllib 可能拒绝）
```

## API 失败模式

| API | 失败请求 | 原因 |
|-----|----------|------|
| Crossref | search=... | 应使用 query= |
| OpenAlex | search=stroke prediction (bare space) | Python urllib 拒绝空格 |
| OpenAlex | search=%20stroke+prediction | quote_plus 可能仍失败 |

## 建议

1. PubMed: 始终用 term= + + 编码空格
2. Crossref: 始终用 query= + + 编码空格
3. OpenAlex: 先用 bare space 测试，如失败则尝试 quote_plus
4. 所有API调用后检查返回状态码，不做假设
