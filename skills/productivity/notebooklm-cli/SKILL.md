---
name: notebooklm-cli
description: "子skill | NotebookLM CLI全功能指南 — 从Q&A知识提取到内容生成(报告/视频/音频/信息图/幻灯片)再到文献检索。响应paper-pipeline的P1阶段调用。v3.2.0新增：source add RPC失陷时的note create降级通路。"
version: 3.5.0
author: Hermes Agent + Synthos
license: MIT
metadata:
  hermes:
    tags: [notebooklm, qa, extraction, content-generation, research]
    related_skills: [paper-pipeline, research-paper-search]
---

# NotebookLM CLI — 知识大脑 (Knowledge Brain) + 逐问法 + 源文件管理

> **架构定位**: NotebookLM = Synthos 的廉价知识大脑 (Tier 1)。通过 CLI 桥接，免费获得 Gemini 级推理能力。详见 `references/knowledge-brain-architecture.md`。可将 Synthos 架构文件上传到 NotebookLM，让 Gemini 理解 7+1 框架约束。若 `source add` 因 Google 后端 API 变更失败（见陷阱 #15），用 `note create` 降级。远程机部署见 `references/remote-machine-setup.md`。

## 核心原理（文言）

**一问一收，不并投** — 每轮只问一个问题，用答案决定下一个。不一次全抛。

**言不必行** — Q&A输出≠源代码执行结果。定义了的`calculate_iou()`不代表模型跑到过那个数值。所有数值必须追溯执行层证据。

**节点有闸** — Gap门/假设门/方法门/实验门，每节点过闸才前进。

## 逐问法（Iterative Q&A Protocol）

### 原理

文献检索不是一次搜完所有问题，而是每次回答一个问题，逐步收束：

```
Q1: 领域地图 ──→ Q2: 共同盲区 ──→ Q3: 空白定位 ──→ Q4: 假设形成
                     ↑答案决定下一个           ↑答案决定下一个
```

### 标准提问序列

| 轮次 | 提问方向 | 产出 |
|:----:|:---------|:-----|
| Q1 | "最相关的工作是什么？核心原理和局限？" | 领域地图 |
| Q2 | "共同盲区是什么？什么维度没人碰过？" | Gap初定位 |
| Q3 | "形式化Gap陈述：(1)已知 (2)未知 (3)意义" | **研究空白** |
| Q4 | "基于Gap，可证伪的假设是什么？If X then Y？淘汰标准？" | **科学假设** |
| Q5 | "用技术方案验证？可行性？已有资产？" | 方法设计 |
| Q6 | "需要什么实验？预期结果？" | 实验方案 |

### 操作规则

```bash
# 从Q1开始，每次clear上下文开始新的探索
notebooklm clear
notebooklm use <project_id>

# Q1: 只问一个维度的问题
notebooklm ask "...[单维度问题]..."

# 等待答案（60-90s），不催促
# 基于答案决定Q2方向

# 需要开启新线索时用clear
notebooklm clear && notebooklm use <project_id>
```

## 三步确权法（P1阶段调用）
| 内容生成覆盖9种基础类型+子格式 | **九器诸格** | report/audio/video/slide-deck/infographic/mind-map/quiz/flashcards/data-table。report有study-guide/blog-post/custom子格式；audio有deep-dive/debate/critique/brief；video有classic/whiteboard/kawaii/cinematic等风格 |
| 三步确权防数据编造 | **三问确权** | 问状态→问数值→问来源 |
| 逐问法胜于全抛 | **一问一收胜并投** | 文献检索每轮一个问题，用答案决定下一个。不一次全抛 |
| 周期>多轮验证全面 | **多轮胜单次** | Q&A拆成短问题，不急不换项目；生成类长时间运行需wait/poll |

## 会话与Notebook管理

```bash
# 认证
notebooklm login                                     # OAuth浏览器登录（Playwright，默认）
notebooklm login --browser-cookies chrome            # 快速认证：从已安装浏览器读cookies（需 pipx inject notebooklm-py rookiepy）
notebooklm login --browser-cookies chrome --account someone@gmail.com  # 多账号时指定
notebooklm login --browser-cookies firefox           # 从Firefox读取
notebooklm login --browser-cookies chromium          # 从Chromium读取
notebooklm login --browser-cookies --include-domains=all  # 包含所有sibling-product cookies
notebooklm auth check                                # 诊断认证状态
notebooklm auth refresh                              # 刷新cookies（不重新登录）
notebooklm auth logout                               # 登出（删除storage_state.json，需重新login）

# 陷阱：auth logout会删除认证文件，之后必须重新login。
# --browser-cookies 是可靠的服务器环境解决方案（无需交互式浏览器窗口），
# 但浏览器必须有有效的Google登录会话。默认Playwright login在无GUI环境中会超时。

# auth check 不可靠：即使 list 正常工作，auth check 可能因 .notebooklm/profiles/default/storage_state.json 不存在而报fail
# — 如果用户使用了自定义 profile 或 storage 路径。真正的烟雾测试是 notebooklm list 能否返回结果。

## 快速烟雾测试（Quick Smoke Test）

新安装或首次登录后，用以下序列验证 CLI 完全可用：

```bash
# 1. 列出笔记本（验证认证和API连接）
notebooklm list                        # 应该看到 Notebook 列表，而非认证错误

# 2. 切换到第一个笔记本并问一个简单问题
notebooklm use <前6字符>               # 输出 "Matched: xxx..."
notebooklm status                      # 显示 Notebook ID + Title
notebooklm ask "一句话总结这个Notebook的核心主题"  # 应该在60-90s内返回带来源引用的答案

# 3. 检查source健康
notebooklm source list | head -5       # 显示source列表，确认各source状态为 ready
notebooklm source clean --dry-run      # 查看是否有错误/重复source可清理

# 4. 测试跨笔记本切换
notebooklm clear && notebooklm use <另一个ID> && notebooklm ask "一句话回答核心内容"

# 5. 验证 clear + use + ask 链式调用
notebooklm use <id> && notebooklm ask "简短回答"  # 单行链式，不需要前置clear
```

验证通过标准：list 返回表格、ask 返回有来源引用的答案、source clean 不报内部错误。

# Notebook切换
notebooklm list                     # 列出所有Notebook（支持partial ID匹配）
notebooklm use <partial_id>         # 切换活动Notebook（前6-8字符即可）
notebooklm status                   # 显示当前Notebook和对话状态
notebooklm clear                    # 清除当前上下文

# Notebook CRUD
notebooklm create "标题"            # 新建
notebooklm rename <id> "新标题"     # 重命名
notebooklm delete <id>              # 删除
notebooklm summary                  # AI生成Notebook摘要
```

## 参考论文源管理 — PDF → MarkItDown/Pandoc 转 MD → source add 上传

> **2026-05-27 确认：Markdown 比 PDF 更适合 NotebookLM 上传。**
> PDF 经常因无可提取文本层、字体编码异常、超大文件导致 `error` 或 `preparing` 超时。
> Markdown 纯文本格式 100% 成功，且 Gemini 检索效果相同。
>
> 推荐管线：`论文源 → MarkItDown/Pandoc 转 MD → source add "$(cat file.md)" --type text`

### 核心区分：网页检索 ≠ 全文源

| 方式 | 命令 | 导入什么 | D7验证可用？ | 推荐度 |
|:-----|:-----|:---------|:------------|:------|
| 网页检索 | `add-research` | 网页源（论坛/博客/新闻） | ❌ 仅元数据 | ⭐ |
| Markdown（首选） | `source add "$(cat file.md)" --type text --title "标题"` | **全文MD** | ✅ 可全文验证 | ⭐⭐⭐ |
| PDF上传 | `source add file.pdf` | PDF全文 | ✅ 可全文验证 | ⚠️ 陷阱多 |
| arXiv URL | `source add "https://..."` | 远程PDF | ✅ | 🟡 需网络 |

| 方式 | 命令 | 导入什么 | D7验证可用？ |
|:-----|:-----|:---------|:------------|
| 网页检索 | `add-research` | 网页源（论坛/博客/新闻） | ❌ 仅元数据 |
| PDF上传 | `source add file.pdf` | PDF全文 | ✅ 可全文验证 |

### 核心坑：PDF必须有可提取文本层

NotebookLM 后端索引 PDF 要求文件包含**可提取的文本层**。扫描版PDF、字体编码异常的arXiv PDF、纯图像PDF（pdftotext输出0字符）都会索引失败，最终转为 `error` 状态。

**上传前必须检查**：
```bash
pdftotext pdfs/{bibkey}.pdf - | wc -c
# 若输出 ≈ 0 → 无文本层，不能用 source add file.pdf
# 若输出 > 100 → 有文本层，可以上传
```

