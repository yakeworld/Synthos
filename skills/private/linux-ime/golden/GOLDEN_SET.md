---
name: linux-ime
description: GOLDEN_SET.md
---

# 金测集: linux-ime

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | Ubuntu + fcitx5 环境，fcitx5 已安装且 daemon 运行，但 GTK3 应用 | 见 expected/case_001.json |
| case_002 | Snap 版 Firefox 硬编码 ibus，环境变量修复无效（Golden Error 路径） | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
