# SearXNG 2026.6.19 Docker 故障排查记录

## 症状

- `[ERROR] Unexpected exit from worker-1`
- 容器状态 `running` 但 HTTP 返回 000 或 500
- `docker logs` 仅显示 granian 启动信息，无 Python 回溯

## 根因

1. **limiter.toml schema 不兼容**：SearXNG 2026.6.19+ 要求严格 schema，简单格式 `[limiter]` + `enabled = false` 仍触发 `TypeError: schema of /etc/searxng/limiter.toml is invalid!`

2. **msgspec 模块缺失**：Python 环境缺少 `msgspec`，导致 `ModuleNotFoundError` 但错误被 granian 吞掉，不在 docker logs 中显示

3. **Volume 覆盖 bind mount**：docker-compose.yaml 中 `/etc/searxng` 同时存在 volume 和 bind mount 时，volume 优先

## 诊断步骤

```bash
# 1. 查看 Python 错误（关键）
docker exec searxng python3 -c "import searx.webapp"

# 2. 检查挂载冲突
docker inspect --format '{{json .Mounts}}' searxng

# 3. 检查 limiter.toml 内容
docker exec searxng cat /etc/searxng/limiter.toml

# 4. 检查 settings.yml 是否被 volume 覆盖
docker exec searxng stat /etc/searxng/settings.yml

# 5. 检查网络（容器内）
docker exec searxng python3 -c "import urllib.request; urllib.request.urlopen('https://www.baidu.com'); print('OK')"
```

## 修复方案

1. 删除 limiter.toml 挂载
2. 在 settings.yml 中设置 `server.limiter: false`
3. 在 docker-compose command 中安装 msgspec
4. 确保 /etc/searxng 是 bind mount 而非 volume

## 已知配置

### settings.yml（最小可用配置）

```yaml
use_default_settings: true
server:
  secret_key: "random-string-here"
  image_proxy: true
  limiter: false
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
engines:
  - name: bing
    engine: bing
    shortcut: b
    disabled: false
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    disabled: false
```

### docker-compose.yaml

使用 `templates/docker-compose-searxng.yaml`

## 网络相关

- Docker Hub 超时：检查镜像加速器（https://docker.1ms.run 可能失效）
- IPv6 路由问题可能导致 Docker Hub 不可达
- SearXNG 容器内网络独立，可能无法访问某些外部网站
- Tailscale exit node 下 Docker Hub 经常超时
