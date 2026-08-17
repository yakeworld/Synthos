---
name: layer-index-optional
description: GOLDEN_SET.md
---

# 金测集: layer-index-optional

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试: 查询"生成科研图表"应命中 figure-generation 技能，并提示"结论- | 见 expected/case_001.json |
| case_002 | 边界/模糊意图测试: 空 query 或模糊意图 (只有工具无方向) 时，不异常中断，返回明确提示并 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
