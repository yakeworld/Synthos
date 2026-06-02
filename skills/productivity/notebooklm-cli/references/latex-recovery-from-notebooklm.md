# LaTeX Recovery from NotebookLM `source fulltext` Extraction

> 2026-05-24实战：NotebookLM中保存的论文 `.tex`，因本地 `git checkout` 误操作丢失后，通过 `source fulltext` 恢复并修复。

## 触发场景

本地 `.tex` 文件因 `git checkout`、误删除、覆盖等原因丢失，但之前上传到 NotebookLM 的版本还在。需要从 NotebookLM 的 source 恢复 LaTeX 源码。

## 恢复流程

### Step 1: 在 NotebookLM 中找到论文 source

```bash
notebooklm list | grep -i "<project_keyword>"
notebooklm use <partial_id>
notebooklm source list | grep -i -E "synthos|paper|论文"
```

找到匹配的 Markdown/PDF source，记录其 ID。

### Step 2: 提取全文

```bash
notebooklm source fulltext -n <notebook_id> <source_id> -o /tmp/recovered.tex
```

### Step 3: 格式修复

NotebookLM 的 `source fulltext` 输出有以下格式损坏：

| 问题 | 现象 | 修复方法 |
|:-----|:-----|:---------|
| 空白行 | 每两行之间一个空白行（仅含空格） | 正则 `\n\s*\n` → `\n\n`（保留段落分隔） |
| Tabular 碎片 | `\times`, `\checkmark`等符号在独立行上 | 正则 `&\s*\n\\times` → `& $\\times$` |
| 数学模式断裂 | `$\n>0.3\n` → `>` 在单独行 | 正则 `\$\s*\n>\s*\n` → `$>$` |
|  号熔断 | "gap-filling 缺开头 `` | 正则 `\ngap-filling\"` → `` ``gap-filling\" `` |
| 游离 $ | 行尾多余的 `$` 打开数学模式 | 删除奇数个的行尾 `$` |
| `\texttt` 中的 `_` | `hypothesis_{cycle}` 中的 `_` 报错 | 加反斜杠：`hypothesis\_\{cycle\}` |

典型 Python 修复脚本结构：

```python
import re

content = open('/tmp/recovered.tex').read()

# 1. 去空白行
content = re.sub(r'\n\s*\n', '\n\n', content)

# 2. 修复 tabular 碎片
content = re.sub(r'&\s*\n\\times\s*\n\s*&', r'& $\\times$ &', content)
content = re.sub(r'&\s*\n\\checkmark\s*\n\s*&', r'& $\\checkmark$ &', content)
content = re.sub(r'&\s*\n\\bigtriangleup\s*\n\s*&', r'& $\\bigtriangleup$ &', content)

# 3. 修复 \gg 熔断 (CON~\n>\nMEM → CON~$\gg$~MEM)
content = re.sub(r'CON~\s*\n>\s*\nMEM\s*\n>\s*\nCMD\s*\n>\s*\nSKL\s*\n>\s*\n~DEF',
                 r'CON~$\\gg$~MEM~$\\gg$~CMD~$\\gg$~SKL~$\\gg$~DEF', content)

# 4. 修复 → 符号
content = re.sub(r'\s*\n\\rightarrow\s*\n', r'$\\rightarrow$ ', content)

# 5. 修复引号
for word in ['gap-filling', 'nutrition', 'nutrition assessment.', 'saving time', 
             'growth-driven', 'gap analysis', 'fill a gap']:
    content = content.replace(f'\n{word}"', f' ``{word}"')

# 6. 修复 \texttt 中的下划线
content = content.replace(
    r'\texttt{hypothesis_{cycle}.yaml}',
    r'\texttt{hypothesis\_\{cycle\}.yaml}'
)

# 7. 修复游离 $
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip().endswith('$') and line.strip().count('$') % 2 == 1:
        lines[i] = line.rstrip('$\n\r') + '\n'
content = '\n'.join(lines)

with open('/tmp/recovered-fixed.tex', 'w') as f:
    f.write(content)
```

### Step 4: 编译验证

```bash
pdflatex -interaction=nonstopmode /tmp/recovered-fixed.tex 2>&1 | grep -E "Error|Fatal"
```

常见错误及修复：

| 错误 | 根因 | 修复 |
|:-----|:-----|:-----|
| `Missing $ inserted` | 游离的 `$`、裸 `_`、裸 `>` | 检查行尾 `$`，给 `_` 和 `>` 加反斜杠或 $ 模式 |
| `Unicode character 文 not set up` | pdflatex 不支持 CJK 字符 | 用 CJKutf8 包+正确字体，或用英文转写替代 |
| `Misplaced \cr` | tabular 中行结束符 `\\` 在独立行 | 确保 `\\` 与最后单元格内容在同一行 |

## 关键陷阱

1. **不要信任第一次编译** — 即使有 `Missing $` 警告，PDF 也可能产生（前几页正常）。编译完成后务必检查 PDF 全文。
2. **引用未定义是正常的** — 第一次编译没有 `.aux` 和 `.bbl` 文件时，所有 `\cite{}` 都显示 `[?]`。第二次编译后解决。
3. **CJKutf8 + pdflatex 需要字体** — `gbsn`（宋体）字体。MiKTeX 可能缺少。检查：`pdflatex` 报 `! LaTeX Error: Unicode character X not set up` 时，说明字体缺失。替代：用英文转写（如 "Wenyan" 代 "文言"）。
4. **`\n` 不是你写的** — 恢复文本中的 `\n` 是 `source fulltext` 的导出换行格式，不是 LaTeX 控制序列。逐行检查并编译即可。
5. **NotebookLM 中保存的是文本而非格式** — 如果上传的是 PDF，`source fulltext` 只提取纯文本，LaTeX 格式会丢失。确保上传的是 `.tex` 或 `.md` 源文件。
