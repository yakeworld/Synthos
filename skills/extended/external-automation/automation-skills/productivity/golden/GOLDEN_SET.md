name: productivity
description: productivity 金测集 — 父级路由（10 个子技能）的可执行测试
---

# 金测集: productivity

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (PROD-001~008)。
> 本技能是 productivity 父级聚合入口（atom_type: parent-skill），仅作为目录索引；
> 子技能通过 Hermes 技能加载机制自动发现，实际执行由子技能完成，父级不硬编码逻辑（PROD-001）。
> 每个 case 验证路由决策的正确性（P1 可复现性）。

## 子技能清单（路由目标）

| # | 子技能 | 典型能力 |
|---|--------|---------|
| 1 | chinese-form-automation | 中文表单自动填写 |
| 2 | jupyter-live-kernel | Jupyter 活内核交互 |
| 3 | maps | 地图/地理查询 |
| 4 | markitdown-convert | 文档转 Markdown |
| 5 | notebooklm-cli | NotebookLM CLI 操作 |
| 6 | notion | Notion 页面/数据库 |
| 7 | obsidian | Obsidian 笔记管理 |
| 8 | powerpoint | PPT 生成 |
| 9 | webhook-subscriptions | Webhook 订阅管理 |
| 10 | youtube-content | YouTube 内容处理 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由：PPT 生成请求 | route=skill_view(name='powerpoint')；request/context 完整转交；父级不硬编码 |
| case_002 | 正常路由：文档转 Markdown 请求 | route=skill_view(name='markitdown-convert')；路由目标与能力匹配精确一致 |
| case_003 | 未知子技能（错误路径） | 请求能力不属于 10 个子技能任何一个 → 结构化错误：含上下文（哪个请求、哪些已知子技能）+ 恢复建议（PROD-006） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 路由目标必须精确为 `powerpoint`，父级仅作索引（PROD-001），无父级吞并参数（PROD-002）
- case_002: 路由目标必须精确为 `markitdown-convert`，能力→子技能映射无歧义
- case_003: 必须拒绝并返回 Golden Error 路径 —— 错误信息含"请求回声 + 10 个已知子技能清单 + ≥2 条恢复建议"，禁止仅返回通用错误（PROD-006）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 路由结果 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 路由目标子技能名必须精确匹配（10 选 1，无歧义）
- 错误路径必须同时含 context 与 recovery 两个字段
- 空输入/异常场景不崩溃（PROD-005）

## 关联

- SKILL.md Genes: PROD-001~008
- SKILL.md 验证清单: 6 项（路由正确 / 输入校验 / 中间步骤 / 输出契约 / 边界处理 / 失败指引）
- 子技能: chinese-form-automation, jupyter-live-kernel, maps, markitdown-convert, notebooklm-cli, notion, obsidian, powerpoint, webhook-subscriptions, youtube-content
