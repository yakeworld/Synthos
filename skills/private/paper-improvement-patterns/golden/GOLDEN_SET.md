---
name: paper-improvement-patterns
description: GOLDEN_SET.md
---

# 金测集: paper-improvement-patterns

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：可编译论文（pdflatex 0 error），多组件方法，Discussion 缺  | 见 expected/case_001.json |
| case_002 | 错误路径测试：新增 bibitem 未被正文 \cite{} 引用（含 %% 注释行内引用），D10 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