**无文本层的PDF → 用arXiv URL直传**（跳过本地文件）：
```bash
notebooklm source add "https://arxiv.org/pdf/{arxiv_id}" --title "{bibkey}" --timeout 60
# NotebookLM 会直接从 arXiv 获取并索引，通常成功
```

**对比**：
| 方式 | 适用场景 | 成功率 |
|:-----|:---------|:-------|
| `source add file.pdf` | 有可提取文本的PDF | ✅ 高 |
| `source add arXiv URL` | 无文本层/扫描PDF/arXiv论文 | ✅ 高（绕过本地格式问题） |
| `source add-drive` | 超大PDF（>50MB） | 🟡 需先配Google Drive OAuth |

### BibTeX→PDF管线（推荐方式）

```
Step 0: 检查PDF文本可提取性
  pdftotext pdfs/{bibkey}.pdf - | wc -c   # < 100字符 → 走Step 2b

Step 1: NotebookLM生成BibTeX元数据（含DOI/arXiv ID）
  notebooklm ask "为每个源文件生成BibTeX条目，含DOI或arXiv ID"
  → 保存为 notebooklm-sources.bib

Step 2a: 有文本层 → 本地PDF上传
  wget -O pdfs/{bibkey}.pdf "https://arxiv.org/pdf/{arxiv_id}.pdf"
  notebooklm source add pdfs/{bibkey}.pdf --title "{bibkey}"

Step 2b: 无文本层 → arXiv URL直传
  notebooklm source add "https://arxiv.org/pdf/{arxiv_id}" --title "{bibkey}"
```

### 命名规范：`{bibkey}.pdf`

| 旧命名（不规范） | 新命名（规范） | bibkey |
|:----------------|:--------------|:-------|
| `Lala2023.pdf` | `lala2025paperqa.pdf` | `lala2025paperqa` |
| `Bai2022.pdf` | `bai2022constitutional.pdf` | `bai2022constitutional` |
| `Lu2024.pdf` | `lu2024ai.pdf` | `lu2024ai` |

规则：
- 文件名 = BibTeX key + `.pdf`
- 全小写，无连字符/下划线/空格
- bibkey = `{author}{year}{keyword}`

## ⚠️ 铁律：必须上传参考文献全文，非摘要

2026-05-31 确认：NotebookLM 源必须是 **全文 Markdown**（由 `markitdown-convert` skill 转换），不可截断为摘要。

**原因**：
- Layer B 7维评审需要上下文完整
- Gemini 检索需要全文才能准确引用
- 摘要版（3000 chars 截断）会让评审漏掉关键方法论细节

**正确做法**：40 篇参考文献 → markitdown 转全文 MD → 合批 → 上传

## 大文件上传模式（Python subprocess）

`notebooklm source add` 将内容作为**位置参数**（非 stdin），Shell 参数列表限制约 128KB 导致 `$(cat file.md)` 对大文件报 `Argument list too long`。

**推荐：Python subprocess 分块上传**：

```python
import subprocess

nb_id = "b8908eab"  # 目标笔记本 ID
content = open("large-file.md").read()
chunk_size = 80000  # 80K chars 以内避免 arg 超限

if len(content) > chunk_size:
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i+chunk_size]
        title = f"文档名 (part {i//chunk_size + 1}/{len(content)//chunk_size + 1})"
        r = subprocess.run(
            ['notebooklm', 'source', 'add', '--type', 'text',
             '--title', title, '--timeout', '120', '-n', nb_id, chunk],
            capture_output=True, text=True, timeout=180
        )
else:
    r = subprocess.run(
        ['notebooklm', 'source', 'add', '--type', 'text',
         '--title', '文档名', '--timeout', '120', '-n', nb_id, content],
        capture_output=True, text=True, timeout=180
    )
```

**为什么不直接用 `--type file`**：`.md` 文件通过 `--type file` 上传后，NotebookLM 后端索引经常卡在 status=3 (preparing) 直到超时，最终转为 error。`--type text` 通过内容字符串直传，100% 成功。

**为什么不通过 stdin**：`notebooklm source add` 不支持 stdin 输入。管道模式报 `Error: Missing argument 'CONTENT'`。

## 批量上传流水线（40篇参考文献完整流程）

```bash
# Step 1: 所有 PDF → Markdown（见 markitdown-convert skill）
# Step 2: 合并为批次文件（每批 ~500KB/10篇）
python3 << 'PYEOF'
import os, math

md_dir = "06-references/pdfs_md"
mds = sorted([f for f in os.listdir(md_dir) if f.endswith('.md')])
papers = [(f.replace('.md',''), os.path.getsize(os.path.join(md_dir, f))) for f in mds]
total_sz = sum(s for _, s in papers)
n_batches = max(1, round(total_sz / (500 * 1024)))

for b in range(n_batches):
    batch = papers[b*len(papers)//n_batches:(b+1)*len(papers)//n_batches]
    with open(f'/tmp/refs-batch{b+1}.md', 'w') as f:
        f.write(f'# References Batch {b+1}/{n_batches} ({len(batch)} papers)\n\n')
        for bibkey, _ in batch:
            fp = os.path.join(md_dir, f'{bibkey}.md')
            with open(fp) as fr: content = fr.read()
            f.write(f'\n---\n## {bibkey}\n\n{content}\n\n')
PYEOF

# Step 3: 用 Python subprocess 分块上传
python3 << 'PYEOF'
import subprocess, math

nb_id = "your_notebook_id"
for b in range(1, n_batches + 1):
    with open(f'/tmp/refs-batch{b}.md') as f:
        content = f.read()
    chunk_size = 80000
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i+chunk_size]
        pi = i // chunk_size + 1
        total = math.ceil(len(content) / chunk_size)
        r = subprocess.run(
            ['notebooklm', 'source', 'add', '--type', 'text',
             '--title', f'参考文献 Batch {b}/{n_batches} (part {pi}/{total})',
             '--timeout', '120', '-n', nb_id, chunk],
            capture_output=True, text=True, timeout=180
        )
PYEOF
```

每个论文目录维护两个文件：

**`bibkey-map.json`** — 文件名 ↔ bibkey 映射
```json
{
  "lala2025paperqa.pdf": "lala2025paperqa",
  "bai2022constitutional.pdf": "bai2022constitutional"
}
```

**`notebooklm-sources.json`** — 已上传到NotebookLM的源文件清单
```json
{
  "version": "1.0",
  "notebook_id": "b54348f4-...",
  "sources": [
    {"title": "lala2025paperqa", "local": "pdfs/lala2025paperqa.pdf", "status": "ready", "type": "pdf"}
  ]
}
```

### 批量上传用后台进程（避免排队等待）

```bash
# 创建上传脚本，循环上传所有PDF
# 每次用 --title "{bibkey}" 确保规范命名
# 完成后更新 notebooklm-sources.json
# 用 terminal(background=true) 启动，继续做其他事
```

### PDF索引超时处理

`notebooklm source add file.pdf` 上传后等待后端索引完成。大PDF（>5MB）可能索引超120秒，CLI返回 `"not ready after 120.0s (last status: 3)"`。

**status 3 = preparing** — PDF已上传到NotebookLM服务器，但后端索引未完成。CLI内部轮询120秒后放弃，但source已存在。

**解决方法：使用 `--json` 模式**：
```bash
# --json 输出机器可读结果，即使索引未完成也能拿到 source_id
notebooklm source add file.pdf --title "bibkey" --json
# → {"id": "f124e35d-...", "status": "preparing", ...}
```

**配套脚本**：
- `scripts/upload-pdfs.sh` — v2.0: 使用 `--json` 提取 source_id，不因索引未完成而报错。记录 status='uploaded' 到 manifest
- `scripts/check-pdfs-ready.sh` — 轮询检查 `uploaded`→`ready` 状态迁移，更新 manifest

```bash
# 推荐工作流：
# 1. 批量上传（不阻塞）
bash /path/to/scripts/upload-pdfs.sh /path/to/paper_dir &

# 2. 等几分钟后检查哪些已就绪
bash /path/to/scripts/check-pdfs-ready.sh /path/to/paper_dir

# 3. 重复步骤2直到所有 source ready
```

### 目录清理规范

每个PDF目录应：
1. 有效PDF保留（验证文件头 `%PDF-`）
2. 无效文件（空/非PDF/文本文件）移入 `_invalid/`
3. 未引用PDF移入 `_uncited/`
4. 重复PDF只保留一份
5. 命名统一为 `{bibkey}.pdf`

### 上传前检查清单

