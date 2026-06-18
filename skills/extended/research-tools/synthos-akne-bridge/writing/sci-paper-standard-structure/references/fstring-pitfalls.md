# Python F-String LaTeX Pitfalls

> 在 Python 中生成 LaTeX 代码时，`\` 开头的命令会被 f-string 错误解析。

## 问题

```python
# ❌ 错误: r"""...\bibliography{references}..."""
# 在 r""" 中 \b 保留为 \b，但某些嵌套场景会破坏
paper = r"""\bibliographystyle{plainnat}
\bibliography{references}"""

# 如果通过 f-string 拼接:
# rf""" 或 f""" 会处理 \b, \c, \n 等转义
```

## 受影响的 LaTeX 命令

| 命令 | 问题 | 表现 |
|:-----|:-----|:-----|
| `\bibliographystyle` | `\b` → 退格 (0x08) | `^Hibliographystyle` |
| `\bibliography` | `\b` → 退格 | `^Hibliography` |
| `\begin` | 安全 | — |
| `\cite` | `\c` 在某些 locale 中变化 | 罕见 |
| `\section` | 安全 | — |
| `\textbf` | 安全 | — |

## 最佳实践

### 方案1: 用 r""" 包裹完整内容（推荐）
```python
paper = r"""\bibliographystyle{plainnat}
\bibliography{references}
"""
```
注意：r""" 不能包含 f-string 插值（`{var}`）。

### 方案2: 分离 LaTeX 命令
```python
bibstyle = "\\bibliographystyle{plainnat}"
bibcmd = "\\bibliography{references}"
paper = bibstyle + "\n" + bibcmd
```

### 方案3: 后置修复
```python
content = open('paper.tex').read()
content = content.replace('\x08', '\\')  # 修复所有退格符
content = content.replace('\\x08', '\\')
with open('paper.tex', 'w') as f:
    f.write(content)
```

### 方案4: 验证
编译前检查：
```bash
cat -A paper.tex | grep -E "\\^H" && echo "ERROR: backspace chars found" || echo "OK"
```
