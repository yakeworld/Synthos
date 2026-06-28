## API 调用参考（2026-06-13 新增）

### 核心路径

```
graph.json: /media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/graph.json
vectors.db: /media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/vectors.db
akne 引擎:  /media/yakeworld/sda2/academic_writer/yakeworld/akne/
```

### Python 导入模式

```python
import sys
sys.path.insert(0, '/media/yakeworld/sda2/academic_writer/yakeworld')
from akne.graph.graph_index import KnowledgeGraph
from akne.reason.query_engine import QueryEngine

kg = KnowledgeGraph('/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/graph.json')
qe = QueryEngine(graph_index=kg)

# KG 直接方法（返回 NetworkX MultiDiGraph 数据结构）
len(kg.graph.nodes())        # 总节点数
len(kg.graph.edges())        # 总边数
kg._nodes_by_type             # {type: set of node_names}
kg._edges_by_type             # {relation_type: list of (source, target) tuples}
kg.find_related(entity, depth=2)  # [(neighbor, relation_chain, metadata)]
kg.bfs_search(entity, depth=2)    # set of reachable node names
kg.traverse(start, max_depth=2)   # similar to bfs_search

# QueryEngine 方法（高级查询）
qe.resolve_entity("BPPV")         # "bppv" (精确/模糊匹配)
qe.get_related_entities("bppv", max_depth=2)  # [(name, distance)]
qe.query("BPPV diagnosis", top_k=5)  # QueryResult 对象
qe.query_graph(start_entity, max_depth=2)  # graph query
qe.query_vector(text, top_k=10)    # vector search (requires vectors.db config)
qe.query_wiki(entity_name)         # wiki content query
```

### 节点类型与数量

| 类型 | 数量 | 说明 |
|------|------|------|
| source | 1145 | Markdown源文件 |
| synthos_paper | 148 | Synthos论文 |
| entity | 126 | 疾病/人物/工具 |
| synthos_skill | 25 | Synthos技能 |
| source_category | 24 | 源文件分类Hub |
| synthos_misc | 7 | 子目录/非论文 |

### 环境陷阱

**execute_code 使用 venv python3.11，但 pip 安装到系统 python3.12**。AKNE 依赖 networkx，通常安装在系统用户的 site-packages（`~/.local/lib/python3.12/site-packages/`），在 venv 中无法访问。

**解决**: 始终使用 `terminal` 直接运行 Python 脚本（`python3 -c "..."`），不要通过 `execute_code` 调用 AKNE 代码。

### 语义搜索限制

- 词袋(Jaccard)匹配，对多词查询如 "eye tracking methodology" 无结果
- 向量数据库存在但需配置 `vector_store` 参数才能生效
- `resolve_entity` 成功率有限：BPPV→bppv✓, Synthos→sources/synthos✓, 温州✓, 杨晓凯→None✗