# Agent Scripting Patterns — Avoiding Common Pitfalls

> Hermes Agent 环境下编写 `execute_code` + `terminal()` 的常见陷阱和正确模式

## 嵌套 f-string 陷阱（Nested f-string Trap）

### 问题

在 `execute_code`（Python 沙箱）中调用 `terminal()` 时，如果 shell 命令里又嵌套了一层 `python3 -c '...'` 并使用了 Python f-string 进行格式化，会产生多层引号转义冲突：

```python
# ❌ 错误：嵌套 f-string 中的 \\ 反斜杠会触发 SyntaxError
r = terminal(f"cd {PROJ} && python3 -c \"print(f'{d.get(\\\"key\\\",\\\"?\\\")}')\"")
# SyntaxError: f-string expression part cannot include a backslash
```

### 根因

Python 的 f-string 表达式内部不允许 `\\` 反斜杠转义。当外层 f-string（`f"..."`）需要生成内层 Python 代码中的双引号时，多层嵌套导致转义链断裂。

### 正确模式

**模式 1：先读文件到变量，本地处理**

```python
# ✅ 正确：用 read_file 或者先终端输出到变量
from hermes_tools import terminal

# 先把数据读出来存到变量
r = terminal("cat /path/to/file.json", timeout=5)
import json
data = json.loads(r['output'])
# 本地处理，无需再套 f-string
print(f"Key: {data.get('key', '?')}")
```

**模式 2：用临时脚本文件**

```python
# ✅ 正确：将复杂逻辑写入临时文件后执行
terminal("cat > /tmp/script.py << 'EOF'", timeout=3)
terminal("""
import json
d = json.load(open('data.json'))
print(f"Key: {d.get('key', '?')}")
""", timeout=5)
terminal("python3 /tmp/script.py", timeout=10)
```

**模式 3：单层 shell + 简单处理**

```python
# ✅ 正确：用 shell 的 jq/grep 替代内层 python
r = terminal("grep 'version:' SKILL.md | cut -d':' -f2", timeout=5)
```

**模式 4：避免 f-string，用 .format() 或 % 格式化**

```python
# ✅ 正确：用 .format() 替代嵌套 f-string
r = terminal("python3 -c 'import json; d=json.load(open(\"file.json\")); print(d.get(\"key\",\"?\"))'", timeout=5)
# 在 execute_code 里，普通字符串（非 f-string）的转义规则是标准的
```

### 快速识别

| 信号 | 问题 | 应对 |
|:-----|:-----|:-----|
| `SyntaxError: f-string expression part cannot include a backslash` | 嵌套 f-string 中的 `\\` | 换用模式1或4 |
| `NameError: name 'd' is not defined` | f-string 中的 `{d...}` 被外层 f-string 误解析 | 双重大括号 `{{d...}}` 或换用 .format() |
| 命令超时但逻辑正确 | `source add` 等长等待操作 | 加 `--timeout 600` 参数 |
| JSON 解析失败但有 `{` | 字符串含有 "Matched:" 等前缀行 | `tail -n +2` 跳过首行 |

### 通用原则

1. **单层优先**：能直接 shell 处理的不用嵌套 python
2. **读→处理的分离**：先用 `terminal()` 读数据到变量，然后本地 Python 处理，不在同一个调用中混用
3. **外层引号用双引号，内层用单引号**：`f"shell '{python_code}'"` 比反过来更易阅读
4. **复杂逻辑写文件**：超过 3 行的 Python 逻辑应写入临时文件再执行
