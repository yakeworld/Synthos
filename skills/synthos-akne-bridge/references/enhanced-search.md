# AKNE语义搜索增强

AKNE增强语义搜索使用TF-IDF + jieba分词 + sklearn实现，作为akne-query.sh simple/full模式的补充。

## 架构

```
akne-enhanced-search.py
├── Enhanced entity resolution (5级评分)
├── Fuzzy node search (子串匹配)
├── TF-IDF text search (sklearn)
├── Graph traversal (KnowledgeGraph)
└── Combined results (graph + text fusion)
```

## 使用方式

```bash
# Simple — 快速查询（~1s）
python3 akne-enhanced-search.py "BPPV" --mode simple

# Full — 增强查询（含TF-IDF，~30s）
python3 akne-enhanced-search.py "半规管" --mode full --top-k 5
```

## 关键实现

- 增强实体解析：精确→子串→Token Jaccard→模糊，阈值≥2.0
- TF-IDF: jieba分词 + sklearn TfidfVectorizer，cosine similarity
- 与graph结果融合：graph boost + text-only 降权
- jieba安装在系统Python 3.12（不在venv）
- TF-IDF索引构建耗时~30s（1145文件）
- 向量搜索仍不覆盖全部源文件（500/1145），TF-IDF是补充方案

## 文件位置

`~/.hermes/scripts/akne-enhanced-search.py`