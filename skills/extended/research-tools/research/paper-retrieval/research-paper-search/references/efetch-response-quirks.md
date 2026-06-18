# PubMed eFetch Response Quirks (v31 — 2026-06-06)

## Quirk 1: retmode=json RETURNS RAW INTEGER FOR SINGLE-ID (v31 — SYSTEMATIC)

**现象**: `efetch?id=X&retmode=json` 返回纯文本 `b'41400465\n'` — 一个原始整数，不是 JSON，不是 text/plain，不是 HTML。

**原因**: NCBI eUtils June 2026 API change. `retmode=json` 对单 ID 请求不再返回 JSON 文档。

**症状**: `json.loads()` 返回 `int`，不是 `dict`。所有后续 `.get("PubmedArticleSet", ...)` 调用失败：`AttributeError: 'int' object has no attribute 'get'`。

**关键特征**: 响应长度为 9 字节（数字+换行），例如 `b'41400465\n'`。这不是错误响应，是 NCBI 的预期输出。

**修复 — 永远不要用 retmode=json 做 eFetch**:
```python
# WRONG — returns raw int, json.loads gives int, not dict
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&retmode=json"
with urllib.request.urlopen(url) as r:
    d = json.loads(r.read())  # d is int, e.g. 41400465
    d.get("PubmedArticleSet")  # AttributeError: 'int' has no 'get'

# CORRECT — use retmode=xml
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&retmode=xml"
with urllib.request.urlopen(url) as r:
    xml = r.read().decode('utf-8')
    # Parse XML: <ArticleTitle>...</ArticleTitle>, <AbstractText>...</AbstractText>
    import re
    title = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml, re.DOTALL)
```

**eSearch vs eFetch**: `esearch` 的 `retmode=json` 仍然正常工作（返回 `esearchresult` 字典）。只 **eFetch** 的 `retmode=json` 被破坏。

**策略**: eFetch 统一使用 `retmode=xml`。XML 解析用 `re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml, re.DOTALL)`。

**v31 实例**: 所有单 ID eFetch 都返回 `b'41400465\n'`，长度 9 字节。多 ID 同样返回单个整数。

## Quirk 2: efetch may return text/plain (fallback for xml failures)

**现象**: `retmode=xml` 有时可能返回 text/plain 或 HTML（较少见，XML 通常稳定）。

**修复**: 如果 XML 解析失败 → 尝试 `retmode=text&rettype=abstract`。

**v27 实例**:
- `efetch?id=41855946,...&retmode=json` → 返回 text/plain（旧行为，v31 已系统性破坏）
- 重试 `retmode=xml` → 正常工作

## Quirk 2: idlist key name (lowercase)

`esearchresult` 返回的 ID 列表键名是 **`idlist`**（小写），不是 `IdList`。

```python
# WRONG — returns empty list
ids = d.get("esearchresult", {}).get("IdList", [])

# CORRECT
ids = d.get("esearchresult", {}).get("idlist", [])
```

## Quirk 3: esummary key is PMID, not under 'pubmed'

```python
# WRONG
pubmed_data = d.get("pubmed", {})

# CORRECT — key is the PMID string
for pmid, summary in d.get("result", {}).items():
    ...
```

## Quirk 4: efetch may need retmode=xml fallback

When `retmode=json` fails, try `retmode=xml` (more stable for structured data), then `retmode=text&rettype=abstract` (for human-readable text).

## Quirk 5: CDATA wrapping in XML

`<ArticleTitle>` and `<AbstractText>` may contain CDATA:
```xml
<ArticleTitle><![CDATA[The effect of X on Y]]></ArticleTitle>
```
Use `re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml, re.DOTALL)` to extract correctly.
