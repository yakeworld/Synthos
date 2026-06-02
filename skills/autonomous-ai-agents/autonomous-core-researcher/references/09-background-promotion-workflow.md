# 09-Background → 独立论文升级工作流

> 2026-05-31 实战：膜性半规管三维重建论文从 `scc-mathematical-morphology/09-background/membranous-reconstruction/` 升级为 `outputs/papers/membranous-scc-reconstruction/`

## 触发场景

当扫描论文库时，发现 `09-background/` 子目录中包含完整的 LaTeX 论文（非碎片笔记），这些论文可能：
- 是该论文专题研究的副产品
- 是先行探索的独立文章
- 从 Todo 论文中转化但未提级

## 检查方法

### 单篇扫描

```bash
# 对每个现有论文，查看其 background 目录
ls -d outputs/papers/*/09-background/*/
# 对每个子目录，看是否有 .tex + .bib
for d in outputs/papers/*/09-background/*/; do
    has_tex=$(find "$d" -name "*.tex" -size +1k 2>/dev/null | head -1)
    has_bib=$(find "$d" -name "*.bib" 2>/dev/null | head -1)
    has_pdf=$(find "$d" -name "*.pdf" -not -empty 2>/dev/null | head -1)
    has_qc=$(ls "$d/quality-report.md" 2>/dev/null)
    
    if [ -n "$has_tex" ] && [ -n "$has_bib" ]; then
        echo "🔍 PROMOTABLE: $(basename $d)"
        echo "  Parent: $(basename $(dirname $(dirname $d)))"
        echo "  Tex: $has_tex"
        echo "  Bib: $has_bib"
        echo "  PDF: $has_pdf"
        [ -n "$has_qc" ] && echo "  QC: ✅" || echo "  QC: ❌"
    fi
done
```

## 升级步骤（比 _todo/ 迁移更简单）

由于 09-background 中的论文通常已有：
- 编译过的 .tex（含样式文件如 sagej.cls, bst 文件）
- 完整 .bib 文件
- 已下载的参考 PDF
- 部分或完整的质量报告

### Step 1: 创建目录

```bash
NAME="membranous-scc-reconstruction"
DST="outputs/papers/$NAME"

mkdir -p "$DST/01-manuscript"
mkdir -p "$DST/02-submission"
mkdir -p "$DST/03-code"
mkdir -p "$DST/04-data"
mkdir -p "$DST/05-figures"
mkdir -p "$DST/06-references/pdfs"
mkdir -p "$DST/07-quality"
mkdir -p "$DST/08-records/optimization-logs"
mkdir -p "$DST/09-background"
```

### Step 2: 复制核心文件

```bash
SRC="outputs/papers/scc-mathematical-morphology/09-background/membranous-reconstruction"

# Manuscript
cp "$SRC/membranous-scc-recon.tex" "$DST/01-manuscript/paper.tex"
cp "$SRC/membranous-scc-recon.pdf" "$DST/01-manuscript/"
cp "$SRC/membranous-scc-recon.bbl" "$DST/01-manuscript/"

# Reference
cp "$SRC/ref.bib" "$DST/06-references/references.bib"

# Style files (Sage/Elsevier 等模板特有)
cp "$SRC/sagej.cls" "$DST/01-manuscript/" 2>/dev/null || true
cp "$SRC/SageH.bst" "$DST/01-manuscript/" 2>/dev/null || true
cp "$SRC/SageV.bst" "$DST/01-manuscript/" 2>/dev/null || true

# Figures
cp "$SRC/figures/"*.png "$DST/05-figures/" 2>/dev/null || true

# PDFs
cp "$SRC/pdfs/"*.pdf "$DST/06-references/pdfs/" 2>/dev/null || true

# Quality
cp "$SRC/quality-report.md" "$DST/07-quality/"
```

### Step 3: 处理路径依赖（符号链接而非改 .tex）

09-background 中的 .tex 通常使用相对路径引用「同目录」下的文件和子目录：

