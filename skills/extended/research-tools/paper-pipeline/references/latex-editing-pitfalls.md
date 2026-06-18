# LaTeX文件编辑陷阱与安全操作

## 致命陷阱：patch工具双转义反斜杠

`skill_manage(action='patch')` 在操作 `.tex` 文件时，会**双重转义所有LaTeX反斜杠**：
- `\subsection` → `\\subsection`  → PDF编译报错
- `\cite{...}` → `\\cite{...}`  → 引用丢失
- `\textbf{...}` → `\\textbf{...}` → 格式丢失

**根本原因**：patch工具将LaTeX的单 `\` 视为转义字符并在写入时再加一层转义。

## 安全操作方式

### ✅ 推荐：整文件重写（write_file）

```python
from hermes_tools import terminal, write_file

# 1. 用terminal读整个文件（注意50KB stdout限制！）
r = terminal('cat /path/to/file.tex')

# 2. 在Python中修改内容
content = r['output']
content = content.replace('old_text', 'new_text')

# 3. 用write_file整文件写回
write_file('/path/to/file.tex', content)
```

### ⚠️ 50KB stdout截断陷阱

`terminal('cat large_file.tex')` 受50KB stdout限制——大文件的内容会被静默截断。感染症状：
- 长行被截断（如算法环境、长段落）
- 丢失内容导致 `Extra }, or forgotten \endgroup` 错误
- 花括号不平衡

**规避**：对>30KB的文件，先用 `read_file` 确认总行数，若截断用分段读取合并。

### ✅ 次选：sed单行替换

```bash
# 直接操作文件字节，无转义问题
sed -i 's/old_text/new_text/g' file.tex
```

### ❌ 避免：patch（patch工具）

除非目标字符串完全不含反斜杠（如替换普通文本段落），否则不要用patch改LaTeX。

## 陷阱4：patch工具感染inline math命令（$\\rightarrow$ → 文本"rightarrow"）

**问题**：当 `patch` 工具修改含 `$\\rightarrow$`（单反斜杠）的段落时，inline math 内的反斜杠也被双转义，变成 `$\\\\rightarrow$`（双反斜杠）。

**表现**：
- 编译不报错（无 LaTeX Error）
- PDF中箭头渲染为英文文本"rightarrow"而非右箭头符号`→`
- 用 `pdftotext` 可检测：文本"rightarrow"出现在非代码上下文中

```bash
# 检测方法：pdftotext提取文本，寻找未渲染的LaTeX命令名称
pdftotext paper.pdf - | grep -i 'rightarrow'
# 若找到"rightarrow"文字，说明渲染失败
```

**根因确认**（用cat -A查看原始字节）：
```bash
# 正确：$\\rightarrow$ （1个反斜杠→LaTeX命令）
# 错误：$\\\\rightarrow$ （2个反斜杠→LaTeX视为行内换行+文本）
sed -n '230p' paper.tex | cat -A
```
**字节级精确修复**（推荐，不影响其他双反斜杠如 `\\\\` 表行尾）：

```python
# 基础模式：修复 $\\\\rightarrow$
with open('paper.tex', 'rb') as f:
    data = bytearray(f.read())
pattern = b"$\\\\rightarrow$"  # 2 backslash bytes
fix = b"$\\\\rightarrow$"       # 1 backslash byte
data = data.replace(pattern, fix)
with open('paper.tex', 'wb') as f:
    f.write(data)
```

**v2.0: 万能字节级修补器（已验证 2026-05-24）** — 当 `patch` 工具同时破坏 `\\textbf` 和 `\\bottomrule` 等命令时，用精确查找+逐字节修复：

```python
with open('paper.tex', 'rb') as f:
    data = bytearray(f.read())

# 找到被破坏的特定区域
target = b"\\textbf{1,540+}"  # 查找已知的目标文本
idx = data.find(target)
if idx >= 0:
    # 检查前面是否有双反斜杠（表示被破坏）
    if data[idx-2:idx] == b"\\\\":
        # 修复：2个反斜杠 → 1个反斜杠（向左缩小1字节）
        data[idx-2:idx] = b"\\"
        idx -= 1  # 索引前移

    # 检查 bottomrule 前的反斜杠数量
    bottomrule_marker = b"\\bottomrule"
    bidx = data.find(bottomrule_marker, idx)
    if bidx > 0:
        # 数一下 bottomrule 前的反斜杠
        count = 0
        pos = bidx - 1
        while pos >= 0 and data[pos] == 0x5c:  # 0x5c = backslash byte
            count += 1
            pos -= 1
        # 应该是3个（\\\\ = 换行 + \\\\bottomrule = 命令）
        if count > 3:
            extra = count - 3
            data[bidx-extra:bidx] = b""

