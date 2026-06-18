# PubMed Title Extraction Patterns (v29 — 2026-06-07)

## 首选：esummary（最快，最简单）

**适用场景**: 只需要 PMID + 标题 + 快速 relevance 判断。不需要摘要全文。

```python
# Step 1: eSearch to get PMIDs
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query, safe='')}&retmax=5&retmode=json"
req = urllib.request.Request(url, headers={"Accept": "application/json"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())

ids = data.get("esearchresult", {}).get("idlist", [])

# Step 2: esummary — 直接返回 {"result": {"PMID1": {"title": "...", ...}, ...}}
if ids:
    ids_str = ",".join(ids)
    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
    req2 = urllib.request.Request(summary_url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        sdata = json.loads(resp2.read())
    
    titles = []
    for pmid, entry in sdata.get("result", {}).items():
        title = entry.get("title", "")
        titles.append(f"PMID{pmid}: {title}")
```

**优点**: 
- JSON 格式，单对象，无多 JSON 问题
- 不需要 XML 解析
- 单请求完成 count + title 提取
- 响应包含 title、source、pubdate、authors 等字段

**缺点**: 
- 只有标题，不含摘要全文
- `esummary` 的 `id` 字段是 PMID 字符串（key），非数字

**何时使用**: 快速 relevance 判断、白空间扫描、cron 轮换扫描。这是**最高频使用模式**。

## 需要摘要全文：XML 模式 + `<ArticleTitle>` 正则

### 正确提取方法

```python
import urllib.request, json, re

# Step 1: eSearch to get PMIDs
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query, safe='')}&retmax=5&retmode=json"
req = urllib.request.Request(url, headers={"Accept": "application/json"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())

ids = data.get("esearchresult", {}).get("idlist", [])

# Step 2: efetch in XML mode
if ids:
    efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml"
    req2 = urllib.request.Request(efetch_url, headers={"Accept": "application/xml"})
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        xml_text = resp2.read().decode('utf-8', errors='replace')
    
    # Step 3: Extract titles with regex
    title_pattern = re.findall(r'<ArticleTitle>(.*?)</ArticleTitle>', xml_text)
    titles = [t.strip() for t in title_pattern]
```

**结果**：干净列表，每篇论文一个标题。

### 失败模式 1：text/abstract 模式

```python
# ❌ 失败 — 返回空列表或不可解析格式
efetch_url = f"...&retmode=text&rettype=abstract"
# 响应格式: PMID- XXXX
#          TI  TITLE
#          AI  AUTHOR
#          ...
#          AB  Abstract
# 用 split('PMID-') 解析可能成功，但某些响应格式不同，导致空列表
```

**教训**：`retmode=text` 的响应格式可能不稳定。XML 模式始终返回 `<ArticleTitle>` 标签，格式稳定。

### 失败模式 2：不指定 Accept header

```python
# ❌ 可能 — 自动协商返回 text/plain 或 HTML
req = urllib.request.Request(efetch_url)
# 不带 Accept: application/xml，NCBI 可能返回 text/plain
```

**教训**：始终指定 `Accept: application/xml` 用于 XML 模式请求。

### 处理 CDATA 包裹

```xml
<ArticleTitle><![CDATA[The effect of X on Y]]></ArticleTitle>
```

正则 `re.findall(r'<ArticleTitle>(.*?)</ArticleTitle>', xml_text)` 会正确提取 `The effect of X on Y`（CDATA 包裹内容会被正确包含）。

### 处理空标题

某些 PMID 可能不存在或无标题（如已删除论文）。解析后应检查空字符串：

```python
titles = [t.strip() for t in title_pattern if t.strip()]  # 过滤空标题
```