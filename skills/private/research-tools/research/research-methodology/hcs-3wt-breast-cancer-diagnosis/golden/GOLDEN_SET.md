---
name: hcs-3wt-b
description: GOLDEN_SET.md
---

# 金测集: hcs-3wt-b

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | WDBC 10x5 stratified CV — full HCS-3WT pipeline on | 见 expected/case_001.json |
| case_002 | PIMA diabetes low-separability dataset — threshold | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
