# API Rate Limiting & Fallback Strategy

> 2026-05-22 实测 | 用于文献检索时避开限速陷阱

## 各API实测状态

| API | 端点 | 限速规则 | 实测行为 | 当前可用性 |
|:----|:-----|:---------|:---------|:----------|
| **arXiv** | `export.arxiv.org/api/query` | 声明 1req/3s | 连接建立后0字节返回，10s超时 | 🔴 服务不稳定（经常down机） |
| **Semantic Scholar** | `api.semanticscholar.org/graph/v1/paper/search` | 无key: 1req/s; 有key: 100req/s | 并行4请求 → HTTP 429封禁，封禁期≥30分钟 | 🟡 需串行+3s间隔 |
| **OpenAlex** | `api.openalex.org/works` | 无正式限速 | 持续可用，无限速 | 🟢 首选外搜源 |

## 搜索执行协议

### 串行搜索（避限速）

```python
# Python伪代码 — 每次搜索后必须sleep
import time, subprocess, json

api_chain = ["openalex", "semantic_scholar", "arxiv"]  # 按优先级
for api in api_chain:
    # 对每个API搜索多个关键词
    for query in queries:
        result = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
        if "429" in result.stdout:
            print(f"429 on {api} — switch to next API")
            break  # 切换到下一个API源
        # 处理结果
        time.sleep(3)  # 强制间隔
```

### 速率限制恢复策略

| 错误码 | 含义 | 恢复操作 |
|:------:|:-----|:---------|
| 429 | Too Many Requests | 停止当前API→等待60s→若仍429则切换到下一源→标记当前源不可用 |
| 连接超时(>10s无字节) | 服务down | 立即切换到下一源，标记为不可用 |
| 200但空结果 | 搜索词无匹配 | 调整搜索词再试一次，仍空则跳过 |

## OpenAlex 正确语法备忘

```bash
# ✅ 正确 — 无 sort=relevance（不合法）
curl -s "https://api.openalex.org/works?search=KEYWORDS&per_page=5&select=title,cited_by_count,publication_year"

# ❌ 错误 — sort=relevance:desc 不合法
# curl -s "https://api.openalex.org/works?search=KEYWORDS&sort=relevance:desc"  # 会报错

# 按引用数降序（默认行为）
curl -s "https://api.openalex.org/works?search=KEYWORDS&sort=cited_by_count:desc&per_page=5"
```

## Semantic Scholar 串行示例

```bash
# 每次请求后必须sleep 3秒
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=3&fields=title,authors,year,citationCount,externalIds,abstract"
sleep 3
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=NEXT_QUERY&limit=3&fields=title,authors,year,citationCount,externalIds,abstract"
# ... 继续
```

## 关键发现（2026-05-22）

1. **并行请求是Semantic Scholar 429的主因** — 不是请求频率超过1req/s，而是短时间内并发多个连接。即使每个连接间隔1s，并发连接也会触发AWS API Gateway的限流。
2. **arXiv (export.arxiv.org) 完全不可用** — DNS解析正常、TCP连接正常、TLS握手正常，但服务器不返回任何数据。猜测是Fastly CDN后端超时或服务端down机。
3. **OpenAlex在AI/CS论文上覆盖面不如Semantic Scholar** — 对特定论文名（如PaperQA）的搜索不敏感，但对通用关键词（如Reflexion, Voyager）效果好。
4. **Semantic Scholar对具体论文ID（arXiv ID/DOI）查询优于关键词搜索** — 单论文元数据查询不受1req/s限制，可快速获取已知论文的引用数和摘要。
