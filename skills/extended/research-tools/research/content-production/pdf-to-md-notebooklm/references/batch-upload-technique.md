# Large-Scale PDF→MD→NotebookLM Upload — 批量上传实战

> 2026-06-01 实战验证：Pima 论文 40 篇 PDF → MD → NotebookLM。40/40 成功。

## 标准批量上传脚本

```bash
#!/bin/bash
# 批量上传 MD 文件到指定 Notebook
# 用法: ./batch_upload.sh <notebook_id> <md_dir>

NB_ID="$1"
MD_DIR="$2"
cd "$MD_DIR"

notebooklm use "$NB_ID"

for f in *.md; do
  name="${f%.md}"
  if notebooklm source add "$PWD/$f" --title "$name" 2>&1 | grep -q "Added source"; then
    echo "✅ $name"
  else
    echo "❌ $name"
  fi
  sleep 0.3  # 避免 API 限流
done
```

## 关键发现

### 1. v0.4.1 自动类型检测

notebooklm-py ≥ 0.4.1 自动识别文件类型（PDF/MD/TXT/URL），基于文件扩展名检测：

```bash
# ✅ 正确（shell：基于文件扩展名自动检测）
notebooklm source add paper.md --title "Author2024"
```

### ⚠️ Python subprocess 必须加 `--type text`

**2026-06-01 实战教训**：通过 Python subprocess 传递内容字符串（而非文件路径）时，自动检测失效，返回 error 36：

```python
# ❌ 错误（Python subprocess 传内容字符串 → error 36）
r = subprocess.run(['notebooklm', 'source', 'add', '-n', nb_id,
    content, '--title', bk, '--timeout', '120'], ...)

# ✅ 正确（必须显式 --type text）
r = subprocess.run(['notebooklm', 'source', 'add', '-n', nb_id,
    '--type', 'text', '--title', bk, '--timeout', '120', content], ...)
```

**根因**：CLI 的自动类型检测基于传入参数的文件扩展名（`.md`/`.pdf` 等）。Python subprocess 作为位置参数传入的是纯内容字符串（无 `.md` 后缀），自动检测无法识别类型。

### 2. 批量上传超时处理

26+ 篇连续上传在 Python subprocess 循环中（每篇 ~8-15 秒）可能触发 300s 执行超时：

```python
# 分批策略（推荐：每批 10-15 篇）
import subprocess, time

def upload_batch(nb_id, items, batch_size=12):
    """分批上传，单批上传后检查是否超时"""
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        for bk, content in batch:
            r = subprocess.run([...], timeout=180)
            time.sleep(0.4)
        print(f"Batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1} done")

# 或在 shell 中直接用 terminal(background=true) 异步执行
```

### 3. 扫描版 PDF 预处理

图片型 PDF（无文本层）需转 MD 后再上传：

```bash
# 检测文本层
pdftotext paper.pdf - | wc -c
# < 100 → 图片型 PDF

# 转 MD（markitdown 对图文混排效果最好）
uvx markitdown paper.pdf > paper.md

# 检查 MD 质量
wc -l paper.md  # 应有 ≥ 100 行
```

### 4. rclone 批量上传备选（Drive 中转）

仅适用于 PDF（MD 走 Drive 会失败）：

```bash
# 上传全部 PDF
rclone copy *.pdf googledrive:target-folder/

# 列出 ID
rclone lsjson googledrive:target-folder/ | jq -r '.[] | "\(.ID) \(.Name)"'

# 逐篇导入
notebooklm source add-drive FILE_ID "Title" --mime-type pdf -n <notebook_id>
```

## 上传后验证

```bash
# 统计源数量
notebooklm source list -n <notebook_id> | grep "ready" | wc -l

# 查找特定论文
notebooklm source list -n <notebook_id> | grep "Author2024"

# 测试检索
notebooklm use <notebook_id> && notebooklm ask "这篇论文的核心贡献是什么？"
```
