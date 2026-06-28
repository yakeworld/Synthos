# akne-query.sh 脚本参考

位置: `~/.hermes/scripts/akne-query.sh`

## 使用方法

```bash
~/.hermes/scripts/akne-query.sh <mode> "<query>"
```

## 6 种模式

### stats — 图谱统计

```bash
~/.hermes/scripts/akne-query.sh stats
```

输出:
```
=== AKNE Stats ===
Nodes: 1475
Edges: 5868
Node types: {'entity': 126, 'synthos_paper': 148, 'synthos_skill': 25, ...}
Edge types: {'source_co_occurrence': 1970, 'source_category': 1145, ...}
vectors.db records: 533
```

### simple — 实体解析 + 相关节点（最常用）

```bash
~/.hermes/scripts/akne-query.sh simple "<query>"
```

输出:
```
entity: <resolved_entity>    # 或 NONE
related_count: <N>
  neighbor: <node_name> | relation: <relation_chain> | type: <node_type>
  ...
```

流程:
1. `QueryEngine.resolve_entity(query)` — 4级相似度
2. Fallback: 遍历所有 node names 做子串匹配
3. 对找到 entity 做 `find_related(entity, depth=2)`
4. 输出前 30 个邻居

示例:
```bash
~/.hermes/scripts/akne-query.sh simple "BPPV"
# → entity: bppv, related_count: 5
```

### graph — BFS 遍历（depth=3 上限）

```bash
~/.hermes/scripts/akne-query.sh graph "<query>"
```

输出:
```
start_node: <entity>          # 或 NONE
total_bfs_nodes: <N>
  node: <node_name> | depth: <0-3> | type: <type>
  ...
```

流程:
1. `resolve_entity` + fallback 子串匹配
2. BFS 从实体开始，depth=0 到 depth=3
3. 按 depth 排序输出

示例:
```bash
~/.hermes/scripts/akne-query.sh graph "BPPV"
# → start_node: bppv, total_bfs_nodes: 6
#    bppv (d=0), 5 neighbors (d=1)
```

### concept — 概念节点搜索

```bash
~/.hermes/scripts/akne-query.sh concept "<query>"
```

输出:
```
concept_count: <N>
  name: <name> | type: <type> | relation: <relation_chain> | metadata: {...}
  ...
```

流程:
1. `resolve_entity` + fallback
2. 如果找到 entity，做 `find_related(entity, depth=2)`
3. 对每个邻居输出: name, type, relation_chain, metadata (前150字符)

示例:
```bash
~/.hermes/scripts/akne-query.sh concept "眩晕"
# → concept_count: 398 (mostly sources/科研)
```

### full — 全功能查询（最强大）

```bash
~/.hermes/scripts/akne-query.sh full "<query>"
```

输出:
```
=== Full AKNE Query ===
query: <query>
query_tokens: ['token1', 'token2', ...]
graph_entity: <entity>        # 或 enhanced_entity (分词匹配)
graph_neighbors: <N>
  <neighbor> | <relation> | type=<type>
enhanced_neighbors: <N>       # 仅当 enhanced_entity 且无 exact match 时显示
  <neighbor> | <relation> | type=<type>
query_confidence: <confidence>
  [<source_type>] <entity_name> score=<score>
    content: <content[:300]>
```

流程:
1. jieba 分词 → 过滤空 token
2. `resolve_entity` — 精确匹配
3. **Enhanced**: 多 token 子串匹配（边界/路径分隔符 ×2，子串 ×1，阈值≥2）
4. 对 exact match 做 graph traversal
5. 对 enhanced match（且无 exact）也做 traversal
6. QueryEngine query(top_k=5) 融合搜索

示例:
```bash
~/.hermes/scripts/akne-query.sh full "半规管"
# → query_tokens: ['半规管']
#    graph_entity: 后半规管新复位法
#    graph_neighbors: 4
#    query_confidence: 0.333
```

### bridge — 审计模式

```bash
~/.hermes/scripts/akne-query.sh bridge
```

输出:
```
=== Bridge Report ===
synthos_paper_total: 148
synthos_paper_with_edges: 116
synthos_paper_with_incoming: 148
synthos_skill_total: 25
synthos_skill_connected: 25
source_category_edges: 1145
category_paper_edges: 255
paper_concept_edges: 335
concept_paper_edges: 281
skill_concept_edges: 18
bridge_path_source_category_paper: YES
bridge_path_concept_paper: YES
orphans: 0
```

检查点:
- `synthos_paper_with_edges > 0` — 有出边的论文
- `synthos_skill_connected = synthos_skill_total` — 所有技能已连接
- `orphans = 0` — 无孤立论文
- `bridge_path_source_category_paper = YES` — source→category→paper 路径存在
- `bridge_path_concept_paper = YES` — 概念↔论文双向路径存在

## 输出格式约定

所有模式使用 `key: value` 格式，方便 Agent 解析:
- `entity:` / `start_node:` / `graph_entity:` — 实体名
- `related_count:` / `total_bfs_nodes:` — 数量
- `neighbor:` / `node:` / `concept:` — 节点详情
- `orphan:` — 孤立节点名
- `status:` / `YES` / `NO` — 布尔状态

## 环境要求

- 系统 Python 3.12（jieba + sentence-transformers 安装位置）
- AKNE 目录: `/media/yakeworld/sda2/academic_writer/yakeworld/akne`
- Graph: `/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/graph.json`
- vectors.db: `/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/vectors.db`
- jieba: 已在系统 Python 安装（10MB）
- 运行方式: `terminal` 工具（**不**在 execute_code 中运行）

## 性能特征

- stats: <100ms
- simple: 100-500ms（取决于邻居数）
- graph: 200-1000ms（取决于图连通性）
- concept: 500-2000ms（遍历所有节点）
- full: 1000-5000ms（jieba 初始化 + 全模式）
- bridge: 2000-5000ms（遍历所有论文和技能）

jieba 首次加载约 0.7s（从 /tmp/jieba.cache 加载），后续调用直接从缓存。
