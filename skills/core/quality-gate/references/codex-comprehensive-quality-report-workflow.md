# Codex tmux 全面质量检查工作流（2026-06-24 实战验证）

## 适用范围

当用户要求"出具全面质量检查报告"或"质量检查"时。涵盖 L0/L0.5/G1-G7 + 三要素评价 + P0/P1/P2 分类的全量审计，且审计后自动修复所有可修问题。

## 核心理念

> **质量检查不应止于报告。** 用户明确要求"你自己做主"——Codex 出报告后，Hermes 必须自主修复所有 P0-P1 问题，然后汇报"修了什么，哪些修不了，为什么"。

## 认知同步原则

Hermes 与 Codex **共享 Synthos/skills/ 目录作为共同事实层**：

```
/media/.../Synthos/skills/
    ├── Hermes: skill_view('quality-gate')  → 读 SKILL.md
    └── Codex:  任务文件指明路径           → 自主加载 SKILL.md
```

**同一文件系统 → 天然同步。** 更新 SKILL.md 后两边都读新版本。不要手工提取模板内容嵌入任务文件——让 Codex 自己从 Synthos 加载。

## 前置条件

- Codex CLI 已安装且可通过 tmux 后台运行
- 论文目录包含 `01-manuscript/paper.tex` + `03-code/` 实验代码 + `06-references/` PDF 文件
- 工作目录：`/media/yakeworld/sda2/Synthos/outputs/papers/<paper-name>/`

## 变体 A：已有报告的重检工作流（2026-06-25 新增）

当论文已有 07-quality/ 下的初步报告和 fix-log，需要做**深度重检**而非首次检查时：

### 与标准流程的差异

| 步骤 | 标准流程 | 重检流程 |
|:-----|:---------|:---------|
| 数据收集 | 扫描所有目录 | **先读已有报告**，了解已知问题、已修内容、当前阻塞 |
| 任务文件 | 写全面检查 | **写针对性检查**——指向已有报告的遗留问题 |
| Codex 分配 | 直接派新任务 | 先**杀 stale 会话**（旧 Codex 可能卡在PDF下载），再新建 |

### 前置检查（Hermes 侧）

```bash
# 1. 读已有报告
cat 07-quality/comprehensive-report-*.md | head -50
cat 07-quality/issue-summary-*.md
cat 07-quality/fix-log-*.md  # 若有

# 2. 了解当前阻塞点
cat state.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'gate: {d.get(\"gate_status\")}, score: {d.get(\"quality_score\")}')
gr = d.get('gates_result', {})
if isinstance(gr, dict):
    bi = gr.get('blocking_issues', {})
    print('Blocking issues:')
    for k, v in bi.items(): print(f'  {k}: {v}')
    pi = gr.get('passing_items', {})
    print('Passing items:')
    for k, v in pi.items(): print(f'  ✅ {k}: {v}')
"

# 3. 检查 PDF 收集状态
ls 06-references/pdfs/ | wc -l
grep '@article\|@inproceedings' references.bib | wc -l
# 计算覆盖率

# 4. 检查是否有 stale Codex 会话
tmux list-sessions 2>/dev/null | grep codex
# 若有，先 capture 其当前进度再决定是否 kill
```

### 重检任务文件要点

- 在任务文件开头指明"这是重检——已有报告在 07-quality/ 下"
- 以已有的issue-summary为输入，逐条验证是否有修复进展
- 检查新引入的数据/修改是否引入了新问题

### 典型场景：PDF收集阻塞

如果重检发现 PDF 收集仍是阻塞（如 31% 覆盖率），**不要重复派 Codex 做 PDF 下载**——已在上一轮失败的任务不会在下一轮自动成功。而是：
1. 记录不可获取的引用为"需书面说明"（经典/书/仓库页面）
2. 在任务文件中明确指示 Codex 跳过 PDF 下载，专注数据检查
3. PDF 覆盖率不足标记为已知限制，不阻塞其他维度的检查

