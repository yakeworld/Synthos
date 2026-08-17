---
name: k230-development-lessons
description: GOLDEN_SET.md
---

# 金测集: k230-development-lessons

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | K230 自动化管理全链：Python 直调 ampy.pyboard.Pyboard 完成代码执行 | 见 expected/case_001.json |
| case_002 | GPIO 按键配置前固件/板型判定：RT-Smart vs CanMV FPIOA 策略 + os. | 见 expected/case_002.json |
| case_003 | 故障恢复决策：ampy run 失败改 Python 直调；串口完全无输出（sendBreak/Ct | 见 expected/case_003.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
