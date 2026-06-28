# 服务器 CAPTCHA 诊断

## 症状

公共搜索引擎返回空结果或 CAPTCHA 页面：
- DDG HTML: "Unfortunately, bots use DuckDuckGo too. Please complete the following challenge"
- Google: noscript 重定向 "Please click here if you are not redirected within a few seconds"
- Bing/Ecosia: "Confirm you're not a robot" / Cloudflare challenge

## 诊断方法

```bash
# 检查是否被 CAPTCHA
curl -s "https://html.duckduckgo.com/html/?q=test" | grep -i captcha

# 检查 IP 信誉
curl -s https://ipinfo.io/json | python3 -m json.tool

# 检查 Google 搜索结果
googler "test" -n 1
```

## 当前状态

- IP: 64.23.234.118 (Tailscale exit node)
- Google: 封杀
- DuckDuckGo: 封杀
- Bing: 封杀
- Ecosia: Cloudflare 封杀

## 解决方案

1. **首选**：SerpAPI/Serper/Brave Search API — 完全绕过
2. **次选**：自建 SearXNG 实例 — 聚合多源，单 IP 压力分散
3. **临时**：切换 Tailscale exit node IP（如果有备用节点）
4. **不推荐**：每次搜索随机换 User-Agent 或添加请求间隔 — 治标不治本

## googler 安装注意

googler **不是** Python 包（`pip install googler` 安装的是 Google API Library）。

正确的 googler（jarun/googler, ⭐6192）：
```bash
wget https://raw.githubusercontent.com/jarun/googler/master/googler
chmod +x googler
./googler "query" -n 3 --json
```

版本 4.3.2，Python 脚本，依赖 Python 3。同样受 IP 封杀影响。
