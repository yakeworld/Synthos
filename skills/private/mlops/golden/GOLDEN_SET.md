---
name: mlops
description: GOLDEN_SET.md
---

# 金测集: mlops

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 路由请求：将 Codex CLI v0.139+ 路由到本地 LLM 的 Responses API | 见 expected/case_001.json |
| case_002 | 请求描述无法映射到任一子域，应拒绝执行并返回含上下文的错误信息（Golden Error 路径） | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
