# EVIDENCE_SCHEMA.md — knowledge-acquisition

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `doi` | 每篇检索到的论文生成一个节点，引用论文DOI |
| `url` | 论文无DOI时的降级方案，引用 open_access_url |
| `arxiv_id` | arXiv论文使用 arxiv ID |
| `empty_result` | 搜索返回空结果时的标记 |
| `api_source` | 每个API查询源产生一个节点，记录查询参数 |

## 节点结构

```json
{
  "source_type": "doi",
  "source_ref": "<DOI>",
  "api_source": "semantic_scholar|pubmed|openalex|crossref",
  "fetch_time": "<ISO>",
  "note": "Retrieved from API search"
}
```

## 传递规则

本原子的 evidence_chain 是所有后续原子的起始点。每个 KnowledgeItem 的 source 字段指向具体的 API 源和论文 DOI/URL。下游原子（knowledge-extraction 等）在此基础上追加新节点。
