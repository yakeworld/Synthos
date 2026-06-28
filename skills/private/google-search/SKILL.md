---

name: google-search
description: 网页搜索引擎封装 — SerpAPI/Brave API → 自建 SearXNG → DDG/Google fallback 三级降级链。所有路径共享统一输出契约 {title, url, snippet, position}。
version: 4.1.0
allowed-tools:
- terminal
- file
license: MIT
author: Synthos
metadata:
  synthos:
    version: 2.1.0
    author: Synthos
    signature: 'query: str -> results: list'
    atom_type: skill
    priority: P1

---

## IO_CONTRACT

- **input**: `query: str, max_results: int, advanced_search: dict`
- **output**: `list[dict]` — 每项 {title, url, snippet, position, engine}

## 触发条件

通用网页搜索、实时信息检索、替代 `web` 工具做结构化搜索提取。

## 三级降级链（严格按优先级）

### 第一级：API 搜索引擎（零 CAPTCHA）

优先级：SerpAPI > Brave Search > Serper

```bash
python3 scripts/web_search.py "query" --engine serpapi --max 10
python3 scripts/web_search.py "query" --engine brave --max 10
python3 scripts/web_search.py "query" --engine serper --max 10
```

API key 从环境变量读取：`SERPAPI_KEY`, `BRAVE_SEARCH_API_KEY`, `SERPER_API_KEY`

### 第二级：自建 SearXNG 实例

**关键配置规则（SearXNG 2026+）**：
### 第二级：自建 SearXNG 实例

**关键配置规则（SearXNG 2026+）**：
1. **必须用 `settings.yml`**（不是 `.yaml`）— SearXNG 2026+ 版本优先读 `.yml`，`.yaml` 挂载被忽略，搜索 API 无法正常工作
2. **`limiter.toml` 必须有 `[limiter]` section** — 新版 schema 校验严格，错误格式会触发 `TypeError` 导致容器重启
3. **`docker compose up` 用 `background=true`** — Hermes 将容器启动识别为长服务进程，前台会报 "long-lived server" 错误

**SearXNG Docker 陷阱（2026-06-21 实战确认）：**

- **陷阱 1 — `settings.yaml` vs `settings.yml`**：容器 volume 挂载 `/etc/searxng` 为 named volume，bind mount 的 `settings.yaml` 被 volume 覆盖，导致容器用默认模板（无 engines 配置）启动 → 搜索返回 403。修复：用 bind mount 直接挂载 `settings.yml` 到 volume 之上，或在 volume 内创建该文件。
- **陷阱 2 — 启动时外部 fetch 阻塞**：SearXNG 2026.6.19 启动时同步请求 `clearurls.xyz`（tracker patterns）和 `wikidata`（infobox），网络不通直接 crash worker。修复：在 `settings.yml` 中添加 `outgoing.request_timeout` 和 `outgoing.max_timeout`，或确保容器可访问这些域。
- **陷阱 3 — `msgspec` 缺失**：SearXNG 2026+ 内嵌 Python 环境缺少 `msgspec`。修复：启动命令中先 `pip install msgspec` 再执行 entrypoint。
- **陷阱 4 — 容器不监听端口但 `docker ps` 显示 running**：worker crash 后 granian 进程退出，容器状态可能短暂为 running 但端口 000。排查：`docker logs --tail 50` 看 granian 是否有 "Unexpected exit from worker-1"。

```bash
cd ~/searxng && docker compose up -d
python3 scripts/web_search.py "query" --engine searxng --max 10 \
    --searxng-url http://127.0.0.1:8080
```

**推荐 settings.yml 模板**（含修复）：
```yaml
use_default_settings: true

outgoing:
  request_timeout: 10
  max_timeout: 10

server:
  secret_key: "your-secret"
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
  - name: wikipedia
    engine: wikipedia
    shortcut: wp
    disabled: false
```

**SearXNG 引擎超时修复——通过 Tailscale Exit Node（2026-06-25 新增）**：

