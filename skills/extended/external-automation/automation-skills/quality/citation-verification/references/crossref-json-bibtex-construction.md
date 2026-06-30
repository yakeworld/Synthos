# Crossref JSON → BibTeX 手动构建指南

## 状态（2026-06-30确认）

Crossref REST API **已废弃** `format=bibtex` 参数。请求返回：
```json
{"status":"failed","message-type":"validation-failure","message":[{"type":"unknown-parameter","value":"format","message":"Parameter format specified but there is no such parameter available on any route"}]}
```

## 正确方法

### Step 1: 获取Crossref JSON
```
GET https://api.crossref.org/works/{DOI}?mailto=YOUR_EMAIL
```
（不指定`format`参数，默认返回JSON）

### Step 2: 提取元数据

响应结构：
```json
{
  "message": {
    "title": ["论文完整标题"],
    "author": [
      {"given": "First", "family": "Last"}
    ],
    "published-print": {"date-parts": [[2024]]},
    "published-online": {"date-parts": [[2024]]},
    "container-title": ["期刊名称"],
    "volume": "1",
    "issue": "1",
    "page": "100-110",
    "DOI": "10.xxxx/xxxxx"
  }
}
```

关键字段：
- `title`: **数组**，取`message.title[0]`
- `author`: **数组**，每项含`given`（名）和`family`（姓）
- `published-print`/`published-online`/`created`/`issued`: 取`date-parts[0][0]`
- `container-title`: **数组**，取第一项。可能是空数组`[]`需fallback
- `volume`, `issue`, `page`: 字符串
- `DOI`: 字符串

### Step 3: 手动构建BibTeX

```python
# 作者名拼接
author_str = ", ".join([f"{a.get('given','')} {a.get('family','')}".strip() for a in authors if a.get('given') and a.get('family')])
if not author_str: author_str = fallback_author_from_key

# 构建条目
@article{AUTHOR_YEAR_TITLE_WORD,
  title = {Title},
  author = {Authors},
  journal = {Journal}, volume={Vol}, number={Iss}, pages={Pages},
  year = {Year},
  doi = {DOI}
}
```

### 边界情况处理

1. **container-title为空数组** → fallback到`info['journal']`（从论文标题解析推测）
2. **作者数组为空** → fallback到paper.tex中的BibTeX key解析结果
3. **year为0或空** → fallback到BibTeX key中的年份（`Begoli2018Need` → 2018）
4. **DOI不存在** → 尝试Semantic Scholar搜索获取DOI
5. **Crossref无响应** → fallback到Semantic Scholar的`title/authors/year`直接构建

## 速率限制

- Crossref: 无明确RPM限制，但需加`time.sleep(0.3-0.5)`避免临时封禁
- Semantic Scholar: 无API key时429，有API key时约15秒后429
- 批量处理时每请求间隔0.3-0.5秒