```bash
cd "$DST/01-manuscript"

# 如果 .tex 用 \\bibliography{ref} 但 bib 在 06-references/references.bib
ln -sf ../06-references/references.bib ref.bib

# 如果 .tex 用 figures/ 图但实际上图在 05-figures/
ln -sf ../05-figures figures

# 如果样式文件在 01-manuscript 目录
# sagej.cls, SageH.bst, SageV.bst 已复制到 01-manuscript
```

**为什么用符号链接而非改 .tex**：
1. 不改 .tex 则保留源文件完整性，未来对比 diff 清晰
2. 多版本文件（v1, v2, paper.tex）各自有不同路径，逐个修改易错
3. 符号链接在 `git` 或版本管理中可跟踪，但 .tex 修改会被覆盖

### Step 4: 编译验证

```bash
cd "$DST/01-manuscript"

# 第一遍
pdflatex -interaction=nonstopmode -halt-on-error paper.tex

# BibTeX
bibtex paper

# 两遍清除交叉引用
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex

# 验证
grep -c "undefined" paper.log && echo "⚠️ 有未定义引用" || echo "✅ 0 undefined"
```

### Step 5: 验证 QC 指标

```bash
python3 -c "
import re

tex = open('paper.tex').read()
lines = [l for l in tex.split(chr(10)) if not l.strip().startswith('%')]
active = chr(10).join(lines)
cites = re.findall(r'\\\\cite[tp]?\\s*\{([^}]+)\}', active)
cited_set = set()
for c in cites:
    for k in c.split(','):
        k = k.strip()
        if k: cited_set.add(k)

bib = open('ref.bib').read()
bib_keys = set(re.findall(r'@\\w+\\{([^,]+),', bib))

orphan = cited_set - bib_keys
zombie = bib_keys - cited_set
cited_count = len(cited_set & bib_keys)
print(f'D8: {len(bib_keys)}')
print(f'D10a: {cited_count}/{len(bib_keys)} = {cited_count/max(len(bib_keys),1)*100:.0f}%')
if orphan: print(f'ORPHAN: {sorted(orphan)}')
if zombie: print(f'ZOMBIE: {sorted(zombie)[:10]} (n={len(zombie)})')
"
```

### Step 6: 质量快照写入 README.md

```markdown
# 论文名

> Promoted from: papers/{parent-paper}/09-background/{dir-name}/ (YYYY-MM-DD)

## Status: ✅ T1 PASS

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| D8 | 30 | All cited |
| D9 | 21/21 = 100% | Real PDFs |
| D10a | 30/30 = 100% | 0 orphan, 0 zombie |
| D1-D7 | 0.85 avg | T1 PASS (see 07-quality/) |

## Known Issues
- P1: D3=0.75 (small sample size)
- ...
```

## 实战记录：膜性SCC论文升级（2026-05-31）

**发现过程**：扫描 `_todo/` 时发现「Three-Dimensional Reconstruction of Membranous Semicircular Canals」只有 Markdown（39KB article.md）和 14 篇参考 PDF，评估为 ★★。同时在 `scc-mathematical-morphology/09-background/membranous-reconstruction/` 发现该论文的完整 LaTeX 版本。

**升级亮点**：
- LaTeX 版本使用 Sage 期刊模板（`sagej.cls` + `SageV.bst`），311 行完整 IMRaD 手稿
- 30 条 bib 条目，全部被引用，D10a=100%
- 21 篇真实 PDF，D9=100%
- 前序双质检 D1-D7 avg=0.85（T1 PASS）
- 编译 12 页，808KB

**耗时**：约 15 分钟（从发现 → 目录创建 → 文件复制 → 符号链接 → 编译 → README → 升级 tracker）

## 注意事项

1. **保留原始文件**：升级后不删除 `09-background/` 中的原始文件（备份）
2. **检查 natbib/bibstyle 兼容性**：有些期刊模板（如 sagej.cls）用 natbib 但与 SageV.bst 不兼容，会触发预编译期非致命错误。无需修复——PDF 仍正常生成
3. **多版本检测**：09-background 目录可能同时包含 Markdown 和 LaTeX 版本。优先升级 LaTeX 版本（可直接编译）
4. **不要重复**：升级前检查 `completed_papers` 列表中是否已有同名/同主题论文
5. **来源追踪**：在 README.md 中注明父论文和原始目录路径，便于后续回溯
