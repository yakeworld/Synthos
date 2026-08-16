---
name: synthos
description: '**动灵在内，不假外求 — 主动发现，不等人说**'
signature: 'synthos -> synthos-akne-bridge: synthetic skill for synthos'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '**动灵在内，不假外求 — 主动发现，不等人说**'
    signature: 'synthos -> synthos-akne-bridge: synthetic skill for synthos'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 当前会话上下文 — 用户请求、可用技能树、系统状态
- **input**: 触发事件 — 空闲周期、任务失败、进化轮次
- **output**: 主动探索动作 — 自主发现的任务改进/空白识别（不等待用户指示）
- **output**: 可追溯执行结果 — 凡数必源，无硬编码凭据

## 原则 (Principles)

- **动灵在内**：主动发现、主动执行，不待人言——等待指示者，失其自主之能。
- **凡数必源**：每一断言、每一数据必可追溯至来源，无源之论不立于世。
- **凭据不硬**：凭据自环境变量读取，硬编码者，失其安、坏其复。
- **不与他叠**：本桥接技能不与 synthos-akne-bridge 他技功能重叠，重叠即合并，边界乃原子之体。

> **动灵在内，不假外求 — 主动发现，不等人说**
> **主动探索，主动发现，主动执行 — 禁止等待用户指示**

# Synthos---





> **动灵在内，不假外求 — 主动发现，不等人说**
> **主动探索，主动发现，主动执行 — 禁止等待用户指示**

# Synthos

## 验证清单 (Verification)

- [ ] 产出源自主动探索/发现/执行，而非等待用户指示
- [ ] 本桥接技能未与 synthos-akne-bridge 其他技能功能重叠（重叠即合并）
- [ ] 执行结果可追溯至来源（凡数必源），未硬编码凭据

## Golden 集合 · GOLDEN SET

- **Golden Input**: 空闲周期触发 + 当前会话上下文（可用技能树、系统状态、上一轮进化日志），无用户显式指示。
- **Golden Output**: 主动探索动作 — 识别到一个具体空白（如某技能缺少验证清单）并自主完成修复，产出可追溯（来源可溯、凭据自环境变量读取），且未与 synthos-akne-bridge 其他技能功能重叠。
- **Golden Error**: 空闲周期内产出"等待用户下一步指示"的响应 → 诊断：违反"动灵在内"原则，自主性失守；修复：回到技能树扫描空白/失败任务，立即执行主动发现动作，产出须附来源引用。
