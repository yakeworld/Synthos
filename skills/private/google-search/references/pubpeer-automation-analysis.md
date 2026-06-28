# PubPeer 自动化 — API 逆向工程

## API 端点分析

从 `https://pubpeer.com/js/app.js` 逆向获取：

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/anonymous/register/` | POST | 无 | 匿名注册（需要 reCAPTCHA v2） |
| `/author/register/` | POST | 无 | 实名注册（需要 reCAPTCHA + 邮箱） |
| `/api/publications/{id}` | GET | 需要 session | 论文详情 + 评论（需要 cookie） |
| `/api/comments/` | GET | 需要 session | 评论列表 |
| `/api/search/` | GET | 需要 CSRF | 搜索论文（需要 cookie + CSRF） |
| `/api/comments/{id}/accept` | POST | 管理员 | 通过评论 |
| `/api/comments/{id}/disable` | POST | 管理员 | 禁用评论 |
| `/api/recent` | GET | 公开 | 最近 40 篇论文（仅标题+ID+评论数，无评论内容） |
| `/api/journals` | GET | 公开 | 期刊列表 |

## reCAPTCHA v2 配置

- **sitekey**: `6LepExcUAAAAAK7rEUQQMtocDPWwIVIbTygeyybf`
- 无法用纯 HTTP 请求绕过
- 需要浏览器自动化（Playwright/Selenium）或付费服务（2Captcha）

## 抓取能力总结

| 数据 | 公开 | 需要什么 |
|------|------|---------|
| 论文列表 (/api/recent) | ✅ | 无 |
| 评论详情 | ❌ | 登录 cookie |
| 搜索 | ❌ | cookie + CSRF |
| 论文详情 | ❌ | 登录 cookie |

## 2026-06-26 实测

- `/api/recent` 返回 40 篇论文，但所有 `total_comments` 为 0（需要登录看评论）
- `/api/publications/{id}` 返回空消息（404）
- 搜索 API 返回 403
