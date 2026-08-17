---
name: paper-experiment-audit
description: GOLDEN_SET.md
---

# 金测集: paper-experiment-audit

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 含 WDBC 实验的 LaTeX 论文目录——thebibliography 与 reference | 见 expected/case_001.json |
| case_002 | 跨版本对比（699 vs 569）或消融复现差值 >0.5% 时，输出 MISMATCH 标记并阻断 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
