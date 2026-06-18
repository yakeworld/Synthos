# Cloudflare 智能检测 + curl_cffi 自动回退

## 原理

部分学术网站（Sci-Hub、部分出版商OA页面）使用 Cloudflare/DDoS-Guard 保护。
标准 `requests` 库无法通过 TLS 指纹验证，返回 403/503 挑战页面。

## smart_download.py 策略

位于 `tools/paper-manager/src/smart_download.py`。

```
smart_download(url, ...)
  │
  ├─ Attempt 1: requests.get()
  │     │
  │     ├─ HTTP 200 + 正常内容 → 直接返回
  │     └─ HTTP 403/503/429 + Cloudflare签名 → 进入Attempt 2
  │
  └─ Attempt 2: curl_cffi.get(impersonate="chrome")
        │
        └─ 返回结果（成功或失败）
```

## Cloudflare 检测特征

| 检测指标 | 具体值 |
|:---------|:-------|
| HTTP 状态码 | 403, 503, 429 |
| Server 头 | `cloudflare` |
| Body 签名 | `cf-browser-verification`, `Checking your browser`, `DDoS protection`, `Just a moment`, `cf-ray` |

## 返回值格式

```python
# 成功
{'ok': True, 'status': 200, 'content': b'...', 'headers': {...}, 'source': 'requests'/'curl_cffi'}

# 失败
{'ok': False, 'error': '...'}
```

## 使用方式

```python
from smart_download import smart_download

result = smart_download('https://example.com/paper.pdf', 
                        timeout=60, 
                        headers={'User-Agent': '...'})

if result['ok'] and result['content'][:4] == b'%PDF':
    with open('paper.pdf', 'wb') as f:
        f.write(result['content'])
```

## 注意事项

- curl_cffi 需要安装: `pip install curl-cffi`
- 第一请求失败后会立即重试，总超时 ≈ 2x 设置的 timeout
- 不阻塞其他下载通道（在 racing engine 中与其他 Tier 并行）
