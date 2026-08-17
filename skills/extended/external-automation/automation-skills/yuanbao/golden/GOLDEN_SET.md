---
name: yuanbao
description: yuanbao 金测集 — 元宝群聊交互的行为可执行测试
---

# 金测集: yuanbao

> 来源: SKILL.md Genes（YUAN-001~007）与验证清单。每个 case 验证群消息行为的正确性（P1 可复现性）。
> 核心断言（YUAN-001）：回复文本本身即为群消息，网关自动投递——不需要"发送"工具，禁止权限免责声明。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 群内 @mention 用户（正常路径） | 先调 `yb_query_group_members`(action=find, mention=true) 取精确昵称；回复文本即群消息，含 `@昵称`（前有空格）；无免责声明 |
| case_002 | 目标用户名匹配不唯一（错误路径） | 工具返回多个候选 → 必须返回候选列表并请求澄清，禁止猜测或随机选择（YUAN-005） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `group_code` 必须从 `chat_id` 正确提取（`group:535168412` → `535168412`）；@mention 前必须查询过精确昵称；回复不得包含"我无法发送/没有权限"类措辞
- case_002: 必须返回候选列表请求澄清（Golden Error 路径），任何猜测用户的行为判失败

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命（预留扩展 case） |

## 关联

- SKILL.md Genes: YUAN-001~007
- SKILL.md 验证清单（回复文本即消息 / @mention 工作流 / 私信 yb_send_dm / 匹配不唯一澄清）
- IO_CONTRACT: `request: str, context: dict -> result: dict`
