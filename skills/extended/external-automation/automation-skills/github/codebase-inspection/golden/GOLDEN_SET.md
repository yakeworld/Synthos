---
name: codebase-inspection
description: codebase-inspection 金测集 — 用 pygount 做 LOC/语言分布/代码注释比的可执行测试
---

# 金测集: codebase-inspection

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (CODE-001~007)。
> 本技能用 `pygount` 分析仓库的 LOC、语言分布、文件数、代码/注释比。
> IO_CONTRACT: input `request: str, context: dict` → output `result: dict`。
> 每个 case 验证一条真实可执行的操作契约（P1 可复现性）；错误路径必须返回结构化
> Golden Error（含 context + ≥2 条恢复建议），禁止仅返回通用错误。
>
> 数值诚实（P0 凡数必源）：expected 中的 code/comment 行数均**实际运行 pygount 得出**，
> 而非臆造；case 在受控 fixture 目录上执行以保证可复现（P1）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：Python 仓库整体规模概览（summary + --folders-to-skip） | 命令含 `--folders-to-skip` 排除 `.git,venv,__pycache__` 等（CODE-001）；`--format=summary` 输出 Language/Files/Code/Comment/%（CODE-002）；Markdown 计 0 代码行（预期，CODE-006）；无依赖目录被扫描（无挂起） |
| case_002 | 正常：仅统计 Python 文件（--suffix=py） | `--suffix=py` 定向过滤（CODE-003）；输出仅含 Python 行（及伪语言标签）；Code 行数与 `find . -name '*.py' \| xargs wc -l` 量级一致 |
| case_003 | 错误：目标目录不存在 | 命中输入约束 → 结构化 Golden Error（context + ≥2 recovery），不崩溃、不产出臆造统计 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 命令必须含 `--folders-to-skip` 且至少排除 `.git,node_modules,venv`（CODE-001）；
  `--format=summary` 汇总表含 Language/Files/Code/Comment 列（CODE-002）；Markdown 行 Code==0
  （预期行为，CODE-006）；fixture 内 Files 数与实际文件数一致，依赖目录未被扫描
- case_002: 命令含 `--suffix=py`（CODE-003）；输出仅含 Python 语言行（及伪语言标签）；
  汇总 Code 行数与独立 `wc -l` 校准量级一致（P0 凡数必源：数值可独立复算）
- case_003: 目标路径不存在时必须返回结构化 Golden Error —— 错误信息同时含 `context`
  （请求回声 + 失败路径 + 错误原因）与 ≥2 条可操作 `recovery`，且 `crashed=false`、
  未产出任何臆造 LOC 统计

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: summary 表 / suffix 过滤结果 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 正常路径命令必须含 `--folders-to-skip`（除非用 `--suffix` 定向过滤且目标目录无依赖）
- 正常路径 summary 必须含 `language / files / code / comment` 四要素
- Markdown 文件 code 必为 0（pygount 将 Markdown 全计为注释，预期行为）
- 错误路径必须同时含 `context` 与 `recovery` 两个字段，`ok=false`，无臆造数值
- 任何 LOC 数值都必须可由第二次独立运行复算（P0 凡数必源 + P1 可复现）

## 关联

- SKILL.md Genes: CODE-001~007
- SKILL.md 验证清单: 6 项（pygount 已装 / --folders-to-skip / summary 格式 / 按项目调整排除或 --suffix / 解读 Markdown=0 代码行 / 呈现清晰汇总）
- 关联技能: （无直接依赖）
