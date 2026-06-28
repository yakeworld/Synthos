---

name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
author: Synthos
license: MIT
version: 1.0.0
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- search_files
platforms:
- linux
- macos
- windows
metadata:
  synthos:
    signature: 'action: str, params: dict -> result: dict'
    related_skills:
    - airtable
    - chinese-form-automation
    - google-workspace
    - jupyter-live-kernel
    - linear


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）




# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, adding wikilinks, and initializing project knowledge bases.

Covers two tiers of work:
- **Tier 1: Note ops** — read, search, create, edit individual notes within an existing vault.
- **Tier 2: Vault init** — initialize a directory as an Obsidian knowledge base with MOC structure, frontmatter, symlinks to source files, and sync scripts.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Vault setup — convert a code/research repo into an Obsidian knowledge base

For converting an existing project directory into an Obsidian knowledge base, see:
- `references/vault-setup-workflow.md` — class-level workflow

## Related files

- `references/vault-setup-workflow.md` — full vault setup workflow

---

## Tier 2: Vault Initialization — 项目知识库搭建

当需要把现有项目目录变成可导航的 Obsidian 知识库时，按以下步骤。

### 何时使用

- 项目已有大量 `.md`、`.tex`、`.pdf` 文件需要组织
- 需要跨文档导航（图谱、反链、标签）
- 需要区分笔记层（分析/注释）和源文件层（原文）

### 步骤

**Step 1: 添加 `.obsidian/` 配置**
```json
// core-plugins.json — 启用图谱、反链、标签、文件搜索
{
  "core:backlink": true,
  "core:graph": true,
  "core:tag-pane": true,
  "core:search": true,
  "core:file-explorer": true,
  "core:command-palette": true
}
```
同时把 `.obsidian/` 加入 `.gitignore`。

**Step 2: 创建 MOC 索引链**

在每个子目录建 `_INDEX.md`（Map of Content），形成可导航的入口：

```
项目根/
├── _INDEX.md              ← 总入口（快速链接到各区域）
├── docs/_INDEX.md          ← 文档区
├── skills/_INDEX.md        ← 技能/知识点区
├── papers/_INDEX.md        ← 论文笔记区
└── outputs/papers/_INDEX.md ← 原文源文件区
```

**Step 3: 添加 YAML frontmatter**

```yaml
---
tags: [paper, iris, segmentation]
aliases: [中文名, English Alt Name]
---
```

**Step 4: 添加参照链接**

每个笔记末尾添加：
```markdown
## 参照
- [[papers/_INDEX|📝 论文目录]]
- [[_INDEX|← 返回根 MOC]]
```

**Step 5: 链接外部源文件**

用符号链接将已有文件（TeX、PDF、数据）映射到 vault 内：
```bash
ln -s /path/to/source/dir outputs/papers/paper-name/
```

**Step 6: 建立与 fact_store 的同步**

在 `scripts/` 下放同步脚本。核心逻辑：
- 扫描修改过的 `.md` 文件
- 提取 `**key**: value`、表格行、frontmatter tags
- 写入 `fact_store` SQLite 数据库
- 重建 FTS 索引

### 已知陷阱

- **不要直接复制源文件**：使用符号链接保持源目录干净，且 Git 不跟踪 vault 元文件
- **MOC 命名**：`_INDEX.md` 的 `_` 前缀让它在 Obsidian 文件浏览器中置顶
- **Wikilink 中的空格**：Obsidian wikilink 支持空格，但路径中有 `'`（单引号）时需用 `\` 转义
- **frontmatter tag 格式**：`tags: [a, b, c]` 比 `tags: a, b, c` 更兼容

### 相关文件

- `references/synthos-vault-init-2026-05-27.md` — Synthos 知识库搭建实例

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