- [ ] 本地PDF已按 `{bibkey}.pdf` 命名
- [ ] `bibkey-map.json` 映射一致
- [ ] **PDF有可提取文本层**：`pdftotext {bibkey}.pdf - | wc -c` 应 > 100，否则用 arXiv URL 上传
- [ ] `notebooklm-sources.json` 记录已上传的源
- [ ] `source add --title "{bibkey}"` 使用bibkey作为标题（无.pdf后缀）
- [ ] 上传后状态为 `ready`（非 `error`）
- [ ] 冗余/错误源已用 `source clean` 或 `source delete -y` 清理

## source clean — 自动去重清理（推荐，v3.4.0更新）

`notebooklm source clean` 自动检测并删除重复、访问错误、不可用的 source，**是清理笔记本的首选方法**（远比逐条 `source delete` 高效）。

```bash
# 预览要清理的内容（不会实际删除）
notebooklm source clean --dry-run
notebooklm source clean -n <notebook_id> --dry-run --json

# ✅ 实际清理（推荐：加 -y 跳过确认）
notebooklm source clean -n <notebook_id> -y     # 一键清理，无需交互
notebooklm source clean -n <notebook_id>         # 交互确认
```

**实战验证**（2026-06-01）：
- Pima 笔记本：`source clean -y` 一次清理 **18 个 error 源**（此前手动删了 83 个才学会 ✅）
- SCC 笔记本：自动检测并删除 **3 个重复源**
- 无需逐条 `yes | notebooklm source delete` — `-y` 标志直接跳过确认

**工作原理**：将 source 分组为三种候选类型：
- `duplicate_of:<id>` — 内容重复（保留一份，删除其余）
- `error_status` — 上传失败的 source（404/访问受限/处理超时）
- 以 10 个为一批次执行，避免 API 限流

**维护建议**：每完成一个项目阶段或在大量上传后执行一次 `source clean -y`。

## 笔记本合并（Notebook Merging Workflow）— 删除重复项目

当同一个项目被导入了两次（如 Owner + Shared 版本，或全角/半角标题差导致的两份），需要将 source 从一个笔记本合并到另一个，再删除冗余。

### 触发场景
- 同一项目的 Owner 笔记本和 Shared 笔记本共存（标题几乎相同）
- 同一篇论文库因标题差异（全角冒号 vs 半角冒号、连字符 vs 空格）分成了两个笔记本
- 内容相关的两个笔记本（如专利文件分散在多个项目中）

### 合并流程

**Step 1：识别重复对**

```bash
notebooklm list                         # 检查是否有相似标题
notebooklm source list -n <nb_id>       # 对比 source 数量
```

**Step 2：对比 source 差异**

```bash
# 获取两个笔记本的 source 列表（JSON 格式只对 Owner 笔记本可靠）
notebooklm source list -n <keep_id> --json | tail -n +2
notebooklm source list -n <from_id> --json | tail -n +2

# 在 Python 或 shell 中比较 title 集合
notebooklm source list -n <keep_id> 2>&1 | grep '│' | cut -d'│' -f3 > /tmp/keep.txt
notebooklm source list -n <from_id> 2>&1 | grep '│' | cut -d'│' -f3 > /tmp/from.txt
# 找出 from 中有而 keep 中没有的 title
grep -v -F -f /tmp/keep.txt /tmp/from.txt
```

**Step 3：搬移独有 source**

根据 source 类型选择搬移方法：

| Source 类型 | 方法 | 命令 |
|:------------|:-----|:-----|
| **Web Page** | 获取 URL 后 re-add | `source get <id> -n <from_id> --json` → 提取 `url` → `source add -n <keep_id> --type url "<url>"` |
| **Markdown / Pasted Text** | fulltext 导出 + 文件导入 | `source fulltext -n <from_id> <sid> -o /tmp/file.md` → `source add -n <keep_id> --type file --title "name" /tmp/file.md` |
| **PDF** | 仅能提取文本（丢失原PDF格式） | `source fulltext -n <from_id> <sid> -o /tmp/file.txt` → `source add -n <keep_id> --type file --title "name.txt" /tmp/file.txt` |
| **DOCX** | 同理，仅文本 | 同上 (fulltext → add as text) |

```bash
# 示例：搬移一个 Web Page 类型的 source
notebooklm source get -n <from_id> <source_id> --json  # 查看 url 字段
notebooklm source add -n <keep_id> --type url "https://..."

# 示例：搬移一个 Markdown 类型的 source
notebooklm source fulltext -n <from_id> <source_id> -o /tmp/transfer.md
notebooklm source add -n <keep_id> --type file --title "original_title.md" /tmp/transfer.md
```

**Step 4：验证搬移结果**

```bash
notebooklm source list -n <keep_id> 2>&1 | grep "<title_fragment>"
# 或查看 source 总数增长
notebooklm source list -n <keep_id> 2>&1 | grep -c '^│'
```

**Step 5：删除源笔记本**

```bash
notebooklm delete -n <from_id> -y
# 验证删除成功
notebooklm list 2>&1 | grep "<from_id>" && echo "仍存在" || echo "已删除"
```

### 已知限制

- **PDF/DOCX 等二进制文件**：`source fulltext` 只输出纯文本，无法保留原格式。如果原始文件不在本地磁盘上，只能将文本内容导入为目标笔记本的文本 source。
- **Shared 笔记本的 JSON 输出**：Shared notebook 的 `--json` 输出可能因 "Matched:" 前缀导致 JSON 解析失败。用 `tail -n +2` 跳过首行后再解析。
- **删除超时**：`notebooklm delete` 可能在 API 层面已成功但 CLI 等待响应超时（exit code 124）。此时尝试再次 `delete` 会返回 "No notebook found"，确认已删除。
- **批量合并的源文件导入超时**：当同时搬移多个 source（>=5个），每个 `source add --type file` 可能需要 30-60 秒完成索引（含 processing + preparing 状态）。连续 5 个以上 source 的合计时间可能超过默认 CLI 超时（120s）。应对策略：使用 `--timeout 600` 参数增加单次等待时间，或在每个 `source add` 之间加入简短间隔避免 API 限流。`source fulltext -o` 导出是瞬时的，超时只发生在 `source add` 阶段。
- **导入后 "preparing" 状态**：`source add` 返回后，新 source 可能显示 `preparing` 状态数秒。这是正常的后端索引延迟，几秒后自动变为 `ready`。无需重复导入。

## 常规源文件管理
### 添加来源（v3.4.0更新：优先 Drive PDF，v0.4.1 自动类型检测）

**v0.4.1+ 自动类型检测**：`source add` 不再需要 `--type text` 或 `--type file` 标志。CLI 根据文件扩展名和内容自动识别 pdf/md/txt/url/youtube。

```bash
# ✅ 推荐：PDF via Drive（处理最快）
rclone copy file.pdf googledrive:folder/
rclone lsjson googledrive:folder/ | jq -r '.[0] | "\(.ID) \(.Name)"'
notebooklm source add-drive FILE_ID "Title" --mime-type pdf

# ✅ v0.4.1 自动检测（无需 --type 标志）
notebooklm source add file.pdf                    # 自动识别为 PDF
notebooklm source add file.md                     # 自动识别为 Markdown
notebooklm source add "https://arxiv.org/pdf/..." # 自动识别为 URL

# ✅ 显式指定类型（仅需覆盖自动检测时）
notebooklm source add "plain text" --type text
```
# 联网研究（文献元数据检索——导入的是网页源，不是PDF全文！）
notebooklm source add-research "query"            # 搜索网页并导入（fast模式）
notebooklm source add-research "query" --mode deep  # 深度研究（更全面）
notebooklm source add-research "query" --import-all # 自动导入所有找到的来源
notebooklm source add-research "query" --mode deep --no-wait  # 非阻塞启动

**⚠️ 关键区分**：`add-research` 导入的是**网页源文件**（博客、新闻、论坛），**不是PDF全文**。要获取PDF：
1. NotebookLM生成BibTeX（含DOI/arXiv ID）
2. 用DOI/arXiv独立下载PDF
3. 用bibkey命名上传。

# 研究进度管理（配合add-research --no-wait）
notebooklm research status                        # 检查研究状态
notebooklm research wait                          # 等待完成（阻塞）
notebooklm research wait --import-all             # 完成并导入全部结果

# 源文件查询
notebooklm source list                            # 列出所有源
notebooklm source get <id>                        # 获取详情
notebooklm source guide <id>                      # AI生成摘要+关键词
notebooklm source fulltext <id>                   # 获取完整索引文本（stdout输出，长内容可选`-o <file>`保存到文件）
notebooklm source fulltext <id> -o <file.md>      # 保存完整索引文本到文件（应对比度超过terminal屏幕，推荐用`-o`代替管道重定向）
notebooklm source stale <id>                      # 检查URL源是否过时

