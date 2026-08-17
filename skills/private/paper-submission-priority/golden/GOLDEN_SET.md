---
name: paper-submission-priority
description: GOLDEN_SET.md
---

# 金测集: paper-submission-priority

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试: 扫描 outputs/papers/* 各论文 state.json (顶层 qua | 见 expected/case_001.json |
| case_002 | 引用健康异常测试: D10a=0 的论文 (concussion-oculomotor-PINN)  | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
