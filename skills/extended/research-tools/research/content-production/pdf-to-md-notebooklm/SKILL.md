---
name: pdf-to-md-notebooklm
description: PDF→Markdown→NotebookLM 全流程管线。支持批量上传、自动类型检测、大文件处理。
version: 1.0.0
allowed-tools:
- terminal
- file
- web
metadata:
  synthos:
    author: Synthos
    signature: 'pdf_paths: list -> md_paths: list'
    related_skills:
    - academic-paper-completion
    - adhd-eye-tracking-review
    - arxiv
    - biorxiv
    - blogwatcher
    version: 2.2.0
    tags:
    - d7
    - literature
    - notebooklm
    - markdown
    - acq
    - batch

---

## IO_CONTRACT

- **input**: `pdf_file: str` — 用户请求描述、上下文信息
- **output**: `md_content: str — PDF转Markdown`


> 对应原则：P2（机械原子暴露输入输出规范）
> 对应原则：P2（机械原子暴露输入输出规范）


# PDF → Markdown → NotebookLM 全流程管线

> 将参考文献从 PDF 转为 Markdown 后上传至 NotebookLM。适用于扫描版 PDF、批量导入、大文件等场景。

## ⚡ 强制触发条件（2026-06-01 新增）

**此流程不是可选的。它是Layer B双质量评审的前置条件。**

### 必须执行的场景

- ✅ **每篇论文进入P4质量门前** — 参考文献必须上传到NotebookLM
- ✅ **Layer B评审前** — 缺参考文献的Layer B评分不可靠
- ✅ **D9 ≥ 80% 已达标后** — 本地有PDF但不等于NotebookLM有
- ✅ **手稿修改后重新编译** — 重新上传手稿时，同时验证参考文献源是否还在

### 禁止跳过

| 理由 | 后果 |
|:-----|:-----|
| "参考文献PDF已经有了" | 但NotebookLM没有，Layer B无法交叉验证 |
| "论文已经在审稿了" | 但引用全文缺失，审稿人可能发现数值不匹配 |
| "之前已经上传过" | 可能有error源或重复源，需要`source clean` |
| "时间不够了" | 宁可推迟Layer B，不可无参考文献评审 |

### 绑定到Paper Pipeline

```
D9 ≥ 80%（本地PDF就绪）
    ↓
pdf-to-md-notebooklm 强制执行
    ↓
参考文献上传到NotebookLM
    ↓
dual-quality-check-v2 P0前置闸门验证（源数 ≥ D8 × 80%）
    ↓
Layer B 7维评审
```

## 核心原理

```
PDF → uvx markitdown → .md → notebooklm source add
```

**为什么转 MD 再上传：**
- 扫描版/图片型 PDF 无文本层，NotebookLM 不可检索
- Markdown 无格式噪音，Gemini 检索效率更高
- `source add` 自动类型检测，无需 `--type` 参数（v0.4.1+）
- 40/40 篇批量上传 100% 成功已验证

## 前提条件

- `uvx` 可用（安装 `pipx install uv`）
- `notebooklm-py >= 0.4.1`（pipx 安装）
- NotebookLM 已登录（`notebooklm profile list` 确认 authenticated）

## 全流程步骤

### Step 1: PDF → Markdown 转换

```bash
# 推荐：uvx markitdown（效果最优，支持图文混排）
uvx markitdown paper.pdf > paper.md 2>/dev/null

# 验证转换质量
wc -l paper.md            # 应有 ≥ 100 行
head -50 paper.md         # 检查首段是否完整
grep -c "```" paper.md    # 代码块保留情况
```

### Step 2: 上传到 NotebookLM

**单篇上传（最基本）：**

```bash
notebooklm use <notebook_id>
notebooklm source add paper.md --title "Author2024"
```

v0.4.1+ 通过文件路径传入时自动检测类型（从扩展名推断），无需 `--type` 参数。

**但Python subprocess传内容字符串时没有扩展名可检测，必须显式加 `--type text`，否则报 Error 36。** 详见陷阱表。

**大文件上传（> 10MB MD）：**

```bash
notebooklm source add paper.md --title "Author2024" --timeout 120
```

### Step 3: 批量上传（推荐脚本）

```bash
cd /path/to/pdfs_md/
notebooklm use <notebook_id>

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

