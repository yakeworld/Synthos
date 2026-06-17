# QueryEngine 架构

QueryEngine (akne/reason/query_engine.py) 是 AKNE 的统一查询入口。

## API

```python
from akne.reason.query_engine import QueryEngine
from akne.graph.graph_index import KnowledgeGraph

kg = KnowledgeGraph('/path/to/graph.json')
qe = QueryEngine(graph_index=kg)

# Entity resolution — 4级相似度
entity = qe.resolve_entity("BPPV")
# → "bppv" (精确) 或 "sources/BPPV/..." (子串)

# Full query — graph + vector + wiki 多源融合
result = qe.query("眩晕 诊断", top_k=5)
# → QueryResult{results: [SearchResult], confidence: 0.667, summary: ""}

# Graph traversal
related = qe.get_related_entities(entity, max_depth=2)
# → [(neighbor, relation_chain), ...]

# Graph search (alias for get_related_entities)
result = qe.query_graph(entity, max_depth=2)

# Vector search (requires vectors.db + embedding model)
result = qe.query_vector("text", top_k=5)

# Wiki search
result = qe.query_wiki("entity_name", read_full=True)
```

## 架构组件

```
QueryEngine
├── _graph_search()     → resolve_entity + traverse() + substring fallback
├── _vector_search()    → SentenceTransformer embeddings (cosine similarity)
├── _wiki_search()      → Obsidian-style wiki node lookup
├── query()             → Merges graph + vector + wiki results, dedup
├── _extract_cross_refs() → Finds common neighbors between vec/graph results
├── _summarize_wiki_header() → Extracts H1 header for content summary
├── _track_query()       → Logs query to session history
├── _cache_get/set()     → LRU cache by query hash
└── clear_cache()
```

## 关键约束

### 1. resolve_entity 只在 QueryEngine

```python
# ❌ 错误
kg.resolve_entity("BPPV")  # AttributeError: 'KnowledgeGraph' object has no attribute 'resolve_entity'

# ✅ 正确
qe = QueryEngine(graph_index=kg)
entity = qe.resolve_entity("BPPV")
```

### 2. 4级 resolve_entity 流程

1. 精确匹配: `self._entity_to_text.get(text.lower(), None)`
2. 子串匹配: 遍历所有 node names，`text.lower() in name.lower()`
3. Token Jaccard: jieba 分词 → token set → Jaccard similarity
4. 模糊匹配: SequenceMatcher ratio > 0.5

### 3. 多词英文查询限制

`_graph_search` 依赖 `resolve_entity` + `traverse()`，对多词英文（"eye tracking methodology"）无效。QueryEngine 的词袋匹配只对已存在的 entity 有效。

### 4. _graph_search 的 substring fallback

当 resolve_entity 找到节点但 traverse 返回 0（leaf node），会回退到节点名子串搜索：
- 节点名以查询开头 → score 0.8
- 节点名包含查询（非开头）→ score 0.6  
- 路径分隔符后匹配 → score 0.5

### 5. 缓存机制

QueryEngine 内部有 `_cache: dict[str, QueryResult]`，用 `query` 文本的 SHA256 hash 作为 key。`clear_cache()` 可清空。

## SearchResult 格式

```python
@dataclass
class SearchResult:
    source_type: str    # 'vector' | 'graph' | 'wiki' | 'source'
    entity_name: str
    score: float        # 0.0-1.0, cosine similarity or graph depth score
    content: str        # excerpt or full text
    source_path: str    # file path or wiki node name
    metadata: dict
```

## 典型查询流程

```python
result = qe.query("BPPV 诊断")
for r in result.results:
    print(f"[{r.source_type}] {r.entity_name} (score={r.score:.3f})")
    print(f"  {r.content[:200]}")
```

## 与 KnowledgeGraph 的关系

```
KnowledgeGraph (akne/graph/graph_index.py)
├── graph: nx.MultiDiGraph()        # NetworkX 图
├── _nodes_by_type: dict            # 按类型索引
├── _edges_by_type: dict            # 按关系类型索引
├── resolve_entity()                # ❌ 不在 KG，在 QueryEngine
├── find_related()                  # BFS neighbor search
├── find_common_neighbors()         # Shared neighbors between two entities
├── find_central_entities()         # PageRank centrality
├── cluster_entities()              # Community detection
├── traverse()                      # Graph traversal with path tracking
├── add_entity/add_concept/link()   # Graph modification
├── save()/to_dict()                # Serialization
└── export_markdown()               # Markdown export

QueryEngine (akne/reason/query_engine.py)
├── graph_index: KnowledgeGraph     # wraps KG
├── vector_store: VectorStore       # optional, for semantic search
├── wiki_root: Path                 # optional, for wiki search
├── _cache: dict                    # query result cache
└── resolve_entity()                # 4级实体解析
└── query()                         # 多源融合查询
```

## 常见查询结果示例

### BPPV (entity)
```
entity: bppv
neighbors (5):
  - sources/BPPV/BPPV诊疗规范 (references)
  - sources/BPPV/Dix-Hallpike试验眼震分析 (references)
  - sources/BPPV/后半规管短臂侧结石症和长臂侧结石症的诊断和治疗 (references)
  - wiki/concepts/前庭解剖 (references)
  - wiki/entities/张雷 (references)
```

### 半规管 (enhanced multi-token)
```
query: 半规管
query_tokens: ['半规管']
graph_entity: 后半规管新复位法
enhanced_entity: None (exact match found)
graph_neighbors (4):
  - sources/BPPV/后半规管BPPV新复位法设计-虚拟仿真研究
  - wiki/entities/bppv
  - wiki/concepts/耳石复位手法
  - wiki/concepts/虚拟仿真研究
query_confidence: 0.333
```

### 眩晕 (398 related sources)
```
entity: .knowledge/sources/科研/眩晕方向.md
related_count: 398
top neighbors:
  - sources/科研 (source_category)
  - .knowledge/sources/科研/---科研思路集中营.md (source_category → source_category_membership)
  - ... 396 more source nodes
```
