# Query Enhancement Recipes

## TF-IDF 配置

### 基础配置（1145 源文件，40916 词汇）

```python
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba

# 对每个文件：jieba 分词 + 空格连接
def tokenize(text):
    return ' '.join(t for t in jieba.cut(text) if len(t.strip()) > 0)

vectorizer = TfidfVectorizer(
    tokenizer=lambda x: x.split(),  # 已分词
    token_pattern=None,
    max_features=5000,
    min_df=1,
    max_df=0.95,
    sublinear_tf=True,  # log(1+tf)
)

# 索引所有源文件（~1.5MB 文本，~30s 构建）
docs = [read_file(path) for path in all_source_files]
tfidf_matrix = vectorizer.fit_transform([tokenize(d) for d in docs])
```

### 查询编码

```python
query_tokens = ' '.join(t for t in jieba.cut(query) if len(t.strip()) > 0)
query_vector = vectorizer.transform([query_tokens])
from sklearn.metrics.pairwise import cosine_similarity
scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
```

### 参数调优

| 参数 | 值 | 效果 |
|------|-----|------|
| `max_features` | 5000 | 控制词汇表大小，避免过拟合 |
| `min_df` | 1 | 至少出现 1 次（全量索引） |
| `max_df` | 0.95 | 过滤 95% 以上文档出现的词（常见中文词） |
| `sublinear_tf` | True | 对数缩放 TF，减少高频词权重 |

## Jieba 分词调优

### 基本用法

```python
import jieba
tokens = list(jieba.cut("眩晕诊断治疗"))
# ['眩晕', '诊断', '治疗']
```

### 多词查询过滤

```python
# 过滤空格 token（jieba 返回中包含 " "）
tokens = [t for t in jieba.cut(query) if t.strip() and len(t.strip()) > 0]
if not tokens:
    tokens = [t for t in query.split() if t.strip()]  # 英文回退
```

### 分词缓存

jieba 首次加载需要 ~0.7s（从 /tmp/jieba.cache 加载）。后续调用几乎瞬间完成。
- 缓存位置：`/tmp/jieba.cache`
- 首次加载：0.7-0.8s
- 后续：~10ms

## 多词匹配策略

### 5 级评分

```python
def score_node(node_name, query_tokens):
    score = 0
    node_lower = node_name.lower()

    for tok in query_tokens:
        tok_lower = tok.lower()
        if len(tok_lower) <= 2:
            continue  # 跳过短词

        if tok_lower == node_lower:
            score += 5  # 1. 精确匹配
        elif node_lower.startswith(tok_lower):
            score += 3  # 2. 前缀匹配
        elif '/' + tok_lower in node_lower:
            score += 2  # 3. 路径分段匹配
        elif tok_lower in node_lower:
            score += 1  # 4. 子串匹配

    return score
```

### 阈值过滤

- 阈值 ≥2：返回结果（确保至少一个有意义的 token 匹配）
- 阈值 ≥5：最高优先级（精确匹配）

### 反向匹配

检查节点名是否出现在查询中（例如查询"三维眼动"，节点名"三维眼球建模"也应匹配）：

```python
for node_part in node_name.split('/'):
    if node_part.lower() in query_lower:
        score += 0.5
```

## 融合评分

图结果 + 文本结果融合：

```python
# 图结果基础分 0.5，文本结果乘 0.7
# 若同一路径同时出现在图和文本中，取 max(0.5, text_score * 0.7)
```

权重调整：
- `graph_only`: 0.5（无文本匹配）
- `text_only`: score × 0.7（无图连接）
- `graph+text`: 0.5 + score × 0.5（两者都有，boost）

## 性能基准

| 查询类型 | 首次（构建索引） | 后续（命中缓存） |
|----------|------------------|-------------------|
| simple | ~0.8s（jieba 加载） | ~0.8s |
| graph | ~1.0s（BFS 遍历） | ~1.0s |
| full | ~30s（TF-IDF 构建） | ~30s |
| bridge | <0.1s | <0.1s |

**注意**：TF-IDF 索引每次运行重新构建（无持久化缓存）。如果需多次查询同一图谱，可考虑持久化 `vectorizer` 和 `tfidf_matrix`。