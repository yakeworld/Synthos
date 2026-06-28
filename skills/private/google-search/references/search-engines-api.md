# API 搜索引擎接入指南

## 为什么优先 API？

公共搜索引擎（Google、DDG、Bing）的服务器 IP 经常被 CAPTCHA 封杀（当前环境 IP 64.23.234.118 已被 Google 和 DDG 同时标记）。API 方式走各自的服务器，完全绕过 CAPTCHA。

## 各 API 对比

| API | 免费额度 | 费用 | 需要信用卡 | 特点 |
|-----|---------|------|-----------|------|
| SerpAPI | 100 次/月 | $50/月 1000次 | 否 | 最接近真实 Google 结果 |
| Serper.dev | 2500 次/月 | $3/月 10000次 | 是 | 速度快，含 Knowledge Graph |
| Brave Search | 2000 次/月 | $0/月 2000次 | 否 | 完全免费，支持 web/news/imagen |
| Google Custom Search | 100 次/天 | $5/1000次超出 | 是 | Google 官方，需创建 CSE |

## 接入命令

### SerpAPI
```bash
export SERPAPI_KEY="your-key-here"
curl -s "https://serpapi.com/search.json?q=AI+news&api_key=$SERPAPI_KEY" \
  | python3 -m json.tool
```

### Serper.dev
```bash
export SERPER_API_KEY="your-key-here"
curl -s -X POST https://google.serper.dev/search \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "AI news 2026"}' \
  | python3 -m json.tool
```

### Brave Search
```bash
export BRAVE_SEARCH_API_KEY="your-key-here"
curl -s "https://api.search.brave.com/res/v1/web/search?q=AI+news" \
  -H "X-Subscription-Token: $BRAVE_SEARCH_API_KEY" \
  -H "Accept: application/json" \
  -H "Accept-Encoding: gzip" \
  | python3 -m json.tool
```

## 统一输出格式

所有引擎输出统一为：
```json
{
  "title": "搜索结果标题",
  "url": "https://...",
  "snippet": "搜索摘要...",
  "position": 1,
  "engine": "serpapi|serper|brave|ddg|googler|searxng"
}
```

## 环境变量检测

脚本启动时自动检测：
```python
API_KEYS = {
    'serpapi': os.environ.get('SERPAPI_KEY'),
    'serper': os.environ.get('SERPER_API_KEY'),
    'brave': os.environ.get('BRAVE_SEARCH_API_KEY'),
}

active_engines = [k for k, v in API_KEYS.items() if v]
if not active_engines:
    print("Warning: No search API keys configured. Falling back to public search.")
```