# 源文件管理
notebooklm source add paper.md                    # 回传论文到Notebook
notebooklm source delete <id>                     # 删除
notebooklm source rename <id> "新名"              # 重命名
notebooklm source refresh <id>                    # 刷新URL/Drive源

**去重**：`add-research --import-all` 可能导入大量重复。优先用内置 `source clean` 命令自动处理（见下方），比手动脚本更可靠。

**批量审计参考**：当需要系统性审查多个NotebookLM项目的研究空白、假设、论文产出、数据挖掘完成度和教学价值时，参考 `references/multi-project-audit-workflow.md`。
```

### 作者核实协议（Author Verification Protocol）

> 2026-05-25 实战教训：Gemini 在回答时会无差别地将用户上传的参考文献（他人的论文）与用户自己的论文混在一起报告。在询问"这个项目有哪些论文"时，Gemini 会诚实地说"这是笔记本中的论文"，但不会区分"这些是用户自己写的"还是"这些是用户上传的参考文献"。

### 必做流程

当询问某个笔记本中特定作者的论文时，**每次都需要显式指明作者名称**：

```bash
# 错误做法（GPT会报告所有源文件中的论文，包括参考文献）
notebooklm ask "列出这个项目中的所有已发表论文"

# 正确做法（必须指定作者名称，让Gemini只过滤匹配的）
notebooklm ask "逐一检查笔记本中所有源文件的作者字段。只列出作者包含 'Xiaokai Yang' 或 '杨晓凯' 的论文。其余参考文献不要列入。"
```

### 作者名前缀匹配（2026-05-25 实战验证）

标准提问模板，按精确度从高到低：

```bash
# 精确全文搜索 - 最可靠
notebooklm ask "逐个检查笔记本中每个源文件的作者字段。只列出作者明确包含 Xiaokai Yang 或 杨晓凯 的论文。没有的话说无。"

# 作者缩写扩展搜索 - 当源文件中使用缩写名时
notebooklm ask "检查所有源文件。作者字段包含 Xiaokai Yang、Xiao-kai Yang、Yang XK、X. Yang 的都算。确认这些缩写是否来自INSTITUTION_NAME_PLACEHOLDER（Wenzhou People's Hospital）。"

# 严格搜索（纯文本框）- 用于快速过滤而不让Gemini做宽松推断
notebooklm ask "作者字段中必须出现完整字符串 Xiaokai Yang 或 杨晓凯。缩写 Yang X 不算，除非有机构名交叉验证。请逐文件报告作者字段的原文。"
```

### 常见陷阱

| 陷阱 | 表现 | 修复 |
|:-----|:-----|:-----|
| **参考文献误报为用户论文** | Gemini 列出笔记本中所有论文，不管用户是否参与 | 每次必须明确指定作者名称过滤 |
| **缩写名混淆** | Yang X 可能是 Xiaokai Yang 也可能是其他姓杨的学者 | 指定三个字符串搜索：Xiaokai Yang / Xiao-kai Yang / Yang XK |
| **学位论文归属模糊** | 学位论文封面研究生姓名可能留空 | 使用机构名（Wenzhou People's Hospital）交叉验证 |
| **同一笔记本含大量无关文献** | 知识库中90%+的源文件可能是参考文献而非用户产出 | 先用 source list 了解总文件数，再用作者过滤 |
| **多篇同名预印本分散在不同笔记本** | Gemini 将同一篇预印本出现在不同笔记本中算多次 | 检查标题+作者去重，同标题只计1篇 |

### 精确项目审计流程（2026-05-25 形成）

当需要全面评估某个研究项目的产出状态时，按以下顺序执行：

1. 查看笔记本source总数
2. 如果<20个源：直接问作者过滤
3. 如果>=20个源：先问总体分为几类，再逐类列出标题+作者
4. 逐个作者过滤 → 只留用户自己的
5. 对匹配到的论文 → 检查是独立成文还是同一文档的章节
6. 区分：已发表 / 已完成手稿 / 仅工程推导 / 仅研究方向

**关键区分**（2026-05-25 教训）：同一专利/技术报告中的多个技术模块 ≠ 多篇独立论文。专利中的4个创新点是同一篇专利的不同章节，不是4篇论文。询问时必须说明不要将同一篇专利/文档的不同章节计数为多篇独立论文。

## 三步确权法（P1阶段核心方法）

#### 第一步：问状态
```bash
notebooklm ask "这个项目目前处于什么阶段？代码/训练/测试？"
```
"代码阶段"→只写方法论不写数值；"训练/测试阶段"→进入第二步

#### 第二步：问数值
```bash
notebooklm ask "训练日志中有哪些具体数值指标？"
```
提取所有数值→记录每个数值的来源文件

#### 第三步：问来源
```bash
notebooklm ask "这些数值是函数定义中的初始值，还是实际运行的输出？"
```
`best_val_iou = 0.0`→未训练；有真实日志输出→可用

| Q&A回答 | 判定 | 论文中怎么用 |
|:--------|:----|:------------|
| "只有代码定义，没有实际数值" | 声明层 | Tables填TBD，摘要定性描述 |
| "有训练日志，Dice=0.9834" | 执行层 | 可用，标注来源文件 |
| "代码未运行/checkpoint不存在" | 未执行 | Tables填TBD |

## 智能问答（QA）

```bash
# 基础问答（自动多轮对话）
notebooklm ask "问题"                       # 默认继续上次对话
notebooklm clear && notebooklm ask "问题"    # 开始新对话（先clear）
notebooklm ask -s src_001 "关于特定源的问题"  # 限定到特定源

# 高级选项
notebooklm ask --json "问题"                # JSON输出（含source引用ID）
notebooklm ask --save-as-note "问题"        # 回答自动保存为笔记
notebooklm ask --note-title "标题" "问题"    # 指定笔记标题

# 对话管理
notebooklm history                          # 查看历史
notebooklm history --save                   # 保存为笔记
notebooklm ask configure                    # 配置回答风格/角色
```

### 逐问法（Sequential Research Questioning）

**用途**：文献检索→空白定位→假设形成（Paper Pipeline P-1阶段的核心方法）。
**区别于三步确权法**：逐问法用于**发现**（Gap→Hypothesis），三步确权法用于**验证**（数据真实性核查）。

**铁律**：每轮只问一个问题，用答案决定下一个。不一次全抛，不让LLM在单轮中猜测研究空白。

### 文献优先的多轮写作协议（Literature-First Protocol）

**原则**：不要直接写论文章节。先通过多轮Q&A提取文献知识，定位研究空白，再逐节构建论文。详见 `references/iterative-literature-first-paper-protocol.md`。

四轮工作流：
1. **Round 1**: 逐篇提取文献的方法、模型、参数
2. **Round 2**: 交叉比对 → 定位研究空白（每个空白标注可信度）
3. **Round 3**: 基于提取结果逐节写论文
4. **Round 4**: 编译验证

#### 标准6问序列

```
Q1: 领域现状 — "这个领域最相关的工作是什么？核心原理和局限？"
    → 输出：方法分类图谱+各自瓶颈
    │
Q2: 共同盲区 — "这些方法共同的盲区是什么？什么维度没人碰过？"
    → 输出：Gap初定位（不是"没人做过"而是"有理由必须做"）
    │
Q3: 形式化Gap — "形式化研究空白：(1)已知 (2)未知 (3)填上它能解决什么"
    → 输出：Gap正式陈述 + "If filled, we can..."
    │ ← Gap门通过后
    │
Q4: 科学假设 — "基于这个Gap，可证伪的假设是什么？(If X then Y + 淘汰标准)"
    → 输出：H1主假设 + H2/H3替代假设 + 淘汰条件
    │ ← 假设门通过后
    │
Q5: 技术方案 — "验证假设需要什么技术路径？已有资源和缺失环节？"
    → 输出：方法流水线 + 可行性评估
    │
Q6: 实验设计 — "需要什么实验？样本量？指标？预期结果？"
    → 输出：实验方案 + 成功/失败标准