with open('paper.tex', 'wb') as f:
    f.write(data)
```

**原理**：字节级操作不受字符串转义影响。`\\\\` 在字节数组中就是两个 0x5c 字节，直接比较和替换，不涉及 Python 字符串的 `\\` 转义规则。可以精准修复 patch 工具造成的局部双反斜杠，同时不影响正常 `\\\\`（如表格行尾换行符）。

**编译 → 验证 → 确认修复**三步确认法：
```bash
xelatex paper.tex
pdftotext paper.pdf - | grep -c "rightarrow"  # 应为0
```

## 编译后验证清单（P4质量门用）

1. `pdflatex` 编译通过（无 `! LaTeX Error`）
2. 无 `Undefined citation` 警告（需两次编译）
3. 花括号平衡（`python3 -c "print(open('f.tex').read().count('{') == open('f.tex').read().count('}'))"`）
4. PDF页数合理（无内容丢失）
5. 关键内容（图、表、算法、附录）肉眼核查

## 陷阱2：read_file 包含行号前缀

**问题**：`read_file()` 返回的内容带有行号前缀 `1|`、`2|` 等显示格式。

**表现**：
```
1|% This is the first line
2|
```

**后果**：如果用输出的内容直接写入文件，每行开头会多出 `行号|`，导致LaTeX完全无法编译。

**修复方法**：
```bash
python3 -c "import re; f=open('damaged.tex','r'); c=f.read(); f.close(); open('fixed.tex','w').write(re.sub(r'^\s*\d+\|', '', c, flags=re.MULTILINE))"
```

**何时使用 `read_file()`**：仅用于查看内容。绝不用于读取后重建文件。

## 陷阱3：terminal('cat') 截断大文件（~50KB限制）

**问题**：`terminal('cat ...')` 的 stdout 输出在约50KB处被截断。

**表现**：文件内容不完整，出现 `[OUTPUT TRUNCATED]` 标记。

**后果**：算法块、长段落丢失。

**安全方案**：使用 `execute_code` 的 Python 环境直接读取：
```python
with open('/path/to/file.tex', 'r') as f:
    content = f.read()
```

## 已知错误模式速查

| 症状 | 根因 | 修复 |
|------|------|------|
| `! Missing \begin{document}` | read_file行号前缀写入文件 | 用regex移除前缀 |
| `! Undefined control sequence` | patch双转义反斜杠 | 全局 sed 修复 |
| `! Incomplete \iffalse` | cat截断导致环境未关闭 | 重建正确内容 |
| `! Extra }, or forgotten \endgroup` | 花括号不匹配 | 检查braces平衡 |

## 陷阱6：read_file 内部截断 + write_file 链式损坏（超静默数据丢失）

**问题**：`read_file()` 本身也有截断限制（与 `terminal('cat')` 的50KB stdout截断不同，这是API内部的limit/offset分页机制）。当文件较大时，`read_file()` 返回 `"truncated": true` 的标记，但**返回的内容本身已经是不完整的**。

**链式破坏路径**：
```
执行代码中用 read_file() 读取大.tex文件
  ↓
返回内容已截断（truncated=true但未检查）
  ↓
Python代码修改内容后 write_file() 写回
  ↓
文件被截断为 read_file() 返回的部分！
  ↓
大量内容（Conclusion/Bibliography/\end{document}）静默丢失
  ↓
