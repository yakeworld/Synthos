# Todo论文迁移：语义化 \cite{} 插入技法

> 2026-05-31 实战提炼。从 _todo/ 迁移论文时，bib 清理（删除僵尸+添加新引用）后需要将新引用插入 .tex 正文。以下是高效、准确的操作模式。

## 核心流程

```
提取tex所有cite组 → 理解每组上下文主题 → 匹配僵尸/新引用的主题 → 追加到对应组 → 编译验证
```

## Step 1: 提取现有 cite 组

```python
lines = [l for l in tex.split('\n') if not l.strip().startswith('%')]
active_tex = '\n'.join(lines)
cite_groups = re.findall(r'\\cite[tp]?\s*\{([^}]+)\}', active_tex)
```

输出示例：
```
Group 0: ['Daugman2007']          # → Iris recognition intro
Group 4: ['Wildes1997']          # → Iris normalization definition
Group 5: ['zhu2004robust']       # → Torsional eye movement tracking
Group 7: ['kothari2021ellseg']   # → Iris-sclera boundary ellipse fitting
```

## Step 2: 理解每个组的上下文

用 `grep -n` 定位每个 cite 组所在的句子，理解它在讲什么：

```bash
grep -n '\\\\cite{Wildes1997}' paper.tex  # → 查看前后文
```

## Step 3: 主题匹配（引用→上下文映射）

| 僵尸/新引用 | 主题 | 插入到哪个组 |
|:------------|:-----|:-------------|
| Bowyer2008 (iris survey) | Iris recognition survey | Daugman2007 或 Wildes1997 (iris介绍处) |
| Ma2004 (Gabor iris) | Iris recognition method | Daugman2007 (iris背景处) |
| Proenca2010 (UBIRIS dataset) | Iris dataset | Wildes1997 (iris normalization处) |
| cai2021landmark (eye seg) | Eye segmentation | kothari2021ellseg (iris boundary处) |
| fuhl2016pupil (pupil detection) | Pupil/eye tracking | zhu2004robust (torsional movement处) |
| Palmero2020 (OpenEDS dataset) | Iris segmentation dataset | rakshit2007pupil (Fourier boundary处) |

## Step 4: 三种插入方式

### 方式 A: 追加到现有组（最常用）

将新键追加到现有 \cite{} 组末尾，用逗号分隔：

```python
# 旧: \cite{Wildes1997}
# 新: \cite{Proenca2010, Wildes1997, He2009, Sun2005}
tex = tex.replace('\\cite{Wildes1997}',
                  '\\cite{Proenca2010, Wildes1997, He2009, Sun2005}', 1)
```

**排序规则**：旧键在前 + 新键在后（保持原有引用优先级）。不要打乱原有序。

### 方式 B: 插入到句子间（新建 cite 组）

在现有句子中插入一个引用性短语，然后加 \cite{}：

```python
# Before: "the reliability of ellipse fitting in oculometric analysis."
# After:  "the reliability of ellipse fitting in oculometric analysis \cite{Chaudhary2019, cai2021landmark}."
tex = tex.replace(
    'the reliability of ellipse fitting in oculometric analysis.',
    'the reliability of ellipse fitting in oculometric analysis \\cite{Chaudhary2019, cai2021landmark}.'
)
```

### 方式 C: 创建新的独立句子（用于奠基/教科书引用）

```python
# Before: "Fundamentally limited by its circular iris boundary assumption..."
# After:  "Fundamentally limited by its circular iris boundary assumption. Standard image processing operations for feature extraction rely on established techniques \cite{gonzales1987digital, mallat1999wavelet}."
tex = tex.replace(
    'Fundamentally limited by its circular iris boundary assumption, failing to adequately address',
    'Fundamentally limited by its circular iris boundary assumption, failing to adequately address. Standard image processing operations for feature extraction rely on established techniques \\cite{gonzales1987digital, mallat1999wavelet}'
)
```

## Step 5: 验证

