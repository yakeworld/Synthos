---
name: skill-absorption
description: GOLDEN_SET.md
---

# 金测集: skill-absorption

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：GitHub Topics 扫描命中吸收目标，执行五层吸收并落盘三层记录 | 见 expected/case_001.json |
| case_002 | 异常/安全测试：输入含未验证可执行代码片段，且台账状态发生非法跳转（tracking 直接到 abs | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
