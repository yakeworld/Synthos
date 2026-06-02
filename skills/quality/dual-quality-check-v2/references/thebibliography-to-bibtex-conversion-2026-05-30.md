# thebibliography → BibTeX 转换工作流

> 实战：SCC论文 v4 (43→34篇) 2026-05-30

## 触发条件

论文使用 `\begin{thebibliography}` 手写 bibitem 时：
- DOI 大面积缺失
- 无法自动检测僵尸引用
- 无法批量下载 PDF
- 切换期刊样式需手动重写所有条目

**检测**: `grep -c '\begin{thebibliography}' paper.tex`

## 转换步骤

### Step 1: 提取所有 bibitem 并解析

```python
import re
with open('paper.tex') as f: tex = f.read()
bibitems = {}
for m in re.finditer(r'\\bibitem\{([^}]+)\}\s+(.+?)(?=\n\\bibitem|\n\\end\{thebibliography\})', tex, re.DOTALL):
    key = m.group(1)
    raw = m.group(2).strip()
    # 去除 \textit{} \textbf{} 等格式命令
    raw = re.sub(r'\\textit\{([^}]+)\}', r'\1', raw)
    raw = re.sub(r'\\textbf\{([^}]+)\}', r'\1', raw)
    bibitems[key] = raw
```

### Step 2: 为每条引用手动整理字段

每个条目需整理为：作者、标题、期刊、卷、年、页、DOI

**DOIs 来源**: REFERENCE_MANIFEST.md, OpenAlex API, Semantic Scholar

OpenAlex 单个DOI查询:
```bash
curl -s "https://api.openalex.org/works/doi:10.xxxx/xxxxx" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f\"TITLE: {d.get('title','')}\")
print(f\"JOURNAL: {d.get('primary_location',{}).get('source',{}).get('display_name','')}\")
print(f\"YEAR: {d.get('publication_year','')}\")
print(f\"VOL/PP: {d.get('biblio',{}).get('volume','')}/{d.get('biblio',{}).get('first_page','')}--{d.get('biblio',{}).get('last_page','')}\")
"
```

### Step 3: 生成 .bib 文件

```python
entry = f"@article{{{key},\n"
entry += f"  author = {{{authors}}},\n"
entry += f"  title = {{{title}}},\n"
entry += f"  journal = {{{journal}}},\n"
entry += f"  volume = {{{volume}}},\n"
entry += f"  year = {{{year}}},\n"
entry += f"  pages = {{{pages}}},\n"
if doi: entry += f"  doi = {{{doi}}},\n"
entry += "}"
```

保存为 `references.bib` 放在 `01-manuscript/` 目录下。

### Step 4: 替换 TeX 文件

用 `\bibliographystyle{}` + `\bibliography{}` 替换整个 `thebibliography` 环境：

```python
tex_new = re.sub(
    r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}',
    r'% References via BibTeX\n\\bibliographystyle{elsarticle-num}\n\\bibliography{references}',
    tex, flags=re.DOTALL
)
```

### Step 5: 修正 natbib 选项冲突

**elsarticle** 类已自带 natbib，再加 `\usepackage[numbers]{natbib}` 会报 **Option clash**。

解决：删除 TeX 文件中多余的 `\usepackage[...]{natbib}` 行。

### Step 6: 编译验证

```bash
pdflatex paper.tex          # 第一次生成 .aux
bibtex paper                 # 生成 .bbl
pdflatex paper.tex           # 第二次解析引用
pdflatex paper.tex           # 第三次最终定稿
```

## 陷阱

### ⚠️ \b 被 Python 正则吃掉

`\bibliography` 中的 `\b` 会被某些 Python regex 操作解释为退格字符 (0x08)：

```
输入:  \bibliography{references}
输出:  ^Hibliography{references}    ← 损坏！
```

**修复方法**：用 `sed` 或 `patch` 工具直接写入正确的反斜杠序列，不要通过 Python 字符串中转。

```bash
# 正确方法：用 sed 直接替换文件
sed -i 's/^Hibliographystyle/\\bibliographystyle/' paper.tex
# 或保持 LaTeX 命令为原始文本，通过 `patch` 工具操作而非 Python re.sub
```

### ⚠️ 作者名字中的特殊字符

BibTeX 对 `$\\beta$`、`\\textmu` 等 LaTeX 命令敏感。若原始 bibitem 中含有：
- `Wnt/$\\beta$-catenin` → 在 BibTeX 中只需保留原样 `Wnt/$\beta$-catenin`

### ⚠️ 年份/卷/页解析

不同的 bibitem 格式：
- `Journal 139 (2012) 245--257` → 卷=139, 年=2012, 页=245--257
- `J. Morphol. 179 (1984) 159--173` → 同上
- `Acta Otolaryngol. Suppl. 434 (1987) 1--22` → 含期号，需 special handling