## 完整工作流（5步闭环）

### Step 1: 数据收集（Hermes 侧预处理）

在发送给 Codex 之前，先收集基本数据用于构建任务文件：

```bash
# 1. 检查目录结构
ls -la outputs/papers/<paper-name>/
ls -la outputs/papers/<paper-name>/03-code/

# 2. 列举所有 JSON 文件
find outputs/papers/<paper-name>/ -name '*.json' -type f | sort

# 3. 检查 state.json
cat outputs/papers/<paper-name>/state.json

# 4. 检查编译日志
grep -c 'Error\\|Warning' outputs/papers/<paper-name>/01-manuscript/paper.log

# 5. 检查参考文献目录
ls outputs/papers/<paper-name>/06-references/ | head -20
```

### ⚠️ 多目录数据源陷阱（2026-06-25 新增）

**问题**：论文的 03-code/ 目录可能只包含一个空目录或软链，实际实验数据在 `experiment/`、`experiments/`、`catboost_info/` 等根目录下。同一论文可能有多个目录包含结果 JSON，且可能数值不同。

**HCS-3WT 案例**（2026-06-25）：
- `03-code/` → 空目录（0KB）
- `experiment/wbc_original_results.json` → `hcs_fn: 0.8, fn_red: -5.0`
- `03-code/experiments/wbc_original_results.json` → `hcs_fn: 1.2, fn_reduction_pct: -28.0`

两份 JSON 的同一个指标相差 12%（0.8 vs 1.2），因不同版本的实验脚本产出。

**检测方法**：
```bash
# 找到所有结果 JSON
find . -name '*result*.json' -type f | sort

# 对关键字段做跨目录交叉比对
python3 -c "
import json, glob, os
key_fields = ['auto_rate', 'auto_acc', 'fn_red', 'hcs_fn', 'hcs_acc', 'dataset']
for f in sorted(glob.glob('**/*result*.json', recursive=True)):
    if os.path.getsize(f) < 100: continue
    try:
        d = json.load(open(f))
        vals = {k: d.get(k) for k in key_fields if k in d}
        if vals:
            print(f'{f}: {vals}')
    except: pass
"
```

**规则**：
- 两个目录的 JSON 完全相同（diff=空）→ ✅ 只是副本，任取一个
- 两个目录的 JSON 有差异（diff≠空）→ ⚠️ DATA_DIVERGENCE，需标记哪个是权威源
- 通常以 03-code/ 下的版本为权威；若 03-code/ 为空，以 experiment/ 下最新修改的为准

### Step 2: 编写任务文件（认知同步协议）

**原则**：Hermes 决策，Codex 执行。任务文件只写「做什么」，不写「怎么做」。

```markdown
# <论文名称> 全面质量检查任务

## 技能加载（必做——自己读 Synthos）

Codex 能从文件系统直接访问**两个**技能仓库：

```
公开库: cat /media/yakeworld/sda2/Synthos/skills/<name>/SKILL.md
私有库: cat /media/yakeworld/sda2/Synthos-private/skills/<name>/SKILL.md
```

任务中按需加载。例如：

1. `cat /media/yakeworld/sda2/Synthos/skills/core/quality-gate/SKILL.md`
   — 公开库：质量闸门方法论
2. `cat /media/yakeworld/sda2/Synthos-private/skills/paperjury/SKILL.md`
   — 私有库：论文陪审团（含论文数据）
3. `cat /media/yakeworld/sda2/Synthos/skills/core/quality-gate/references/comprehensive-quality-report-template.md`
   — 报告模板

**注意**：技能方法在公开库，审计数据和论文实例在私有库。按需加载。私库技能路径为 `skills/private/<name>/SKILL.md`（相对路径，Codex 工作目录在 Synthos 根下）。

## 工作目录
cd /media/yakeworld/sda2/Synthos/outputs/papers/<paper-name>/

## 检查范围
按 quality-gate 技能要求执行全面质量检查，包括但不限于：
- 凡数必源矩阵：逐数值追踪到 JSON/CSV 源
- 凡引必查清单：PDF存在性+DOI匹配+体裁验证
- 代码诚实验证：独立复现关键数字
- 虚构检测扫描：7种LLM虚构模式
- 通用六域报告（Q1-Q6）+ 类型专项报告 + 参考文献审查 + 附件问题清单

## 报告输出
保存到 07-quality/codex-comprehensive-report-<date>.md
格式：四份独立报告 + 附录（详见 comprehensive-quality-report-template.md）
```

