---
name: codebase-inspection
description: codebase-inspection
version: 1.0.0
category: mlops
signature: 'codebase-inspection -> mlops: Analyze repositories for lines of code,
  language breakdown, file counts, and cod'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告
## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# Codebase Inspection with pygount

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

## When This Skill Triggers

This skill is activated when the user asks you to:
- Count lines of code (LOC) in a project or repository
- Provide a language breakdown of a codebase
- Analyze codebase size, composition, or structure
- Get code-vs-comment ratios
- Answer "how big is this repo" type questions
- Understand the tech stack composition of a project

## When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.

## Verification Checklist

Before considering the codebase inspection task complete:

- [ ] pygount installed (or installation attempted)
- [ ] Appropriate `--folders-to-skip` used to exclude dependency/build directories
- [ ] Ran pygount with summary format to get language breakdown
- [ ] Reviewed results: language names, file counts, code lines, comment lines, percentages
- [ ] If specific language analysis needed: used `--suffix` filter
- [ ] Results interpreted correctly (Markdown = 0 code lines is expected)
- [ ] Presented clear summary to user with actionable insights

## 验证清单 · VERIFICATION

- [ ] `pygount` 已安装（`pip install --break-system-packages pygount 2>/dev/null || pip install pygount` 执行成功或已存在）
- [ ] 命令包含 `--folders-to-skip`，至少排除 `.git,node_modules,venv` 等依赖/构建目录，防止扫描挂起
- [ ] 使用 `--format=summary` 运行 pygount，获得语言分布、文件数、代码/注释行数汇总表
- [ ] 按项目类型调整 `--folders-to-skip`（Python / JS-TS / 通用 catch-all）或按需用 `--suffix` 定向过滤语言
- [ ] 结果解读符合预期：Markdown 计 0 代码行、JSON 计数保守（必要时用 `wc -l` 校准）
- [ ] 向用户呈现清晰的汇总（语言、文件数、代码行、注释行、百分比）并给出可操作的洞察

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Codebase Inspection

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[CODE-001]** 执行代码库扫描前 → 必须使用 `--folders-to-skip` 排除 `.git`、`node_modules`、`venv` 等依赖及构建目录，防止扫描挂起或耗时过长
- **[CODE-002]** 需要获取整体代码规模概览 → 优先使用 `--format=summary` 格式输出，以获取语言分布、文件数及代码/注释行数的汇总表格
- **[CODE-003]** 仅需分析特定技术栈或语言 → 使用 `--suffix` 参数指定文件扩展名（如 `py`, `yaml`），以过滤无关文件并提升扫描效率
- **[CODE-004]** 面对大型 Monorepo 或超大规模仓库 → 避免全量扫描，应结合 `--suffix` 定向扫描特定语言，或分模块执行以控制资源消耗
- **[CODE-005]** 需要程序化处理或集成到自动化流程 → 使用 `--format=json` 输出结构化数据，以便后续脚本解析和计算
- **[CODE-006]** 解读 Markdown 或 JSON 文件的代码行数时 → 需知悉 pygount 将 Markdown 全计为注释（0 代码行）且对 JSON 计数保守，必要时用 `wc -l` 辅助校准
- **[CODE-007]** 需要识别代码库中的冗余或异常文件 → 关注输出中的伪语言标签（如 `__duplicate__` 重复文件、`__generated__` 生成文件、`__binary__` 二进制文件）以评估代码健康度

## 示例 · EXAMPLES

### Example 1 — Python 仓库整体规模概览
- **输入**: "这个 repo 有多大？"，工作目录 `/path/to/repo`
- **操作**: `pygount --format=summary --folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache" .`
- **输出**: 汇总表（Language / Files / Code / Comment / %），含 Python 等语言分布
- **验证**: 各语言 Files 数与实际文件数一致；无 node_modules/venv 被扫描（无挂起）；Markdown 显示 0 代码行（预期行为）

### Example 2 — 仅统计 Python 文件
- **输入**: "只数 .py 文件的行数"
- **操作**: `pygount --suffix=py --format=summary .`
- **输出**: 仅 Python 语言的 Files / Code / Comment 统计
- **验证**: 输出仅含 `Python` 行（及可能的伪语言标签）；Code 行数与 `find . -name '*.py' | xargs wc -l` 量级一致

### Example 3 — JSON 输出供程序化集成
- **输入**: 自动化流程需结构化代码规模数据
- **操作**: `pygount --format=json --folders-to-skip=".git,node_modules,venv" .`
- **输出**: JSON 数组，每项含 language、code_lines、doc_lines、file_count 等字段
- **验证**: `python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(x['code_lines'] for x in d))"` 可解析并求和，与 summary 表代码行总量一致
