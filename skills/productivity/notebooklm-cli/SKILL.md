---
name: notebooklm-cli
description: 子skill | NotebookLM CLI全功能指南 — Q&A知识提取、内容生成(报告/视频/音频/信息图/幻灯片)、文献检索。响应paper-pipeline的P1阶段调用。
allowed-tools:
- terminal
- file
- web
license: MIT
metadata:
  synthos:
    version: 3.5.0
    author: Synthos
    signature: 'action: str, params: dict -> result: dict'
---

# NotebookLM CLI — 知识大脑

> **架构定位**: NotebookLM = Synthos 的廉价知识大脑 (Tier 1)。详见 `references/knowledge-brain-architecture.md`。

## 核心原理（文言）

**一问一收，不并投** — 每轮只问一个问题，用答案决定下一个。不一次全抛。

**言不必行** — Q&A输出≠源代码执行结果。

**节点有闸** — Gap门/假设门/方法门/实验门，每节点过闸才前进。

## 快速参考

| 功能 | 命令 | 参考 |
|:-----|:-----|:------|
| 登录 | `notebooklm login` | `references/cli-cheatsheet.md` |
| 列表 | `notebooklm list` | — |
| 切换 | `notebooklm use <partial_id>` | — |
| 问答 | `notebooklm ask "问题"` | 逐问法见下 |
| 搜索 | `notebooklm source add-research "query"` | 导入网页源(非PDF) |
| 上传 | `notebooklm source add file.pdf` | v0.4.1+自动类型检测 |
| PDF上传 | `source add "https://arxiv.org/pdf/{id}"` | arXiv URL直传 |
| 清理 | `notebooklm source clean -n <id> -y` | 自动去重清理 |
| 删除 | `notebooklm source delete <id> -y` | Owner项目有效 |
| 生成 | `notebooklm generate <type>` | report/video/audio/slide-deck/infographic |
| 下载 | `notebooklm download <type> <id>` | 语法因类型而异 |
| 状态 | `notebooklm artifact list` | 监控生成任务 |

### 逐问法（核心方法）

每轮一个问题，答案决定下一个。标准序列：Q1领域地图→Q2共同盲区→Q3形式化Gap→Q4科学假设→Q5技术方案→Q6实验设计。

详见 `references/iterative-literature-first-paper-protocol.md`。

### 三步确权法

1. 问状态 → 2. 问数值 → 3. 问来源

## 关键陷阱

- ⚠️ 传入Markdown: `source add "$(cat file.md)" --type text`（非 `file.md`）
- ⚠️ YAML frontmatter导致`---`被click解析错误: 上传前剥离
- ⚠️ 无文本层PDF: 用 `pdftotext pdf - | wc -c` 检查，≈0则用arXiv URL直传
- ⚠️ 同一项目禁止并行`ask`(串话)
- ⚠️ Slide-deck下载认证失败: Gemini描述→python-pptx重建
- ⚠️ Shell参数限制: `$(cat bigfile)` 超80KB报错, 用Python subprocess
- ⚠️ `source delete`在Shared项目伪成功(仅Owner有效)
- ⚠️ PDF索引超时: 无可提取文本层, 预先`pdftotext`检查

完整陷阱列表见 `references/notebooklm-cli-pitfalls.md`。