**关键要素**：
- ✅ **不再嵌入技能内容**——Codex 自己从 Synthos 加载，永远最新
- ✅ 指定工作目录
- ✅ 指定 Synthos 技能路径（绝对路径）
- ✅ 指定报告模板路径
- ✅ 指定输出格式和保存位置

### Step 3: 通过 tmux 发送任务

遵循 `codex-tmux-control` 的铁律：

```bash
# Terminal Call 1: 创建会话（如果不存在）
tmux new-session -d -s codex-quality -c /media/yakeworld/sda2/Synthos/outputs/papers/<paper-name>

# Terminal Call 2: 启动 Codex
tmux send-keys -t codex-quality 'codex --yolo'

# Terminal Call 3: 回车
tmux send-keys -t codex-quality Enter

# Terminal Call 4: 等 45s 确认就绪
sleep 45 && tmux capture-pane -t codex-quality -p | tail -5

# Terminal Call 5: 发送指令文本（不含 Enter）
tmux send-keys -t codex-quality '请读取 /tmp/codex_<task>_task.md 并执行全面质量检查，完成后报告结果'

# Terminal Call 6: 发送 Enter（独立调用）
tmux send-keys -t codex-quality Enter

# Terminal Call 7: 等 30-120s 后检查进度
sleep 30 && tmux capture-pane -t codex-quality -p -S -20 | tail -20

# 继续检查
sleep 90 && tmux capture-pane -t codex-quality -p -S -30 | tail -30
```

### Step 4: 读取报告

Codex 完成后，读取报告并提取所有 P0/P1 问题：

```bash
cat /media/yakeworld/sda2/Synthos/outputs/papers/<paper-name>/07-quality/<report-name>.md
```

**重点关注**：
- 🔴 **P0 问题** — 必须修复，逐条判断能否自主修复
- 🟡 **P1 问题** — 建议修复，能修的都修
- 检查每个问题的"修复建议"是否可执行

### Step 5: 自主修复闭环 🔄（2026-06-24 新增 — 这是最关键的一步）

**原则**：不要让用户看到"这里有 N 个问题待修复"的报告。自己修。

#### 修复决策矩阵

| 问题类型 | 自主可修? | 操作 |
|:---------|:---------:|:-----|
| paper.tex 数值错误 | ✅ | 直接 patch paper.tex，数值来自 JSON |
| paper.tex 文本声明错误 | ✅ | 直接 patch（模型数 30→33、删除声明性引用等） |
| bib 清理（orphan/DOI/重复） | ✅ | write_file 重写 references.bib |
| 错误 PDF 文件 | ✅ | 删除，从 SS/Crossref 重新下载 |
| Kapoor2023 等 Cloudflare 墙 | ❌ | 删除错误 PDF，在 fix-log 留下 OA 下载链接 |
| 实验代码/JSON 残留文件 | ✅ | 删除或更新 stale JSON 的 ensemble 数据 |
| p-value/Cohen's d 未记录 | ❌ | 需重新运行实验 — 在 fix-log 标记 |
| LaTeX 编译反斜杠污染 | ✅ | Python 正则修复 |
| 编译错误 | ✅ | 清理辅助文件，run pdflatex×3 + bibtex |
| state.json 更新 | ✅ | 写入修复后的 quality_score 和 notes |