```

#### 操作注意事项

| 情况 | 做法 |
|:-----|:-----|
| 想开始新对话 | 直接 `use <id> && ask "..."`，不需要`clear` |
| 想延续上轮线索 | 直接 `ask`（自动继续） |
| 上一轮答案太长 | 拆成子问题 `ask "具体说第2点的实验设计"` |
| 连续超时2次 | 源文件太大，压缩或换项目 |
| 需要新视角 | `clear` + `ask "换个角度，..."` |

#### 逐问法 vs 三步确权法

| 维度 | 逐问法 | 三步确权法 |
|:-----|:-------|:-----------|
| 目的 | **发现** — 找Gap、形成假设 | **验证** — 确认数据真实性 |
| 时序 | 论文写作前（P-1阶段） | 论文写作中（P1阶段） |
| 问题 | 开放式（"盲区是什么"） | 封闭式（"数值是实际输出还是默认值"） |
| 输出 | Gap陈述、假设声明 | 数据来源标注、执行层证据 |
| 后续 | 进入P0前置审计 | 进入P2论文构建 |

### 论文质量评审（Q5门 — 7维SCI评审）

当论文源码上传到NotebookLM后，可作为外部审稿人执行7维质量评审。对于外部毕业论文/学位论文，改用 `references/thesis-review-protocol.md` 的完整三维审查流程（七维评审 + 引用审计 + 格式术语检查）。

```bash
# 标准7维评审提问
notebooklm ask "请对论文进行全面7维SCI质量评审，每维评分(0-1)和改进建议：
1. 科学贡献(Scientific Contribution) — CARS Move3
2. 方法学严谨性(Methodological Rigor) — 形式化定义、算法
3. 结果可信度(Results Credibility) — 数据真实性、统计检验
4. 完整性(Completeness) — IMRaD、表>=2、Limitations>=3
5. 清晰性(Clarity) — CARS Introduction、Toulmin Discussion
6. 新颖性(Novelty) — 非"没人做过"而是"有理由必须做"
7. 引用质量(Citation Quality) — 相关性、格式规范"
```

**评分校准**：NotebookLM评分通常偏高+0.05~0.15，视为"上限分数"。最终投稿前须人工校准。

**改进建议处理**：
| 优先级 | 判定 | 行动 |
|:------|:-----|:-----|
| P0 | D7引用安全风险/D2数学错误 | 立即修复 |
| P1 | 评分<0.85的维度 | 进入修订循环 |
| P2 | 评分>=0.85但有小优化 | 可选优化 |
| P3 | 新内容建议(新图/表/实验) | 记录待办 |

**对话恢复**：
```bash
notebooklm use <project_id>
notebooklm ask "请详细展开关于D2方法学严谨性的改进建议"
```

完整5门体系见 `paper-pipeline` skill的 `references/notebooklm-quality-gates.md`。

### 论文写作（P2阶段核心方法）

参见 `references/paper-section-generation.md` — 通过NotebookLM Q&A逐节生成SCI论文的完整工作流，包含四个IMRaD章节的提问模板和组合编译流程。

### 5门质量系统（P4阶段初始评审）

当需要快速初稿反馈时，用NotebookLM做5门质量评估，每个门**必须包含评分 + 可执行补救方案**。完整模板见 `paper-pipeline` skill的 `references/notebooklm-quality-gates.md`。

**逐门执行**：Q1→Q2→Q3→Q4→Q5，一次一门，不跳步。每门完成后根据补救方案执行改进，改进后再重新评估该门，PASS才进入下一门。

**补救流程**：
```bash
# 1. 根据补救建议启动联网搜索
notebooklm source add-research "suggested query" --mode deep --no-wait
# 2. 等待并导入
notebooklm research wait --import-all
# 3. 重新评估
notebooklm ask "重新评估该门，特别关注之前<0.85的维度是否有改善"
```

**已知陷阱**：
- GitHub引用过多会拉低权威性评分（系统论文尤甚），应有意识地补充同行评审文献
- NotebookLM评分通常偏高+0.05~0.15，视为上限分数

## 内容生成（12种产物类型）

所有生成命令的通用模式：
```bash
notebooklm generate <type> [description] [options]
notebooklm download <type> <artifact_id>
```

### Report（报告）
```bash
notebooklm generate report                                    # 简报（默认）
notebooklm generate report --format study-guide              # 学习指南
notebooklm generate report --format blog-post                # 博客文章
notebooklm generate report --format custom "白皮书要求..."  # 自定义
notebooklm generate report -s src_001 -s src_002            # 限定源
```

### Video（视频）
```bash
notebooklm generate video "explainer for kids"                # 解释类视频
notebooklm generate video --style kawaii                     # 卡通风格
notebooklm generate video --style whiteboard                 # 白板风格
notebooklm generate video --format cinematic                # Veo 3 AI纪录片（需AI Ultra）
notebooklm generate video --format cinematic "documentary"  # 别名
```

视频风格：auto | classic | whiteboard | kawaii | anime | watercolor | retro-print | heritage | paper-craft

### Audio / Podcast（音频）
```bash
notebooklm generate audio                                     # 默认deep-dive
notebooklm generate audio --format debate                    # 辩论形式
notebooklm generate audio --format critique                  # 批判式分析
notebooklm generate audio --format brief                     # 简洁版
notebooklm generate audio --length short|default|long        # 长度控制
```

### 4.4 📊 Slide Deck（幻灯片）

```bash
notebooklm generate slide-deck "description of presentation"
# 支持修改单页：
notebooklm generate revise-slide <deck_id> <slide_num> "new content"
```

**⚠️ 下载认证失败的工作流**：`download slide-deck` 的媒体下载 RPC 要求比列表/问答更高的认证级别。当 `notebooklm download slide-deck` 返回 "received HTML instead of media file" 时，不要持续重试——改用以下替代方案：

**替代方案：Gemini 内容提取 + python-pptx 重建**

```bash
# Step 1: 让 Gemini 描述生成的幻灯片内容
notebooklm ask "请详细描述你刚才生成的 '[标题]' 幻灯片的内容，逐页列出每页的标题、要点"

# Step 2: 用 python-pptx 重建（参考用户的既有设计语言）
python3 << 'PYEOF'
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
# ... 根据 Gemini 描述逐页创建
prs.save("output.pptx")
PYEOF

# Step 3: 转换为图片做视觉 QA
libreoffice --headless --convert-to pdf output.pptx
pdftoppm -png -r 150 output.pdf page
```

**优点**：这比直接下载更好，因为你可以控制设计语言（匹配用户已有的 PPT 风格），而不只是接受 NotebookLM 的默认模板。
```bash
notebooklm generate slide-deck "presentation for grand rounds"
# 支持修改单页：
notebooklm generate revise-slide <deck_id> <slide_num> "new content"
```

**⚠️ 下载失败恢复**：`notebooklm download slide-deck` 可能因 cookies 过期或多账号路由问题失败（`received HTML instead of media file`）。恢复工作流见 `references/competition-document-latex-workflow.md` — 让 Gemini 描述内容 → python-pptx 手工重建。

### Infographic（信息图）
```bash
notebooklm generate infographic                              # 自动生成高分辨率PNG
```

### Mind Map（思维导图）
```bash
notebooklm generate mind-map                                 # 生成知识结构图
```

### 其他类型
```bash
notebooklm generate quiz                                     # 测验题（JSON格式，含答案和解析）
notebooklm generate flashcards                               # 记忆卡片
notebooklm generate data-table "描述表格内容和目的"            # 数据表格 — **必须提供DESCRIPTION参数**
```

### 生成管理
```bash
# 状态监控
notebooklm artifact list                                     # 列出所有生成物（含in_progress/completed状态）
notebooklm artifact get <id>                                 # 获取详情
notebooklm artifact poll <type> <id>                         # 单次状态检查
# artifact wait 用法示例（不带artifact ID参数会让CLI自动选择）：
notebooklm artifact wait report                              # 阻塞等待report完成

# 下载与导出（不同type的下载语法不同）
notebooklm download report <filename.md>                     # 报告下载为markdown
notebooklm download infographic <filename.png>               # 信息图下载为PNG
notebooklm download audio <filename.mp3>                     # 音频下载
notebooklm download slide-deck <filename.pptx>               # 幻灯片下载
notebooklm download quiz <filename.md>                       # 测验下载
notebooklm download flashcards <filename.md>                 # 闪卡下载
notebooklm download data-table <filename.md>                 # 数据表下载（CSV格式的markdown）
notebooklm artifact export <id> google-docs                  # 导出到Google Docs

# 管理
notebooklm artifact rename <id> "新名称"
notebooklm artifact delete <id>
```

## 笔记与协作

### 笔记管理
```bash
notebooklm note list                    # 列出
notebooklm note create "内容"           # 创建
notebooklm note get <id>                # 查看
notebooklm note save <id> "新内容"      # 更新
notebooklm note delete <id>             # 删除
```

### 分享协作
```bash
notebooklm share add email@domain.com                       # 分享（默认viewer）
notebooklm share add email --permission editor              # 编辑权限
notebooklm share add email -m "合作邀请"                    # 带消息
notebooklm share public                                     # 公开分享
notebooklm share list                                       # 查看权限
notebooklm share remove <email>                             # 移除
```

## 语言与配置

```bash
notebooklm language list                  # 查看支持的语言
notebooklm language get                   # 查看当前语言
notebooklm language set zh_Hans           # 设为简体中文（全局设置）
```

## 用户画像挖掘（User Profiling via NotebookLM）

当用户说"理解我"、"了解我"或提到个人介绍时，主动扫描用户的 NotebookLM 项目构建完整画像。详见 `references/user-profiling-via-notebooklm.md`。

工作流：项目摸底 → delegate_task 并行探查（3组）→ 四维萃取（身份/哲学/方向/偏好）→ 写入 USER.md + MEMORY.md → 请用户验证

### 批量删除重复 source（2026-05-27 经验）

当 NotebookLM 项目中有大量同名 `paper.pdf` source 需要清理时：

```bash
# Owner 项目（可用 CLI 删除）
notebooklm source delete <full_source_id> -n <notebook_id> -y   # -y 跳过确认
# 或用 partial ID 匹配
notebooklm source delete <partial_id> -y

