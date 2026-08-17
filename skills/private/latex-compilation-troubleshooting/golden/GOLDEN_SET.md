---
name: latex-compilation-troubleshooting
description: GOLDEN_SET.md
---

# 金测集: latex-compilation-troubleshooting

## 测试用例
| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 外部 references.bib 论文首次编译后出现 natbib Citation undefi | 见 expected/case_001.json |
| case_002 | bibtex 报 'I found no ibstyle command'（paper.bbl  | 见 expected/case_002.json |
| case_003 | BibTeX 报 'didn't find a database entry for X' 但条目存 | 见 expected/case_003.json |
## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
