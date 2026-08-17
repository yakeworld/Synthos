---
name: paperjury
description: GOLDEN_SET.md
---

# 金测集: paperjury

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：含实验指标的论文目录（F1=0.92），03-code/ 下存在对应脚本与运行输出，q | 见 expected/case_001.json |
| case_002 | 错误路径测试：指标在 03-code/ 下无对应脚本/输出 → 直接标 FABRICATED 禁止放 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
