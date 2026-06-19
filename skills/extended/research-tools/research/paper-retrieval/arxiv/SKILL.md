---


name: arxiv
related_skills: ["knowledge-acquisition"]
description: >-
  arXiv论文搜索 — 按关键词/作者/类别/ID检索。支持Tor SOCKS代理访问。
version: 2.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    version: 2.0.0
    author: Synthos
    signature: 'query_params: dict -> paper_results: list[dict]'
    related_skills:
    - knowledge-acquisition


---




# arXiv

## IO_CONTRACT

- **input**: `query_params: dict` — 搜索参数（keyword/author/category/id/max_results/date_range）
- **output**: `paper_results: list[dict]` — 论文列表（title/authors/abstract/arxiv_id/pdf_url/date）
- **side_effects**: arXiv API HTTPS GET → 无状态变更
> 对应原则：P2（机械原子暴露输入输出规范）

## 快速命令

### 基本搜索

```bash
# 全文搜索（all: 标题+摘要+分类）
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=all:llm+AND+all:reasoning&max_results=10"

# 标题搜索（ti:）— 更精确
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=ti:chain+of+thought&max_results=5"

# 摘要搜索（abs:）
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=abs:reinforcement+learning&max_results=5"

# 作者搜索（au:）
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=au:Goodfellow+I&max_results=3"

# 分类搜索（cat:）
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=cat:cs.LG&max_results=10"

# ID 精确查询（id_list:）
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?id_list=2103.00020,2103.00021&max_results=5"
```

### 高级搜索

```bash
# 组合查询：标题包含A且摘要包含B
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=ti:llm+AND+abs:reasoning&max_results=10"

# 日期范围过滤
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=all:LLM+AND+submittedDate:[20240101+TO+20241231]&max_results=20"

# 排除某些词
curl -sL --socks5-hostname 127.0.0.1:9050 \
  "https://export.arxiv.org/api/query?search_query=all:reasoning+AND+NOT+all:survey&max_results=10"
```

## Tor SOCKS 代理

arXiv API 通过 Tor SOCKS5 访问：

```bash
# 关键: --socks5-hostname 使 DNS 解析在 Tor 内完成
# 关键: HTTPS（不是 HTTP）— arXiv 的 HTTP 会 301 到 HTTPS
# 关键: -L 跟随重定向（如必须）

curl -sL --socks5-hostname 127.0.0.1:9050 "https://export.arxiv.org/api/query?..."
```

## Python 方式（Tor SOCKS）

```python
import urllib.request
import urllib.parse

# Tor SOCKS5 代理（socks5-hostname: DNS解析在远端完成）
proxy = urllib.request.ProxyHandler({
    'https': 'socks5h://127.0.0.1:9050'
})
opener = urllib.request.build_opener(proxy)

query = "llm reasoning"
url = f"https://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&max_results=10"

req = urllib.request.Request(url)
with opener.open(req, timeout=30) as resp:
    xml_data = resp.read()
```

## XML 响应解析

```python
import xml.etree.ElementTree as ET

# 解析 arXiv Atom XML
root = ET.fromstring(xml_data)
ns = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

results = []
for entry in root.findall('atom:entry', ns):
    results.append({
        'title': entry.find('atom:title', ns).text.strip(),
        'arxiv_id': entry.find('atom:id', ns).text.split('/')[-1],
        'pdf_url': entry.find('.//atom:link[@rel="related"]', ns).get('href'),
        'abstract': entry.find('atom:summary', ns).text.strip(),
        'published': entry.find('atom:published', ns).text,
        'categories': [
            c.get('term') for c in entry.findall('atom:category', ns)
        ],
        'authors': [
            a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)
        ]
    })
```

## arXiv 查询语法速查

| 前缀 | 含义 | 示例 |
|:-----|:-----|:-----|
| `all:` | 标题+摘要+分类 | `all:llm` |
| `ti:` | 标题 | `ti:reinforcement` |
| `abs:` | 摘要 | `abs:transformer` |
| `au:` | 作者 | `au:Goodfellow` |
| `cat:` | 分类 | `cat:cs.AI` |
| `co:` | 评论 | `co:12+pages` |
| `jr:` | 期刊引用 | `jr:Nature` |
| `ext:` | 扩展信息 | `ext:10+figures` |
| `rl:` | 报告类别 | `rl:10` |

## 逻辑运算符

- `AND` — 逻辑与（默认，空格即 AND）
- `OR` — 逻辑或
- `NOT` — 逻辑非
- `()` — 括号分组
- `+` — 空格编码（URL 中）

## 已知陷阱

1. **必须用 HTTPS** — arXiv HTTP 端点 301 到 HTTPS，需要 `-L` 跟随
2. **Tor 代理 DNS** — 用 `--socks5-hostname`（不是 `--socks5`）确保 DNS 在远端解析
3. **XML 命名空间** — 必须处理 `atom:` 和 `arxiv:` 命名空间
4. **标题含换行符** — `<title>` 可能包含 `\n`，需要 `.strip()`
5. **摘要超长** — 摘要可能数百字，截断为需要的长度
6. **arxiv_id 格式** — 可能在 `<id>` 中或单独字段，需从 URL 提取
7. **PDF URL** — `<link rel="related">` 指向 PDF，不是 `<link rel="alternate">`（HTML）
8. **分类字段** — `term` 属性，如 `cs.LG`、`cs.CL`、`cs.AI`

## 参考文件

- `references/openalex-api.md` — 跨源对比参考

## 验证清单

- [ ] 至少搜索了 ≥2 个数据源
- [ ] 结果包含 title、abstract、arxiv_id、pdf_url
- [ ] XML 解析正确（命名空间处理）
- [ ] 所有结果有 provenance 字段
