# .docx修订版生成 — 黑体标记修改工作流

> 基于2026-06-23 两份BCI方案修改实战

## 用户偏好

用户要求的文档修订输出方式是：**所有修改部分用黑体（加粗）标识**，以便快速定位变更。不要在修订版上加批注/标注/高亮/下划线——黑体是唯一标记。

## 标准工作流

### Step 1: 建立修改清单

审查阶段记录所有修改点，格式如下：

```
| # | 位置 | 类型 | 原文摘要 | 修改方案 |
|:-:|:-----|:-----|:---------|:---------|
| 1 | P6 | 技术论证 | "SNR远超侵入式BCI" | 改为与EEG对比 |
```

### Step 2: python-docx逐点应用

```python
from docx import Document
doc = Document('源文件.docx')

def mark_and_replace(para, old_str, new_str):
    """在段落中替换old_str为new_str，新内容加粗."""
    if old_str not in para.text:
        return False
    
    idx = para.text.index(old_str)
    before = para.text[:idx]
    after = para.text[idx + len(old_str):]
    
    # 清空原有run
    for run in para.runs:
        run.text = ''
    
    # 重建：前文（常规）→ 修改内容（黑体）→ 后文（常规）
    if before:
        r = para.add_run(before)
        r.font.size = Pt(10.5)
    
    r = para.add_run(new_str)
    r.bold = True          # ← 黑体标记
    r.font.size = Pt(10.5)
    
    if after:
        r = para.add_run(after)
        r.font.size = Pt(10.5)
    
    return True

# 遍历段落，逐点应用
for para in doc.paragraphs:
    mark_and_replace(para, '原文', '修改后文本')
    mark_and_replace(para, '另一处原文', '另一处修改')

doc.save('修改版.docx')
```

### Step 3: 段落替换 vs 全文替换

- **局部替换**（推荐）：仅替换段落内的一段文本，保留周围上下文。用 `mark_and_replace()`。
- **全文替换**：替换整个段落的全部文本。用 `make_whole_para_bold(para, new_text)`。
- **不要用重写全文**：清空所有段落再重写的做法会丢失原始格式（字体/段落间距/列表/缩进）。

### Step 4: 表格处理（专利附录添加）

```python
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

def add_table_with_borders(doc, headers, data):
    """创建带边框的表格."""
    table = doc.add_table(rows=1+len(data), cols=len(headers))
    # 表头
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # 表头底色
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D9E2F3"/>')
        cell._tc.get_or_add_tcPr().append(shading)
    
    # 数据行
    for r_idx, row_data in enumerate(data):
        for c_idx, val in enumerate(row_data):
            cell = table.rows[r_idx+1].cells[c_idx]
            cell.text = val
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    
    # 边框
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(...)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '  <w:top w:val="single" w:sz="4" w:space="0" w:color="666666"/>'
        '  <w:left w:val="single" w:sz="4" w:space="0" w:color="666666"/>'
        '  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="666666"/>'
        '  <w:right w:val="single" w:sz="4" w:space="0" w:color="666666"/>'
        '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="666666"/>'
        '  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="666666"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)
    return table
```

### Step 5: 输出验证

修改后必须验证，不可假设正确：

```python
doc = Document('修改版.docx')
for i, p in enumerate(doc.paragraphs):
    if '原文关键词' in p.text:
        # 确认已被替换
        assert '修改后关键词' in p.text, f'P{i} 替换失败！'
```

### Step 6: 残留风险扫描

在验证之后，再扫一遍**原始关键词**，确认没有遗漏：

| 原文本 | 应替换为 | 扫描关键词 |
|:-------|:---------|:-----------|
| "硬件成本" | "硬件物料成本" | "硬件成本"（不含物料） |
| "64项完稿" | "94项技术储备" | "64项" |
| "侵入式BCI" | 删除 | "侵入式BCI" |

## 典型陷阱

### 🔴 段落跨多个run
.docx 中一段文本可能被拆成多个run（因为同一段落内有不同格式）。直接用 `.text` 读全文没问题，但替换后重建run时要小心——**清空所有run再重建**而不是只修改某个run。

### 🟡 表头/页眉/页脚中的文本
正文段落遍历不覆盖表头/页眉/页脚中的文本。如有修改需要单独处理：
```python
for section in doc.sections:
    for para in section.header.paragraphs:
        mark_and_replace(para, ...)
```

### 🟡 中文字体
中文字体设置需用 `r.font.name` + 设置东亚字体：
```python
from docx.oxml.ns import qn
r = para.add_run('文本')
r.font.name = '宋体'
r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
```
