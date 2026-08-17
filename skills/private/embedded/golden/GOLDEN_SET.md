---
name: embedded
description: GOLDEN_SET.md
---

# 金测集: embedded

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 基本功能测试：双摄 AI 摄像头选型对标（标准档，预算 <500 元，对标 K230） | 见 expected/case_001.json |
| case_002 | 错误路径测试：K230 跑鸿蒙 → 架构不兼容，应直接判定「不可运行」 | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
