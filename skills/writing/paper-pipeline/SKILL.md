---
name: paper-pipeline
description: '主skill | SCI论文全流程编排器。声明与执行分离、逐问收束、节点闸门、闭环进化。调用子skill: notebooklm-cli, sci-paper-standard-structure, research-paper-search, sci-paper-quality-review。质量检查统一通过 quality-gate。'
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
metadata:
  synthos:
    version: 3.13.0
    author: Synthos
    signature: 'paper_name: str -> pipeline_report: dict'
    absorbed_skills:
    - notebooklm-writing-workflow
    - synthos-writing-workflow
    - scc-paper-writing-norms
    - academic-paper-completion
    - public-dataset-prediction-paper
    - paper-reference-pipeline
    - research-paper-writing
    execution_note: 吸收子skill内容在 references/*-absorbed.md
---

# Paper Pipeline — 科研全流程编排器

## 原理层 · 文言

| 概念 | 文言 | 义 |
|:-----|:-----|:----|
| 声明与执行分离 | **先立后行，不混不乱** | 写好全文再编译，不边写边编 |
| 逐问收束 | **一问一答，渐次收窄** | 每轮NotebookLM问一个具体问题 |
| 节点闸门 | **节不过则停，门不通则返** | 每阶段完成必经质量门 |
| 闭环进化 | **投完不弃，检之改之** | 投稿后仍可自检修订 |
| 论文即验证 | **文以验法，技乃所产** | 可复用的技能才是真正产出 |
| 持续推进 | **流水线不间歇，论文逐个推进** | paper-orchestrator常驻后台，非cron定时触发 |

## 两种运行模式

| 模式 | 方式 | 适用场景 |
|:-----|:------|:---------|
| **持续运行** | `paper-orchestrator.py` (tmux常驻) | 论文队列批量处理，24小时不中断 |
| **定时触发** | cron jobs (每次独立会话) | 监控、扫描、报告等轻量任务 |
| **手动触发** | 用户直接调用 | 单篇论文深度处理 |

### 持续运行模式

`paper-orchestrator.py` 是常驻后台的论文管线Worker，通过tmux保持持久会话。

**启动方式：**
```bash
tmux new-session -d -s paper-orch -n worker
tmux send-keys -t paper-orch:worker "cd /home/yakeworld/.hermes/scripts && python3 paper-orchestrator.py" Enter
```

**生命周期：**
- 持续扫描队列，每10秒检查一次
- 对每篇论文：检查状态 → 读取缺失步骤 → 调用API → 更新状态
- 处理完自动进入队列下一位（按完成度从低到高）
- 支持优雅停止（SIGTERM/SIGINT），异常自动重试3次
- 每步完成后sleep(5)让GPU喘气
- 日志：`/home/yakeworld/.hermes/cron/logs/paper-orchestrator.log`
- PID文件：`/home/yakeworld/.hermes/cron/logs/paper-orchestrator.pid`

**Control commands:**
```bash
python3 paper-orchestrator.py start  # 启动
python3 paper-orchestrator.py stop   # 优雅停止
python3 paper-orchestrator.py status # 查看队列状态
python3 paper-orchestrator.py tail   # 实时查看日志
```

**⚠️ 2026-06-05: Script missing.** `paper-orchestrator.py` is referenced by this skill but does not exist on disk at `scripts/paper-orchestrator.py` or any known path. The cron jobs `paper-orchestrator` and any workflow relying on it will fail with `ModuleNotFoundError`. Either:
1. Create the orchestrator script (see design in skill body), OR
2. Disable the `paper-orchestrator` cron job until script exists, OR
3. Process papers manually via `cron` → `step_gap_analysis` → `step_abstract` → manual writing of remaining steps.

**Important**: Papers completed via manual cron processing (without orchestrator) will NOT have a full `paper.tex` assembled. The `assemble_pdf_from_steps.py` script only pulls the last step file into a minimal .tex. To get a full compiled PDF, the orchestrator must have assembled `paper.tex` from all 8 steps during the original write phase. If paper.tex is missing or minimal:
- Check if `01-manuscript/paper.tex` exists and has >100 lines
- If not, manual assembly is needed (read all step_*.md files and concatenate)
- See reference: `references/pdf-compilation-flow.md`

**处理逻辑：**
1. 扫描所有论文目录 (`/media/yakeworld/sda2/Synthos/outputs/papers/`)
2. 优先处理有内容但进度低的论文（有.tex或.abstract.md）
3. 按IMRaD标准顺序：gap_analysis → abstract → intro → method → results → discussion → ref_check → quality_check
4. 每步输出保存到 `01-manuscript/step_<步骤名>.md`
5. 更新 `state.json` 记录完成步骤

### PDF 编译（cron 手动触发）

当 cron 完成所有 8 步后，需手动触发 PDF 编译：
```bash
python3 /media/yakeworld/sda2/Synthos/skills/writing/latex-output/scripts/assemble_pdf_from_steps.py <paper_dir>/01-manuscript
pdflatex -interaction nonstopmode paper.tex
pdflatex -interaction nonstopmode paper.tex  # 第二次消除 cross-reference
```
详细流程见 `references/pdf-compilation-flow.md`。

### 定时触发模式（保留用于监控/扫描）

- `synthos-evolution-probe` (每6h) → 轻量进化检查
- `papers-daily-scan` (每6h) → 质量检查
- `literature-monitor` (每天) → 文献监控
- `bib-standardization` (每天) → 引用标准化
- `daily-papers-report` (每天) → 日报生成
- `synthos-evolution-full` (每天) → 完整11步进化
- `autonomous-core-researcher` (每3h) → 最重的科研探索

**关键区别：**
- ✗ 持续运行模式不再是"每次cron触发都是全新的会话"
- ✓ 所有任务都是cron定时触发 → 运行 → 退出 → 仅适用于监控/扫描任务
- ✓ 论文处理任务由常驻进程处理，保持上下文连续性

## 六阶段流程