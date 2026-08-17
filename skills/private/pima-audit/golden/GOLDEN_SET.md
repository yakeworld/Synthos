---
name: pima-audit
description: GOLDEN_SET.md
---

# 金测集: pima-audit

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常审计路径：PIDD 泄漏审计目录（独立 .py 脚本、实验条件固定、文献库含 accuracy> | 见 expected/case_001.json |
| case_002 | 失败路径覆盖：跨数据集审计实验条件不一致 + 无输出 Notebook + Pima/HCS-3WT | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