#### 执行顺序

```
读取报告 → 分析每个 P0/P1 问题 → 分类为"可自主修复"和"需人工"
  → 并行执行所有可自主修复的操作
  → 清理 LaTeX 辅助文件
  → 重新编译：pdflatex → bibtex → pdflatex → pdflatex
  → 验证编译成功（0 errors, 0 undefined refs）
  → 更新 state.json（notes、gate_timestamp、quality_score）
  → 写 fix-log.md（修了什么、修不了的标记为 TODO）
  → 发送 PDF 给用户
```

#### 修复操作速查表

```bash
# 1. paper.tex: patch 单处文字
patch -i 'paper.tex' -o '旧文字' -n '新文字'

# 2. paper.tex: 多处同一修改（如 30→33）
# 每处独立 patch

# 3. references.bib: 完整重写（清理大量 orphan 时）
# 不要 patch bib（会重复/损坏条目），用 write_file

# 4. LaTeX 反斜杠修复（patch 工具双转义后）
python3 -c "
import re
with open('paper.tex') as f:
    c = f.read()
# 修复 \\\\\\\\X → \\\\X
c = re.sub(r'\\\\\\\\\\\\([a-zA-Z])', r'\\\\\\1', c)
with open('paper.tex', 'w') as f:
    f.write(c)
"

# 5. LaTeX 重新编译
rm -f *.aux *.bbl *.blg *.out *.lof *.lot *.toc
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex

# 6. 验证编译结果 — 检查 errors 和 undefined refs
grep -c 'Error' paper.log  # 应为 0
grep -c 'undefined' paper.log  # 应为 0（section/table ref 排除）

# 7. state.json: 用 write_file 重写（patch 容易引入 JSON 语法错误）
```

#### fix-log 模板

在 `07-quality/fix-log-<date>.md` 记录自主修复结果：

```markdown
# 自主修复报告

> 修复时间：YYYY-MM-DD HH:MM
> 修复模式：自主执行（基于 Codex 质量报告）

## 修复清单

### ✅ P0-N: 问题描述 — 已修复
- 操作：具体操作
- 文件：修改了哪些文件
- 验证：如何验证修复正确

### ❌ P0-N: 问题描述 — 需人工处理
- 原因：为什么不能自主修复
- 待办：用户需要做什么、用什么工具、提供链接/命令

## 编译状态
`pdflatex → bibtex → pdflatex → pdflatex` ✅/❌
- N pages, N KB, N errors, N warnings
- N undefined references

## 剩余待办
汇总所有未自主修复的问题
```

## 实战效果（2026-06-24 PIMA）

| 指标 | 值 |
|:-----|:---|
| 任务文件 | `/tmp/codex_quality_report_task.md` (5.6KB) |
| Codex 处理时间 | 1分44秒 |
| 报告 | 476行，43个数值声明，7个JSON文件 |
| 发现 P0 | 3个 |
| **自主修复 P0** | **3个（1个待手工下载PDF）** |
| **自主修复 P1** | **~6个（模型数/OpenML/bib清理等）** |
| 修复耗时 | ~5分钟 |
| 最终评分 | 72→85（修复后 state.json 更新） |

## 注意事项

1. **任务文件必须自包含** — Codex 无 Hermes 的会话 memory
2. **等待时间** — vLLM 负载高时 Codex 响应需 1-3min
3. **不要用 delegate_task** — 全量质量检查会超时 600s
4. **勿在用户等待时报告"有 N 个问题"** — 用户看到的是已修复的版本
5. **LaTeX 反斜杠陷阱** — patch 工具必然双转义 `\cite`、`\pm` 等命令，每次 patch 后必须检查并修复
6. **bib 文件用 write_file** — patch 工具会损坏 BibTeX 条目结构
7. **Kapoor 式 PDF 验证** — 用 SS API 查 `openAccessPdf.url` 比直接从 bib 下载更可靠，但不能过 Cloudflare
