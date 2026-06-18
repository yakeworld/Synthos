# Cloudflare 反爬虫拦截处理

## 现象

在 Hermes Agent cron 环境中，对 `openalex.org` 发起 `curl` 请求可能返回 Cloudflare JS challenge HTML 而非 JSON：

```html
<!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
...<script>...</script>...
```

HTTP 状态码 200，但内容是 HTML。

## 检测

解析响应前检查第一个非空白字符：

```python
content = open('/tmp/oa_result.json').read().strip()
if content.startswith('<'):
    # Cloudflare blocked
    data = {"meta": {"count": 0}, "results": []}
else:
    data = json.loads(content)
```

## 处理策略

1. **不重试** — Cloudflare 拦截是环境级别的，同一会话中重试无效
2. **记录到 notes** — 在 agent-tracker.json 中记录 `openalex_blocked_YYYY-MM-DD`
3. **回退到 PubMed** — PubMed (NCBI eutils) 不受影响，用 3-domain 验证协议
4. **记录到 agent-log** — `|[Cron] <date> | action=cloudflare_block | fallback=pubmed |`

## 恢复

Cloudflare 拦截是暂时的。下次 cron 会话可能恢复正常。每次运行都检查，不要假设永久阻塞。