当 SearXNG 所有引擎全部返回 `ConnectTimeout`（不是个别超时，是集体超时），首先排查宿主机本身是否无外网：

```bash
# 第一步：确认宿主机自身能否上网
curl -s --max-time 10 -o /dev/null -w "%{http_code} %{time_total}s" https://www.google.com.hk
# HTTP 000 = 宿主机无外网，非 SearXNG 问题
```

**诊断流程**：
1. 检查 Docker 代理容器：`docker ps` 确认是否有 shadowsocks/socks5 代理运行
2. 如果 SOCKS5 能握手（`SOCKS5 request granted`）但 TLS 超时 → 远端 SS server 不转发流量，不是本地问题
3. 检查 Tailscale 是否有 exit node 可用：`tailscale status` 寻找含 `offers exit node` 标记的对端
4. 启用 exit node：`sudo tailscale set --exit-node=<IP> --exit-node-allow-lan-access`
5. 验证宿主机连通：重新 curl
6. 验证 SearXNG 容器（Docker bridge 网络自动走宿主路由）：`curl -s --max-time 30 "http://127.0.0.1:8080/search?q=test&format=json"`

**注意**：Tailscale exit node 是系统级路由，启用后所有 Docker 容器出站也自动通过 exit node，SearXNG 无需额外代理配置。但须加 `--exit-node-allow-lan-access` 以免阻断 Docker 内部网络。

**SearXNG 引擎超时修复——通过 Tor 路由（2026-06-24 新增）**：
当前出口节点（64.23.234.118）被 Google/Bing 封锁，导致 SearXNG 的 bing/google 引擎超时（httpx.ConnectTimeout）。

修复：在 docker-compose.yaml 中为 SearXNG 容器添加 Tor SOCKS5 代理：
```yaml
services:
  searxng:
    environment:
      - HTTP_PROXY=socks5h://172.17.0.1:9050
      - HTTPS_PROXY=socks5h://172.17.0.1:9050
```
（宿主机 Tor 监听 127.0.0.1:9050，Docker 默认 bridge 网络下宿主机地址为 172.17.0.1）

如果 Tor 出口节点仍被封锁，尝试切换 Tor 电路：`sudo systemctl reload tor`

**2026-06-21 SearXNG limiter.toml 陷阱**：
SearXNG 2026.6.19+ 的 `limiter.toml` 即使包含 `[limiter]` section 且 `enabled = false` 仍可能触发 `TypeError: schema of /etc/searxng/limiter.toml is invalid!`。

**修复方案**：
1. 删除 `limiter.toml` 挂载：从 docker-compose.yaml 中移除 `- ./searxng-limiter.toml:/etc/searxng/limiter.toml:ro`
2. 在 settings.yml 中配置 `server.limiter: false`
3. 在启动命令中安装缺失的 Python 依赖：`command: /bin/sh -c "pip install msgspec && /usr/local/searxng/entrypoint.sh"`

**Google Scholar 引擎已知限制**：SearXNG 的 `google_scholar` 引擎（`engine: google_scholar`）几乎总是被 Google Scholar 的反爬机制拦截，返回 `access denied`。即使宿主机直连 `scholar.google.com` 正常（HTTP 200），SearXNG 的请求模式仍被识别为 bot。**不要依赖此引擎**。

**2026-06-26 实证确认**：宿主机直连 scholar.google.com 返回 HTTP 200，但 SearXNG 的 google_scholar 引擎返回 0 条结果，指定 `engines=google%20scholar` 同样返回 0 条。google 主引擎可间接出 scholar 链接，但专用引擎不可用。**；学术搜索通过常规 google 引擎即可（能间接出 scholar 链接），或由用户浏览器直连 scholar.google.com。

**SearXNG 引擎选型建议**：对于神经内科/临床科研用户的日常工作，Google 引擎覆盖面远优于 Bing（学术内容、DOI、诊疗指南）。Bing 仅作为 Google 不可用时的降级。

