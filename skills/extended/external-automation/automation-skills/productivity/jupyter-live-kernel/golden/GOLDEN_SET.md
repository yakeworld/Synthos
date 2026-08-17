---
name: jupyter-live-kernel
description: Jupyter Live Kernel (hamelnb) 金测集：覆盖跨 execute 状态持久化 + restart-run-all 验证（正常路径）与内核执行异常 ename/evalue 解析（错误路径）
---

# 金测集: jupyter-live-kernel

> 本集合是本技能验证的单一真理来源。所有改进必须通过 golden 测试。
> 用例文件位于 `cases/`，预期结果位于 `expected/`，同名对应（`case_XXX.json` ↔ `expected/case_XXX.json`）。

## 被测行为（来自 SKILL.md Genes）

- **JUPY-001** 需要跨步骤保持变量状态/迭代探索 → 使用 Live Kernel 替代无状态 execute_code。
- **JUPY-002** 所有脚本命令 → 始终带 `--compact` 标志，输出为可解析 JSON。
- **JUPY-006** 子命令参数顺序 → 全局标志 `--path` 位于子子命令之前（`variables --path nb.ipynb list`）。
- **JUPY-007** 执行出错 → 解析返回 JSON 的 `ename`/`evalue` 定位异常。
- **JUPY-003** 首次执行/内核重启后可能超时 → 重试一次而非立即报错。

## 测试用例

| ID | 文件 | 描述 | 关键检查 |
|----|------|------|---------|
| 1 | `cases/case_001.json` | 跨 execute 状态持久化 + variables list（正常路径） | 第二次 execute 无需重新 import；`variables list` 含 `df`；所有命令含 `--compact`；`--path` 位于子子命令之前 |
| 2 | `cases/case_002.json` | 内核执行 NameError + 首次超时重试（错误路径） | 返回 JSON 含 `ename == "NameError"` 与 `evalue`；首次超时后重试一次成功；解析错误字段定位根因 |

## 预期结果结构

- `expected/case_001.json`: 期望的 execute/variables 输出（compact JSON、变量列表、状态持久化证据）+ 逐项检查。
- `expected/case_002.json`: 期望的错误输出结构（ename/evalue、重试行为、最终成功状态）+ 逐项检查。

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
