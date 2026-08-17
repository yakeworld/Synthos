---
name: dataset-discovery
description: Golden Set — 数据集发现测试集
---

# 金测集: dataset-discovery

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 每项验证必须可执行、可记录、可复现。

## 测试用例

| ID | 描述 | 关键检查 | 权重 |
|----|------|---------|------|
| 001 | OpenML 分页检索正常路径：医学关键词 "breast cancer" + `limit=50, offset=0` | JSON 无截断（无 `limit>200`）；从 `data.dataset` 数组按 `did` 提取候选（DATA-006）；质量指标以 `float()` 转换（DATA-002）；使用 `/api/v1/json/data/list/` 端点（DATA-004）；与 `outputs/papers/` 交叉去重 | critical |
| 002 | UCI stroke 全源 404 错误路径：数据源俱失效时合成数据集备案 | 按 DATA-005 报错提示数据源不可用；`random.seed(42)` 固定种子生成合成数据集（12 特征, 5179 行）；明示合成身份；镜像验证以 `head -1` 首行内容为准（DATA-003），不凭 HTTP 200 | critical |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 001 验证：响应 JSON 完整可解析、`data.dataset` 提取正确、指标为 float 类型、无 `limit>200` 请求
- 002 验证：合成数据可复现（固定种子 42）、schema 匹配（12 特征×5179 行）、文档明示合成身份

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
