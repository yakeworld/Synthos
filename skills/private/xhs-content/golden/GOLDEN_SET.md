---
name: xhs-content
description: GOLDEN_SET.md
---

# 金测集: xhs-content

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | Generate XHS post package for 'Linux 环境排障三步法' with | 见 expected/case_001.json |
| case_002 | Generate XHS post with mixed figures (Pillow cards | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
