# D7 BibTeX Metadata Integrity Audit

> 2026-05-26 实战诞生：3D Eyeball Model‑Constrained Iris Segmentation 论文的双质量检查中，Gemini Layer B 揪出了 3 处引用元数据硬伤，Type A（本地）漏掉了。本流程确保这些错误在进出双质检前就被捕获。

## 常见错误模式

### 1. 重复 DOI

不同条目使用完全相同的 DOI。同一篇论文会出现：`proencca2010iris` 和 `wang2002study` 都用 `10.1016/j.imavis.2009.03.003`。

**检测**：
```bash
grep -oP 'doi\s*=\s*\{[^}]+\}' references.bib | sort | uniq -d
```

### 2. DOI 前缀与出版物类型不匹配

- 会议论文（ISMAR/CVPR/NeurIPS）挂期刊 DOI（`10.1016/...`）
- 期刊论文挂会议 DOI（`10.1109/ISMAR...`）
- 典型：`Mobile Information Systems` 期刊论文却用了 `10.1109/ISMAR55827.2022.00053`

**检测**：对每个条目, 检查 DOI 前缀与 `journal=`/`booktitle=` 是否逻辑一致。

| DOI 前缀 | 出版物类型 |
|:---------|:-----------|
| `10.1016/` | 期刊 (Elsevier) |
| `10.1109/` | 会议 (IEEE) |
| `10.1007/` | 期刊/会议 (Springer) |
| `10.1155/` | 期刊 (Hindawi) |
| `10.1038/` | 期刊 (Nature) |

```bash
# 检查 DOI 与 publication venue 一致性
grep -E 'journal\s*=|booktitle\s*=|doi\s*=' references.bib | paste - - | head -30
```

### 3. 错误关联的 PDF 文件

`file = {:bibtex_pdfs/pdfs/wang2002study.pdf:PDF}` 中 PDF 实际是 Proença 2010 的论文。

**检测**：
```bash
# 逐条验证 PDF 元数据与 bib 条目一致
for f in bibtex_pdfs/pdfs/*.pdf; do
  key=$(basename "$f" .pdf)
  bib_title=$(grep -A5 "^@.*{$key," references.bib | grep 'title' | sed 's/.*= {//;s/},//')
  pdf_title=$(pdfinfo "$f" 2>/dev/null | grep 'Title:' | sed 's/Title:\s*//')
  if [ "$bib_title" != "$pdf_title" ]; then
    echo "MISMATCH: $key"
    echo "  bib: $bib_title"
    echo "  pdf: $pdf_title"
  fi
done
```

### 4. 缺失 DOI

```bash
# 找出没有 DOI 的条目
grep -B5 '^@' references.bib | grep -v 'doi\s*=' | grep '^@' | grep -v '@Comment'
```

### 5. 作者名格式不规范

`Wang, Sung` 缺少首字母，应为 `Wang, Jian-Gang and Sung, Eric`。

**检测**：
```bash
# 找出只有单字段的作者名（缺少名首字母）
grep 'author\s*=' references.bib | grep -oP '\{[^}]+\}' | tr ',' '\n' | grep -P '^[A-Z][a-z]+$'
```

## 批量修复流程

```bash
# Step 1: 完整扫描
echo "=== 重复 DOI ==="
grep -oP 'doi\s*=\s*\{[^}]+\}' references.bib | sort | uniq -d

echo "=== 缺失 DOI ==="
grep -B5 '^@' references.bib | grep -v 'doi\s*=' | grep '^@' 

echo "=== PDF 元数据 mismatch ==="
for f in bibtex_pdfs/pdfs/*.pdf 2>/dev/null; do
  key=$(basename "$f" .pdf)
  bib=$(grep -A5 "^@.*{$key," references.bib | grep 'title' | head -1)
  pdf=$(pdfinfo "$f" 2>/dev/null | grep 'Title:' | head -1)
  if [ -n "$bib" ] && [ -n "$pdf" ]; then
    bib_t=$(echo "$bib" | sed 's/.*{\\?//;s/},*$//;s/^ *//;s/ *$//')
    pdf_t=$(echo "$pdf" | sed 's/Title:\s*//')
    if [ "$bib_t" != "$pdf_t" ] && [ "${#bib_t}" -gt 5 ]; then
      echo "MISMATCH: $key — bib=\"$bib_t\" vs pdf=\"$pdf_t\""
    fi
  fi
done

# Step 2: 修复（用 write_file 整文件重写，不用 patch）
# 对每个错误：
#   - 重复 DOI → 确认哪个条目是正确的，删除另一个条目的 doi 字段
#   - DOI 不匹配 → 查 Semantic Scholar / 出版商网站获取正确 DOI
#   - PDF 错误 → 删除 file 字段并标注 TODO
#   - 缺失 DOI → 查 Semantic Scholar API 补全

# Step 3: 重新编译验证
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
grep -c '^!' paper.log  # 应为 0
grep -c 'Warning.*Citation' paper.log  # 应为 0
```

## 预期收益

| 修正类型 | D7 预期提升 |
|:---------|:-----------:|
| 重复 DOI 修复 | +0.05~0.10 |
| DOI 不匹配修复 | +0.03~0.08 |
| PDF 清理 | +0.02~0.05 |
| 缺失 DOI 补全 | +0.03~0.08 |
| **累计** | **+0.10~0.25** |

实战案例（2026-05-26）：3D Eyeball 论文 D7 从 0.70 → 0.95（+0.25），主要受益于 3 处元数据错误修复 + Layer B 重新验证确认。