# ⚠️ Shared 项目（不可用 CLI 删除）
# source delete 报告成功但实际不生效。需在 NotebookLM 网页端手动删除。
```

**关键**：必须用 `-y` 标志（非 `echo "y" | ...` 管道），管道模式对 CLI 的交互提示不可靠。使用 `source list` 获取完整 source ID 后再 `source delete`。`Shared` 笔记本的 source 不可通过 API/CLI 删除。

### 论文↔NotebookLM映射

### 多论文共享项目命名（2026-05-26）

当一个 NotebookLM 项目服务于多篇同主题论文时，上传文件名必须唯一以避免混淆：

```bash
# ✅ 正确：每篇论文独立命名
notebooklm source add hcs3wt-breast-cancer-v2.pdf --title "HCS-3WT Breast Cancer v2"
notebooklm source add iris-yolo-v3.pdf --title "Iris_YOLO v3"

# ❌ 错误：通用名在共享项目中冲突
notebooklm source add paper.pdf --title "paper"     # 会和另一篇的 paper.pdf 冲突
```

**命名格式**：`{paper-dir-name}-v{N}.pdf`，用 `--title` 标注完整论文名+版本。

### 回传流程

写完论文后回传NotebookLM（P4质量门必需步骤）：
```bash
# ✅ 推荐：传文件内容，后端识别为 Markdown
notebooklm source add "$(cat paper.md)" --type text --title "Paper v3 - title" -n <nb_id> --timeout 120

# 备选：PDF 回传（有文本层时可用）
notebooklm source add paper.pdf --title "Paper v3 - title"
```

当 `source add` 因 Google 后端 RPC 失效时，使用 `note create` 降级——Note 同样被 Gemini 索引检索。  
**注意：优先用 `source add "$(cat file.md)" --type text`（实战验证），`note create` 为降级通路。**
```bash
# 降级方案：将文件内容通过 note create 上传
notebooklm use <notebook_id>
notebooklm note create "$(cat file.md)" --title "Paper v3 - title"
notebooklm note create "$(cat synthos-framework.md)" --title "Synthos 7+1 Framework"
```

**验证**：上传后用 `ask` 测试 Gemini 是否能检索到内容。如果 `ask` 能回答关于该文件的问题，说明索引成功。

## 验证清单

- [ ] 三步确权法执行完毕（问状态→问数值→问来源）
- [ ] 有源的数值都标注了来源文件
- [ ] 至少使用一项内容生成功能（report/video/audio/infographic/slide-deck）
- [ ] 研究检索至少启动1-2个关键词的 deep 搜索
- [ ] paper.md已回传（或note保存）
- [ ] 生成物已下载到本地
- [ ] Source clean 已执行（如果有 add-research 或批量上传）
- [ ] 如果发现重复项目，已执行笔记本合并（fulltext → add → delete）

### 多账号认证与 authuser 路由

当本地浏览器登录了多个 Google 账号（常见于共享服务器环境），NotebookLM CLI 的 RPC 请求可能路由到错误的账号索引，导致 `GET_NOTEBOOK` 返回 "Not found" 错误。以下是完整的排查与修复流程。

### 账号枚举

```bash
# 查看所有可用账号及其 authuser 索引
notebooklm auth inspect
# 输出示例：
# ghfdshgf79@gmail.com | default (authuser=0)
# yakeworld@gmail.com  |         (authuser=1)
# gushiedu@gmail.com   |         (authuser=2)
```

### 针对性提取

知道正确账号后，用 `--account` 精确定位：

```bash
# 提取指定账号的 cookies（写入 default profile）
notebooklm login --browser-cookies auto --account yakeworld@gmail.com

# 创建独立 profile（方便多账号切换）
notebooklm login --browser-cookies auto --account yakeworld@gmail.com --profile-name yakeworld

# 后续使用：指定 profile
notebooklm -p yakeworld use <notebook_id>
notebooklm -p yakeworld ask "问题"
```

### 万能命令（推荐 — 一次性搞定多账号）

```bash
# 提取所有账号到独立 profile（auto-named from email local-parts）
notebooklm login --browser-cookies auto --all-accounts

# 然后切换使用：
notebooklm -p ghfdshgf79 use <id>     # 默认账号
notebooklm -p yakeworld use <id>       # yakeworld 账号
```

### 认证诊断

```bash
notebooklm auth check              # 检查 storage_state 完整性
notebooklm auth refresh            # 刷新 cookies（不重新登录）

# 快速烟雾测试（比 auth check 更可靠）：
notebooklm list                    # 如果返回笔记本列表，认证有效
```

### ⚠️ 幻灯片下载特殊认证要求

`notebooklm generate slide-deck` 生成的 PPTX/PDF 下载需要比 `list`/`ask`/`use` 等操作**更新鲜**的认证令牌。即使 `list` 和 `ask` 正常工作，下载可能因"received HTML instead of media file"而失败。

**排查步骤**：
1. `notebooklm auth refresh` — 尝试刷新令牌
2. 如果仍失败：清除多余的其他账号 cookie（多账号场景），只保留当前账号的 `__Secure-1PSID`/`__Secure-3PSID`/GAPS
3. 如果还失败：用 Playwright 浏览器登录 (`notebooklm login`)，而非 `--browser-cookies`
4. **备用方案**：用 `notebooklm ask` 让 Gemini 描述生成的幻灯片内容，然后用 python-pptx 手工重建

**根因**：下载 RPC 端点 `artifacts.download` 使用独立的鉴权路径，与 `list`/`ask` 不同。多账号 cookie 混合时，服务器将请求路由到错误的 authuser 索引，返回登录页 HTML 而非媒体文件。

### 常见问题排查

| 症状 | 原因 | 解决 |
|:-----|:-----|:-----|
| `list` 能看但 `use` 报 "Not found" | authuser 路由错位 → RPC 发到了错误账号 | 用 `auth inspect` 查看账号列表 → `login --browser-cookies auto --account <正确邮箱>` |
| `list` 返回的笔记本不同于之前看到的 | 当前 profile 使用的 cookies 来自不同 Google 账号 | 同上，提取正确账号 |
| Playwright login 超时 | 无 GUI 环境无法交互式登录 | 用 `--browser-cookies` 替代（需本地浏览器有有效的 Google 会话） |
| `login --browser-cookies` 报 rookipy 未安装 | pipx venv 中未安装 rookipy | `pipx inject notebooklm-py rookipy` |
| `login --browser-cookies` 提示 "No valid Google auth cookies" | 浏览器中未登录任何 Google 账号 | 在本地浏览器中登录 Google，再试。或使用 Playwright login（需 GUI） |

### 实战案例

服务器环境，3个 Google 账号，帕金森笔记本在 `ghfdshgf79@gmail.com` 下：
```bash
# 1. 先枚举账号
notebooklm auth inspect

# 2. 推荐：提取所有账号到独立 profile（避免多账号 cookie 冲突）
notebooklm login --browser-cookies auto --all-accounts

# 3. 使用对应 profile
notebooklm -p ghfdshgf79 use <notebook_id>
notebooklm -p ghfdshgf79 ask "问题"
```

### authuser 路由深坑排查

`notebooklm list` 能列出笔记本，但 `notebooklm use <id>` 仍报 "authuser 路由错误" 的最常见原因：

**症状**：`list` 正常返回 → `use` 报 "defaults to account index 0" → 即使 `--account` 提取也无效

**根因链**：
1. `--browser-cookies chromium`（不带 `--account`）时，rookiepy 提取了 Chromium 中**所有登录账号**的 cookie
2. 这些 cookie 中的 GAPS 令牌分属不同 authuser 索引（`1:`、`2:` 等）
3. 但 `notebooklm` 命名空间的 `authuser` 元数据只记录了一个值（通常是 0）
4. RPC 请求按元数据发送 `authuser=0` 或 `?authuser=<email>`，但 GAPS cookie 指向 authuser=1
5. Google 服务器路由到 authuser=0 → 找不到该账号下的笔记本 → 返回 404

**排查步骤**：
```bash
# 步骤 1：看 GAPS cookie 的实际 authuser 索引
python3 -c "
import json
p = '/home/yakeworld/.notebooklm/profiles/<profile>/storage_state.json'
with open(p) as f:
    data = json.load(f)
