---
name: synthos-io-contract
description: I/O contract for synthos
---

# I/O Contract: synthos

> 自主进化科研教学认知操作系统 — 6认知原子 × 3元组件完整Research Pipeline。

## Input

`task: str — 科研任务描述`

## Output

`results: dict — 包含中间产物、质量评分、下一步建议`

## Example

```
hermes skill synthos on research topic
```

## Constraints

- 输入必须合法且可执行
- 输出必须可解析
- 超出约束时返回明确错误信息
