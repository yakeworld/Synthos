# Tailscale Exit Node — Sci-Hub 下载

## 核心事实

本机所有出站流量已通过 Tailscale 自动路由至 exit node：
- **Exit Node**: `ubuntu--s-1vcpu-2gb-intel-nyc1-01` (64.23.234.118)
- **Tailscale IP**: 100.65.157.17
- **延迟**: ~148ms (本机 → exit node)
- **出口 IP**: `curl ifconfig.me → 64.23.234.118`

## 验证方法

```bash
# 确认出口 IP 为 64.23.234.118
curl -s https://ifconfig.me
# 应输出: 64.23.234.118

# 确认 traceroute 经过 exit node
traceroute -n ifconfig.me
# 第1跳: 100.65.157.17 (Tailscale IP)
# 第2跳: 138.68.x.x (Digital Ocean NYC)

# 确认 Tailscale exit node active
tailscale status
# 应显示: active; exit node; direct 64.23.234.118:41641
```

## Sci-Hub 使用

Exit node 使 Sci-Hub 全部可达，无需 Tor：

```bash
# 直接 HTTP 连接 (curl_cffi requests 均可)
curl -s -L "https://sci-hub.al/10.1234/example" -o paper.pdf
curl -s -L "https://sci-hub.ru/10.1234/example" -o paper.pdf
```

已验证有效域（通过 exit node）:
- `sci-hub.al` — HTML → iframe → PDF（实测成功）
- `sci-hub.ru` — 直接可达
- 其他域应同样有效（无需单独验证）

## Tor 备用

仅当 exit node 不可用时使用：

```bash
# Tor SOCKS5 代理
export all_proxy=socks5h://127.0.0.1:9050
curl -s -L "https://sci-hub.al/DOI" -o paper.pdf
```

Tor 限制: pysocks 不支持 IPv6，部分域连接超时。仅 sci-hub.al 曾成功。

## MedData 注意

MedData 对境外 IP(64.23.234.118)有频率/IP限制：
- 本机通过 exit node 访问 MedData，更容易触发限制
- 如需要国内 IP 访问 MedData，需临时切换网络出口

## 故障排查

1. 如果 `curl ifconfig.me` 不返回 64.23.234.118 → 流量未走 exit node
2. 如果 traceroute 第1跳不是 100.65.157.17 → 路由异常
3. 如果 Sci-Hub 返回 403 → 检查是否为 exit node IP 被封（罕见）
4. 如果 MedData 返回占位 PDF → 该论文不在 MedData 收录范围