ns = data.get('notebooklm', {}).get('account', {})
print('metadata authuser:', ns.get('authuser'), 'email:', ns.get('email'))
for c in data.get('cookies', []):
    if 'GAPS' in c.get('name', ''):
        print(f'GAPS prefix: {c[\"value\"][:2]} (1: = authuser=1)')
"

# 步骤 2：如果 metadata.authuser 与 GAPS 前缀不匹配，手动修正
# 打开 storage_state.json，找到 "notebooklm" 键，确保 account.authuser 与 GAPS 前缀一致
# GAPS: "1:..." → authuser: 1

# 步骤 3：如果手动编辑后仍无效，用 --all-accounts 重新提取
notebooklm login --browser-cookies auto --all-accounts
notebooklm -p <正确账号> use <notebook_id>
```

**关键诊断信号**：
| 观察 | 结论 | 操作 |
|:-----|:-----|:-----|
| `list` 有笔记本，`use` 报 404 | authuser 路由错位 | 用 `auth inspect` 枚举 → `--all-accounts` 提取 |
| GAPS 前缀为 `1:` 但 metadata authuser=0 | 元数据与 cookie 不一致 | 手动修正 metadata 或重新提取 |
| `login --browser-cookies chromium` 成功但笔记本列表与之前不同 | 提取了错误账号的 cookie | 用 `--account <具体邮箱>` 精确定位 |

### 失败降级策略

如果 authuser 路由问题持续无法修复（`use --force` 仍无法访问 RPC），分两步：
1. **立即执行**：用外部文献库（OpenAlex、Semantic Scholar、arXiv）做文献检索，不依赖 NotebookLM
2. **后续补强**：请用户在 NotebookLM 网页端运行关键 Q&A 并导出结果，再融合到论文中
3. **长期修复**：用 `--all-accounts` 创建独立 profile 解决多账号路由

不要因 NotebookLM 认证问题就放弃综述类任务——外部文献搜索同样有效。

## Knowledge Base Audit Workflow (absorbed)

> 吸收自: `knowledge-base-audit` skill (archived). NotebookLM 审计和维护工作流, 包含全量盘点、主题分类、来源质量评估、缺口识别和跨笔记本链接。

### 全量盘点

```bash
notebooklm list --json                     # 获取所有笔记本元数据
notebooklm source list -n <nb_id>          # 获取笔记本内来源
```

### 主题分类映射

用于按内容领域对大量笔记本进行分类。常见医学研究分类:
- ADHD/眼动追踪: ["ADHD", "眼动", "eye tracking", "eyetracking", "注视", "扫视"]
- 前庭/VOR/BPPV: ["VOR", "前庭", "BPPV", "眩晕", "耳石", "vestibular"]
- 眼科/虹膜/3D眼球: ["眼", "虹膜", "iris", "瞳孔", "pupil", "角膜", "眼球", "eyeball", "ocul"]
- AI/ML/编程: ["AI", "ML", "机器学习", "深度", "神经网", "OpenCode", "智能体", "agent"]
- NSFC/基金/项目申报: ["NSFC", "国自然", "基金", "标书", "申报", "英才计划"]
- 科研方法论/论文写作: ["CRISP", "TRIPOD", "论文写作", "科研设计"]

### 来源质量评估

| 指标 | 评估标准 |
|:-----|:---------|
| 来源数量 | 丰富(30+ PDF/MD) vs 单薄(1-5 sources) |
| 来源类型 | PDF(全文) / Markdown(摘要) / 粘贴文本(碎片) |
| 新鲜度 | 偏好近1-2年内文献 |
| 状态 | 全部 "ready" 良好; 有过期来源需刷新 |

### 跨笔记本概念链接

NotebookLM 不支持原生跨笔记本链接。创建映射文档作为桥梁:

```markdown
智医天问 concept    →    Super Individual equivalent
碳硅共生哲学         →    方法论基础
半人马协作模式       →    T型能力模型
```

将该文档添加到两个笔记本, 即可概念关联。

### 优先级行动

| 优先级 | 行动 | 条件 |
|:-------|:-----|:-----|
| P0 (立即) | 添加关键缺失来源 | 核心项目笔记本 ≤2个来源 |
| P1 (截止前) | 重命名不规范标题 | PDF 名为 "201806596.pdf" |
| P2 (维护) | 关联相关笔记本, 分类 "其他" | 10+ 笔记在 "其他" |

完整参考见 `references/knowledge-base-audit.md`.

# 陷阱

00. **⚠️ Markdown 文件上传：必须用 `$(cat)` 传内容 + `--type text`**  \
    `source add paper.md` → status=error（后端不识 `.md` 扩展名）。  \
    也不要用 `source add paper.md --type text` → 这只传了路径字符串。  \
    正确命令：
    ```
    notebooklm source add "$(cat paper.md)" --type text --title "标题" -n <nb_id> --timeout 120
    ```
    验证：source list 显示 type = "📝 Markdown"（非 "Pasted Text"），status = ready。
    备用方案：`note create --content "$(cat paper.md)" --title "标题"` 也可行，但创建 Note 非 Source。
    2026-05-27 实战：8 篇论文 + 1 篇 arXiv 测试，全部成功。

    **🌟 2026-05-27 补充：YAML Frontmatter 陷阱**  \
    Synthos 论文的 Markdown 文件含 YAML 前件（`--- tags: [paper, ...]`），直接 `"$(cat paper.md)"` 传递给 CLI 时，`---` 被 click 解析器误判为命令行选项，导致 `Error: No such option: ---`。  \
    解决方案：上传前剥离前件。
    ```bash
    # 剥离 YAML frontmatter 后再 $(cat)
    awk 'BEGIN{n=0} /^---$/{n++;next} n==1{next} n>=2{print}' paper.md > /tmp/clean.txt
    notebooklm source add "$(cat /tmp/clean.txt)" --type text --title "标题" -n <nb_id> --timeout 120
    ```
    验证：source list 显示 type = "📝 Markdown"，可正常检索内容。

1. **超时处理** — `ask`超时时拆成短问题，不急不换项目。同一项目连续超时2次→可能是源文件太大，选其他项目。

2. **生成任务耗时** — `generate video --format cinematic`需30-40分钟。slide-deck和audio也需等待。用`--no-wait`启动后通过`artifact list`监控状态。

3. **研究导入失败** — `research wait --import-all`可能超时。先`research wait`等待完成，失败后重新执行即可，来源不会被丢失。

4. **`source add PDF失败`** — 两原因：
   - **无文本层**：用 `pdftotext file.pdf - | wc -c` 检查，若 ≈ 0 则PDF扫描版/字体编码异常。**改用 arXiv URL 直传**：`notebooklm source add "https://arxiv.org/pdf/{id}" --title "{bibkey}"`
   - **超大PDF**：>50MB超时，改用文本/LaTeX源或保存为note。

5. **`quality review 评分偏高`** — NotebookLM 的 SCI 7维质量评审评分通常比严格人工评审高 0.05-0.15，用于初稿快速反馈而非定稿门槛。详情见 `references/quality-assessment-workflow.md`。

6. **Mind Map输出为Note ID** — `generate mind-map`输出一个Note ID（如`a09da9af-..`），但note list可能不显示。检索方式：`notebooklm note get <note_id>` 获取JSON格式的树结构。

7. **多任务并行** — 可在后台同时启动多个`generate`任务（audio/slide-deck/infographic）。用`artifact list`统一监控状态。

8. **`clear`丢失notebook上下文** — `notebooklm clear`后当前notebook ID会被清除。正确做法：直接 `notebooklm use <id> && notebooklm ask "..."` 省略`clear`。NotebookLM自动开启新对话线程。

9. **下载语法因类型而异** — `download report`接受文件名参数；`download infographic`也接受文件名参数；`download quiz`/`download flashcards`不接受文件名参数。每种类型先`--help`确认语法。

10. **`summary` 命令一致性失败而 `ask` 正常工作** — `notebooklm summary` 可能因 RPC 错误（如 `RPC rLM1Ne returned null result data`）返回空结果，但这**不代表笔记本不可用**。`summary` 失败后：①检查 `use` 是否已成功匹配；②若 `use` 成功则直接执行 `ask`，跳过 `summary`。

11. **`UnknownTypeWarning` 不影响功能** — `notebooklm source list` 可能输出 `Unknown source type code 6/0` 等警告，这是 CLI v0.5.0 的已知上游问题。不影响任何功能——source 仍正常列出和检索。

12. **`ask`生成LaTeX不含完整文档结构** — Q&A输出的LaTeX通常只包含章节内容，缺少`\begin{document}`、`\bibliography{}`等框架。保存为section文件后在主文件中组合时需自行补充文档结构。

13. **多轮串行ask上下文管理** — 逐问法不同轮次间（Q1→Q2→Q3）若需要全新视角，先`clear && use`再提问；若延续上轮线索则直接`ask`。

14. **同一项目禁止并行 `ask`** — NotebookLM CLI 是单会话模型。对**同一个项目**同时启动多个 `ask` 后台进程，会导致回答串话（两个答案混淆）。正确做法：串行 `ask` — 等上一个结果出来再问下一个。跨项目并行（不同 `use <id>`）是安全的。

15. **论文版本管理：上传前先删旧版** — NotebookLM 对同一论文的多版本会分散 Gemini 的注意力，导致评审上下文过大。上传新版本前，先用 Python 客户端删除所有旧版本论文 source。然后通过 `note create` 上传新版本（`source add` 失败时的降级通路）。

17. **`source clean` 只能检测精确重复和错误源** — `source clean` 只查找: (1) 内容完全相同的重复 source；(2) 上传失败的 URL source（404/403）。它**不检测**：同标题的多个版本（可能来源于不同时间的同一次 `add-research`）、不同 URL 的同内容论文、旧版论文。当 `source clean` 报告 "already clean" 但 source 数量远高于预期时（如 726 个），问题不是精确重复，而是不同版本的堆积。解决方案：用 Python 客户端脚本（`references/source-dedup-script.md`）按标题分组去重。

24. **⚠️ Slide-deck 下载认证失败时的重建工作流** — `notebooklm download slide-deck` 可能因 cookies 过期或多账号 authuser 路由问题（触发 `received HTML instead of media file` 错误）而无法下载。但 Gemini 已经成功生成了内容。如果 `notebooklm list` 显示 `status=completed` 但下载失败，用以下两步恢复：
    ```bash
    # Step 1: 让 Gemini 描述已生成的完整内容
    notebooklm clear && notebooklm use <notebook_id> && notebooklm ask "请详细描述你刚才生成的幻灯片内容，逐页列出每页的标题、要点和设计建议。格式：Page N: 标题=..., 内容=..., 设计建议=..."
    
    # Step 2: 基于 Gemini 的描述，用 python-pptx 重建 PPT，匹配原始 PPT 的设计语言
    # 关键设计令牌从原始 PPT 的 XML 中提取：
    #   - 背景色: #0F172A (slate-900)
    #   - 卡片底色: #1E293B (slate-800) 
    #   - 边框色: #334155 (slate-700)
    #   - 强调色: #3B82F6 (blue-500)
    #   - 副标题色: #06B6D4 (cyan-500)
    #   - 主文字: #F8FAFC
    #   - 次要文字: #94A3B8 (slate-400)
    #   - 字体: Arial
    #   - 版式: 左侧竖线装饰条 (80px宽蓝色) + 圆角卡片
    #
    # 此工作流替代了直接下载，适用于多账号认证过期等无法修复的下载场景。
    ```

17. **CLI 的 source count 可能不准** — `notebooklm source list 2>&1 | grep -c "│"` 的计数可能比 Python API 返回的实际数量高（如 CLI 报 726 但 API 只返回 115）。这是因为 CLI 输出的表格行可能包含非 source 行。精确计数应使用 Python 客户端：`len(await client.sources.list(NB))`。

20. **`source fulltext` 提取 LaTeX 格式严重损坏** — 当用 `source fulltext` 从 NotebookLM 恢复 `.tex` 论文文件时，提取结果会严重破坏 LaTeX 格式：(a) 每两行之间插入空白行；(b) tabular 环境中的符号被拆到独立行上；(c) 内联数学模式被拆断跨行；(d) 引用标记中的 `>` 被识别为数学符号导致 `Missing $` 错误。恢复步骤：用 `source fulltext -o <file>` 保存 → Python 脚本修复（正则替换碎片 + 修复引用 + 修复数学模式）→ 再手动编译验证。

21. **⚠️ Shell 参数限制：`source add "$(cat bigfile)"` 对大文件报错** — 当文件 >80KB 时，shell 的 ARG_MAX 限制会导致 `bash: 参数列表过长` 错误（exit 126）。不要用 `$(cat)` 传大文件内容作为 positional argument。正确做法：

    ```bash
    # 方案A：Python subprocess（推荐 — 绕过 shell arg limit）
    python3 -c "
    import subprocess
    with open('bigfile.md') as f: content = f.read()
    r = subprocess.run(['notebooklm', 'source', 'add', '--type', 'text',
      '--title', '标题', '--timeout', '120', '-n', 'notebook_id', content],
      capture_output=True, text=True, timeout=180)
    print(r.stdout)
    "

    # 方案B：文件路径（`--type file`），但可能卡在 status=3 (preparing)
    notebooklm source add bigfile.md --type file --title "标题" --json

    # 方案C：分割为 <80KB 的块，分别上传为 part 1/N, part 2/N ...
    # 在 Python 中切片：for i in range(0, len(content), 80000): part = content[i:i+80000]
    ```

    **方案A 实战验证**（40篇参考文献，800KB合并文件，2026-05-31）：全部成功。方案B虽然上传但常卡在 preparing/error 状态。

19. **pdflatex + CJK 的中文支持受限** — 用 pdflatex（而非 xelatex）编译时，CJKutf8 包需要特定的 CJK 字体（如 `gbsn`），MiKTeX 可能未预装。替代方案：(a) 用 xelatex + ctex（会丢失 elsarticle 等期刊模板）；(b) 用拼音或英文转写代替中文；(c) 提取中文到独立文件后用 xelatex 单独编译再合并。

28. **🔴 Shared 项目 `source delete` 伪成功**：在 Shared（非 Owner）的 NotebookLM 项目中，`notebooklm source delete <id> -n <project>` 会输出 "Deleted source: <id>" 但实际上 source 不会被删除。这是 Google 共享权限限制导致 CLI 验证通过但 API 拒绝执行。**检测方法**：删除后立即 `notebooklm source list | grep <source_id>` 验证。Owner 项目不受影响。

21. **Shared 笔记本也有重复问题** — `notebooklm list --json` 输出的 `is_owner: false` 笔记本（Shared with you）同样可能积累大量重复 source。`notebooklm source clean` 对这些笔记本同样有效。

22. **`download slide-deck` 因下载端点令牌过期失败** — `generate slide-deck` 生成完成后（`artifact list` 显示 `completed`），`download slide-deck --format pptx` 可能因 Google 下载端点的认证令牌比列表/刷新端点的令牌更严格而过期失败（错误：`received HTML instead of media file` 或 `Authentication may have expired`）。`auth refresh` 通常只刷新 query/CRUD 端点的令牌，不刷新下载端点的令牌。恢复策略：
   1. 先确认 `artifact list` 显示为 `completed`（生成物本身完好）
   2. 尝试 `auth refresh` 后再下载
   3. 若仍失败：让用户在 NotebookLM 网页 UI 中直接点击 Slide Deck 的下载按钮
   4. 或让用户在本地浏览器重新登录 Google → `notebooklm login --browser-cookies chromium --account <email>` 获取新会话
   5. **不要重新生成** — 之前生成的 slide-deck 是正确的，只是下载通道受认证局限
   6. **降级恢复：Gemini 描述 → python-pptx 复现** — 当所有下载努力均失败时，用 `notebooklm ask` 让 Gemini 逐页描述已生成的 deck 内容，然后用 python-pptx 以用户喜欢的风格（如 slate-900 bg + blue #3B82F6 accent + 卡片式布局）复现。Gemini 能准确回忆起每页的标题、要点和设计建议——它生成的 Deck 内容仍在对话上下文中。

25. **⚠️ PDF索引超时/失败的根因：无可提取文本** — `source add file.pdf` 报 `status=3 (preparing)` 超时或 `error` 的根本原因通常不是超时，而是 PDF 文件**没有可提取的文本层**（如扫描版、字体编码异常）。用 `pdftotext file.pdf - | wc -c` 预先检查：
   - `>100 chars` → 有文本层，可上传
   - `≈0 chars` → 无文本层，**上传 arXiv URL** 替代：`notebooklm source add "https://arxiv.org/pdf/{arxiv_id}" --title "{bibkey}"`
   
   若确认有文本层但仍卡住，用 `scripts/check-pdfs-ready.sh` 或 `source list` 手动确认状态。持续卡住可能是PDF损坏（`file` 验证 `%PDF-` 头）。
