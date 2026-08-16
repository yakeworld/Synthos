---
name: tool-pdf-extraction
category: tool
description: knowledge-extraction 工具契约 — markitdown/pdftotext 级联、四域提取、JSON 输出
version: 1.0.0
---

# PDF 加载与知识输出契约

> **工程层**：本文档只定义工具调用的事实契约（转换命令、级联规则、输出路径）。
> 为何优先 Markdown、四域提取标准见上层 `knowledge-extraction/SKILL.md`（哲学层）。

## 1. 论文加载（markitdown 优先）

| 方式 | 命令 | 适用 |
|------|------|------|
| A（首选） | `markitdown paper.pdf > /tmp/paper_content.md` | 正常 PDF：保留表格结构、标题层级 |
| B（回退） | `pdftotext -layout paper.pdf /tmp/paper_content.txt` | markitdown 失败（扫描/超大/加密） |
| C | `cat /path/to/paper.md` | 已有 Markdown |
| D | `web_extract(url)` 或粘贴摘要 | 摘要/网页 |

### 级联规则

1. 先跑 `markitdown paper.pdf > /tmp/try.md`
2. 检查输出：`wc -c /tmp/try.md` ≥ 200 且含文本 → ✅ 用 Markdown（设 `meta.source = "markdown_extracted"`）
3. 失败（空/超时）→ 回退 pdftotext（设 `meta.source = "pdf_text"`）

> **为何优先 Markdown**：表格结构保留 → 证据提取更准（数值不乱）；标题层级保留 → section 标注从"猜"变"定"。

## 2. 输出契约（JSON）

```bash
mkdir -p outputs/{paper_dir}/07-quality/
python3 -c "import json; json.dump(knowledge_item, open('outputs/{paper_dir}/07-quality/knowledge.json','w'), indent=2, ensure_ascii=False)"
```

| 项 | 值 |
|----|-----|
| 输出路径 | `outputs/{paper_slug}/07-quality/knowledge.json` |
| 编码 | UTF-8（`ensure_ascii=False`） |
| 格式 | 缩进 2 空格 JSON |
| 内容 | KnowledgeItem（实体/关系/主张/证据四域） |

## 3. 错误处理

| 症状 | 判定 | 处置 |
|------|------|------|
| `markitdown` 空输出/超时 | 扫描 PDF/加密/超大 | 回退 `pdftotext -layout` |
| `pdftotext` 无文本 | 纯扫描件 | 标注无法提取，不伪造 |
| 输出目录不存在 | 路径未建 | 先 `mkdir -p` |
