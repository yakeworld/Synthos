# Python 转义三层陷阱：shell → Python → regex

> 编辑 LaTeX 文件时引用此文件。凡是涉及 `\cite{}` 的 Python 字符串操作，都必须按此规则正确转义。

## 核心规则

文件中的目标: `\cite{key}`     (1个反斜杠)

| 执行方式 | str.replace / 字串 | re.findall (正则) |
|:---------|:-------------------|:-------------------|
| `.py` 脚本 | `'\\cite{'` (双斜杠) | `r'\\cite{'` (raw双斜杠) |
| `python3 -c` | `'\\\\cite{'` (四斜杠) | `r'\\\\cite{'` (raw四斜杠) |

## 三层为什么不同

```
.py 文件:   Python字面量 → str
             '\\cite{'  →  输出 \cite{   ✓

python3 -c: Bash         → Python字面量 → str
             '\\\\cite{'  →  经bash: \\cite{  →  输出 \cite{   ✓
```

shell 会吃掉一层 `\\` → `\`，所以 `.py` 里写 `\\` 的地方在 `python3 -c` 里要写 `\\\\`。

## 验证方法

每次替换后立即验证：
```python
result = tex.replace(old, new)
assert 'NewBibKey' in result, f'REPLACEMENT FAILED: NewBibKey not in result'
# 再写文件
with open('paper.tex', 'w') as f: f.write(result)
```

## 常见错误模式

| 错误写法 | 实际效果 | 问题 |
|:---------|:---------|:-----|
| `.py` 中 `'\\\\cite{'` | 字符串是 `\\cite{` (2斜杠) | 不匹配文件 `\cite{` (1斜杠) |
| `python3 -c` 中 `'\\cite{'` | bash吃一层变 `'cite{'` | Python中 `\c` 不是合法转义 |
| 正测 `r'\cite{'` | regex 崩溃 | `\c` 不是有效 regex 转义 |
