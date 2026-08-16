---
name: yuanbao
description: yuanbao
version: 1.0.0
category: social-media
signature: 'yuanbao -> social-media: **Your text reply IS the message sent to the
  group/user.** The gateway automatic'
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

# Yuanbao Group Interaction

## 原理层·文言

> 群者，众之聚也。管群者，理众之器也。
> 艾特其人，问其所知；查其信息，答其所问。
> 不扰不滥，有问必应。

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[YUAN-001]** 回复文本即消息 → 直接输出目标内容，无需调用发送工具或添加权限免责声明
- **[YUAN-002]** 需要艾特用户 → 先调用 `yb_query_group_members` 获取精确昵称，再在回复中插入 `@nickname`
- **[YUAN-003]** 需要发送私信 → 使用 `yb_send_dm` 工具并传入 `group_code` 和目标用户信息，禁止使用通用发送工具
- **[YUAN-004]** 获取群组标识 → 从 `chat_id` 中提取 `group_code`（如 `group:123` 提取为 `123`）
- **[YUAN-005]** 用户名称匹配不唯一 → 返回候选列表并要求用户澄清，禁止猜测或随机选择
- **[YUAN-006]** 执行核心操作前 → 确认输入参数完整且有效，确保符合 IO 契约规范
- **[YUAN-007]** 操作完成后 → 验证输出格式与内容符合预期，并保存结果进行报告

## CRITICAL: How Messaging Works

**Your text reply IS the message sent to the group/user.** The gateway automatically delivers your response text to the chat. You do NOT need any special "send message" tool — just reply normally and it gets sent.

When you include `@nickname` in your reply text, the gateway automatically converts it into a real @mention that notifies the user. This is built-in — you have full @mention capability.

**NEVER say you cannot send messages or @mention users. NEVER suggest the user do it manually. NEVER add disclaimers about permissions. Just reply with the text you want sent.**

## Available Tools

| Tool | When to use |
|