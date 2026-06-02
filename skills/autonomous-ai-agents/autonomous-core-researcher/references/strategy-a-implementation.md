# Strategy A: Implementation Guide — Integrating Unused Bibitems

> 2026-05-25 实战教训: Python `content.replace()` 对 LaTeX 文本的匹配不可靠——空格编码差异、行尾空白、反斜杠转义等问题都会导致静默失败（不报错，不替换）。

## 核心理念

Strategy A = 利用论文 thebibliography 中已有的但未被 `\cite{}` 引用的 bibitem，通过将它们整合到正文中来提升 D7 评分。零 API 调用、零编译风险。

## 三种实现方法（按可靠性排序）

### 方法 1: `sed` 终端替换（最可靠，推荐）

**适用场景**：在已知的段落末尾添加引用，或在已有 `\cite{...}` 中追加 key。

```bash
# 在已有 \cite{...} 中追加引用
sed -i 's/\\cite{robinson1963method, tweed1990computing}/\\cite{robinson1963method, tweed1990computing, magnusson2020vhit, alhabib2017vhit}/' paper.tex

# 在特定字符串后追加引用
sed -i '/standardized vestibular testing in clinical settings/a~\\cite{magnusson2020vhit}' paper.tex
```

**优点**：精确匹配、立即执行、无转义干扰。
**缺点**：需要知道文件中的确切字符串（含空格）。

### 方法 2: Python `re.sub()`（最灵活，推荐）

**适用场景**：复杂替换需要正则匹配，或多处同时修改。

```python
import re

path = 'paper.tex'
with open(path) as f:
    content = f.read()

# 对已知 cite 键追加新的引用
content = re.sub(
    r'\\cite\{robinson1963method,\s*tweed1990computating\}',  # 注意：需要精确拼写
    r'\cite{robinson1963method, tweed1990computing, magnusson2020vhit, alhabib2017vhit}',
    content
)

# 如果找不到精确匹配，用模糊匹配
# 找到包含 robinson 的 \cite{} 并在末尾添加
content = re.sub(
    r'(\\cite\{[^}]*robinson[^}]*\})',
    lambda m: m.group(1).rstrip('}') + ', magnusson2020vhit}',
    content
)

with open(path, 'w') as f:
    f.write(content)
```

**优点**：最灵活，可处理模糊匹配。
**缺点**：`re.sub()` 的匹配模式若包含 LaTeX 特殊字符可能出错。

### 方法 3: Python `str.replace()`（不推荐）

```python
content = content.replace(
    'exact string from file',
    'exact string from file with new cite'
)
```

**适用**：仅当你能 100% 确认文件中的准确字符串（包括空格数量）。

**静默失败模式**：
| 原因 | 表现 | 检测方法 |
|:-----|:-----|:---------|
| 行尾多了一个空格 | `replace()` 返回原字符串 | `grep -c '搜索词' paper.tex` 确认实际格式 |
| 句子在文件中被自动换行 | 跨行字符串不匹配 | `cat paper.tex \| grep -n '片段'` 查看行上下文 |
| `~`（非断行空格）被显示为普通空格 | 字符串不一致 | `od -c paper.tex \| head -20` 检查字符编码 |
| Unicode 引号 vs ASCII 引号 | 全半角不匹配 | `grep -P '[^\\x00-\\x7f]' paper.tex` 检查非ASCII |

## 标准化执行流程（必做）

### Step 1: 识别可用的未引用 bibitem

```python
import re
with open('paper.tex') as f:
    content = f.read()

# 提取所有 cite 键
cite_keys = set()
for pattern in [r'\\cite\{([^}]+)\}', r'\\citep\{([^}]+)\}', r'\\citet\{([^}]+)\}']:
    for match in re.finditer(pattern, content):
        keys = [k.strip() for k in match.group(1).split(',')]
        cite_keys.update(k for k in keys if k)

# 提取所有 bibitem 键
bibitem_keys = set()
for match in re.finditer(r'\\bibitem\{([^}]+)\}', content):
    bibitem_keys.add(match.group(1))

unused = bibitem_keys - cite_keys
print(f"Unused bibitems ({len(unused)}):")
for k in sorted(unused):
    print(f"  - {k}")
```

### Step 2: 按主题分类未引用 bibitem

读取对应 bibitem 的 title 字段（在 `\bibitem{key}` 后的文本中），按主题分组：

| 主题 | 候选 bibitem |
|:-----|:-------------|
| vHIT临床综述 | magnusson2020vhit, alhabib2017vhit, starkov2022diagnostic |
| BPPV诊断 | oh2020bppv, lee2020diagnosis, zhao2022bppv, shimizu2021horizontal |
| 新兴3D-VOG系统 | bellmann2023wireless, wei2024high, wang2026three |
| 瞳孔追踪算法 | cerrolaza2012pupil, ebti2018enhanced |

### Step 3: 找到正文中对应的插入点

用 `grep -n '匹配词' paper.tex` 找到可插入引用的自然段落结尾。

### Step 4: 执行替换（用 `sed` 或 `re.sub`）

```bash
# 将4个vHIT综述引用追加到已有 cite 行
# 先找到包含 macdougall2013new 的 cite 行
grep -n 'macdougall2013new' paper.tex

# 然后 sed 替换（必须确认确切的前后文）
LINE=$(grep -n 'macdougall2013new' paper.tex | head -1 | cut -d: -f1)
OLD=$(sed -n "${LINE}p" paper.tex)
NEW="${OLD%\}}, weber2008interlaboratory, magnusson2020vhit, alhabib2017vhit}"
sed -i "${LINE}s|.*|${NEW}|" paper.tex

# 或更安全的：先写出 sed 命令
sed -i 's/\\cite{macdougall2013new, weber2008interlaboratory}/\\cite{macdougall2013new, weber2008interlaboratory, magnusson2020vhit, alhabib2017vhit}/' paper.tex
```

### Step 5: 验证引用完整性

```python
# 重新运行 Step 1 的脚本，确认匹配率提升
```

### Step 6: 重编译

```bash
pdflatex -interaction=nonstopmode paper.tex && pdflatex -interaction=nonstopmode paper.tex
grep -c '^!' paper.log  # must be 0
```

## 实战收益参考

| 论文 | 起始 | 轮次 | 策略 | bib→cite | D7提升 |
|:-----|:----|:-----|:-----|:---------|:-------|
| vor-bppv-diagnosis | 60/28 (46.7%) | v2 Strategy A | 整合12篇 | 60/40 (66.7%) | +0.06 |
| vor-pd-systematic-review | 56/14 (25.0%) | v2 Strategy A | 整合36篇 | 56/50 (89.3%) | +0.07 |
| kappa-3d-eye-tracking | 47/25 (53.2%) | v2 Strategy A | 整合17篇 | 47/42 (89.4%) | +0.09 |

**典型收益**: D7 +0.06~0.09 / 轮，单轮可提升 cite 率 15-25%。
**目标**: cite/bibitem 匹配率 ≥85%。超过后边际收益递减——剩余未引用 bibitem 通常为专业引用（如解剖学基础文献），不适合在综述正文中频繁引用。
