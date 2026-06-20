# curl_cffi — TLS指纹伪装核心库

## 用途

`curl_cffi` 是 `pdf-download-racing` 技能中 Cloudflare/Site-block 绕过层的核心依赖。
用于模拟真实浏览器的 TLS 指纹，绕过 Cloudflare JS Challenge 和 IP 封禁。

## 安装

```bash
pip install curl_cffi
```

## 核心用法

```python
from curl_cffi import requests

# Chrome 120 指纹 — 模拟真实 Chrome 浏览器
r = requests.get(
    "https://example.com",
    impersonate="chrome120",  # 模拟 Chrome 120 TLS 指纹
    timeout=30
)

# 支持的 impersonate 值:
# chrome, chrome100, chrome107, chrome110, chrome116, chrome120, chrome123
# safari, safari15_3, safari15_5, safari17, safari17_0
# firefox, edge

# 检测拦截后自动降级:
import requests as req
try:
    r = req.get(url, timeout=15)
    if r.status_code in (403, 503, 429):
        # 自动切 curl_cffi
        r = requests.get(url, impersonate="chrome120", timeout=30)
except:
    r = requests.get(url, impersonate="chrome120", timeout=30)
```

## 已知有效绕过目标

- **ScienceDirect** — 403 → 切 curl_cffi 可访问
- **Wiley** — 部分 403 → 切 curl_cffi 可访问
- **IEEE** — 部分 403 → 切 curl_cffi 可访问
- **ACM** — 部分 403 → 切 curl_cffi 可访问

## 已知不可绕过

- **Springer** — 404/403, curl_cffi 无效（服务端直接拒绝）
- **Nature** — 404, curl_cffi 无效
- **Elsevier (部分)** — 403, curl_cffi 无效
- **Cloudflare 503 + 高级JS挑战** — 需完整浏览器会话

## 与 "cloakbrowser" 的关系

用户可能混淆了以下工具：

| 名称 | 实际存在？ | 说明 |
|:-----|:-----------|:------|
| `curl_cffi` | ✅ 存在 | Python 库，TLS指纹伪装，已在系统中安装 |
| `cloakbrowser` | ❌ 不存在 | 可能是对 curl_cffi 的误记，或指 Playwright stealth 模式 |
| `stealth.min.js` | ✅ 存在 | Playwright 中注入的反检测脚本，非独立包 |
| `playwright-stealth` | ✅ 存在 | Playwright + stealth 插件的组合，非独立包 |

**系统当前浏览器下载方案：**
1. Playwright Chromium/Firefox（已安装）→ 完整浏览器会话
2. curl_cffi（已安装）→ TLS指纹伪装
3. Tor SOCKS5H → sci-hub.vg（唯一可靠的 Sci-Hub 路径）

**不要尝试 `pip install cloakbrowser` — 包不存在。**

## 安装验证

```bash
# 验证已安装
pip show curl_cffi
# 输出: curl_cffi-0.15.0

# 验证可用
python3 -c "from curl_cffi import requests; print('OK')"
```

## 参考

- GitHub: https://github.com/lelylan/curl_cffi
- PyPI: https://pypi.org/project/curl-cffi/
- 在 pdf-download-racing 技能中的使用：`scripts/smart_download.py` + `references/cloudflare-smart-download.md`