pdflatex报 Missing \begin{document}
```

**实战案例**（2026-05-25）：用 `read_file()` 读取73KB的 paper.tex（741行），因为 `read_file` 的 limit 分页只返回了 ~530行，修改其中一行后用 `write_file` 写回，文件从741行变为529行——整个 Translation Barriers 节（含6个Barrier）、RVO-AIRS框架、Priority Future Directions、Limitations、Conclusion、Bibliography（81+15=96 bibitem）全部丢失。

**关键差异**：这不是 `terminal('cat')` 的50KB stdout截断——两者是独立的截断机制。即使文件<50KB，read_file也可能因其内部limit/offset分页机制而截断。`return "truncated": true` 不会阻止 write_file 写入不完整内容。

### 检测

```bash
# read_file 输出含 truncated=true
# 但 write_file 已经写了不完整的版本

# 症状1: 文件行数明显减少
wc -l paper.tex  # 如 529 vs 预期 741+15

# 症状2: 缺少关键章节
grep -c '\\\\end{document}' paper.tex  # 应为 1
grep -c '\\\\begin{thebibliography}' paper.tex  # 应为 1

# 症状3: 编译报 Missing \\begin{document}
pdflatex paper.tex 2>&1 | grep "Error"
```

### 预防

**铁律**：任何涉及 `read_file()` → 修改 → `write_file()` 的链式操作，必须在写文件前执行以下验证：

```python
# 在 write_file 前强制验证
r = read_file('/path/to/paper.tex')
content = r['content']  # 可能是截断的！

# 验证1: 检查 truncated 标记
if r.get('truncated', False) or r.get('total_lines', 0) < expected_min_lines:
    raise ValueError(f"read_file returned TRUNCATED content ({r.get('total_lines',0)} lines vs expected {expected_min_lines})")

# 验证2: 检查关键章节完整
assert '\\\\end{document}' in content, "Missing end{document}! Read was truncated"
assert '\\\\begin{thebibliography}' in content, "Missing bibliography! Read was truncated"

# 验证3: 文件大小合理（无断崖式下降）
if len(content) < 30000:  # 阈值取决于具体文件
    raise ValueError("Content too small, likely truncated")
```

**推荐替代方案**：LaTeX编辑永远优先使用 `terminal` 中的 `sed` 或 `python3 << 'PYEOF'` heredoc（用 `with open()` 直接操作文件系统），而非 `read_file/write_file` 管道。

### 截断恢复

当发现文件已被 write_file 截断后：

```bash
# Step 1: 用 sed 清理 read_file 留下的行号前缀（如果有）
sed -i 's/^[[:space:]]*[0-9]*|[[:space:]]*[0-9]*|//' paper.tex
sed -i 's/^[[:space:]]*[0-9]*|//' paper.tex

# Step 2: 检查还剩什么
wc -l paper.tex
grep -n '\\\\section\|\\\\subsection' paper.tex | tail -5

# Step 3: 重建缺失内容（追加模式）
# 用 python3 << 'PYEOF' heredoc 构造完整缺失段落
# 用 with open('paper.tex', 'a') 追加写回
```

**实战恢复模板**（追加多个缺失章节）：
```python
# 在 heredoc 中构造并追加
append_text = r"""
\subsection{Missing Section Title}

Content of the missing section...

\subsection{Another Missing Section}
...

\begin{thebibliography}{99}
\bibitem{Ref1} ...
\bibitem{Ref2} ...
\end{thebibliography}

\end{document}
"""

with open('paper.tex', 'a') as f:
    f.write(append_text)

# 验证
with open('paper.tex') as f:
    c = f.read()
assert '\\\\end{document}' in c
```

## 陷阱5：Python open() 行级插入匹配错误锚点导致文件截断

**问题**：用 Python `open()` + `split('\n')` 进行行级插入时，使用通用锚点（如 `\end{enumerate}`）匹配到**错误的位置**，导致内容插入在错误的章节，且 join-back 时可能丢失后续内容。

**实战案例**（2026-05-25）：试图在 Introduction 的贡献列表（第一个 `\end{enumerate}`）后插入比较表，但代码匹配到了 Methods 的纳入标准列表（第二个 `\end{enumerate}`）。插入后 `'\n'.join(lines)` 丢失了 371 行内容（整个 Conclusion + Bibliography + `\end{document}`），文件从 894 行截断为 523 行，编译报 `Missing \begin{document}`。

**根因**：Python 代码用以下模式查找第二个 `\end{enumerate}`：
```python
for i, line in enumerate(lines):
    if '\\end{enumerate}' in line:
        count += 1
        if count == 2:
            idx1_line = i
            break
