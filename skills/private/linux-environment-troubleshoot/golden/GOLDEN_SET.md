---
name: linux-environment-troubleshoot
description: GOLDEN_SET.md
---

# 金测集: linux-environment-troubleshoot

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | MiKTeX 编译失败报 'No space left on device'：先查磁盘排除真满，再清 | 见 expected/case_001.json |
| case_002 | Python venv 隔离失效：pip 装包落入系统解释器，修正 pyvenv.cfg 并改用 v | 见 expected/case_002.json |
| case_003 | dpkg/apt 中断或锁死：dpkg --configure -a 修复 + 清除 /var/li | 见 expected/case_003.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
