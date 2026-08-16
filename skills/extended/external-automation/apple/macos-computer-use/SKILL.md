---
name: macos-computer-use
description: macos-computer-use
version: 1.0.0
category: apple
signature: 'macos-computer-use -> apple: You have a `computer_use` tool that drives
  the Mac in the **background**.'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills:
    - apple
    - findmy
    - imessage
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

- **input**: `task: str, app: str` — 用户请求描述、上下文信息
- **output**: `result: dict — macOS操作结果`

> 对应原则：P2（机械原子暴露输入输出规范）

# macOS Computer Use (universal, any-model)

You have a `computer_use` tool that drives the Mac in the **background**.
Your actions do NOT move the user's cursor, steal keyboard focus, or switch
Spaces. The user can keep typing in their editor while you click around in
Safari in another Space. This is the opposite of pyautogui-style automation.

Everything here works with any tool-capable model — Claude, GPT, Gemini, or
an open model running through a local OpenAI-compatible endpoint. There is
no Anthropic-native schema to learn.

## The canonical workflow

**Step 1 — Capture first.** Almost every task starts with:

```
computer_use(action="capture", mode="som", app="Safari")
```

Returns a screenshot with numbered overlays on every interactable element
AND an AX-tree index like:

```
#1  AXButton 'Back' @ (12, 80, 28, 28) [Safari]
#2  AXTextField 'Address and Search' @ (80, 80, 900, 32) [Safari]
#7  AXLink 'Sign In' @ (900, 420, 80, 24) [Safari]
...
```

**Step 2 — Click by element index.** This is the single most important
habit:

```
computer_use(action="click", element=7)
```

Much more reliable than pixel coordinates for every model. Claude was
trained on both; other models are often only reliable with indices.

**Step 3 — Verify.** After any state-changing action, re-capture. You can
save a round-trip by asking for the post-action capture inline:

```
computer_use(action="click", element=7, capture_after=True)
```

## Capture modes

| `mode` | Returns | Best for |
|