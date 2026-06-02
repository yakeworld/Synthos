# rvo-ai-screening D10a Fix — 2026-06-02

> thebibliography 模式，29 个僵尸 bibitem，D10a=72%→100%

## 背景

`rvo-ai-screening` 是一篇系统综述论文（42页，~85KB LaTeX），使用 `thebibliography` 引用模式。初始状态：
- 103 个 bibitem
- 74 个被正文 `\cite{}` 引用
- **29 个僵尸**（在 bib 但从未被 \cite）
- D10a = 72%

## 步骤

### 1. 检测未使用 `\cite{}` 的纯文本引用

对 29 个僵尸逐一在正文搜索作者名+年份的纯文本模式：

```python
patterns_to_check = [
    r'\(Author et al\., Year\)',      # (Reitsma et al., 2005)
    r'Author et al\. \(Year\)',       # Reitsma et al. (2005)
    r'Author\(Year\)',                # Reitsma(2005)
]
```

**命中**: `Reitsma2005` — 正文 Methods 段写为 "(Reitsma et al., 2005)" 而非 `\citep{Reitsma2005}`。

**行动**: 用 `\citep{Reitsma2005}` 替换该纯文本引用。该 bibitem 变为活跃引用。

### 2. 删除其余 28 个僵尸 bibitem

使用 Python 按换行符在 `\bibitem` 前切分 bibsection：

```python
import re
entries = re.split(r'\n(?=\\bibitem)', bib_section)
kept = [entries[0]]  # thebibliography 开头
for entry in entries[1:]:
    if any(z in entry for z in zombies_to_delete):
        continue  # 跳过僵尸
    kept.append(entry)
new_bib_section = '\n'.join(kept)
```

### 3. 更新计数器

`\begin{thebibliography}{99}` → `\begin{thebibliography}{75}`

```python
count = len(re.findall(r'\\bibitem', new_bib_section))
new_bib_section = re.sub(r'\\begin\{thebibliography\}\{\d+\}',
                           rf'\\begin{{thebibliography}}{{{count}}}', 
                           new_bib_section)
```

### 4. 编译验证

```bash
pdflatex -interaction=nonstopmode paper.tex  # 第一遍
pdflatex -interaction=nonstopmode paper.tex  # 第二遍
# 确认 0 undefined, 0 warnings
```

## 结果

| 指标 | 修复前 | 修复后 |
|:-----|:------:|:------:|
| Bibitems | 103 | 75 |
| Cited | 74 | 75 |
| Zombies | 29 | 0 |
| D10a | 72% | **100%** |
| Compile | — | ✅ 42pp, 0 warnings |

## 要点

1. **纯文本引用陷阱**: 生物医学论文常把经典方法引用写成 "(Author et al., Year)" 而非 `\cite{}`。D10a 扫描时这些 bibitem 显示为僵尸，但实际已在正文中出现。
2. **系统综述的 bib 大小**: 这类论文的 bibitem 数常远超 D8 阈值（103 >> 30），删除僵尸不会导致 D8 不足。
3. **不逐一激活**: 对系统综述，28 个 RVO AI 论文虽然都相关，但它们未被作者选入正文——删除比强行插入更诚实。
