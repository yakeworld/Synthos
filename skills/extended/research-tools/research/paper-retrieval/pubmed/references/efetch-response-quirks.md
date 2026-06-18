# PubMed eFetch Response Quirks (v27 — 2026-06-06)

## Quirk 1: efetch may return text/plain instead of JSON

**现象**: `retmode=json` 有时会返回纯文本或 HTML 响应而非有效 JSON。

**原因**: NCBI eUtils 可能因速率限制、请求格式问题或内部错误返回非 JSON 格式。

**症状**: `json.decoder.JSONDecodeError` 或 `Expecting value: line 1 column 1`。

**修复**:
```python
import urllib.request

content = urllib.request.urlopen(url).read().decode()
if content.startswith('{'):
    data = json.loads(content)
elif content.startswith('<'):
    # XML format — parse with re or xml.etree
    pass
else:
    # text/plain — parse PubMed text format
    # Format: PMID- \nTitle\n  Abstract: ...
    pass
```

**v27 实例**:
- `efetch?id=41855946,41508981,41504426,41430424,41254940&retmode=json` → 返回 `"J Psychopharmacol. 2001 Jun;15(2):96-104..."` (text/plain)
- 重试 `retmode=xml` → 正常工作
- 重试 `retmode=text&rettype=abstract` → 正常工作

**策略**: 如果 JSON 解析失败 → 尝试 xml → 尝试 text → 使用 efetch 重试 2 次。

## Quirk 2: idlist key name (lowercase)

`esearchresult` 返回的 ID 列表键名是 **`idlist`**（小写），不是 `IdList`（首字母大写）。

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

## Quirk 4: esearch count vs returned IDs

`esearch` 的 `count` 字段显示总匹配数，但 `idlist` 只返回 `retmax` 条 ID。如果 count > retmax，需要分页获取所有 ID。

**v27 实例**:
- `saccade adaptation` → count=1425, retmax=1 → idlist 只有 1 条（但 count 正确）
- `cochlear amplifier mathematical model` → count=5, retmax=5 → idlist 有 5 条
- **注意**: count 是准确的，但 idlist 长度 = min(count, retmax)

## Quirk 5: efetch returns multiple PMIDs but parsing fails silently

当 efetch 返回多个 PMID 的 XML 时，如果某些 PMID 不存在，`<ArticleTitle>` 可能为空。解析时不应报错，而应跳过空标题。

## Quirk 6: XML CDATA wrapping

`<ArticleTitle>` 和 `<AbstractText>` 可能包含 CDATA 包裹的内容：
```xml
<ArticleTitle><![CDATA[The effect of X on Y]]></ArticleTitle>
<AbstractText><![CDATA[This study examined...]]></AbstractText>
```
用 `re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml, re.DOTALL)` 可以正确提取。
