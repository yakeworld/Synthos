# Golden Set — gif-search

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 技能核心：通过 Tenor API（`https://tenor.googleapis.com/v2/search`）搜索/下载 GIF。
> 本集合覆盖：正常路径（搜索并提取 URL，含 URL 编码规则）与错误路径（API key 缺失 → 401/403）。

## 测试用例表

| Case | 类型 | 输入摘要 | 预期 |
|------|------|----------|------|
| case_001 | 正常路径 · 搜索 + 提取 | `q="thumbs up"`, `limit=5`，含空格的查询词 | 请求 URL 中空格编码为 `+`（`q=thumbs+up`）；返回 JSON 含 `.results`（≤ limit 条）；`jq -r '.results[].media_formats.gif.url'` 与 `tinygif.url` 非空且可访问 |
| case_002 | 错误路径 · 无 API key | `TENOR_API_KEY` 未设置 / 无效 | API 返回 401/403（`status: 401`），不进入 jq 提取；错误信息含上下文与恢复建议（设置 `TENOR_API_KEY`，从 https://developers.google.com/tenor/guides/quickstart 获取） |

## 通过标准

- **case_001**
  - [ ] 构造的 URL 为 `https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}`（空格→`+`，GIF-002）
  - [ ] `limit` 在 1-50 范围内
  - [ ] 响应 `.results` 为非空数组且长度 ≤ limit
  - [ ] 每条结果含 `media_formats.gif.url` 与 `media_formats.tinygif.url`，均为非空字符串
  - [ ] 聊天/Markdown 场景优先使用 `tinygif` URL 或 `![alt](url)` 直接嵌入（GIF-001 / GIF-006）
- **case_002**
  - [ ] HTTP 状态码为 401 或 403
  - [ ] 不产生本地 GIF 文件，不抛出未捕获异常
  - [ ] 错误信息包含上下文（缺失/无效的 key、请求端点）与恢复建议（设置 `TENOR_API_KEY` 环境变量）

## 复现命令

```bash
export TENOR_API_KEY=...  # 从 Google Cloud Console / Tenor quickstart 获取
# case_001
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
# case_002
unset TENOR_API_KEY
curl -s -o /dev/null -w "%{http_code}" "https://tenor.googleapis.com/v2/search?q=cat&limit=1"   # 期望 400/401
```

> 注：正常路径依赖外部 Tenor API 与有效 `TENOR_API_KEY`；expected 中的 URL/字段结构为 API 契约级断言，
> 具体返回条目的 id/title 不纳入精确匹配（外部服务会变化，凡数必源：以实测为准）。