```
当文档中有多个 `\end{enumerate}` 时，计数偏移一个就插错了位置。

**症状**：
- `Missing \begin{document}` 编译错误（但文件头上确实有）
- 文件行数明显少于预期（如 523 vs 894）
- `\end{document}` 不存在

**修复方法**（恢复被截断的文件）：
```bash
# 情况A：如果原内容还存在记忆/缓存中
# 最佳方案：write_file 整文件重写（从记忆中的正确版本重建）

# 情况B：如果 git 有备份
git checkout -- paper.tex

# 情况C：无备份 → 从 PDF 提取已有内容 + 手动补全末尾缺失的章节
```

### 安全 Python 插入模式（已验证 2026-05-25）

使用 `str.find()` + 唯一上下文锚点，**不用行计数**：

```python
# ❌ 危险：行计数+通用锚点
lines = content.split('\n')
count = 0
for i, line in enumerate(lines):
    if '\\end{enumerate}' in line:
        count += 1
        if count == 2:
            # 插入了错误位置！
            break

# ✅ 安全：唯一上下文锚点
# 找到贡献列表的结束（其后的文字是 METHODS 章节标题）
anchor = "\\end{enumerate}\n\n%\n% ============================================================\n% 2. METHODS"
idx = content.find(anchor)
if idx > 0:
    # 在 anchor 前插入新内容
    insert_text = "\\end{enumerate}\n\n\\begin{table}[htbp]\n...\n\\end{table}\n\n%"
    content = content[:idx] + insert_text + content[idx:]
```

**关键原则**：
1. **使用 `str.find()` 而非 `split('\n')` + 行计数** — 字符串查找能匹配跨行上下文
2. **锚点至少包含跳转位置前后各 2-3 行** — 消除歧义（`\end{enumerate}` 太短，用 `end{enumerate} + 注释行 + section 标题`）
3. **整个文件操作，不 split/join** — 避免 `'\n'.join(lines)` 把段落内的换行合并打散
4. **验证三要素**：写入后立即检查 `\end{document}` 存在、文件行数合理(±10%)、花括号平衡

### 安全插入脚本模板

```python
# 模板：在 LaTeX 文件中插入内容（使用唯一锚点）
with open('paper.tex', 'r') as f:
    content = f.read()

# Step 1: 找到目标位置（唯一上下文，至少3行）
anchor = "目标位置的上下文文本\n至少3行\n包含注释和下一节的标题"
idx = content.find(anchor)

if idx >= 0:
    # Step 2: 构造插入内容（含 anchor 重复以替换）
    new_content = insert_text + "\n" + anchor
    content = content[:idx] + new_content + content[idx + len(anchor):]
    
    # Step 3: 验证
    assert '\\end{document}' in content, "丢失 \\end{document}!"
    assert abs(len(content.split('\\n')) - original_line_count) < 50
    
    with open('paper.tex', 'w') as f:
        f.write(content)
else:
    print(f"锚点未找到: {anchor[:40]}...")
```

## 安全编辑工作流（v2 更新版）

```
小修改（<3处, 无歧义锚点）:
  -> execute_code: Python with open() + str.find() 单一锚点替换
     ⚠️ 不要用 split('\\n') + line counting

多定位点替换（3-6处, 已知字符串）:
  -> terminal: python3 << 'PYEOF' heredoc
     ✅ 最安全的大文件多点编辑方式
     ✅ 无 read_file 截断风险
     ✅ 无 patch 双转义风险
     ✅ 用 with open() 直接操作文件系统
  ⚠️ 替换字符串中的 \\cite{...} 在Python单引号字符串中保持单反斜杠即可
  
大修改/重写:
  -> write_file 完整重写（构造全部内容）

大文件（>50KB）:
  -> Python with open() 在 execute_code 或 terminal heredoc 中操作
     ⚠️ 用 str.find() + 多行锚点，不用行分割

插入内容到特定位置:
  -> str.find(unique_anchor) + 字符串替换
  -> 锚点至少含目标位置前后各2-3行内容消除歧义

写入后验证:
  -> assert '\\\\end{document}' in content
  -> assert abs(new_line_count - expected) < 50
  -> assert '\\\\begin{thebibliography}' in content (if applicable)
