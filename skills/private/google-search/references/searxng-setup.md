# SearXNG 部署配置

## 前置条件

- Docker + docker compose v2
- 服务器需可访问 Docker Hub（或配置镜像加速器）

## 快速启动

```bash
mkdir -p ~/searxng && cd ~/searxng
```

### docker-compose.yaml

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./settings.yml:/etc/searxng/settings.yml:ro
      - ./searxng-limiter.toml:/etc/searxng/limiter.toml:ro
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
      - SEARXNG_SECRET=random-secret-key-change-me
    cap_drop:
      - NET_RAW
```

### settings.yml（SearXNG 2026+ 仅读 .yml）

**警告**：文件名必须是 `settings.yml`，不是 `settings.yaml`。SearXNG 2026+ 优先读 `.yml`，`.yaml` 挂载被忽略 → JSON API 不可用。

```yaml
use_cache: true
search:
  auto_locale: true
  safe_search: 0
  default_lang: zh-CN
  languages:
    - "zh-CN"
    - "zh"
    - "en"
  formats:
    - html
    - json
```

### limiter.toml（新版 schema）

SearXNG 2026+ 对 limiter.toml 有 schema 校验，旧格式（无 section header）会报 `TypeError: schema of limiter.toml is invalid!` 导致容器反复重启。

```toml
[limiter]
enabled = false
```

### 启动

```bash
docker compose up -d
# 验证
curl -s http://127.0.0.1:8080/search?q=test&format=json | python3 -m json.tool
```

## Docker Hub 连接问题

Tailscale exit node 环境下 Docker Hub 经常超时。

**根因排查**：先检查是否有 systemd proxy drop-in：
```bash
systemctl show docker.service --property=Environment
cat /etc/systemd/system/docker.service.d/proxy.conf
```

如果存在 `HTTP_PROXY=socks5://...` 指向已下线的 shadowsocks 容器（如 `172.18.0.12`），Docker pull 会因代理不可用而超时。

**解决方案**：
1. 删除 proxy override：`sudo rm /etc/systemd/system/docker.service.d/proxy.conf && sudo systemctl daemon-reload`
2. 配置镜像加速器（`/etc/docker/daemon.json`）
3. `sudo systemctl restart docker`
4. 见 `references/docker-proxy-trap.md` 完整指南

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://hub.rat.dev"
  ]
}
```

然后 `sudo systemctl restart docker`

## 常用搜索命令

```bash
# JSON 格式（适合程序调用）
curl -s "http://127.0.0.1:8080/search?q=人工智能+2026&format=json" \
  -H "User-Agent: Mozilla/5.0" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); [print(r['title'], r['url']) for r in data['results']]"

# HTML 格式（适合调试）
curl -s "http://127.0.0.1:8080/search?q=test" | grep -o 'class="result__title[^"]*"[^>]*>[^<]*'

# 指定搜索引擎
curl -s "http://127.0.0.1:8080/search?q=test&engines=google,duckduckgo"

# 指定语言
curl -s "http://127.0.0.1:8080/search?q=test&language=zh"
```

## 输出格式（JSON）

```json
{
  "results": [
    {
      "title": "搜索结果标题",
      "url": "https://...",
      "content": "搜索摘要...",
      "engine": "google",
      "score": 0.95
    }
  ],
  "number_of_results": 123
}
```
