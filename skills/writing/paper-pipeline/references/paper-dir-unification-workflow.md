# 论文目录统一合并工作流

> **场景**：发现外部目录（如 `投稿文件汇总/`、`~/桌面/article_todo/`）有论文草稿但不在 Synthos outputs 下。
> **目标**：迁移到 `/media/yakeworld/sda2/Synthos/outputs/papers/{name}/` 并标准化 09-子目录结构。
> **2026-06-04 实战**：从 `投稿文件汇总/` 合并 crispdm-pima / crispdm-heart / crispdm-wdbc 三篇。

## 触发条件

| 场景 | 行动 |
|:-----|:------|
| 用户询问「全文在哪」或「工作目录在哪」 | 先查 Synthos outputs → 若不在则触发合并 |
| 用户说「统一工作目录」 | 全量扫描外部源，所有未纳入的论文一次合并 |
| 新接手一篇论文，路径在 Synthos outputs 之外 | 立即迁入，不留在原地工作 |

## 扫描外部源

```bash
EXTERNAL="/media/yakeworld/sda2/投稿文件汇总"
for d in "$EXTERNAL"/*/; do
    name=$(basename "$d")
    if [ -d "/media/yakeworld/sda2/Synthos/outputs/papers/$name" ]; then
        echo "⚠️ 已存在: $name"
    else
        echo "🆕 未纳入: $name — $(ls "$d/paper/"*.tex 2>/dev/null | wc -l) 个tex文件"
    fi
done
```

## 合并步骤（每篇）

### Step 1: 创建标准09-子目录

```bash
DEST="/media/yakeworld/sda2/Synthos/outputs/papers/{name}"
mkdir -p $DEST/{01-manuscript,02-submission,03-code,04-data,05-figures,06-references/pdfs,07-quality,08-records,09-background}
```

### Step 2: 拷贝核心文件

| 源文件 | 目标 | 说明 |
|:-------|:-----|:------|
| `paper/paper.tex` | `01-manuscript/paper.tex` | 最新手稿 |
| `01-manuscript/paper.pdf` | `01-manuscript/paper.pdf` | 编译PDF |
| `paper/references.bib` | `06-references/references.bib` | 参考文献 |
| `paper/*.pdf` | `01-manuscript/` | 论文用图 |
| `experiment/*.py` | `03-code/experiment/` | 实验脚本 |
| `analysis/*.md` | `09-background/` | 分析文档 |

```bash
cp source/paper/paper.tex $DEST/01-manuscript/
cp source/01-manuscript/paper.pdf $DEST/01-manuscript/ 2>/dev/null
cp source/paper/references.bib $DEST/06-references/
cp source/experiment/*.py $DEST/03-code/experiment/ 2>/dev/null
cp -r source/analysis/* $DEST/09-background/ 2>/dev/null
```

### Step 3: 创建符号链接

```bash
# 01-manuscript 下的 symlink
ln -sf ../06-references/references.bib $DEST/01-manuscript/references.bib
ln -sf ../fig_architecture.pdf $DEST/01-manuscript/fig_architecture.pdf 2>/dev/null
```

### Step 4: 迁移已有 PDF 全文

如果 Synthos outputs 下已有同名论文目录且包含 `06-references/pdfs/` 中的 PDF：

```bash
# PDF 已在目标路径 → 不需额外拷贝
# 只需确保 bib 文件是最新版
```

### Step 5: 编译验证

```bash
cd $DEST/01-manuscript
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
grep -c 'undefined' paper.log || echo "0 undefined"
```

### Step 6: 验证并报告

```bash
echo "paper.tex: $(wc -l < paper.tex)行"
echo "references.bib: $(wc -l < references.bib)行"
echo "PDFs: $(ls ../06-references/pdfs/*.pdf 2>/dev/null | wc -l)篇"
```

## 实战：三篇 CRISP-DM 论文合并（2026-06-04）

| 论文 | 源路径 | 合并内容 | 状态 |
|:-----|:-------|:---------|:-----|
| crispdm-pima | 投稿文件汇总/crispdm-pima/ | .tex + .bib + 5个.py + 42篇PDF | ✅ 编译9页0错误 |
| crispdm-heart | 投稿文件汇总/crispdm-heart/ | .tex + .pdf + heart_crispdm_helix.py | ✅ 含实验代码 |
| crispdm-wdbc | 投稿文件汇总/crispdm-wdbc/ | .tex + .pdf + .bib + wdbc_crispdm_helix.py | ✅ 含references.bib |

完成后通知用户：
```
投稿文件汇总 → Synthos outputs 全部统一完毕。
今后仅操作 Synthos/outputs/papers/ 即可。
```

## 已知外部源清单（需持续扫描）

| 外部源 | 状态 |
|:-------|:-----|
| `投稿文件汇总/` | ✅ 已合并（3篇） |
| `~/桌面/article_todo/` | 🟡 8篇待写（未纳入） |
| 其他 `~/桌面/*.tex` | 🟡 发现即合并 |
