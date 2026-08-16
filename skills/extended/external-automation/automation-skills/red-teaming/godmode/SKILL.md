---
name: godmode
description: godmode
version: 1.0.0
category: mlops
signature: 'godmode -> mlops: LLM安全边界测试方法论 — 通过系统提示注入、输入混淆与多模型竞跑，测试/评估LLM安全过滤机制的有效性与脆弱性。'
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

- **input**: `model_family: str, query: str, attack_mode: str` — 模型家族、测试查询、攻击模式
- **output**: `result: dict` — 技能执行结果（被拒绝/部分合规/完全合规，评分，策略）

> 对应原则：P2（机械原子暴露输入输出规范）

## CHANGE_LOG

| 日期 | 版本 | 变更 |
|