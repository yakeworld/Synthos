# D10a 计算方法

## 核心原则

D10a = 正文中实际引用的 bib entry 数 / 总 bib entry 数

## .bib 文件 vs .tex 文件

### .bib 文件 (references.bib)

BibTeX 源文件，使用 `@type{key}` 格式：

```python
import re
with open('references.bib', 'r') as f:
    bib_content = f.read()
# 正确：匹配 @article{key, @book{key, @techreport{key 等
entries = re.findall(r'@(\w+)\{([^,\s]+)', bib_content)
unique_keys = set([e[1] for e in entries])
```

### .tex 文件 (paper.tex)

LaTeX 源文件，正文中用 `\cite{key1,key2}` 引用。
注意：`\\bibitem{key}` 不在 .tex 中出现，它在编译后生成的 `.bbl` 文件中。

```python
with open('paper.tex', 'r') as f:
    tex_content = f.read()
# 提取正文中所有引用
cites = re.findall(r'\\cite\{([^}]+)\}', tex_content)
unique_cites = set()
for group in cites:
    for key in group.split(','):
        key = key.strip()
        if key:
            unique_cites.add(key)
```

## D10a 计算

```python
d10a = len(unique_cites) / len(unique_bib) if unique_bib else 0
print(f"D10a: {d10a:.2%}")
```

## 健康标准

| D10a | 状态 | 说明 |
|------|------|------|
| 0% | 致命 | 有 bib 条目但正文未引用 |
| 0-50% | 差 | 大部分条目未引用 |
| 50-80% | 一般 | 需要补充引用 |
| 80-99% | 健康 | 可接受，5-10% unused 是正常的 |
| 100% | 完美 | 所有条目都被引用 |

**重要**：5-10% 的 unused bib entries 是正常的。背景引用、延伸阅读、工具/框架参考可能不需要在正文中明确 cite。

## 常见陷阱

1. **用 `\\bibitem` 匹配 .bib 文件** → 结果为 0。`\\bibitem` 只在 `.bbl` 文件中存在。
2. **用 `\\bibitem` 匹配 .tex 文件** → 找不到。`.tex` 正文中只有 `\cite{}`，没有 `\bibitem{}`。
3. **重复引用 key** → 用 set 去重。
4. **多个 key 用逗号分隔** → 需 split 后逐个处理。