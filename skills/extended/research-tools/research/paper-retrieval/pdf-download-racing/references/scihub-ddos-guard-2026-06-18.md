# Sci-Hub DDoS-Guard 全面失效 — 2026-06-18 诊断记录

## 现象
所有11个Sci-Hub域名访问均返回DDoS-Guard JavaScript挑战页面，无法获取任何PDF。

## 原因
1. 不是浏览器指纹检测 — curl_cffi impersonate已覆盖但仍被拦截
2. 是服务端JS渲染挑战 — 需要执行JavaScript才能获取真实页面
3. Python HTTP客户端无法执行JS — requests/curl_cffi都只能拿到挑战页面
4. 可能需要无头浏览器如Playwright/Selenium执行JS后访问

## 影响
所有Sci-Hub下载路径完全失效，自动化论文管线参考文献补充功能严重降级。

## 替代方案
1. MedData（机构凭据）— 唯一可行的自动化路径
2. 浏览器无头模式（Playwright/Selenium）— 可执行JS挑战页
3. 手动下载 — 通过机构网络访问出版社
4. PubMed Central OA API — EFetch用于开放获取文献
5. DOI Content Negotiation — Accept: application/pdf

## 待实现
- 测试Playwright/Selenium绕过DDoS-Guard
- 测试PubMed Central EFetch API
- 测试DOI Content Negotiation
- 补充LibGen路径（非医学文献）