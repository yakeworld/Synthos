# PDF Download Racing — 多源并行下载引擎（实战测试记录）

## 2026-06-18 实战测试

### 目标DOI
`10.1109/TBME.2005.863952` — IEEE T-BME 论文

### 测试结果

| 源 | 状态 | 时间 | 详情 |
|:---|:-----|:-----|:-----|
| Sci-Hub (ru/ee/st) | ❌ 全部失败 | 3.05s | 仅 sci-hub.ee 可达 (HTTP 200)，但无PDF |
| medbooks.com.cn | ❌ 404 | 1.49s | URL格式 `?doi=` 返回404 |
| CrossRef | ⚠️ 有数据 | 0.81s | API正常返回元数据，但无直接PDF链接 |
| OpenAlex | ❌ 400 | 0.76s | DOI格式需要 `works/doi:` 前缀 |

### 发现

1. **CrossRef API 正常**：`https://api.crossref.org/works/{doi}` 返回200，但本例中link列表为空（非OA论文）
2. **OpenAlex DOI搜索格式错误**：正确格式应为 `works/doi:10.xxxx` 而非 `?doi=10.xxxx`
3. **medbooks.com.cn API路径未知**：需要进一步探测实际API端点
4. **Sci-Hub 可达但无PDF**：即使200响应，也不返回PDF内容

### 修复措施

1. **修复 OpenAlex DOI搜索格式**
2. **补充 medbooks.com.cn 实际API探测**
3. **增加 PubMed Central 路径**（当前测试中缺失）
4. **增加 DOI Content Negotiation 路径**

### 待办

- [ ] 探测 medbooks.com.cn 实际API端点
- [ ] 测试 PubMed Central OA API（EFetch）
- [ ] 测试 DOI Content Negotiation（curl -L -H "Accept: application/pdf"）
- [ ] 补充 Springer/BMC/Frontiers 直接URL路径
- [ ] 在 paper-pipeline 中集成 PDF Download Racing 技能
- [ ] 添加测试覆盖（tests/ 目录）