```

### ✅ Python heredoc 模板（终端安全多点编辑）

```bash
python3 << 'PYEOF'
with open('/path/to/paper.tex', 'r') as f:
    content = f.read()

# 替换1
content = content.replace(
    'old text 1',
    'new text 1'
)

# 替换2
content = content.replace(
    'old text 2',
    'new text 2'
)

# ... 更多替换

# 验证完整性
assert '\\end{document}' in content
assert content.count('\\begin{thebibliography}') == 1
print(f"File size: {len(content)} bytes")

# 写入
with open('/path/to/paper.tex', 'w') as f:
    f.write(content)
print("Done!")
PYEOF
```

## 文件损坏恢复

当 `.tex` 文件被 `read_file` 行号前缀或 `cat` 输出截断污染后，出现文字 `[OUTPUT TRUNCATED]` 或 `行号|` 前缀：

### 检测

```bash
# 检查行号前缀
head -5 damaged.tex | cat -A
# 应看到 1|% Synthos... 等

# 检查截断标记
grep -c 'TRUNCATED' damaged.tex

# 检查brace平衡
python3 -c "print(open('f.tex').read().count('{') == open('f.tex').read().count('}'))"
```

### 修复步骤

**情况A：行号前缀污染**
```bash
python3 -c "
import re
with open('damaged.tex') as f:
    c = f.read()
c = re.sub(r'^\s*\d+\|', '', c, flags=re.MULTILINE)
with open('fixed.tex', 'w') as f:
    f.write(c)
"
```

**情况B：截断标记污染**（文件含 `[OUTPUT TRUNCATED]` 文字）
```bash
python3 << 'PYEOF'
with open('corrupted.tex') as f:
    lines = f.readlines()

# 找到截断区域
start = end = None
for i, line in enumerate(lines):
    if 'TRUNCATED' in line:
        start = i - 2  # 2行前
    if 'fragment that should follow' in line:  # 替换为实际跟随片段
        end = i + 1

# 用正确内容替换
replacement = open('correct_content.txt').read().split('\n')
new_lines = lines[:start] + replacement + lines[end:]
with open('fixed.tex', 'w') as f:
    f.writelines(new_lines)
PYEOF
```

**情况C：双转义反斜杠**
```bash
# 批量修复常见LaTeX命令
sed -i 's/\\\\\\\\subsection/\\subsection/g; s/\\\\\\\\section/\\section/g; s/\\\\\\\\label/\\label/g; s/\\\\\\\\textbf/\\textbf/g; s/\\\\\\\\emph/\\emph/g; s/\\\\\\\\texttt/\\texttt/g; s/\\\\\\\\cite/\\cite/g; s/\\\\\\\\begin/\\begin/g; s/\\\\\\\\end/\\end/g; s/\\\\\\\\url/\\url/g; s/\\\\\\\\ref/\\ref/g; s/\\\\\\\\item/\\item/g' file.tex

# 但要注意 tabular 中的 \\midrule, \\bottomrule, \\toprule 必须保留 \\\\（行尾换行符）
# 如果在上述修复中被过度修正, 用以下补偿:
sed -i 's/\\\\midrule/\\\\\\midrule/g; s/\\\\bottomrule/\\\\\\bottomrule/g; s/\\\\toprule/\\\\\\toprule/g' file.tex
```

### 陷阱4：patch工具感染inline math命令（$\\rightarrow$ → 文本"rightarrow"）

**问题**：当 `patch` 工具修改含 `$\\rightarrow$`（单反斜杠）的段落时，inline math 内的反斜杠也被双转义，变成 `$\\\\rightarrow$`（双反斜杠）。

**表现**：
- 编译不报错（无 LaTeX Error）
- PDF中箭头渲染为英文文本"rightarrow"而非右箭头符号`→`
- 用 `pdftotext` 可检测：文本"rightarrow"出现在非代码上下文中

```bash
# 检测方法：pdftotext提取文本，寻找未渲染的LaTeX命令名称
pdftotext paper.pdf - | grep -i 'rightarrow'
# 若找到"rightarrow"文字，说明渲染失败
```

**根因确认**（用cat -A查看原始字节）：
```bash
# 正确：$\\rightarrow$ （1个反斜杠→LaTeX命令）
# 错误：$\\\\rightarrow$ （2个反斜杠→LaTeX视为行内换行+文本）
sed -n '230p' paper.tex | cat -A
```
**字节级精确修复**（推荐，不影响其他双反斜杠如 `\\\\` 表行尾）：

```python
# 基础模式：修复 $\\\\rightarrow$
with open('paper.tex', 'rb') as f:
    data = bytearray(f.read())
