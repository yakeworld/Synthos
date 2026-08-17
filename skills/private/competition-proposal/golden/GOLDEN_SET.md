---
name: competition-proposal
description: GOLDEN_SET.md
---

# 金测集: competition-proposal

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：四段式叙事申报书填充，含去技化转换与模板清理 | 见 expected/case_001.json |
| case_002 | 错误路径测试：模板行数不足或赛道必填字段不满足时，应报错而非静默截断 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
