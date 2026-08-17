---
name: pidd-leakage-audit
description: GOLDEN_SET.md
---

# 金测集: pidd-leakage-audit

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 折内预处理：PIDD 数据集上在数据分割前执行 SMOTE 的 10-fold CV 脚本（泄漏路径 | 见 expected/case_001.json |
| case_002 | SHAP 可解释性分析 + CRISP-DM 引用规范：在系统 Python 为 Debian nu | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
