# Vault 搭建工作流 — 从代码/研究仓库到 Obsidian 知识库

> 通用流程。适用于任何已有 markdown 文件的项目仓库。

## 步骤

### 第1步：初始化 vault 配置

```bash
# 在项目根目录创建 Obsidian 配置
mkdir -p .obsidian

# 基础配置
cat > .obsidian/app.json << 'EOF'
{
  "alwaysUpdateLinks": true,
  "attachmentFolderPath": "assets",
  "newFileLocation": "current"
}
EOF

cat > .obsidian/appearance.json << 'EOF'
{
  "baseFontSize": 16,
  "theme": "obsidian"
}
EOF

cat > .obsidian/core-plugins.json << 'EOF'
{
  "core:backlink": true,
  "core:graph": true,
  "core:tag-pane": true,
  "core:search": true,
  "core:file-explorer": true,
  "core:switcher": true
}
EOF

# .gitignore 中加入 .obsidian/
echo -e "\n# Obsidian vault config (local-only)\n.obsidian/" >> .gitignore
```

### 第2步：创建 MOC（Map of Content）索引链

每个主要子目录一个 `_INDEX.md`，根目录一个总的。用 `#moc` 标签标记。

**根 MOC 模板：** 概述 + 知识地图表格 + 快速链接 + 参照

```
项目根
├── _INDEX.md          ← 根入口：表格列出所有子目录 + 链接
├── docs/_INDEX.md     ← 架构文档索引
├── skills/_INDEX.md   ← 技能/能力索引
├── papers/_INDEX.md   ← 论文产出索引
├── experiments/_INDEX.md ← 实验记录索引
```

MOC 关键原则：
- 每个 `_INDEX.md` 开头加 `tags: [moc, ...]` frontmatter
- 用 `[[wikilink]]` 而非 URL 链接
- 末尾加参照节：`[[上一级|← 返回]]`、`[[下一级|→ 继续]]`

### 第3步：为现有文档添加 frontmatter

```yaml
---
tags: [topic1, topic2]
aliases: [Alternative Name, 中文别名]
---
```

Obsidian 图谱视图依赖 frontmatter 中的 tags 来着色和过滤。

### 第4步：文档格式转换

论文/文档原文（PDF/TeX/Office）需转 Markdown 才能被 Obsidian 索引：

| 源格式 | 工具 | 命令 |
|:-------|:-----|:------|
| PDF | MarkItDown | `uvx markitdown input.pdf > paper.md` |
| TeX/LaTeX | Pandoc | `pandoc paper.tex -t markdown -o paper.md` |
| DOCX | Pandoc | `pandoc paper.docx -t markdown -o paper.md` |

转换后补充 frontmatter（见 `markitdown-convert` skill）。

### 第5步：添加参照链接

在已转换的文档末尾添加：

```markdown
---

## 参照

- [[_INDEX|← 返回根 MOC]]
- [[相关文档|相关文档]]
```

## 适用场景

- 研究项目仓库（如本会话的 Synthos 项目）
- Hermes Agent 技能库
- 论文写作项目
- 代码框架文档

## 陷阱

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | 文件路径含特殊字符（回车符、弯引号） | 先用 `cat -v` 检测，用 `python3 -c` 修复 |
| 2 | 过多层级导致 Obsidian 加载慢 | 保持 ≤4 层目录深度 |
| 3 | 转换冲突：同一目录已含 .md 又转 PDF | 先检查：`find . -name "*.md"`，已有则优先用 |
| 4 | Pandoc 找不到 .bib | 从 TeX 所在目录执行 pandoc |
| 5 | MarkItDown PDF 依赖缺失 | `uv tool install markitdown --with markitdown[pdf]` |
