---
name: obsidian
description: GOLDEN_SET.md
---

# GOLDEN_SET.md — obsidian

> 对应原则：P0（证据可溯性：每个期望输出可追溯到具体文件工具调用）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能金标准为自设（`self_defined`），验证目标：**给定 vault 路径与笔记操作请求，技能能否用原生文件工具（`read_file` / `write_file` / `patch` / `search_files`）完成笔记读写，且 Vault 初始化产物符合 MOC/frontmatter/symlink 约定**。不依赖 shell 命令（`cat`/`find`/`grep`/`ls`）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| Tier 1 笔记操作 | 2 | 读取笔记、按文件名搜索 |
| Tier 2 Vault 初始化 | 1 | 生成 `_INDEX.md` MOC + frontmatter + symlink 计划 |
| 错误路径 | 1 | 未展开的 `$OBSIDIAN_VAULT_PATH` 变量必须被拒绝并给出恢复建议 |

## 测试用例 (cases/)

### case_001: 读取已有笔记（正常路径）
- **输入**: 已解析 vault 路径（含空格）+ 目标笔记绝对路径
- **期望**: 用 `read_file` 返回带行号的 Markdown 内容；不出现 shell `cat` 调用

### case_002: 按内容正则搜索笔记（正常路径）
- **输入**: vault 路径 + content 正则 + `file_glob: "*.md"`
- **期望**: 用 `search_files target:"content"` 返回匹配文件与行号；匹配数 ≥1 且文件均位于 vault 内

### case_003: Vault 初始化（Tier 2，正常路径）
- **输入**: 项目根目录含 `docs/`、`papers/` 子目录的目录树
- **期望**: 各子目录生成 `_INDEX.md`（`_` 前缀置顶）、笔记 frontmatter 用数组格式 `tags: [a, b]`、外部源文件计划用 symlink 而非 copy、`.gitignore` 追加 `.obsidian/`

### case_004: 未解析 Vault 路径（错误路径）
- **输入**: `vault_path: "$OBSIDIAN_VAULT_PATH"`（未展开变量）
- **期望**: 拒绝执行，返回 `error` 含 "resolve vault path" 上下文与恢复建议（先用 terminal 解析或回退 `~/Documents/Obsidian Vault`），不发生文件操作

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，采用**语义等价判定**：
- `tool_calls` 中的工具名必须精确匹配（`read_file`/`search_files`/`write_file`/`patch`）
- 路径字段必须是具体绝对路径，不得含未展开的 `$` 变量
- 错误路径必须含 `error` 字段且非空，`tool_calls` 不含文件写入类工具

## pass_threshold: 0.80

含义：4 个测试用例中，至少 3 个通过（80%）。

### 阈值理由
- **不设 1.0**：笔记内容存在行号/分页变体，搜索匹配行集合允许等价
- **不设 < 0.8**：路径解析正确性与原生工具使用是本技能核心约定（Genes OBSI-001/002），错误直接导致路径空格/引号转义失败
- 4 个 case 中错误路径（case_004）为 critical 权重，失败即阻断
