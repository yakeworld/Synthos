---
name: notion
description: notion 金测集 — Notion API (curl) 页面/数据库/块操作的可执行测试
---

# 金测集: notion

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (NOTI-001~007) + IO_CONTRACT。
> 核心能力：通过 curl 调用 Notion API（version 2025-09-03）管理页面、数据库
> （2025-09-03 起称 data sources）、块与搜索。
> IO_CONTRACT: input `action: str, params: dict` → output `result: dict`。
> 每个 case 验证请求头/双 ID 区分/属性结构与错误处理（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：在数据库中创建页面 | `POST /v1/pages` 用 `database_id` 作 parent（NOTI-002）；属性结构符合类型规范（Title 嵌套 `text.content`、Select 用 `name`，NOTI-005）；请求头完整（NOTI-001） |
| case_002 | 正常：查询数据库（data_source_id） | `POST /v1/data_sources/{id}/query`（NOTI-004）；filter+sorts 结构正确；响应经 `jq` 解析 `.results[0].properties`（NOTI-006） |
| case_003 | 错误路径：未共享 Integration 的 404/permission 错误 | 响应含明确原因（NOTI-003）；错误信息含上下文+恢复建议（UI 共享步骤），不重试轰炸（频率 ≤3 req/s，NOTI-007） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 创建页面 parent 必须为 `{"database_id": "..."}`（非 data_source_id，NOTI-002）；Title 属性为 `{"title": [{"text": {"content": "..."}}]}`、Select 为 `{"select": {"name": "..."}}`（NOTI-005）；请求带 `Notion-Version: 2025-09-03` 与 Bearer `$NOTION_API_KEY`（key 来自 `~/.hermes/.env`，`ntn_`/`secret_` 前缀，未硬编码）
- case_002: 查询端点必须为 `/v1/data_sources/{data_source_id}/query`（NOTI-004，不得混用 database_id）；filter 结构与属性类型匹配；响应经 `jq` 校验 `.results[0].properties` 存在且字段稳定
- case_003: 404/object_not_found/403 响应必须解析出 `code`+`message`，错误输出含上下文（哪个 ID、哪个端点）与恢复建议（Notion UI: "..." → "Connect to" → 选择 Integration）；未对同一 404 连续重试（≤3 req/s，NOTI-007）
- 所有 case: key 仅从环境变量读取（凭据管理铁律）；curl 带 `-s` 且管道 `jq`（NOTI-006）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 请求（method/endpoint/headers/body）/ 响应结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- endpoint/headers 精确匹配，ID 与属性值可不同，但结构必须一致
- 响应必须是 JSON dict，键名稳定（`object`, `id`, `properties` 等）
- 错误路径必须同时含 `error` 上下文与 `recovery` 建议两个字段（异常约束）

## 关联

- SKILL.md Genes: NOTI-001~007
- SKILL.md 验证清单: 6 项（env key / Notion-Version 头 / UI 共享 / 双 ID 区分 / 属性结构+频率 / jq 解析）
- 相关技能: airtable, google-workspace, linear（同类外部自动化）
