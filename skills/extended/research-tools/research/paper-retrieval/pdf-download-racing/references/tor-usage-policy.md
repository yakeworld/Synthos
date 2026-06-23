# Tor 使用策略（2026-06-23）

## 核心原则

Tor（`socks5h://127.0.0.1:9050`）只用于被出口IP封锁的学术资源。不走国内平台和正规API。

## 通道矩阵

| 通道 | 用Tor? | 策略 | 原因 |
|:-----|:-------|:-----|:------|
| SciHub | ✅ 第二遍重试 | 直连失败→自动Tor重试 | SciHub域被轮换封锁，Tor可恢复访问 |
| LibGen | 🟡 可试 | 直连失败→Tor重试 | 当前全部不通，Tor可能解开 |
| Crossref API | 🟡 可试 | 直连404→Tor重试 | 出口IP段被学术网站屏蔽 |
| **MedData** | ❌ **禁止** | 只用直连 | 国内机构认证平台，Tor触发风控 |
| Semantic Scholar | ❌ 不需要 | 只用直连 | 无封锁问题 |
| OA直连(Frontiers/PLOS) | ❌ 不需要 | 只用直连 | 正规出版社，Tor触发CAPTCHA |
| arXiv | ❌ 不需要 | 只用直连 | 开放获取，本出口可达 |

## 代码实现

`scihub_racing.py` 中 `try_scihub_curl()` 实现两遍扫描：
1. 直连 curl_cffi → 试所有域
2. 全失败且Tor可用 → Tor SOCKS5代理重试
