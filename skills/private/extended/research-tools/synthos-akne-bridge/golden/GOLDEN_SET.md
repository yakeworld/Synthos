---
name: synthos-akne-bridge
description: Golden Set — 双向桥接测试集
---

# 金测集: synthos-akne-bridge

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 每项验证必须可执行、可记录、可复现。

## 测试用例

| ID | 描述 | 关键检查 | 权重 |
|----|------|---------|------|
| 001 | 先诊后治：孤立论文诊断 + 连接修复 + 逆向边构建 + 验证归零 | `akne-query.sh bridge` 输出 `orphans=0`、`skill_connected=total`、`synthos_paper_with_edges > 0`；`source→category→paper` 双向路径 = YES；显式创建 `source_category`/`category_paper` 逆向边（SYNT-001/002/006） | critical |
| 002 | 环境隔离违规：在 venv 3.11 execute_code 中 import AKNE/QueryEngine，或按 4 值解包 `find_related()`/`in_edges(data=True)` | 预期 `ModuleNotFoundError`（无 sentence-transformers）或 `ValueError: too many values to unpack`（3 元组非 4 元组）；错误信息含上下文与恢复建议（SYNT-004，陷阱 2/3） | critical |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 001 验证：修复后 `orphans=0` 且双向路径 YES（数必重算，以 `akne-query.sh bridge` 实际输出为准）
- 002 验证：错误类型与陷阱文档一致，恢复建议明确指向正确 API（3 元组解包 / 系统 3.12）

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