40 篇 MD 文件批量上传实战验证：40/40 成功，0 失败。

### Step 4（可选）: Google Drive 中转 PDF

当无法直连 NotebookLM 时，先上传 PDF 到 Drive 再导入：

```bash
# 上传 PDF 到 Drive
rclone copy *.pdf googledrive:target-folder/

# 获取文件 ID
rclone lsjson googledrive:target-folder/ | jq -r '.[] | "\(.ID) \(.Name)"'

# 从 Drive 导入（仅 PDF 有效）
notebooklm source add-drive FILE_ID "Title" --mime-type pdf -n <notebook_id>
```

> ⚠️ `add-drive` 仅支持 PDF。Markdown 文件走 Drive 中转会返回 "API returned no data"，必须用本地 `source add`。

### 验证上传

```bash
notebooklm source list -n <notebook_id> 2>&1 | grep "Author2024"
```

## 实战验证（2026-06-01）

| 项目 | 结果 |
|:-----|:----:|
| Pima 论文 40 篇 PDF → MD → NotebookLM | ✅ 40/40 成功 |
| SCC 论文 34 篇 PDF → Drive → NotebookLM | ✅ 34/34 成功 |
| 上传方式（Pima） | `source add /path/file.md --title "Name"` 直传 |
| 上传方式（SCC） | `rclone upload → add-drive FILE_ID --mime-type pdf` Drive 中转 |
| **关键发现** | **Drive 中转处理速度远快于直传 MD**（直传 MD 120s 超时，Drive PDF 即时 ready） |

## 已知陷阱

| 陷阱 | 表现 | 修复 |
|:-----|:-----|:-----|
| 扫描版 PDF 无文本 | MD 文件仅几行 | 转 MD 后检查 `wc -l < 100`，需 OCR 预处理 |
| `add-drive` 传 MD 失败 | "API returned no data" | 改用本地 `source add` 直接上传 |
| 批量上传限流 | 部分返回超时或 429 | 加 `sleep 0.3~0.5` 间隔 |
| rclone 大文件超时 | 多文件上传卡住 | 分批上传或加 `--timeout` |
| 上传后堆积 error/重复源 | 大量 error 源 + 重复 | **`notebooklm source clean -y`** 一键清除，比逐条 `delete` 快 100x |
| 顽固 PDF (10-15%) | Drive "API no data" + MD 120s超时 | 标记为"手动上传"，不影响 D9≥80% |
| `source delete` 交互 | 删除需 y/N 确认 | **改用 `source clean -y`** 批量清理；逐条删除用 `yes \\| notebooklm source delete <id>` |
| **`--type text` in Python subprocess** (2026-06-01) | Python subprocess 传内容字符串 (`source add content --title "Name"`) → error 36 | **shell 中自动检测工作（基于文件扩展名），Python subprocess 必须显式加 `--type text`**。详见 `references/batch-upload-technique.md` 陷阱节 |
| **批量上传超时** (2026-06-01) | 26+ 篇 Python subprocess 循环上传超时 300s | 分批 10-15 篇/批，或改用 `terminal(background=true)` 异步执行 |

## 参照

- [[notebooklm-cli|NotebookLM CLI skill]]
- [[paper-pipeline|论文管线]]
- [[markitdown-convert|MarkItDown 转换 skill]]

## 实战示例：Pima 论文 40 篇参考文献上传

```bash
# 1. 转换 PDF → MD
cd /media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/pdfs/
for f in *.pdf; do
  uvx markitdown "$f" > "../pdfs_md/${f%.pdf}.md" 2>/dev/null
done

# 2. 批量上传到 Pima notebook（ID: 8e1174cd）
notebooklm use 8e1174cd
cd ../pdfs_md/
for f in *.md; do
  name="${f%.md}"
  notebooklm source add "$PWD/$f" --title "$name"
  sleep 0.3
done

# 结果：40/40 ✅
```
