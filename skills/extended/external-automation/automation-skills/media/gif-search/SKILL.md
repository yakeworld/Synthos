---
name: gif-search
description: gif-search
version: 1.0.0
category: creative
signature: 'gif-search -> creative: Search and download GIFs directly via the Tenor
  API using curl. No extra tools n'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# GIF Search (Tenor API)

Search and download GIFs directly via the Tenor API using curl. No extra tools needed.

## When to use

Useful for finding reaction GIFs, creating visual content, and sending GIFs in chat.

## Setup

Set your Tenor API key in your environment (add to `~/.hermes/.env`):

```bash
TENOR_API_KEY=your_key_here
```

Get a free API key at https://developers.google.com/tenor/guides/quickstart — the Google Cloud Console Tenor API key is free and has generous rate limits.

## Prerequisites

- `curl` and `jq` (both standard on macOS/Linux)
- `TENOR_API_KEY` environment variable

## Search for GIFs

```bash
# Search and get GIF URLs
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# Get smaller/preview versions
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

## Download a GIF

```bash
# Search and download the top result
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

## Get Full Metadata

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | jq '.results[] | {title: .title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url, dimensions: .media_formats.gif.dims}'
```

## API Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `key` | API key (from `$TENOR_API_KEY` env var) |
| `media_filter` | Filter formats: `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |
| `locale` | Language: `en_US`, `es`, `fr`, etc. |

## Available Media Formats

Each result has multiple formats under `.media_formats`:

| Format | Use case |
|--------|----------|
| `gif` | Full quality GIF |
| `tinygif` | Small preview GIF |
| `mp4` | Video version (smaller file size) |
| `tinymp4` | Small preview video |
| `webm` | WebM video |
| `nanogif` | Tiny thumbnail |

## Notes

- URL-encode the query: spaces as `+`, special chars as `%XX`
- For sending in chat, `tinygif` URLs are lighter weight
- GIF URLs can be used directly in markdown: `![alt](url)`

## 验证清单 · VERIFICATION

- [ ] `TENOR_API_KEY` 环境变量已设置且有效，curl 请求未返回 401/403
- [ ] 查询词已正确 URL 编码（空格→`+`，特殊字符→`%XX`），API 正常返回 `.results`
- [ ] `limit` 参数在 1-50 范围内，按需设置了 `contentfilter` 安全级别
- [ ] jq 提取的 URL 字段（`media_formats.gif.url` / `tinygif.url`）非空且可访问
- [ ] 下载后本地 GIF 文件存在且非零字节，可正常打开
- [ ] 聊天/Markdown 场景使用了轻量 `tinygif` 格式或 URL 直接嵌入 `![alt](url)`

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Gif Search

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[GIF-001]** 需要获取轻量级预览或聊天场景下的 GIF → 优先使用 `tinygif` 或 `nanogif` 格式以减小文件体积
- **[GIF-002]** 执行 Tenor API 搜索请求 → 必须将查询词中的空格编码为 `+` 并对特殊字符进行 URL 编码
- **[GIF-003]** 需要下载特定 GIF 文件到本地 → 先通过 API 获取 `media_formats.gif.url`，再使用 `curl -sL` 下载该 URL
- **[GIF-004]** 需要获取 GIF 的完整元数据（标题、尺寸等） → 使用 `jq` 提取 `.results[]` 中的 `title`、`url` 及 `dims` 字段
- **[GIF-005]** 需要控制搜索结果的数量或内容安全级别 → 在 API 请求中显式设置 `limit` (1-50) 和 `contentfilter` 参数
- **[GIF-006]** 需要在 Markdown 中直接引用 GIF → 直接使用 API 返回的 GIF URL 嵌入 `![alt](url)` 语法，无需本地下载
