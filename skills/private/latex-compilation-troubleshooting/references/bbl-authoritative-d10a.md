# .bbl 作为 D10a 验证权威来源

## 原理

当论文使用 `\bibliography{reference4}`（外部 .bib）时，D10a 验证的**唯一权威来源**是 `.bbl` 文件。

`.bib` 文件可能包含未被 bibtex 解析的条目（格式错误、重复、不可达 DOI）。`.bbl` 只包含 bibtex 实际处理并输出的条目。

## 验证流程

### 步骤 1：编译生成 .bbl
```bash
pdflatex -interaction=nonstopmode paper.tex  # 生成 .aux
bibtex paper                                 # 生成 .bbl
pdflatex -interaction=nonstopmode paper.tex  # 解析引用
pdflatex -interaction=nonstopmode paper.tex  # 最终版
```

### 步骤 2：提取 .bbl 中的 bibitem keys
```python
import re
with open('paper.bbl') as f:
    bbl = f.read()
bibitems = set(re.findall(r'\\bibitem\{([^}]*)\}', bbl))
# 示例: {'daugman2009iris', 'bowyer2008image', ...}
```

### 步骤 3：提取 paper.tex 中的 cite keys
```python
with open('paper.tex') as f:
    tex = f.read()
cites = re.findall(r'\\cite[tp]?\{([^}]+)\}', tex)
cite_keys = set()
for c in cites:
    for part in c.split(','):
        key = part.strip()
        if key and key not in ['<label>', 'lamport94']:
            cite_keys.add(key)
```

### 步骤 4：计算 D10a
```python
orphaned = cite_keys - bibitems      # 在 tex 中但不在 .bbl 中（格式错误）
missing = bibitems - cite_keys       # 在 .bbl 中但未被引用（orphan）
d10a = (len(bibitems) - len(missing)) / len(bibitems) if bibitems else 0
```

## 常见陷阱

### 陷阱 1：注释中的引用
```tex
%%       Daugman \cite{daugman2001statistical} and \cite{bowyer2008image}.
```
`\cite{}` 在 `%%` 注释行中 → bibtex 忽略 → .bbl 不包含这些 key → D10a 不增加。
**修复**：将 `\cite{}` 移至正文段落中。

### 陷阱 2：highlights → itemize
elsarticle 的 `\begin{highlights}` 需要 `elsarticle-harvard.sty`，默认不可用。
导致 `Missing \item` 错误。
**修复**：改为 `\begin{itemize}`。

### 陷阱 3：equation* 在 enumerate/itemize 内
LaTeX 不允许浮动环境（equation*, figure, table）嵌套在列表环境中。
导致 `Something's wrong--perhaps a missing \item.` 错误。
**修复**：将 equation 移出 enumerate/itemize，放在 enumerate 外面。

### 陷阱 4：D8 计数与 D10a 计数分离
- `.bib` 中的条目数 ≠ `.bbl` 中的条目数（bibtex 可能过滤）
- D8 应该统计 `.bib` 条目
- D10a 必须从 `.bbl` 验证（权威）
- 如果 `.bib` 有 37 条但 `.bbl` 只有 28 条 → 检查 `.bib` 格式错误

## 验证命令速查

```bash
# .bbl 条目数
grep -c '\\bibitem' paper.bbl

# .tex 中的引用数
grep -oP '\\cite[tp]?\{[^}]+\}' paper.tex | sort -u | wc -l

# 是否有未定义引用
grep -c 'undefined' paper.log
# 应该为 0（bibtex 正确运行后）

# .bbl 是否为空（bibtex 未运行）
wc -c paper.bbl
# 如果 0 字节 → bibtex 未运行或失败
```

## 2026-06-15 实战记录

论文：3d-eyeball-iris-segmentation

1. 发现引用在注释行（L649: `%% Daugman \cite{daugman2001statistical}`）
2. 修正为正文引用后，D8=30（从28增加）
3. D10a 从 .bbl 验证：30/30 = 100%
4. 编译 0 错误，0 未定义引用

教训：引用在注释中是 bibtex 不可见的。必须确保所有 `\cite{}` 在正文中。