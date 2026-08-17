---
name: prose-cluster-hybrid-citation-fix
description: GOLDEN_SET.md
---

# 金测集: prose-cluster-hybrid-citation-fix

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | Golden 正常路径：paper.tex 含 9 个未锚定 bibitem + 密集散文段落，IM | 见 expected/case_001.json |
| case_002 | Golden 失败路径：批量替换后验证脚本 Orphans > 0（存在未锚定 bibitem 键） | 见 expected/case_002.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
