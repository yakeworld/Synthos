---
name: golden-test-methodology
description: GOLDEN_SET.md
---

# 金测集: golden-test-methodology

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：对技能清单执行 golden 覆盖率统计，验证三要素（GOLDEN_SET.md +  | 见 expected/case_001.json |
| case_002 | 方法论验证：检查 golden 创建规范（cases 与 expected 一一配对、权重区分度、命 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
