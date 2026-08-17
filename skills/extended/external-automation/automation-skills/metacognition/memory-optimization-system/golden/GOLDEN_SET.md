---
name: memory-optimization-system
description: 记忆系统优化的金测集：覆盖上下文卸载、FSRS 健康评估、记忆空间铁律分级清理的语义化用例
---

# 金测集: memory-optimization-system

> 本集合是本技能验证的单一真理来源。所有改进必须通过 golden 测试。
> 用例文件位于 `cases/`，预期结果位于 `expected/`，同名对应（`case_XXX.json` ↔ `expected/case_XXX.json`）。

## 被测行为（来自 SKILL.md Genes）

- **MEMO-001** 工具输出超过 10KB 或 50 行 → 保存原文至 `~/.hermes/context_refs/{hash}.md`，回复仅保留 Mermaid 摘要 + 引用路径（L1）；>50KB → L2 只保存。
- **MEMO-002 / FSRS 评估** `R = 1/(1 + age_days/(9*2.5))`；`access_count==0 且 age>14天` → 可移除；`R<0.3` → 低可检索；`R>0.7 且 access>=2` → 健康；其余 → 正常。
- **MEMO-003 空间铁律** memory 空间 >85% → 主动清理；>90% → 清理+压缩；>95% → 强制压缩至 <70%。

## 测试用例

| ID | 文件 | 描述 | 关键检查 |
|----|------|------|---------|
| 1 | `cases/case_001.json` | 长工具输出 L1 卸载（正常路径） | 45KB 输出触发 L1：`offload.level == "L1"`，`context_refs` 含 1 个 hash 路径，回复只含摘要不含原文 |
| 2 | `cases/case_002.json` | FSRS 低可检索 + 空间 92%（错误/异常路径） | 3 个记忆条目分级为「低可检索 / 正常 / 健康」；空间 92% 触发「清理+压缩」，`after.space_pct < 90`；`access=0 且 age>14` 条目判「可移除」 |

## 预期结果结构

- `expected/case_001.json`: 期望的 `optimization_report`（offload 级别、context_refs、mermaid_summary 存在性、上下文字节数下降）。
- `expected/case_002.json`: 期望的逐条目 FSRS 分级映射 + 铁律动作（tier、action、after 空间区间）+ 可移除条目列表。

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 每个 case 的 JSON 均可被 `python3 -c "import json,sys; json.load(open(sys.argv[1]))"` 解析

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