**核心排查步骤**：
1. `docker logs --tail 50 searxng` — 检查 `[ERROR] Unexpected exit from worker-1` 后的 Python 回溯
2. `docker exec searxng python3 -c "import searx.webapp; print('OK')"` — 验证模块可导入
3. `docker inspect --format '{{json .Mounts}}' searxng` — 确认 /etc/searxng 是 bind mount 而非 volume
4. `docker exec searxng cat /etc/searxng/limiter.toml` — 检查 limiter.toml 内容

### 第三级：Startpage 通过 Tor（2026-06-24 实测可用）

当 API 和 SearXNG 都失败时（常见：出口节点 IP 被 Google/Bing 封锁，API key 缺省或无效）：

```bash
# Tor 必须在运行（systemctl status tor 确认）
# Startpage 通过 Tor SOCKS5H 返回真实搜索结果，无 CAPTCHA
curl -s --socks5-hostname 127.0.0.1:9050 --max-time 30 \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.startpage.com/sp/search?query=关键词+URL编码" \
  | python3 -c "
import sys, re
html = sys.stdin.read()
links = re.findall(r'<a[^>]*class=\"[^\"]*result-title[^\"]*\"[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>', html, re.DOTALL)
for url, title in links[:8]:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    if title_clean and len(title_clean) > 10:
        print(f'{title_clean}\n  {url}\n')
"
```

**2026-06-24 实证**：Startpage 通过 Tor 成功返回 8 条有效搜索结果（cochrane.org、nhlbi.nih.gov、jbi.global 等），而同一时刻的 Google/Bing/DDG 全部返回 CAPTCHA。Startpage 是当前唯一可行的免费搜索路径。

**注意事项**：
- Tor 电路可能不稳定，超时后重试 1-2 次
- Startpage 结果解析依赖 CSS class 名称（可能变动）
- 非 HTTPS 页面可能被 Tor exit node 拦截

### 第四级：公共搜索引擎（可能被 CAPTCHA）

DDG HTML → googler CLI → 直接 curl Google（作为最后降级）

```bash
python3 scripts/web_search.py "query" --engine ddg --max 10
python3 scripts/web_search.py "query" --engine googler --max 10
```

## 环境准备清单

1. **API key 检测**：启动时检查 SERPAPI_KEY/BRAVE_SEARCH_API_KEY/SERPER_API_KEY
2. **Docker Hub 连接问题**：Tailscale exit node 下 Docker Hub 可能超时 → 检查 systemd proxy drop-in（`/etc/systemd/system/docker.service.d/proxy.conf`）
3. **Docker 镜像加速器**：若 Docker Hub 超时，需配置 /etc/docker/daemon.json 添加 registry-mirrors
4. **SearXNG 镜像**：约 200MB，首次拉取约 30 秒
5. **googler CLI**：非 Python 包，是 bash 脚本，从 GitHub raw 下载。`pip install googler` 装的是 Google API Library，不是命令行搜索工具

## 参考

- `templates/docker-compose-searxng.yaml` — 已知可用的 SearXNG docker-compose 模板（含 msgspec 安装、无 limiter.toml）
- `references/searxng-setup.md` — SearXNG 部署配置模板（含 settings.yml 格式和 limiter.toml schema）
- `references/searxng-2026-troubleshooting.md` — SearXNG 2026.6.19 具体故障排查：worker 静默崩溃、msgspec 缺失、volume 覆盖
- `references/searxng-troubleshooting.md` — SearXNG 通用故障排查：worker 静默崩溃、settings 扩展名、limiter.toml schema、volume 冲突、重启循环
- `references/search-engines-api.md` — API 搜索引擎接入指南
- `references/searxng-google-scholar.md` — Google Scholar 引擎 access denied 限制详解及替代方案
- `references/captcha-blocked-ip.md` — 服务器 CAPTCHA 诊断
- `references/docker-proxy-trap.md` — Docker systemd proxy 陷阱排查
- `references/pubpeer-automation-analysis.md` — PubPeer API 逆向工程：端点分析、reCAPTCHA v2 配置、抓取能力评估

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
