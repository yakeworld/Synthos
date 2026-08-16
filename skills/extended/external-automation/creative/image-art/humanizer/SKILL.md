---
name: humanizer
description: humanizer
version: 1.0.0
category: creative
signature: 'humanizer -> creative: AI文本检测规避方法论 — 识别并消除AI生成文本的29种模式特征，注入人类写作个性与声音，使文本听起来自然、有观点、有灵魂。'
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

- **input**: `text: str, target_tone: str` — 待处理文本、目标语调
- **output**: `humanized_text: str` — 人性化改写文本

> 对应原则：P2（机械原子暴露输入输出规范）

## CHANGE_LOG

| 日期 | 版本 | 变更 |
|