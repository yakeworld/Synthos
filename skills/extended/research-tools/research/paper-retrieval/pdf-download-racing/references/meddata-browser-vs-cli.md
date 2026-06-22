# MedData Browser vs CLI Access (2026-06-18 Session Debug)

## Problem

User confirmed "浏览器可以下载" MedData 论文（Barany Society 等），但 CLI curl 无法获取真实 PDF——全部返回占位文件（MD5=`fd469bd7cd29446f2800f099e3b71457`）或空响应。

## ❌ 已过时 — 参见 SKILL.md「实测流程 (2026-06-23 校正)」

CLI 路径通过 `download_one.py` 已可正常下载外文论文全文。
旧结论"MedData不收录Western期刊"是出口IP被封锁导致的误判。
此文件保留仅作历史记录。

### CLI 路径（已验证）

```
SSO POST https://uuct.medbooks.com.cn:9443/sso/login
  → bucToken
GET  http://www.meddata.com.cn/api/sso/user/login?bucToken=...
  → meddataToken
GET  http://www.meddata.com.cn/api/abstract/full_look?token=&abstractId=&doi=...
  → status + fileName
GET  http://www.meddata.com.cn/api/abstract/viewtext?fileName=&token=...
  → PDF（仅国内收录论文，Western = 占位）
```

### 浏览器路径（用户确认可行，但当前 `browser_navigate` 工具不稳定）

浏览器访问 MedData 网站 → 登录 → 搜索论文 → 点击下载。Web 界面可能：
1. 通过 JS 调用额外 API 端点
2. 触发不同的下载流程（如生成临时 URL、触发 CDN 下载）
3. 携带完整的 Cookie/Session 上下文

### 实战案例

| 论文 | DOI | CLI curl 结果 | 浏览器预期 | OA 可下载? |
|------|-----|---------------|-----------|-----------|
| Barany Society (Ling2020) | 10.3389/fneur.2020.00602 | 占位 PDF | 应可下载 | ✅ Frontiers OA，663KB |
| Western Elsevier/Springer | 各种 | 占位 PDF | 可能不同 | ❌ 多数不可 |

## Strategy

1. **优先 OA 直连**：Frontiers (`10.3389/`)、PLOS、PMC 等 OA 期刊直接 `curl` 官网链接
2. **浏览器路径**：当 `browser_navigate` 可用时，通过浏览器访问 MedData 网站
3. **CLI 路径**：仅对确认有收录的国内/中文论文使用
4. **始终验证**：下载后检查 MD5 ≠ 占位指纹

## Key Takeaway

MedData 的 CLI API 覆盖有限，仅对国内收录论文有效。Western 论文需要走 OA 直连或浏览器路径。用户反馈 "浏览器可以下载" 是一个重要信号——当 CLI 路径失败时，浏览器路径可能更可靠。
