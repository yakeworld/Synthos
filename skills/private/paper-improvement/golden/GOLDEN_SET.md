---
name: paper-improvement
description: GOLDEN_SET.md
---

# 金测集: paper-improvement

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：完整论文目录，含 3 条假 DOI、实验模型清单偏差项（LightGBM/CatBoo | 见 expected/case_001.json |
| case_002 | 失败路径测试：输入不完整（缺 PDF），PAPE-001 必须立即阻断；另含 LaTeX 替换失败触 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
