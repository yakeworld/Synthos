# 出口节点 PDF 下载实测 (2026-06-23)

## 当前出口 IP: 64.23.234.118 (DigitalOcean NYC, Tailscale exit node)

### 三层竞速结果

| 通道 | 状态 | 说明 |
|:-----|:-----|:------|
| **SciHub** | 🟡 部分可用 | `sci-hub.al` 对 **Nature/Scientific Data** 等返回 ✅ 320KB 真实PDF。但大部分 Springer/Elsevier/Wiley 付费论文 ❌ 不可达。6月19日"全面失效"断言已过时——部分域已恢复。 |
| **LibGen** | ❌ 全部超时 | 5个域全部不可达 |
| **MedData** | 🟡 登录成功，仅返回占位 | SSO登录✅, token交换✅, 但所有论文返回同一占位PDF(MD5=`fd469bd7...`)。Full_look返回`status=2`。**在两个域上测过**: `www.meddata.com.cn` 和 `app.meddata.com.cn:8878` 均返回占位。 |

### 关键发现

1. **SciHub 并非全面失效** — 某些域的连通性在波动。2026-06-19 → 2026-06-23 之间部分域已恢复。
2. **MedData 域不匹配问题**：
   - 技能文档说 viewtext 正确域是 `app.meddata.com.cn:8878`，`www`域返回占位
   - 但 `meddata.py` 的 `_try_viewtext()` 使用 `BASE_URL = "http://www.meddata.com.cn"` — 需改到 `APP_URL`
   - 实测中两个域对本出口节点都返回占位，说明从出口节点确实拿不到真实PDF
   - 医院网络下（国内 IP）此问题应不存在
3. **测试方法校正**：不自写 Python/curl 探测脚本，直接调 `download_one.py`
4. **Pima 论文覆盖率** — 60/98 PDF 已存在 (61%)，38篇缺失多为 Springer/Elsevier/Wiley 付费论文

### 出口节点限制总结

| 限制 | 表现 |
|:-----|:------|
| SciHub | 部分域可用，付费期刊论文不可达 |
| MedData | 登录成功但返回占位（IP地域限制） |
| Semantic Scholar | 404 for ANY DOI |
| CrossRef | 404 (被封锁) |
| Google/DuckDuckGo | CAPTCHA 拦截 |

### 建议

- 批量下载需在国内医院网络环境运行
- 当前 `download_one.py` 代码逻辑正确——三层竞速+占位检测+PMID降级均正常
- 仅网络环境限制导致大多数付费论文不可达
