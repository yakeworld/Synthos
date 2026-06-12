---
name: quality-gate
description: IO_CONTRACT — Skill quality-gate 输入输出契约
---

# 输入输出契约: quality-gate

## 输入
- 任务/需求描述
- 目标/预期输出

## 输出
- 对应工具操作的完整结果

## 契约验证
- 输入是否完整?
- 输出是否达到预期?

## 签名
```
"deliverable: str, quality_matrix: dict, target_level: str -> gate_result: GateResult, gaps: list[Gap]"
```