pattern = b"$\\\\rightarrow$"  # 2 backslash bytes
fix = b"$\\\\rightarrow$"       # 1 backslash byte
data = data.replace(pattern, fix)
with open('paper.tex', 'wb') as f:
    f.write(data)
```

**v2.0: 万能字节级修补器（已验证 2026-05-24）** — 当 `patch` 工具同时破坏 `\\textbf` 和 `\\bottomrule` 等命令时，用精确查找+逐字节修复：

```python
with open('paper.tex', 'rb') as f:
    data = bytearray(f.read())

# 找到被破坏的特定区域
target = b"\\textbf{1,540+}"  # 查找已知的目标文本
idx = data.find(target)
if idx >= 0:
    # 检查前面是否有双反斜杠（表示被破坏）
    if data[idx-2:idx] == b"\\\\":
        # 修复：2个反斜杠 → 1个反斜杠（向左缩小1字节）
        data[idx-2:idx] = b"\\"
        idx -= 1  # 索引前移

    # 检查 bottomrule 前的反斜杠数量
    bottomrule_marker = b"\\bottomrule"
    bidx = data.find(bottomrule_marker, idx)
    if bidx > 0:
        # 数一下 bottomrule 前的反斜杠
        count = 0
        pos = bidx - 1
        while pos >= 0 and data[pos] == 0x5c:  # 0x5c = backslash byte
            count += 1
            pos -= 1
        # 应该是3个（\\\\ = 换行 + \\\\bottomrule = 命令）
        if count > 3:
            extra = count - 3
            data[bidx-extra:bidx] = b""

with open('paper.tex', 'wb') as f:
    f.write(data)
```

**原理**：字节级操作不受字符串转义影响。`\\\\` 在字节数组中就是两个 0x5c 字节，直接比较和替换，不涉及 Python 字符串的 `\\` 转义规则。可以精准修复 patch 工具造成的局部双反斜杠，同时不影响正常 `\\\\`（如表格行尾换行符）。

**编译 → 验证 → 确认修复**三步确认法：
```bash
xelatex paper.tex
pdftotext paper.pdf - | grep -c "rightarrow"  # 应为0
```

## 陷阱7：patch工具 replace_all=True 导致 bib 文件爆炸式重复

**问题**：用 `skill_manage(action='patch', replace_all=True)` 在 `.bib` 文件中添加多个新条目时，若 `old_string` 太泛化（如条目结尾+下一条目开头的公共模式），`replace_all=True` 会匹配 bib 文件中 **每一个** 条目的结尾，在每个条目后都插入新条目块。结果文件从 ~300 行膨胀到 ~1800 行。

**实战案例**（2026-06-01）：用泛化模式 `  doi = {...},\n}\n\n@Article{Xxx,...` 追加 5 个新 bib 条目。`replace_all=True` 把每个条目都匹配了，5 个条目 × 30 处插入 = 150+ 个重复条目。

**安全方法**：
- ✅ 直接 append：`cat new.bib >> references.bib`
- ✅ 整文件重写：`python3 -c "open('f.bib','w').write(open('f.bib').read()+open('new.bib').read())"`
- ❌ 避免：`patch` + `replace_all=True` 在 bib 中插内容

**检测**：写入后 `wc -l refs.bib` 确认无异常暴增。

## 编译后验证清单（P4质量门用）提升版

1. `pdflatex` 编译通过（无 `! LaTeX Error`）
2. 无 `Undefined citation` 警告（需两次编译）
3. 花括号平衡
4. PDF页数合理（对比期望页数）
5. 关键内容（图、表、算法、附录）肉眼核查
6. **无 `[OUTPUT TRUNCATED]` 文字残留**
7. **无行号前缀 `数字|` 残留**
8. **无 `\\\\command` 双转义模式**（检查所有 `\\[a-z]` 开头的命令）
