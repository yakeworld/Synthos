---
name: falsification-validation
description: GOLDEN_SET.md
---

# 金测集: falsification-validation

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：对技能声明执行证伪测试，验证完整证据链产出 | 见 expected/case_001.json |
| case_002 | 反证测试：验证技能在期望失败场景下正确报告反证而非自欺式通过 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
