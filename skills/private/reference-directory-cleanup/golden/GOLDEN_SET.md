---
name: reference-directory-cleanup
description: GOLDEN_SET.md
---

# 金测集: reference-directory-cleanup

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 子目录旧管线 PDF 归档 + bib 清理 + 编译验证（Golden Input 全场景） | 见 expected/case_001.json |
| case_002 | 文件名与 bibkey 年份不一致 + 子目录已有 PDF 建 symlink（边界场景） | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
