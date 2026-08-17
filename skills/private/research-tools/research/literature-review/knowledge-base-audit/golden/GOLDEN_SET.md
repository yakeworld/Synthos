---
name: knowledge-base-audit
description: GOLDEN_SET.md
---

# 金测集: knowledge-base-audit

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：真实 NotebookLM 库状态，执行 P0/P1/P2 分级审计与修复 | 见 expected/case_001.json |
| case_002 | 异常测试：notebooklm list 返回未认证错误，但 profile 目录存有 148 co | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
