---
name: creative
description: creative 父级路由金测集 — 验证创意请求正确路由到子类别/子技能
---

# 金测集: creative

> 来源: SKILL.md Genes CREA-001~006 + 验证清单。每个 case 验证父级路由入口能否将创意请求正确分发到对应子类别/子技能（P1 可复现性）。
> 父级职责: 创意请求路由器，按媒介类型分发到 5 个子类别。

## 路由逻辑

| 请求特征 | 路由目标（子类别） | 依据 |
|----------|----------|------|
| 图表/架构图/信息图/学术图 | `diagrams/` | CREA-001: 按媒介路由 |
| 视频/动画/音乐/FFmpeg | `video-audio/` | CREA-001: 按媒介路由 |
| 素描/像素艺术/漫画/图像生成 | `image-art/` | CREA-001: 按媒介路由 |
| p5.js/网页/TouchDesigner/代码 | `web-code/` | CREA-001: 按媒介路由 |
| ComfyUI/论文转PPT/创意发散 | `tools/` | CREA-001: 按媒介路由 |
| 空请求/无效格式/未知子技能 | 拒绝 + 结构化错误 | CREA-005: 边界验证 + 恢复建议 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由: 学术图表请求 → diagrams/ | routed_to == 'diagrams', target_skill == 'academic-diagram' |
| case_002 | 错误路径: 空创意请求 | 返回 error, 含上下文与恢复建议, 不崩溃 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `routed_to` 必须为正确子类别，`target_skill` 精确匹配，`creative_request`/`style`/`output_format` 三参数非空校验通过
- case_002: 必须返回结构化错误（含 `error_type`、`context`、`recovery`），不得静默失败（CREA-005: 空输入时提供包含上下文和恢复建议的明确错误信息）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 关联

- SKILL.md Genes: CREA-001~006
- 子类别: diagrams/, video-audio/, image-art/, web-code/, tools/
- 验证清单: SKILL.md L63-68

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始金测集，2 个 case（正常路由 + 空请求错误路径） | Synthos Agent |
