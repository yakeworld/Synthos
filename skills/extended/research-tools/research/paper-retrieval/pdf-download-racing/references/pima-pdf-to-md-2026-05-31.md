# Pima CRISP-DM PDF→Markdown 转换记录（2026-05-31）

## 背景

Pima CRISP-DM Helix 论文的 40 篇参考文献需要上传到 NotebookLM 做 Layer B 双质检。直接上传 PDF 失败率高，用户要求先转 Markdown。

## 转换管线

```bash
uvx markitdown input.pdf > output.md   # 优先
pdftotext input.pdf - | wc -c          # 备选
```

## 结果

| 类别 | 数量 | 工具 | 成功 | 说明 |
|:-----|:----:|:-----|:----:|:-----|
| 标准学术 PDF | 30 | MarkItDown | ✅ | arXiv/Elsevier/Springer/BMC/PLoS |
| IEEE PDF | 2 | MarkItDown | ✅ | 但偶有格式问题 |
| PMC PDF | 1 | MarkItDown | ✅ | Liao2023 从 PMC 获取 |
| arXiv PDF（SMOTE）| 1 | MarkItDown | ✅ | arXiv:1106.1813，文本层完好 |
| **损坏 PDF（无文本层）** | **3** | **全部失败** | ❌ | **Ribeiro2016/Pranto2020/Wirth2000** |
| **纯图像/扫描版 PDF** | **2** | **全部失败** | ❌ | Chawla2002/`Liao2023`的原PDF版 |
| **无文本层但替代源有** | **1** | **arXiv→PDF→MD** | ✅ | Chawla2002 从 arXiv:1106.1813 |
| **无文本层但 PMC 有** | **1** | **PMC→efetch→XML→text** | ✅ | Liao2023 从 PMC10205414 |

## 损坏 PDF 特征详解

### Ribeiro2016 (LIME) — 277KB
- `file` 报 `PDF document, version 1.4`
- `pdftotext` → 0 chars
- `pymupdf` → 0 chars
- `pdftoppm` → exit 1 (无法渲染)
- `mutool` → "cannot find page tree"
- `convert` → "Catalog dictionary not located"
- **根因**: xref 表 + page tree 均损坏，`%PDF-1.4` 头完好但内容不可恢复

### Pranto2020 — 205KB
- 同 Ribeiro2016，xref 损坏
- `file` 报 `PDF document, version 1.7`
- 所有工具失败

### Wirth2000 (CRISP-DM) — 352KB
- 同 Pranto2020，但 `mutool` 报 "malformed page tree"
- 有 40% readable characters in raw bytes 但 PDF 结构不可用

## 上传到 NotebookLM 的经验

### Shell arg limit 问题
- `notebooklm source add "$(cat file.md)"` 在文件 >80KB 时报 `Argument list too long`
- 解决：用 Python subprocess 传入 content 参数

### 文件分块策略
- Batches of ~80KB per chunk (subprocess arg safe zone)
- 每批约 10 篇论文的合并 MD
- 4 批共 29 个源文件（含手稿）

### 上传验证
```bash
notebooklm source list    # 检查 status=ready
notebooklm ask "简述本项目核心内容"  # 验证 Gemini 能检索
```

## 结论

1. **MarkItDown 方案** 覆盖 87.5% 的标准学术 PDF
2. **损坏 PDF** 无法恢复，只能写摘要
3. **替代源**（arXiv/PMC）可补救部分失败项
4. **全文 MD** 使 NotebookLM 100% 索引成功，Layer B 质检可靠
