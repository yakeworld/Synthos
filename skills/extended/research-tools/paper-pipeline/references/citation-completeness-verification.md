# Citation Completeness Verification — 交叉验证 bibitem ↔ cite

> **用途**：在编辑 `bibitem`/`cite` 后（增/删/改引用）和编译前，确保每个 bibitem 都被 cite，且每个 cite 都有对应 bibitem。
> **2026-05-25 实战**：amd-ai-screening v2 添加 10 个新 bibitem 后，5 个 cite 未正确插入 → 脚本实时发现，避免带残缺引用编译。

## 核心验证脚本（Python `re` 模式）

在 `execute_code` 环境中运行：

```python
import re

# 读取论文
path = "/path/to/paper.tex"
with open(path, 'r') as f:
    content = f.read()

# 提取 bibitem 和 cite 键
bib_items = re.findall(r'\\\\bibitem\\{([^}]+)\\}', content)
# 同时处理 \\cite{...}, \\citep{...}, \\citet{...}（elsarticle 变体）
cite_calls = re.findall(r'\\\\cite[tp]?\\{([^}]+)\\}', content)

bib_keys = set(bib_items)
cite_keys = set()
for c in cite_calls:
    for k in c.split(','):
        cite_keys.add(k.strip())

print(f"Bibitems: {len(bib_items)}, Cite calls: {len(cite_calls)}")
print(f"Unique bib: {len(bib_keys)}, Unique cite: {len(cite_keys)}")

uncited = bib_keys - cite_keys
unrefed = cite_keys - bib_keys

if uncited:
    print(f"❌ UNCITED bibitems: {sorted(uncited)}")
if unrefed:
    print(f"❌ UNREFERENCED cites: {sorted(unrefed)}")
if not uncited and not unrefed:
    print("✅ All bibitems matched to cites — clean")
```

### Known pitfall: f-string with backslash

In the `execute_code` sandbox, **f-strings cannot contain backslashes in expression parts**:

```python
# ❌ FAILS with SyntaxError
print(f"Bibitem count: {content.count('\\bibitem{')}")

# ✅ WORKS — assign to variable first
bib_count = content.count('\\bibitem{')
print(f"Bibitem count: {bib_count}")
```

## 对每个新引用做精确验证

当添加了新 bibitem 后（如本次 10 个），检查是否每个都被正确引用：

```python
new_refs = ['Key1', 'Key2', 'Key3', ...]
for ref in new_refs:
    total = content.count(f'\\cite{{{ref}')
    total += content.count(f'\\cite{{{ref},')
    total += content.count(f', {ref}')
    status = "✅" if total > 0 else "❌ NOT CITED"
    print(f"  {ref}: {status}")
```

注意：`\\cite{{Key1}}`, `\\cite{{Key1, Key2}}`, `\\cite{{Key2, Key1}}` 三种格式都要覆盖检测。

## ⚠️ 陷阱：write_file 写入 literal `\\n`

**问题**：使用 `'\\n'.join(lines)` 构造新内容后通过 `write_file` 写入，写入的内容**是字面 `\\n` 文本而非换行符**。

```python
lines = content.split('\\n')
# ... modify lines ...
new_content = '\\n'.join(lines)   # ❌ 写入后是 literal \\n（会被解释为反斜杠+n）
write_file(path, new_content)     # 文件内容: line1\\nline2\\nline3
```

**根因**：`write_file` 将字符串逐字写入，不解释转义序列。`'\\n'` 在 Python 中就是两个字符 `\\` 和 `n`。

**修复**：

```python
# 方法1：用真实换行符 join
new_content = '\\n'.join(lines)   # 还是 '\\n'...

# ✅ 正确：
new_content = '\n'.join(lines)    # 不含反斜杠，就是换行符实际字节

# 方法2：读取后修复（如果已经写入了错误内容）
with open(path, 'r') as f:
    raw = f.read()
# 检查是否有 literal \\n
if '\\n' in raw[:500]:
    fixed = raw.replace('\\n', '\n')
    with open(path, 'w') as f:
        f.write(fixed)

# 方法3（推荐）：直接在 execute_code 中用 Python open() 写入
with open(path, 'w') as f:
    f.write(new_content)           # open() 正常解释转义序列
```

**首选工作流**：在 `execute_code` 中全程使用 Python `with open()` 读写（而非 split/join + write_file），避免转义问题。

## 完整编辑+验证工作流

```python
path = "/path/to/paper.tex"

# Step 1: 读取
with open(path, 'r') as f:
    raw_content = f.read()

# Step 2: 修改（使用 str.find() + 唯一锚点，不用行分割）
#   见 references/latex-editing-pitfalls.md 的安全插入模式

# Step 3: 写入
with open(path, 'w') as f:
    f.write(modified_content)

# Step 4: 验证引用完整性
bib_keys = set(re.findall(r'\\bibitem\{([^}]+)\}', modified_content))
cite_keys_flat = []
for c in re.findall(r'\\cite\{([^}]+)\}', modified_content):
    cite_keys_flat.extend(k.strip() for k in c.split(','))
cite_keys = set(cite_keys_flat)

assert not (bib_keys - cite_keys), f"Uncited: {bib_keys - cite_keys}"
assert not (cite_keys - bib_keys), f"No bibitem: {cite_keys - bib_keys}"
print(f"✅ {len(bib_keys)} bibitems ↔ {len(cite_keys)} cites — all matched")

# Step 5: 编译验证
#   见 组合编译 节
```

## 集成到 P4 质量门

此验证是 P4 质量门的前置步骤。在 `pdflatex` 编译前执行此脚本，可以：
- 避免编译出带 `??` 的未定义引用
- 避免在 2-pass 编译中被 undefined citation 噪音淹没
- 在添加新引用后即时发现插入遗漏