```bash
# 1. 检查所有新键是否出现在cite组中
grep -o 'Bowyer2008' paper.tex | wc -l  # 应 ≥1

# 2. 检查D10a
python3 -c "
import re
with open('paper.tex') as f:
    lines = [l for l in f if not l.strip().startswith('%')]
cites = re.findall(r'\\\\\\\\cite[tp]?\\s*\\{([^}]+)\\}', '\n'.join(lines))
cited = set(k.strip() for c in cites for k in c.split(','))
with open('references.bib') as f: bib_keys = set(re.findall(r'@\\w+\\{([^,]+),', f.read()))
orphan = cited - bib_keys
print(f'D10a: {len(cited&bib_keys)}/{len(bib_keys)}' if not orphan else f'FAIL orphan={orphan}')
"

# 3. 编译验证
pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper
grep -c 'undefined' paper.log
```

## 已知陷阱

### 1. 🔴 Python 转义三层陷阱：shell → Python → regex（2026-05-31 实战）

**问题**：编辑 .tex 时，Python 中 `\cite` 的转义因执行方式不同而不同，很容易写错导致静默失败。

**根因**：LaTeX 文件存储 `\cite` 为单字符 `\` + `cite`。Python 读取后字符串中是 `\cite`。但 Python 的字符串字面量和 regex 各有自己的转义规则，加上 bash 的转义规则，形成了三层转义。

#### 三场景对照表

| 场景 | 作用层 | 正则 `findall` | 字串 `replace` | 文件里的目标文本 |
|:-----|:-------|:---------------|:---------------|:----------------|
| `.py` 文件中 | Python→regex | `r'\\\\cite{'` | `'\\\\cite{'` | `\cite{` |
| `python3 -c` 中 | Shell→Python→regex | `r'\\\\\\\\cite{'` | `'\\\\\\\\cite{'` | `\cite{` |
| grep 命令行 | Shell→grep | `\\\\cite{` | — | `\cite{` |

**注**：上表是当前文档的常用转义值，但**各列的值实际上不同**——因为 `.py` 文件和 `python3 -c` 的转义层数不同。

#### 实际正确的值

**在 `.py` 脚本文件中**（无 shell 层）：
- `str.replace(old, new)` 的 `old` 字符串：`'\\cite{'` — 非 raw 字符串中 `\\` = 一个 `\`
- `re.findall(r'\\cite{', tex)` — raw 字符串 `r'\\cite{'` = `\`, `\`, `c`, `i`, `t`, `e`, `{`，在 regex 中 `\\` = 匹配字面 `\`

**在 `python3 -c "..."` 中**（有一层 shell 转义）：
- Bash 需要 `\\` 才能产生一个 `\` 给 Python
- Python 再需要 `\\` 才能产生一个 `\` 给字符串
- 所以 `str.replace` 的 old 需要 `'\\\\cite{'`（bash 吃一层变 `\\cite{`，Python 吃一层变 `\cite{`）
- 正则需要 `r'\\\\cite{'`（bash 吃一层变 `r'\\cite{'`，Python 吃一层变 regex 的 `\\cite` 匹配 `\cite`）

#### 快速判定口诀

```
.py 文件里:     Python 字符串里的 \cite 写 '\\cite{'  (双斜杠)
python3 -c:     Python 字符串里的 \cite 写 '\\\\cite{' (四斜杠)
regex (.py):    r'\\cite{'  (双斜杠，因为 raw)
regex (shell):  r'\\\\cite{' (四斜杠，shell吃一层)
```

### 2. 不要打乱现有引用顺序
追加新键到末尾，不要在开头插入。

### 3. latexdiff / 追踪更改
如果论文曾在投稿或 revision，改写句子可能触发 diff。优先用方式 A（追加到现有组）保持最小改动。

### 4. 教科书引用用方式 C
教科书（如 gonzales1987digital, mallat1999wavelet）不适合追加到具体方法/数据集组，需要独立句子。

### 5. sed 逃逸困难
LaTeX 文件中 `\cite{...}\.` 等模式的 sed 替换需要多层转义。推荐用 Python 的 `str.replace()`（简单替换）或 `re.sub()`（模式匹配）。
