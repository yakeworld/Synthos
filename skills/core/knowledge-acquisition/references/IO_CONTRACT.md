# IO_CONTRACT.md — knowledge-acquisition

> 对应原则：P2（机械原子暴露输入输出规范）
> 权威来源：`docs/atom-io-schemas.md` §1

## input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `query` | string | ● | 搜索查询（与 search_query 等效） |
| `search_query` | string | | query 的别名 |
| `sources` | list[string] | | 默认 `["semantic_scholar", "pubmed", "crossref", "arxiv"]` |
| `max_results` | integer | | 默认 10 |
| `domain` | string | | 领域过滤 |

## output_schema

### raw_papers: list[Paper]

| 字段 | 类型 | 必需 |
|------|------|:--:|
| `title` | string | ● |
| `doi` | string | |
| `abstract` | string | |
| `year` | integer | |
| `authors` | list[string] | ● |
| `source` | string | ● |
| `open_access_url` | string | | 开放获取URL（来自S2/arXiv/Unpaywall） |
| `arxiv_id` | string | | arXiv ID |
| `pmid` | string | | PubMed ID |
| `pdf_path` | string | | 下载后的本地PDF路径（如成功） |
| `pdf_status` | string | | `"open_access"`\|`"arxiv"`\|`"pmc"`\|`"unpaywall_oa"`\|`"doi_redirect"`\|`"scihub"`\|`"cached"`\|`"unavailable"` |
| `pdf_note` | string | | 下载失败时的原因 |

### metadata

| 字段 | 类型 | 必需 |
|------|------|:--:|
| `total_found` | integer | ● |
| `sources_used` | list[string] | ● |
| `search_query` | string | ● |
| `max_results_requested` | integer | ● |
| `pdfs_downloaded` | integer | ● |
| `pdf_directory` | string | ● |
| `timestamp` | string | ● |

## 数据源 fallback 链

1. Semantic Scholar (API key required)
2. PubMed (E-utilities, no key)
3. Crossref (REST API, no key)
4. arXiv (OAI-PMH, no key)

## 去重规则

- DOI 精确匹配（主键）
- 标题相似度 ≥ 0.90（备选）
