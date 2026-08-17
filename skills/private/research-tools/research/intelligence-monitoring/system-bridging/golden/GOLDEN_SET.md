---
name: system-bridging
description: GOLDEN_SET.md
---

# 金测集: system-bridging

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：两系统根目录已摸底，单向 A→B 桥接，幂等重跑 | 见 expected/case_001.json |
| case_002 | 异常测试：system_a_root 缺失 + 关键词匹配产生权重低于阈值/邻接超限的边 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
