---
name: citation-bib-crossref
description: Golden Set — 引用完整性审计测试集
---

# 金测集: citation-bib-crossref

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 每项验证必须可执行、可记录、可复现。

## 测试用例

| ID | 描述 | 关键检查 | 权重 |
|----|------|---------|------|
| 001 | 全健康正常路径：pima-crispdm 论文库（.tex + .bib，33 个 bib 条目）审计 | D8=33、D10a=100%，孤儿引用=0，僵尸条目=0，问题分级清单为空，健康 ✅（CITA-001） | critical |
| 002 | 重症错误路径：3d-eye-bppv-diagnosis 无 .bib 文件审计 | D8=0 重症（CITA-002），列出全部 62 个孤儿标签（Aw2013, Balatsouras2012, ...），D10a=0.0%，给出补齐 .bib 的恢复建议 | critical |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 001 验证：D8=33 且 D10a=100% 且孤儿=0 且僵尸=0（数必重算，以脚本实际输出为准）
- 002 验证：D8=0 且孤儿标签数=62 且分级=重症且含恢复建议（CITA-002/006）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 约束

1. 仅新增 golden/ 相关文件，不改 SKILL.md
2. 所有 JSON 必须有效（`python3 -c "import json; json.load(open(...))"` 验证）
3. 不 git commit
