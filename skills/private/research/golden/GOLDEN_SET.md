---
name: research
description: GOLDEN_SET.md
---

# 金测集: research

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 多方向文献监控：瞳孔追踪 + 眼动分析，近 3 个月，双源并行召回 | 见 expected/case_001.json |
| case_002 | Golden Error 场景：curl 被安全扫描拦截 + arXiv 宽泛查询噪声 → 回退与精 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
