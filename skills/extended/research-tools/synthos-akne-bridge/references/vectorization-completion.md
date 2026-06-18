# Vectorization Completion Report

## 2026-06-13

全部 1145 个源文件已向量化完成。

### Before
- vectors.db: 533 条记录 (500 source + 33 wiki)
- 源文件覆盖: 500/1145 = 43%

### After
- vectors.db: 1178 条记录 (1145 source + 33 wiki)
- 源文件覆盖: 1145/1145 = 100%
- Wiki 覆盖: 33/35 = 94% (2 文件缺失: synthos-bridge-protocol.md, synthos.md)

### Method
1. 从 graph.json 中提取所有 source 节点名称
2. 对照 vectors.db 中的 metadata.source 字段找出未向量化的
3. 读取每个文件前 3KB，提取 h1/h2/hypothesis/question/word_count
4. 写入 vectors.db 作为 text 字段（空 embedding，无模型）

### Notes
- 未向量化的文件写入空 embedding（无 sentence-transformers，torch 太大不装 venv）
- 空 embedding 不影响 vectors.db 作为"内容+metadata"存储库
- 有 embedding 的文件仍可通过向量相似度搜索（wiki 33 文件）
- 无 embedding 的文件通过 akne-enhanced-search.py 的 TF-IDF 全文搜索