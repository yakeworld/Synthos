# CloakBrowser vs curl_cffi — 对比与集成策略

## 定位差异

| 维度 | curl_cffi | CloakBrowser |
|------|-----------|-------------|
| 层级 | HTTP 客户端库 | 完整浏览器 |
| 协议 | HTTP/HTTPS | 完整浏览器（HTTP+WS+JS） |
| TLS 伪装 | ✅（Chrome 指纹） | N/A（原生 Chromium） |
| JS 渲染 | ❌ | ✅ |
| Cookie 管理 | 手动 | 自动（per-profile） |
| 性能 | 高（无渲染开销） | 中（内存密集） |
| 适用 | API 请求、爬虫 | 需要 JS 渲染的反检测页面 |
| 资源 | ~5MB 依赖 | ~200MB（Chromium 二进制） |

## 集成策略

### 当前 pdf-download-racing 路径

```
1. curl_cffi (TLS 伪装) → 最快，API 级别
2. Requests → 普通 HTTP
3. Tor + curl_cffi → 匿名化
4. Playwright (无 stealth) → 备用
```

### 加入 CloakBrowser 后

```
1. curl_cffi (TLS 伪装) → 最快，API 级别（不改变）
2. Requests → 普通 HTTP（不改变）
3. Tor + curl_cffi → 匿名化（不改变）
4. CloakBrowser → 新增：需要完整浏览器渲染的反检测场景
5. Playwright + stealth → 备用
```

### 何时用 CloakBrowser

- 目标网站有高级 bot 检测（行为分析、指纹检查、TLS 指纹+行为组合）
- 需要 JS 渲染的页面（SPA、动态加载内容）
- 需要持久化 cookie/session 的多步骤流程
- Cloudflare 5秒挑战等高级防护

### 何时用 curl_cffi

- 标准 API 请求
- 需要快速并发请求
- 带宽/内存有限
- 不需要 JS 渲染

## 2026-06-21 实测状态

- CloakBrowser 在 PyPI 上版本 0.3.32
- 项目 26,707 stars，活跃维护
- 本机尚未安装
- 当前 pdf-download-racing 主要依赖 curl_cffi，运行正常
- 无紧急需求安装，作为备用路径储备