---
name: paper-pipeline
description: "主skill | SCI论文全流程编排器。v3.18.10新增Trap#42跨项目参考文献污染检测（Synthos Paper ID后缀/占位符键名/空条目/Prose提及无cite）。v3.18.9新增Trap#41 paper-queue.json幽灵条目逆方向。v3.18.5-8: D10a批量扫描+natbib盲区+注释过滤+路由修复。v3.18: Track A晋升协议。v3.16: 队列自愈+ABSOLUTE WHITE独立验证。v3.15: 轨道B四步工作流。"
version: 3.18.10
author: "Synthos + 临床科研设计与论文写作 + 用户杨晓凯"
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: "SCI论文全流程编排器。v3.18.10新增Trap#42跨项目参考文献污染检测。v3.18.9新增Trap#41 paper-queue.json幽灵条目逆方向。v3.18.5-8: D10a批量扫描+natbib盲区+注释过滤+路由修复。v3.18: Track A晋升协议。v3.16: 队列自愈+ABSOLUTE WHITE独立验证。v3.15: 轨道B四步工作流。"
    signature: |
      paper_name: str -> pipeline_report: dict | pipeline_report: dict (stage, status, quality_score, next_step)
    related_skills: [quality-gate, evolution, project-experience-distillation, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification, sci-paper-quality-review, conversation-to-memory, knowledge-extraction, knowledge-acquisition, academic-atom-architecture, reference-verification]

---

## IO_CONTRACT

- **input**: `paper_name: str` — 论文目录名，相对于 papers/ 目录
- **output**: `pipeline_report: dict` — 包含 stage, status, quality_score, next_step 的流水线报告
- **side_effects**: 更新论文目录下的 state.json、quality_check.md、LaTeX 源文件及编译产物
> 对应原则：P2（机械原子暴露输入输出规范）
# Paper Pipeline — 科研全流程编排器（哲学驱动版）

## 支持参考文件

- `references/3d-curve-fitting-figures.md` — 3D曲线拟合图生成规范
- `references/citation-count-vs-bib-count.md` — 引用计数与Bib条目数的正确关系（引用>条目数=正常）
- `references/cross-project-contamination-patterns.md` — 跨项目参考文献污染检测模式（Synthos Paper ID后缀、占位符键名、空条目、prose提及无\cite）（v3.18.10新增）
- `references/meddata-authentication-debugging.md` — MedData PDF 下载认证系统分析（见 quality-gate/references/，跨技能引用）

| 概念 | 文言 | 义 |
|:-----|:---|:---|
| 声明与执行分离 | **先立后行，不混不乱** | 写好全文再编译，不边写边编 |
| 逐问收束 | **一问一答，渐次收窄** | 每轮NotebookLM问一个具体问题，答案逐轮收敛 |
| 节点闸门 | **节不过则停，门不通则返** | 每阶段完成必经质量门，不通过不前进 |
| 闭环进化 | **投完不弃，检之改之** | 投稿后仍可自检修订，为下轮迭代储备 |
| 论文即验证 | **文以验法，技乃所产** | 论文不是终极目标——它验证系统是否工作；可复用的技能才是真正产出 |
| 自我进化 | **一气流注，不假再生** | 从方向到投稿全流程自动化，连续运行，高质量科研自然涌现 |

> **文以验法，技乃所产。自进化是唯一目标，论文是验证手段，技能是系统产物。**

## 论文管线双轨制（2026-06-18 新增）

> **论文质量为唯一KPI**，研究空白进知识库不进论文管线。轨道A（论文管线）和轨道B（知识库）是两条平行轨道，不再混用。

### 轨道A：论文管线
- 进入条件：有paper.tex + status.json
- 流程：G1-G7质量门禁
- 输出：ready_for_submission

### 轨道B：知识库 — Autonomous Core Researcher 知识条目工作流

> **cron产出直接走轨道B。** 每轮运行只执行一个步骤（ONE step per run）。research-queue.json 不存在时自动从 _knowledge_only/ 初始化。

#### 进入条件
- 无paper.tex但有研究内容（有step_*.md、参考文献、代码、目录）→ 目录结构在 `_knowledge_only/` 下

#### 四步内循环（ONE step per cron run）

```
Run N:   literature_scan     — 扫描研究空白，检查white space
Run N+1: gap_analysis        — 深入分析，明确G6 first-mover
Run N+2: hypothesis_generation — 生成可证伪假说
Run N+3: knowledge_entry     — 产出 knowledge_entry_*.md + 更新评分
                             → 完成后标记 candidate 为 completed
```

每步需要 `skill_view()` 加载对应的认知原子技能（knowledge-acquisition / knowledge-extraction 等）。

#### literature_scan 协议 — ABSOLUTE WHITE 独立验证（v3.16）

> **核心原则**：不信任 gap_analysis.md 中的 ABSOLUTE WHITE 声明。它们可能来自早期 LLM 运行且未经验证，或已过期（写作期间有新论文发表）。

**执行流程**：

```
Step 1: 读取 candidate 的 gap_analysis.md / hypothesis.md（如存在）
  → 提取所有 ABSOLUTE WHITE 声明及其 PubMed 查询词
Step 2: 独立运行 PubMed 验证（≥7 个查询，含变体）
  → 每个查询输出：命中数 + 前 3 篇论文的 PMID + 标题
Step 3: 对任何命中（包括相邻竞争者），获取摘要并分析：
  ├── 直接竞争者（相同方法+相同领域）→ ABSOLUTE WHITE 失效
  ├── 相邻竞争者（相同方法+不同领域，或不同方法+相同领域）→ 记录并明确差异化
  └── 不相关 → 忽略
Step 4: 输出 refined_white_space 声明 + 竞争者边界地图
Step 5: 写入 step_literature_scan.md
```

**ABSOLUTE WHITE 失效时的处理**：
- 不删除 candidate → 修订 gap 为 "GAP EXISTS BUT NARROWER"
- 记录直接竞争者到 literature_scan 输出
- 若竞争太密集（≥3 篇直接竞争者）→ 标记为 stuck，跳过

#### Track A 碰撞检测（v3.16）

> **2026-06-18 实战**: 113-scleral-remodeling-ODE 在 Track B 初始化时，Track A 已有 3 篇 scleral 相关论文（187, 150, corneoscleral-shell）。

**literature_scan 执行时**：
1. `grep` paper-queue.json 查找 candidate 关键词（如 "scleral"）
2. 对命中论文，读取其 paper.tex 标题和摘要
3. 明确记录差异化：
   - 方法层面：Track B 是 ECM 生化动力学 vs Track A 是结构生物力学
   - 疾病层面：Track B 是近视 vs Track A 是青光眼/角膜扩张
   - 模型层面：Track B 是 MMP→胶原→刚度级联 vs Track A 是弹性模量演化
4. 若无法差异化（方法+领域+模型全部重叠）→ 标记为 duplicate，不加入队列

#### research-queue.json 自愈协议（每次 cron 运行前执行）— v3.18

> **2026-06-18 实战**: 2026-06-18 第二次运行发现新变种——4个 candidates 有 paper.tex 但不在 paper-queue.json 中，卡在 _knowledge_only/。自愈协议跳过它们但未晋升。新增 Step A（晋升协议）。

**⚠️ research-queue.json 使用 `candidates` 数组（而非 `queue`）。** 以下协议的 Python 实现中，访问 `queue["candidates"]` 而非 `queue["queue"]`。访问前先 `cat research-queue.json` 查看实际格式——生产环境文件可能仍使用旧版 `queue` 键名。

**Step 0 — 自愈 + 晋升（每次读写 research-queue.json 前执行）：**

```
读取 research-queue.json（不存在则自动初始化）
  ↓
Phase 1 — 已有 candidate 清理:
  对每个 candidate:
  ├── candidate 已存在于 paper-queue.json 中（Track A）？
  │   ├── 从 research-queue.json 移除（逻辑清除）
  │   ├── 检查 physical 目录位置：
  │   │   ├── 在 _knowledge_only/<candidate_id>/ 下？ → 非论文目录已有 paper.tex → mv 到 ../<candidate_id>（物理搬迁）
  │   │   ├── 同时存在于 _knowledge_only/ 和 papers/？ → 内容不同保留两份（divergent copy），只从队列移除
  │   │   └── 已在 papers/ 下 → 只需队列移除
  │   └── 记录 relocation 日志到 research-queue.json 的 cleanup_run 字段
  ├── candidate 在 _knowledge_only/ 中无目录？ → 移除（幽灵条目）
  ├── candidate 在 _knowledge_only/ 中无 step_*.md 且无 .py 且无 paper.tex？ → 移除（空壳）
  ├── 同一 candidate_id 出现多次？ → 保留步骤最多的，删除其余（去重）
  └── 保留
  ↓
Phase 2 — 新 candidate 发现:
  对 _knowledge_only/ 中未在 research-queue.json 的 queue 中的子目录:
  ├── 有 paper.tex？
  │   ├── 检查 paper-queue.json 是否有同名冲突（Track A 已存在？）
  │   │   ├── 已有同名 → 物理搬迁到 papers/（mv _knowledge_only/<dir> ../<dir>），不经过 Phase 3
  │   │   │   ⚠️ 检查 papers/ 中是否已有同名目录；若有且内容不同，保留 _knowledge_only/ 副本（divergent copy），不搬迁
  │   │   └── 无同名 → 执行 Phase 3（Track A 晋升协议）
  │   └── 记录搬迁日志
  ├── 有 step_*.md OR .py 仿真代码 OR 参考文献？ → 添加为 pending
  └── 空壳（有效文件 < 5）→ 删除目录
  ↓
Phase 3 — Track A 晋升协议（针对有 paper.tex 且未在 paper-queue.json 中的 candidate）:
  对每个有 paper.tex 的未入队目录:
  ├── 检查 paper-queue.json 是否有同名冲突（再次确认——Phase 2 已检查）
  ├── 无冲突 → 轻量晋升（首选 `python3 scripts/promote-track-a.py` 自动执行）:
  │   ├── 读取现有 state.json 中的 quality_score, gate_status, stage
  │   ├── mv _knowledge_only/<dir> ../<dir>
  │   ├── 确保有 index.md（缺少则创建，source=promoted_from_track_b）
  │   ├── 确保有 01-manuscript/paper.tex（缺少则从根目录拷贝或创建软链接）
  │   └── 添加条目到 paper-queue.json（**保持 state.json 的现有值**，勿覆盖为 qs=60）
  ├── 有冲突（同名或高度相似）→ 保留现状，记录冲突原因
  └── 不在 research-queue.json 中记录晋升后的条目（它们已走 Track A）
  ↓
更新 total_candidates, total_pending, next_candidate, next_step
```

> **2026-06-18 实战教训**: 之前 Phase 1 的"移除"只做了逻辑清除（从 queue 删除），未做物理搬迁。25 篇已入 paper-queue.json 的 Track A 论文的目录残留在 _knowledge_only/ 中，造成"幽灵条目逆问题"。本版本修复：Phase 1 增加物理目录位置检查 + mv 搬迁；Phase 2 增加 paper-queue.json 预检查，避免已入队论文误入 Phase 3。

**空壳删除阈值**：目录包含有效文件（非 .aux/.log/.out/.spl/.toc）< 5 → 删除。

#### research-queue.json 初始化（首次运行无queue时）

从 `_knowledge_only/` 扫描所有子目录建立候选列表，每个目录对应一个 candidate：

```json
{
  "candidate_id": "<paper-dir-name>",
  "status": "pending",
  "current_step": null,
  "steps_completed": [],
  "quality_score": null,
  "knowledge_score": null,
  "gate_status": "PENDING",
  "next_candidate": "<first-pending>",
  "next_step": "literature_scan"
}
```

**规则**：research-queue.json 不存在时自动初始化，不要报错退出。

#### knowledge_entry 产出物结构

`knowledge_entry_{candidate_id}.md` — Markdown文件，必需节：

| 节 | 内容 |
|:---|:-----|
| 元数据 | Type, Source, Status, Generated, Quality Score |
| Research Gap | ABSOLUTE_WHITE 验证结果 |
| Approach | 方法概要 |
| Key Findings | 核心数值结果表（metric + value + verdict）|
| Clinical Implications | 临床转化意义 |
| Knowledge Score | 六维评分 + 加权平均 |
| Tags | 关键词标签 |

#### Knowledge Score 评分矩阵

| 维度 | 权重 | 示例高分 |
|:-----|:----:|:---------|
| Gap Significance | 0.25 | ABSOLUTE_WHITE 验证通过 |
| Methodological Soundness | 0.20 | ODE+PINN+SO(3)约束 |
| Result Completeness | 0.20 | 参数+轨迹+分类+分岔+消融 |
| Clinical Translation | 0.15 | BVL分级+跌倒风险+康复分层 |
| Reproducibility | 0.10 | 合成数据+代码声明 |
| Narrative Quality | 0.10 | 完整结构+引用链+tags |

**加权平均 ≥ 0.80 为 T2 PASS**。

#### state.json 更新协议（knowledge_entry 完成后）

quality_score 加 2 分（从 gap_analysis 基础分提升），新增 knowledge_score 字段，gate_status 设为 PASS。

#### quality_score 基准增量

| 步骤 | 基准分 |
|:-----|:------:|
| literature_scan | 60 |
| gap_analysis | 65 |
| hypothesis_generation | 72 |
| knowledge_entry | 80 |

#### 队列递进规则

```
状态: pending → in_progress → completed 或 stuck
```

每步完成后：追加 steps_completed → 更新 current_step → 更新评分 → 设 next_candidate 为下一个 PENDING。

#### 陷阱

1. research-queue.json 不存在→自动从 _knowledge_only/ 初始化
2. _knowledge_only/ 为空→输出 [SILENT] 退出
3. candidate 无 state.json→从目录内容推断基础分
4. quality_score(0-100) ≠ knowledge_score(0.0-1.0)
5. 已完成步骤不重复处理 (基于 state.json 的 steps_completed 字段判定, 而非 queue 状态)
6. 若 knowledge_entry_*.md 存在但 queue 丢失, state.json 的 steps_completed 为准, 跳过已完成步骤不重复执行

🔴 **research-queue.json 格式陷阱（2026-06-18 实战）**: `candidates` 数组 vs `queue` 数组
   - research-queue.json 使用 `candidates` 作为数组键名（非 `queue`）
   - 访问前先 `cat research-queue.json` 查看实际格式
   - 格式：`{ "candidates": [...], "total_candidates": N, ... }`
   - Python 访问：`queue["candidates"]` 而非 `queue["queue"]`

🔴 **Phase 3 晋升时不要覆盖已存在的 state.json（2026-06-18 实战）**:
   - 4个候选项的 state.json 中 quality_score=70, gate_status=PASS, stage=publication_complete
   - 硬编码 qs=60, gate=PENDING 会创建人为降级，触发不必要的 paper-repair
   - **原则**：读取 state.json 的现有值，honour 它们，只添加 paper-queue.json 条目

### 空壳处理
- 清理空壳（<5文件）→ 删除
- 归档低价值内容 → _drafts_archive/
- 知识库轨道 → _knowledge_only/

详见 `references/dual-track-system.md`

## P0 预检闸门（引用预检）— v3.13新增

> 在目录标准化（09-dir）和质量检查（P4）之前，必须先做引用预检。
> **D8≥30 ≠ 引用健康。zombie条目会虚增D8，且编译时产生未定义引用警告。**
> 本闸门确保进入P4的引用数据是干净的。

### 步骤1: D10a僵尸/孤儿检测（P0闸门）

对每篇论文的 `.tex` + `.bib`，在标准化前执行：

**⚠️ 先检测引用模式**：`\begin{thebibliography}` 存在 → thebibliography 模式（从 tex 提取 bibitem 键）；否则 → BibTeX 模式（从 .bib 提取键）。详见 Trap 33。

**⚠️ 先检测引用风格**：natbib 论文使用 `\citep{}` / `\citet{}` 而非 `\cite{}`。标准 `\cite[tp]?\s*\{` 正则对 natbib 论文返回 0 匹配——**必须先 grep 确认实际引用命令再选正则**。

```python
import re, os

with open('paper.tex') as f: tex = f.read()

# 检测引用风格 — 选择正确的正则
if '\\citep{' in tex or '\\citet{' in tex:
    # natbib 风格 — 用覆盖所有变体的正则
    cite_pattern = r'\\(?:cite|citep|citet|citenp|citealp|citealt)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}'
elif '\\cite{' in tex:
    cite_pattern = r'\\cite[tp]?\s*\{([^}]+)\}'
else:
    cite_pattern = r'\\cite[tp]?\s*\{([^}]+)\}'  # 默认

# 提取cite键 — 逐行过滤，跳过LaTeX注释行（%开头）
# ⚠️ 全局re.finditer会匹配注释中的\cite{}，导致D10a虚高（Trap #39）
tex_cites = set()
for line in tex.split('\n'):
    stripped = line.strip()
    if stripped.startswith('%'):
        continue  # 跳过LaTeX注释行
    for m in re.finditer(cite_pattern, line):
        for k in m.group(1).split(','):
            k = k.strip()
            if k and k not in ('<label>', 'lamport94'):
                tex_cites.add(k)

# 检测引用模式并提取bib键
if '\\begin{thebibliography}' in tex:
    # thebibliography 模式 — 从 tex 提取 bibitem 键
    bib_keys = set(re.findall(r'\\bibitem\{([^}]+)\}', tex))
    bib_source = 'thebibliography (inline)'
elif os.path.exists('references.bib'):
    with open('references.bib') as f: bib = f.read()
    bib_keys = set(re.findall(r'@\w+\{[^,]+,', bib))
    bib_source = 'references.bib'
else:
    bib_keys = set()
    bib_source = 'MISSING'

# 计算
orphan = tex_cites - bib_keys   # tex有但bib无 → 零容忍
zombie = bib_keys - tex_cites   # bib有但tex无 → 需清理
matched = tex_cites & bib_keys
d10a = len(matched) / max(len(bib_keys), 1) * 100
print(f"模式: {bib_source}")
print(f"正被引用: {len(matched)}")
print(f"孤儿: {len(orphan)} — 必须修复")
print(f"僵尸: {len(zombie)} — 建议删除")
print(f"D10a: {d10a:.1f}%")
```

**阈值**：
| 指标 | 阈值 | 行动 |
|:-----|:----:|:-----|
| 孤儿引用 | 0 | 零容忍 — 必须从正文删除或从bib补充 |
| 僵尸引用 | 0 | 清理后继续；≤3可接受（临时储备引用） |
| nocite | 禁用 | `\\nocite{*}` → 必须拆解为手动\\cite后删除 |

**实战案例**（pima-crispdm 2026-05-31）：
| 指标 | 清理前 | 清理后 |
|:-----|:------:|:------:|
| Bib条目 | 49 | 41 |
| 僵尸 | 8（Amri2025等） | 0 |
| D10a | 41/49=84% | 41/41=100% |
| D8 | 49（虚高） | 41（真实） |

清理后D8从49降至41，但D10a从84%升至100%。

**⚠️ 多版本Tex的引用比较（2026-06-18新增）**:
论文目录中可能包含多个修订版本（如 revision20241118v1.tex 至 v4.tex）。**版本号高不等于引用覆盖好**。必须对每个 .tex 文件运行 D10a 比较，选择引用最多的版本作为最终版本。

```python
import re, os

# 对每个 .tex 文件
for tf in os.listdir(paper_dir):
    if not tf.endswith('.tex'): continue
    with open(f'01-manuscript/{tf}') as f:
        tex = f.read()
    cites = re.findall(r'\\\\cite[tp]?\{([^}]+)\}', tex)
    keys = set()
    for c in cites:
        for k in c.split(','):
            k = k.strip()
            if k and k not in ('<label>', 'lamport94', 'citep', 'cite'):
                keys.add(k)
    orphan = keys - bib_keys
    zombie = bib_keys - keys
    # 记录: tf, cite_count, orphan_count, zombie_count, d10a
```

**实战案例**（3D Eyeball 2026-06-18）：
| 版本 | 引用键数 | 孤儿 | 僵尸 | D10a |
|:-----|:---------|:-----|:-----|:-----|
| v3 | 49 | 0 | 6 | 89.1% |
| v4 | 28 | 2 | 27 | 50.9% |

v4 比 v3 丢失22个引用（`bowyer2008image`, `lee2008fake`, `nguyen2017long`, `proencca2005/2009` 等）。必须选择 v3。

### 步骤2: 编译前置检查

标准化前检查编译可行性：

```bash
# 1. 检查 bib → tex 路径
grep 'bibliography{' paper.tex
# 如果结果是 \\bibliography{references}，需要 references.bib 在同目录或TEXINPUTS中

# 2. 检查图片路径
grep 'includegraphics' paper.tex

# 3. 标准化后建立符号链接（如 tex 在 01-manuscript/ 而 bib 在根目录）
cd 01-manuscript/
ln -sf ../references.bib .
ln -sf ../fig_architecture.pdf .
```

### 步骤3: PDF命名标准化

PDF文件名必须与bibkey大小写一致：

```bash
# 读取bibkeys
bibkeys=$(grep -oP '@\w+\{\K[^,]+' references.bib)

# 对每个PDF，找case-insensitive匹配的bibkey
for f in pdfs/*.pdf; do
    base=$(basename "$f" .pdf)
    match=$(grep -i "@\w+{"$base"," references.bib 2>/dev/null)
    if [ -n "$match" ] && [ "$(basename $f .pdf)" != "$match" ]; then
        mv "$f" "pdfs/${match}.pdf"
    fi
done

# 清理无匹配的PDF
for f in pdfs/*.pdf; do
    key=$(basename $f .pdf)
    if ! grep -q "@\w+{"$key"," references.bib; then
        echo "ORPHAN: $f → 删除"
        rm "$f"
    fi
done
```

**常见命名不一致**：
| 原始名 | 正确bibkey | 处理 |
|:-------|:-----------|:-----|
| `ayon2019.pdf` | `Ayon2019` | 大小写对齐 |
| `Collins2015TRIPOD.pdf` | `Collins2015` | 去后缀匹配 |
| `breiman2001.pdf` | `Breiman2001` | 大小写对齐 |

### 步骤4: PDF真实性校验

D9计数前，用文件头校验：

```python
import os
real, fake = 0, 0
for f in os.listdir('06-references/pdfs/'):
    if not f.endswith('.pdf'): continue
    with open(f'06-references/pdfs/{f}', 'rb') as fh:
        if fh.read(5) == b'%PDF-': real += 1
        else: fake += 1; print(f"FAKE: {f}")
print(f"D9: {real}/{total} = {real/total*100:.0f}%")
```

---

## 批量双质检工作流（v3.10新增）

> 当需要对多篇论文（10+）批量重新跑双质量检查时，不要逐篇手动操作。用两阶段批处理脚本自动执行。

### Phase 1: 批量编译 + 上传到 NotebookLM

```python
# batch_qc_phase1.py — 预放在 outputs/papers/ 目录
# 对每篇论文：
#   1. 找到主 .tex 文件（偏好 article.tex > paper.tex > 其他）
#   2. pdflatex 编译（含 thebibliography/bibtex 检测）
#   3. 上传到对应的 NotebookLM 项目，使用 {论文目录名}-v1.pdf 唯一命名
#   4. 记录成功/失败到 batch-qc-log.md
```

**论文 → NotebookLM 项目映射表**（存放于 `references/paper-nb-mapping.md`）：

| 论文方向 | NotebookLM 项目 | 项目ID |
|:---------|:----------------|:-------|
| Synthos 系统 / AI综述 | Synthos主知识库 | b54348f4 |
| Kappa系列 | 基于iTrace的人群kappa角 | 571024b4 |
| VOR系列 | 知识引导VOR数字孪生 | c0bba510 |
| BPPV系列 | BPPV三维仿真研究 | 95509a49 |
| PD眼动 | Ocular Biomarkers PD | 4a0f1345 |
| Trustworthy AI | Gated Triage乳腺癌 | 949a6014 |
| 虹膜/3D眼球 | 3D眼球模型扭转追踪 | b6698e12 |

### Phase 2: 批量 Layer B Gemini 评审

```python
# batch_qc_phase2.py
# 对 Phase 1 已上传的每篇论文：
#   1. notebooklm use <project_id>
#   2. notebooklm ask "7维SCI评审" prompt（300s超时）
#   3. 解析 D1-D7 评分
#   4. 写入 quality-report.md
#   5. 每篇间隔 10s 避免限流
#   6. 状态保存到 batch-qc-phase2-state.json（崩溃可续跑）
```

### 参考PDF批量管理（v3.11新增）

> **关键发现（2026-05-27）：参考PDF的内容可能完全与文件名不符。** 本轮42篇论文扫描发现多篇PDF的文件名暗示某论文，实际内容却完全不相关——如 `chaudhary2019opensource.pdf` 在iris-3d-anatomical-opt目录下，实际内容却是Dedekind半环域代数论文。

### 流程：扫描 → 验证 → 标准化 → 上传

```mermaid
flowchart LR
    A[扫描所有论文目录] --> B[寻找references.bib + pdfs/]
    B --> C[提取PDF真实内容<br/>pdftotext + arXiv ID]
    C --> D{bibkey vs 内容匹配?}
    D -->|匹配| E[cp到refs-md/{bibkey}.pdf]
    D -->|不匹配| F[标记为MISNAMED<br/>→ 从bib找正确DOI/arXiv]
    F --> G[下载正确PDF<br/>→ 重命名为{bibkey}.pdf]
    G --> H[上传到NotebookLM]
    E --> H
    H --> I[更新notebooklm-sources.json]
```

### Step 1: 全库扫描

```bash
PAPERS=/media/yakeworld/sda2/Synthos/outputs/papers

# 创建 refs-md/ 结构（每篇论文一个，集中存放规范命名的参考PDF）
for d in "$PAPERS"/*/; do
    [ -d "$d/refs-md" ] || mkdir "$d/refs-md"
done

# 复制已有参考PDF到refs-md/
find "$PAPERS" -path "*/pdfs/*.pdf" ! -name "paper.pdf" ! -path "*/_invalid/*" \
  -exec sh -c 'cp "$1" "$(dirname "$(dirname "$1")")/refs-md/$(basename "$1")"' _ {} \;

# 统计
find "$PAPERS" -path "*/refs-md/*.pdf" | wc -l
```

### Step 2: 内容验证（核心——防命名错乱）

```bash
# 对每个参考PDF，提取前200字确认真实内容
for pdf in "$PAPERS"/*/refs-md/*.pdf; do
    echo "=== $(basename $pdf) ==="
    pdftotext "$pdf" - 2>/dev/null | head -5 | tr '\n' ' ' | head -200
    echo ""
done
```

**2026-05-27 实战发现的系统性命名错误**：

| 文件名 | 所在论文 | 实际内容 |
|:-------|:---------|:---------|
| `chaudhary2019opensource.pdf` | iris-3d-anatomical-opt | Dedekind半环域代数（arXiv:1907.07162 math.RA） |
| `perry2020keypoints.pdf` | iris-3d-anatomical-opt | 流行病建模与控制（arXiv:2010.15438 math.OC） |
| `chaudhary2019.pdf` | iris-yolo | 图论Erdos-Posa性质（arXiv:1910.00642 math.CO） |
| `chen2023.pdf` | iris-yolo | 表情估计（arXiv:2106.08596 cs.CV） |
| `sapkota2026.pdf` | iris-yolo | 编码理论（arXiv:2601.00250 math.CO） |
| `sulake2026.pdf` | iris-yolo | 语音表征学习 |
| `tian2025.pdf` | iris-yolo | Dirac方程解（arXiv:2502.00303 math.CA） |
| `bischl2025.pdf` | hcs3wt-breast-cancer | JSS统计软件mlr包（非乳腺癌） |

**根因**：LLM下载参考PDF时，arXiv ID或DOI被写错，PDF下载了另一篇论文但保留了正确文件名。`bibkey` 是正确引用意愿，但PDF内容并未验证。

### Step 3: 创建标准化清单（notebooklm-sources.json）

```python
import os, json
PAPERS = "..."  # 论文库路径
for d in os.listdir(PAPERS):
    dp = f"{PAPERS}/{d}"
    if not os.path.isdir(dp): continue

    manifest = {
        'paper': d,
        'bib_entry_count': 0,  # 从references.bib读取
        'refs': []
    }

    refdir = f"{dp}/refs-md"
    if os.path.isdir(refdir):
        for f in os.listdir(refdir):
            if f.endswith('.pdf'):
                fp = os.path.join(refdir, f)
                manifest['refs'].append({
                    'bibkey': f.replace('.pdf', ''),
                    'size_kb': round(os.path.getsize(fp)/1024, 1),
                    'status': 'ready' if os.path.getsize(fp) > 10000 else 'empty'
                })

    with open(f"{dp}/notebooklm-sources.json", 'w') as f:
        json.dump(manifest, f, indent=2)
```

### Step 4: 命名规范化 + 上传NotebookLM

**命名规则**：`{姓氏}{年份}.pdf`（如 `Daugman1993.pdf`, `kothari2021ellseg.pdf`）

上传命令：
```bash
notebooklm use <notebook_id>
for pdf in paper-dir/refs-md/*.pdf; do
    bibkey=$(basename "$pdf" .pdf)
    notebooklm source add "$pdf" --title "$bibkey"
done
```

**注意**：NotebookLM的 `source add` 在后台shell环境中可能因 `bash: 无法设定终端进程组` 报错。正确做法是在交互式终端直接运行，或用 `python3` 脚本调用CLI（见 `scripts/` 目录）。

### 📁 论文草稿来源管理

除 `outputs/papers/` 下的已编排论文外，用户还有两处草稿来源：

1. **`~/桌面/article_todo/`** — 8篇待写论文（6眼动+2前庭），详见 `references/article-todo-inventory.md`
2. **`~/桌面/synthos_paper.tex`** — Synthos系统论文早期草稿（repo版更成熟：`outputs/papers/synthos-system-paper/synthos-paper.tex`）

**启动一篇todo论文前**：先查阅 `article-todo-inventory.md` 了解结构和成熟度，再决定是全文重写还是直接编译已有LaTeX。对于已有初稿的论文优化，使用 `todo-paper-optimization-workflow.md` 三步法。

## 支持脚本

- `scripts/promote-track-a.py` — 自动晋升 _knowledge_only/ 中有 paper.tex 的候选项至 Track A
- `scripts/paper-maturity-scan.py` — 扫描论文库成熟度，按评分排序（引用数、D10a、PDF、质控、图表等维度）
- `scripts/d10a-batch-scan.py` — 批量 D10a 扫描所有 thebibliography 论文，按 zombie 数量排序输出（v3.18.5新增）
- `scripts/batch-3d-logspiral-fit.py` — 3D对数螺旋拟合批量处理
- `scripts/batch_logspiral_fit.py` — 3D对数螺旋拟合
- `scripts/fit_logspiral_3d.py` — 3D对数螺旋拟合核心算法


17. **🔴 定量实验中的 benchmark 降级（Quantitative Eval without Benchmark Datasets）**：当基准数据集（BSDS500、KITTI等）因安全扫描器阻断/付费墙/网络不可达而无法下载时，使用 `skimage.data` 内置标准测试图像做原理验证性定量实验。详见 `references/quantitative-evaluation-with-builtin-data.md`。

18. **🟡 natbib conflicts with thebibliography (2026-06-12 Paper 187)**: When using `\\begin{thebibliography}` (plain BibTeX in-text entries), do NOT load `\\usepackage{natbib}`. It causes "Bibliography not compatible with author-year citations" error at compile. Fix: remove natbib, use plain `\\cite{key}`. When using BibTeX mode (`.bib` file + `\\bibliography{}`), use natbib for `\\citep{}`, `\\citet{}` author-year format. **Decision tree**: thebibliography in tex → no natbib; separate .bib file → natbib ok.

19. **🔴 论文管线质量门禁从未执行（2026-06-18 发现）**：66篇有paper.tex的论文中，0篇有status.json——整个论文管线从未正确执行过G1-G7质量门禁。所有论文都处于"未完成"状态。

**根因**：论文管线只管"产出.tex"，不管"写入status.json"。cron的paper-repair和paper-quality-review都运行正常，但没有产出任何实际改进。

**修复协议**：
```
发现论文有.tex但无status.json
  ↓
Step 1: 生成基础status.json（stage=pre-gate, status=pending_review, quality=0.0）
Step 2: 执行G1-G7门禁检查
Step 3: 更新status.json为完整状态
Step 4: 如有论文通过G7，标记为ready_for_submission
```

**防止措施**：论文管线P4阶段必须同时写入status.json，不再允许"只写.tex不写status"的模式。

20. **🟡 dual-ellipse-fitting命名冲突（2026-05-28发现）**：dual-ellipse-fitting和dual-ellipse-pupil-localization两个目录都包含论文内容。命名冲突可能引起混淆。

21. **🔴 研究队列 stagnant entries（2026-06-18 发现）**：research-queue.json 中 7/7 候选人全部已晋升 Track A（有 paper.tex），但队列从未清理。队列声称 33 pending，实际有效候选人为 0。

**根因**：候选人晋升 Track A 后，research-queue 无自动清理机制。每轮 cron 的 literature_scan 只处理 next_candidate，不扫描其余条目。

**修复**：v3.16 新增 research-queue 自愈协议 — 每次 cron 运行前，检测并清理已晋升/幽灵/重复/空壳条目。

22. **🔴 ABSOLUTE WHITE 声明未经验证（2026-06-18 发现）**：113-scleral-remodeling-ODE 的 gap_analysis.md 声称 7 个 PubMed 查询全部为 0（ABSOLUTE WHITE），但 literature_scan 独立验证发现 Rozema 2025（myopia ODE 模型，相邻竞争者）。

**根因**：gap_analysis.md 由早期 LLM 运行生成，其 ABSOLUTE WHITE 声明可能过期（新论文发表）或不准确（查询覆盖不全）。literature_scan 不应信任 gap_analysis.md 的声明。

**修复**：v3.16 新增 literature_scan 协议 — 独立运行 ≥7 个 PubMed 查询，区分直接竞争者 vs 相邻竞争者，输出 refined_white_space + 竞争者边界地图。

23. **🟡 Track B 候选人与 Track A 论文碰撞（2026-06-18 发现）**：113-scleral-remodeling-ODE 初始化时，Track A 已有 187-scleral、150-scleral、corneoscleral-shell 三篇 scleral 论文。

**修复**：v3.16 新增 Track A 碰撞检测 — literature_scan 时 grep paper-queue 查找关键词，读取现有论文标题，明确记录方法/疾病/模型三层差异化。无法差异化则标记 duplicate 不入队。

24. **🔴 论文散落在桌面而非管线目录（2026-06-18 发现）**：3D Eyeball论文在 `~/桌面/article_todo/` 下，不在 `outputs/papers/` 标准目录中。

**修复协议**：
```
发现论文在桌面
  ↓
Step 1: 创建标准管线目录 outputs/papers/<paper-name>/
Step 2: 按7子目录结构拷贝文件
  ├── 01-manuscript/ → .tex, .pdf, .docx, .md
  ├── 02-data/ → 数据集
  ├── 03-code/ → .py, .sh
  ├── 04-results/ → 结果文件
  ├── 05-figures/ → 图片文件
  ├── 06-references/ → references.bib + PDFs
  ├── 07-quality/ → quality_check.md
└── index.md → 元数据文件
Step 3: 更新 paper-queue.json 和 research-queue.json
Step 4: 执行P0预检（D10a僵尸/孤儿检测）
Step 5: 执行P4双质检
```

**标准目录结构检查清单**：
```bash
# 验证标准结构
paper_dir="/media/yakeworld/sda2/Synthos/outputs/papers/<paper-name>"
for dir in 01-manuscript 02-data 03-code 04-results 05-figures 06-references 07-quality; do
    [ -d "$paper_dir/$dir" ] && echo "✅ $dir" || echo "❌ $dir"
done
[ -f "$paper_dir/index.md" ] && echo "✅ index.md" || echo "❌ index.md"
[ -f "$paper_dir/01-manuscript/paper.tex" ] && echo "✅ paper.tex" || echo "❌ paper.tex"
[ -f "$paper_dir/06-references/references.bib" ] && echo "✅ references.bib" || echo "❌ references.bib"
```

**桌面论文目录常见结构**：
- 通常包含 `.tex`, `.pdf`, `.docx`, `.bib`, `code.py`, `figures/`, `bibtex_pdfs/` 等
- 可能有多次修订版本（revision20241118v1.tex, revision20241118v2.tex等）
- bibtex_pdfs/ 目录包含参考文献PDF（可能命名不规范，也可能有子目录如 pdfs/）
- latexnew/ 目录包含编译产物
- 除 .bib 外还可能有 .txt（如 reference4.txt）

**迁移注意事项**：
1. 桌面源文件保留，不删除
2. **⚠️ 版本号陷阱**: 高版本号.tex ≠ 高质量版本。revision20241118v4.tex 比 v3.tex 丢失22个引用，D10a从89.1%暴跌至50.9%。必须逐篇比较各版本引用覆盖率（cite计数/孤儿/僵尸），选择**引用最多**的版本，而非版本号最高的。
3. 参考文献PDF按bibkey重命名后放入06-references/
   - **注意**: bibtex_pdfs/ 下可能有子目录结构（如 bibtex_pdfs/pdfs/*.pdf），需递归查找
   - 拷贝前检查: `find bibtex_pdfs/ -name "*.pdf"` 获取所有PDF路径
4. .bib 和 .txt 参考文件都需拷贝（如 reference4.bib + reference4.txt）
5. 图片文件放入05-figures/
6. 代码文件放入03-code/
7. 创建index.md记录论文元数据
8. **bibtex_pdfs/ 结构差异**: 有些论文直接 `bibtex_pdfs/*.pdf`，有些是 `bibtex_pdfs/pdfs/*.pdf`，需动态探测

25. **🟡 版本回退导致引用丢失（2026-06-18 发现）**: v4.tex 比 v3.tex 丢失22个引用。高版本号.tex ≠ 高质量版本。

**检测**: 必须对所有 .tex 文件运行 D10a 比较，选择引用最多的版本，而非版本号最高的。见上方多版本Tex比较协议。

26. **🟡 同一bibkey重复引用（2026-06-18 发现）**: 将 `matsumoto2000algorithm` 替换为 `newman2000real` 后，`newman2000real` 已存在，导致 `newman2000real, newman2000real` 重复引用。

**修复**: 替换前检查bibkey是否已存在于该行，避免重复。或使用 `sort -u` 对引用键去重。

27. **🟡 _knowledge_only 候选人有 paper.tex 但不在 paper-queue.json 中（2026-06-18 发现）**: 4个候选人（124-vitreous-humor-ODE, BPPV-canalith-ODE, paper-95-nystagmus-PINN, vestibular-adaptation-PINN）有 paper.tex 但未加入 Track A。自愈协议只"跳过"它们，不会主动晋升。

**根因**: Step 0 的规则 "有 paper.tex？ → 跳过（应走 Track A）" 只做了跳过，没有晋升机制。这些论文卡在 _knowledge_only/ 中无人处理。

**修复协议（Track A 晋升协议——轻量版，区别于桌面论文迁移）**:
> **自动化脚本可用**: 运行 `python3 scripts/promote-track-a.py`（从 `outputs/papers/` 目录）自动扫描并晋升所有符合条件的候选项。

```
自愈协议 Step 0 中发现 candidate 有 paper.tex 但不在 paper-queue.json 中
  ↓
Step A1: 检查 paper-queue.json 是否已有同名或相似 paper_id
Step A2: 若无冲突，执行轻量晋升：
  ├── mv _knowledge_only/<candidate> ../<candidate>  （移到 papers/ 根目录）
  ├── 检查目录结构是否完整（01-manuscript/ 等）
  ├── **读取 state.json**，honour现有 quality_score/gate_status/stage——勿覆盖为 qs=60
  ├── 创建基础 index.md（元数据 + 来源标记: promoted_from_track_b）
  ├── 添加条目到 paper-queue.json（保持 state.json 的现有质量分数值）
  └── 记录晋升日志到 research-queue.json 的 notes
Step A3: 若有命名冲突（如 113-scleral-remodeling-ODE 与 187-scleral-remodeling-ODE）：
  ├── 保留现状（不移动）
  └── 在 research-queue.json 中记录冲突 + 建议手动处理
  ↓
晋升完成后，candidate 从 Track B 队列移除
```

**vs 桌面论文迁移（Trap 24）的区别**:
| 维度 | 桌面论文迁移（Trap 24） | _knowledge_only 晋升（Trap 27） |
|:-----|:-----------------------|:-------------------------------|
| 源目录 | `~/桌面/article_todo/` | `outputs/papers/_knowledge_only/` |
| 结构 | 无标准结构，需手动建7子目录 | 已有部分目录结构 |
| 复杂度 | 高（需重建目录、检查版本号、重命名PDF等） | 低（目录已基本就绪） |
| 必须步骤 | P0预检 + P4双质检 | 基础 gate check + 入 paper-queue |

**注意**: 晋升到 Track A 后，论文仍需走 G1-G7 质量门禁。晋升只是"入队"，不是"完成"。

28. **🟡 未注册孤儿——论文在 papers/ 根目录有 paper.tex + state.json 但不在 paper-queue.json（2026-06-18 发现）**: 9 篇论文存在于 papers/ 根目录，有完整 paper.tex 和 state.json，但从未加入 paper-queue.json。这些是"已存在的 Track A 论文"但因为各种原因（cron 中断、手动创建、_knowledge_only 晋升后队列未同步等）遗漏在队列外。

**检测**: 每次 Paper Repair Agent 运行时，先执行 orphan 检测（见 `references/orphan-detection-onboarding.md`）。

**入职协议**:\n```\nStep 1: 检测 papers/ 下有 paper.tex 但不在 paper-queue.json 的目录\nStep 2: 读取 state.json，确认 gate_status 和 quality_score\nStep 3: 按标准格式添加到 paper-queue.json（status=completed, reason=orphan_onboarded）\nStep 4: 每轮最多入职 5 篇（cron 上限）\n```\n\n**常见入职论文特征**: qs 65-70, D10a=100%, G1-G7 PASS, stage=publication_complete，只是队列遗漏。\n\n**幽灵条目（逆问题）**: 60 篇在 paper-queue.json 中但目录不在 papers/ 根目录——它们的研究目录残留在 _knowledge_only/ 中未移动。需要批量 `mv _knowledge_only/<dir> ../<dir>`，但大规模执行需谨慎（检查同名冲突）。

**🟡 发散副本（Divergent Copy）——同目录出现在 _knowledge_only/ 和 papers/ 两个位置且内容不同（2026-06-18 发现）**:
   - 3d-eyeball-iris-segmentation 在 _knowledge_only/ 和 papers/ 中都有目录但内容不同
   - _knowledge_only/ 版本有 02-submission/ 和独立 paper.tex；papers/ 版本有 01-manuscript/ 和 article.tex
   - **处理策略**：保留两份，不做自动删除或覆盖。自愈协议只从 research-queue.json 移除队列引用，不物理删除任一副本。
   - **根因**：papers/ 版本来自正常的论文管线流程；_knowledge_only/ 版本可能是从桌面迁移或手动创建的独立工作副本。
   - **修复**: self-healing Phase 1 中增加 divergent copy 检测——当两个位置的目录都非空且内容不同时，标记为 divergent，不搬迁不删除。

29. **🔴 作者顺序修改后的编译+同步流程（2026-06-18 实战）**: 修改 `.tex` 作者顺序后，必须完成以下闭环：

```
Step 1: patch .tex 文件（本机）修改 author 顺序
Step 2: 重新创建符号链接（reference4.bib, Figure_*.jpg, graphical_abstract.pdf）
       cd 01-manuscript/ && ln -sf ../06-references/references.bib reference4.bib
       ln -sf ../05-figures/Figure_*.jpg . && ln -sf ../05-figures/graphical_abstract.pdf .
       ⚠️ 路径始终为 ../05-figures/（非 ../../05-figures/）
Step 3: 重新编译 — pdflatex → bibtex → pdflatex × 2 → pdflatex × 1
Step 4: 验证编译结果 — 0 errors, 0 undefined warnings
Step 5: SCP 新 PDF 到 work1 — scp <pdf> work1:/mnt/nfs/article/<paper>/01-manuscript/
Step 6: 报告用户 — 确认修改完成，提供最终 PDF 路径
```

**⚠️ 陷阱**：修改 `.tex` 后不重编+不同步，用户看到的 PDF 与 `.tex` 不一致，造成混乱。必须闭环执行，不得中断。

30. **🟡 IEEE/SPIE 付费墙模式 — PDF 无法自动下载（2026-06-18 实战）**: 4 篇 IEEE/SPIE 论文因付费墙无法通过 Sci-Hub、Semantic Scholar、OpenAlex 自动下载 PDF，但 DOI 已验证有效：

| BibKey | 来源 | DOI | 状态 |
|--------|------|-----|------|
| he2024enhancedeepiris | IEEE Access | 10.1109/ACCESS.2024.3388169 | ❌ 418 反爬 |
| huo2021heterogeneous | SPIE JEI | 10.1117/1.JEI.30.6.063015 | ❌ 付费墙 |
| Sarker2021 | IEEE 会议 | 10.1109/icece64886.2024.11024855 | ❌ 付费墙 |
| li2019efficient | IEEE ISMAR | 10.1109/ISMAR55827.2022.00053 | ❌ 付费墙 |

**处理策略**：DOI 验证通过后，PDF 缺失不计入质量扣分。需在质量报告中注明"4 篇因付费墙 PDF 缺失"。用户需手动通过机构访问或图书馆获取。

31. **🟡 论文管线文件共享流程（work1 NFS 共享）（2026-06-18 实战）**: 用户通过 work1 的 `/mnt/nfs/article/` 共享目录查看论文文件：

32. **🔴 D10a 队列/state.json 声明不可信 — 必须独立验证（2026-06-18 实战）**: 3d-pupil-localization 的 queue 和 state.json 均声称 D10a=100%，但独立扫描发现 3 个 zombie 条目（Atchison2005, Daugman2009, Fitzgibbon2001），实际 D10a=88.9%。

**根因**：D10a 值可能来自早期运行或模板生成时写入，后续 bib 增删使声明过期。queue 同步不保证 D10a 字段与 bib 实际状态一致。

**检测协议**（每次 Paper Repair Agent 运行时执行）：
```
对每篇待修复论文，在信任 state.json 的 D10a 值之前：
  ↓
Step 1: 独立运行 P0 预检脚本（步骤1的 Python 代码）
Step 2: 比较独立扫描结果 vs state.json/reference_health/D10a
Step 3: 若不一致 → 修复 bib（去僵尸/补孤儿），重编译，更新 state.json
Step 4: 将修正后的 D10a 写入 queue notes
```

**实战数据**：本次运行发现 1 篇 D10a 声明不实（100%→88.9%）+ 2 篇 thebibliography 论文的 state.json D10a=0.0（实际 100%）。3/5 处理论文有 D10a 不一致。

33. **🟡 thebibliography 论文的 D10a 盲区（2026-06-18 实战）**: optic-nerve-head-deformation-ODE 和 vestibular-adaptation-ODE 均使用 `\\begin{thebibliography}` + `\\bibitem{key}` 格式（无独立 .bib 文件）。它们的 state.json 中 D10a=0.0，因为 D10a 扫描脚本只检查 `references.bib` 文件，对 thebibliography 论文返回了 0。

**正确的 thebibliography D10a 计算**：从 tex 文件直接提取 `\\bibitem{key}` 和 `\\cite{key}` 并比较：
```python
# thebibliography mode — extract bibitem keys from tex
bibitem_keys = set(re.findall(r'\\\\\\\\bibitem\\{([^}]+)\\}', tex))
# 然后用 tex_cites vs bibitem_keys 计算 D10a
matched = tex_cites & bibitem_keys
d10a = len(matched) / max(len(bibitem_keys), 1) * 100
```

**检测**：若 `references.bib` 不存在或为空，且 tex 包含 `\\begin{thebibliography}`，则切换为 thebibliography 模式计算 D10a。修复后在 state.json 的 `reference_health` 中正确写入 D10a 值。

```bash
# 拷贝论文管线到共享目录
scp -r /media/yakeworld/sda2/Synthos/outputs/papers/<paper>/ work1:/mnt/nfs/article/<paper>/

# 验证
ssh work1 "find /mnt/nfs/article/<paper> -name '*.tex' -o name '*.pdf' | head -20"
```

**约定**：修改论文后必须重新编译+拷贝，确保用户通过共享看到的是最新版本。

35. **🔴 旧管线PDF残留导致目录结构错乱（2026-06-18 实战）**: pima-crispdm管线中`06-references/`根目录包含7个旧管线遗留PDF（不属于当前Bib），pdfs子目录有44个PDF，pdfs_md子目录有40个MD文件——这些是旧管线（NotebookLM导入、历史引用）残留，与当前Bib完全不匹配。根目录本应保持扁平（PDF文件+references.bib），不应有子目录。

36. **🟡 参考文献目录标准化模式 — 参照3d-eyeball-iris-segmentation（2026-06-18 实战）**:

**标准结构**（根目录保持扁平）：
```
06-references/
├── references.bib          # Bib文件
├── author2023title.pdf     # 每个Bib key对应一个PDF（PDF名 = Bib key）
├── Collins2015TRIPOD.pdf   # 符号链接：→ Collins2015.pdf
└── Lundberg2017SHAP.pdf    # 符号链接：→ Lundberg2017.pdf
```

**关键规则**：
- PDF文件名应与Bib key大小写一致（如 `Chawla2002.pdf`）
- Bib key含多部分时（如 `Collins2015TRIPOD`），PDF可简化为 `Collins2015.pdf`，通过符号链接映射
- 符号链接：`ln -sf Collins2015.pdf Collins2015TRIPOD.pdf`
- **不需要** `pdfs/` 子目录（空子目录可选保留但不应有文件）
- **不需要** `pdfs_md/` 子目录（旧管线遗留，应删除）
- **不需要** `bibkey-map.json`、`notebooklm-sources.json`、`REFERENCE_MANIFEST.md` 等元数据文件
- **不需要** `references.bib.bak` 等备份文件

**清理流程**：
```bash
Step 1: 删除根目录所有不属于当前Bib的文件（grep Bib key匹配）
Step 2: 从pdfs子目录提取与当前Bib匹配的PDF到根目录
Step 3: 对名称不匹配的Bib key创建符号链接
Step 4: 删除pdfs/（不再使用）和pdfs_md/子目录
Step 5: 删除bak文件（references.bib.bak*）
Step 6: 删除元数据文件（bibkey-map.json等）
```

**注意事项**：
- 不要假设pdfs子目录中的PDF都与当前Bib对应——旧管线PDF可能完全不相关
- 名称不匹配（如 `Shams2025.pdf` vs `Shams2023BRFSS` Bib key）需要检查内容而非仅看文件名
- 3d-eyeball标准: 45个PDF在根目录 + references.bib + 空pdfs/子目录
- 缺失PDF的Bib key标记为需下载，不计入D10a计算（D10a基于已匹配的unique cite keys ∩ bib_keys）

36. **🔴 natbib 论文的 D10a 盲区 — 标准 `\cite` 正则返回 0 匹配（2026-06-18 实战）**: `3d-eyeball-iris-segmentation` 使用 natbib + elsarticle-num 格式，所有引用命令为 `\citep{key}` 而非 `\cite{key}`。标准正则 `r'\\cite[tp]?\s*\{([^}]+)\}'` 返回 0 匹配，导致 D10a 扫描完全失效。

**根因**：P0 预检脚本假设所有论文使用 `\cite` 或 `\citep`/`\citet`，但正则只用 `\cite[tp]?` 前缀。natbib 的 `\citep`、`\citet`、`\citenp`、`\citealp`、`\citealt` 等变体需要不同的正则。

**检测**：扫描前先 grep 确认引用风格：
```bash
grep -c '\\citep{' paper.tex  # natbib
grep -c '\\citet{' paper.tex  # natbib
grep -c '\\cite{' paper.tex   # 标准
```
若 natbib 变体 > 0，则切换为 natbib 正则：`r'\\(?:cite|citep|citet|citenp|citealp|citealt)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}'`

**⚠️ 注释中 thebibliography 检测陷阱（2026-06-19 实战）**：elsarticle 模板在 `%%` 注释中包含 `\begin{thebibliography}` 占位符（如 `%% \begin{thebibliography}`），但实际使用 `\bibliography{references}` 外部 .bib。简单的 `in tex` 检测会误判为 thebibliography 模式。**必须逐行检查，跳过以 `%` 开头的注释行**：
```python
has_real_thebib = False
for line in tex.split('\n'):
    stripped = line.strip()
    if stripped.startswith('%%') or stripped.startswith('%'):
        continue
    if '\\begin{thebibliography}' in stripped:
        has_real_thebib = True
        break
```

**实战数据**：
| 论文 | 引用风格 | 标准正则匹配 | natbib正则匹配 | Bib条目 | 实际D10a |
|:-----|:---------|:------------|:--------------|:--------|:---------|
| 3d-eyeball-iris-segmentation | natbib (`\citep{}`) | 0 | 30 | 49 | 57.1% |
| pima-crispdm | natbib+plain | — | — | 33 | 100% |

**修复**：v3.18.4 更新 P0 预检脚本 — 引用风格检测 + natbib 正则回退。

37. **🟡 Paper Repair Agent "无可行修复" 的标准报告格式（2026-06-18 实战）**: cron 运行时可能发现队列中所有低分论文都有不可自动化修复的缺陷（Variant K 缺数据、HARD_FAIL 伪造结果、ghost 条目），输出 "0 papers repaired" 是正常且信息丰富的报告，不是失败。

38. **🔴 Zero-citation thebibliography 论文 — D10a 修复只加了 bibitem 未加 `\cite{}` 命令（2026-06-19 实战）**: 批量扫描发现 14/132 篇 thebibliography 论文存在 zombie bibitem（bibliography 中有条目但文本中从未使用 `\cite{}` 引用）。其中 3 篇为**完全零引用**（`pupillary-light-reflex-ODE`, `Paper_101_optokinetic-reflex-PINN`, `182-accommodation-ciliary-muscle-ODE`）——bibliography 被完整构造但从未通过任何 `\cite{}` 命令连接到正文。其它 11 篇有 2-14 个 zombie bibitems。

| 论文 | QS | Bib | Cites | Zombies | 严重程度 |
|:------|:---:|:---:|:-----:|:-------:|:---------|
| `pupillary-light-reflex-ODE` | 80 | 20 | **0** | 20 | 🔴 零引用 |
| `Paper_101_optokinetic-reflex-PINN` | 84 | 15 | **0** | 15 | 🔴 零引用 |
| `182-accommodation-ciliary-muscle-ODE` | 96 | 13 | **0** | 13 | 🔴 零引用 |
| `147-lens-capsule-biomechanics-ODE` | 96 | 20 | 6 | 14 | 🟡 70% zombie |
| `148-corneal-epithelial-wound-healing-ODE` | 78 | 18 | 6 | 12 | 🟡 |
| `151-ocular-torsion-dynamics-ODE` | 78 | 20 | 9 | 11 | 🟡 |
| `153-choroidal-blood-flow-ODE` | 78 | 20 | 10 | 10 | 🟡 |
| `152-intraocular-pressure-rhythm-ODE` | 96 | 20 | 11 | 9 | 🟡 |
| `086-endolymph-perilymph-coupling-ode` | 75 | 16 | 9 | 8+1 | 🟡 8 zombies + 1 orphan |

**根因**：2026-06-14/15 的多轮 "D10a fix" 运行**只添加了 bibitem 条目但从未在正文中插入 `\cite{}` 命令**。修复后的验证只检查了 "orphan 是否归零"（tex_cites 全部在 bib 中），但未检查 "zombie 是否归零"（bib 条目全部被引用）。这些论文经过编译后 `\cite{}` 缺失不会产生 LaTeX 错误——bibitem 只是静默地被忽略。

**检测协议**（Paper Repair Agent 每次运行时执行）：
```
对每篇 thebibliography 论文：
  ↓
Step 1: 独立运行 D10a 扫描（不信任 state.json 的 D10a 值）
Step 2: 计算 zombie_count = len(bib_keys) - len(tex_cites ∩ bib_keys)
Step 3: 若 zombie_count > 0 → 标记需要清理：
  ├── 若 cite_count = 0（零引用）→ HARD_FAIL: 论文无正式引用，需人工插入 \cite{}
  ├── 若 zombie_count ≤ 3 → 删除 zombie bibitems，重编译，更新 state.json
  └── 若 zombie_count > 3 → 逐个检查 zombie 是否在 prose 中被提及（如 "Lasker et al."）
       ├── prose 提及 → 转换为 \cite{key} 命令
       └── 无 prose 提及 → 删除 zombie bibitems
Step 4: 更新 state.json 的 reference_health 为实际值
```

**批量扫描脚本**：`scripts/d10a-batch-scan.py` — 扫描所有 thebibliography 论文并按 zombie 数量排序，输出 CSV 格式。用法：`python3 scripts/d10a-batch-scan.py` 或指定论文 `python3 scripts/d10a-batch-scan.py paper_1 paper_2`。

39. **🔴 注释中 \\cite{} 导致 D10a 虚高（2026-06-19 实战）**: `bppv-nystagmus-pinn` 的 paper.tex 第1行为 LaTeX 注释 `% BPPV \\cite{furman2019} Nystagmus PINN \\cite{raissi2019} — Auto-assembled from steps`。全局 `re.finditer(cite_pattern, tex)` 将注释中的 `\\cite{furman2019}` 和 `\\cite{raissi2019}` 计入 tex_cites，使 D10a 从真实的 60%（3/5）虚高至 100%（5/5）。

40. **🔴 d10a-batch-scan.py 模式路由假阳性（2026-06-19 实战）**: elsarticle 模板论文同时包含 `\begin{thebibliography}`（实际使用）和 `\bibliography{references}`（模板残留），旧逻辑 `not has_real_thebib or has_bibcmd` 将 thebibliography 论文误路由到 BibTeX 模式。BibTeX 模式从 `.bib` 文件提取键——若 `.bib` 键集不同于 thebibliography 键集，所有 bib 条目被误报为 zombie。实战：14 篇扫描中 10/14 为假阳性（tinnitus-pinn-ode, bppv-nystagmus-pinn 等实际 D10a=100%，被误标为 80%/0%）。

**根因**：`has_bibcmd = '\\bibliography{' in tex` 对注释中的 `\bibliography{}` 也返回 True（如 `%% \bibliography{references}`）。

**修复（v3.18.8）**：
```python
# 1. has_bibcmd 也做逐行注释过滤
has_bibcmd = False
for line in tex.split('\n'):
    if line.strip().startswith('%'): continue
    if '\\bibliography{' in line: has_bibcmd = True; break

# 2. 路由优先级：真实 thebibliography > BibTeX
if has_real_thebib:
    # thebibliography 优先——始终使用内联 bibitem 键
elif has_bibcmd:
    # 仅在无 thebibliography 时回退到 BibTeX
```

**根因**：P0 预检脚本的 cite 提取使用 `re.finditer(cite_pattern, tex)` 对全文做全局匹配，不区分注释行和正文行。之前 2026-06-15 的 "auto-gate fix" 因此错误地声称 D10a=100% 并写入 state.json。

**检测**：逐行读取 tex，跳过以 `%` 开头的行再提取 cite 键。见 P0 预检脚本（已更新为逐行过滤版）。

**实战数据**：
| 论文 | 注释中 cite | 实际 cite（非注释）| Bib | 声明 D10a | 实际 D10a |
|:-----|:-----------|:-------------------|:---|:---------|:--------|
| bppv-nystagmus-pinn | 2 (furman2019, raissi2019) | 3 (chen2018, lasker2025, chaturvedi2026) | 5 | 100% | 60% |

**修复**: 将注释中的 citation 提升到正文适当位置（如 abstract 中首次提及该概念处），删除注释中的 `\\cite{}`。

41. **🟡 paper-queue.json 幽灵条目逆方向 — 队列中有条目但目录已在 _archive/ 或 _drafts_archive/（2026-06-19 实战）**: Trap #28 覆盖了"纸在盘不在队"（disk→queue方向），但反向问题"队在盘不在"同样发生——论文目录被移入 `_archive/` 或 `_drafts_archive/` 后，paper-queue.json 条目未同步标记为 archived。

42. **🔴 跨项目参考文献污染检测 — Synthos Paper ID 后缀 + 占位符键名 + 空条目 + Prose提及无\cite（2026-06-20 实战）**: 早期 D10a 修复运行（2026-06-14/15）构造 bibitems 时误加入了其他 Synthos 论文的内部引用，产生了四类污染模式：

| 模式 | 示例 | 检测方法 |
|:-----|:-----|:---------|
| Synthos Paper ID 后缀 | `saccade-kinematic-76`, `endolymph-hydropressure-83` | `grep -E '[a-z]+-[0-9]{2}$'` |
| 占位符键名 | `computational-baseline` | 不匹配 AuthorYear 格式 |
| 空条目 | `@Article{nguyen2017long,` 无body | 无 author/title/year 字段 |
| Prose提及无\cite | `(Raissi et al., 2019)` 无 `\cite{}` | `grep '([A-Z][a-z]+ et al'` |

**实战（2026-06-20）**: 086-endolymph D10a=50%（声称100%），发现7个跨项目zombie（saccade-kinematic-76, endolymph-hydropressure-83, computational-baseline, parnes1999, cohen2021, chen2018, jagtap2022）+ 1个orphan typo（sculer1987→Schuknecht1987）+ 1个prose mention无cite（Raissi et al., 2019）。3d-eyeball发现2个空条目（nguyen2017long, nguyen2020constrained）。

**修复协议**：僵尸键匹配污染模式 → 直接删除（非真实引用）；空条目 → 删除；prose提及有匹配bibitem → 转换为 `\cite{}`。详见 `references/cross-project-contamination-patterns.md`。

**触发场景**：Paper Repair Agent 运行时发现队列中 qs<60 或 gate=FAIL 的条目，但对应目录不存在于 papers/ 根目录。

**幽灵来源**：
| 目录位置 | 含义 | 处理 |
|:---------|:-----|:-----|
| `_archive/<paper>/` | 论文已归档（成熟度不足/方向调整） | 标记 status=archived |
| `_drafts_archive/<paper>/` | 论文已归档为草稿 | 标记 status=archived |
| 完全不存在 | 目录已被删除 | 标记 status=archived, reason=missing |

**检测协议**（Paper Repair Agent 每次运行时执行）：
```
对每篇待修复论文：
  ↓
Step 1: 检查 papers/<paper_id>/ 目录是否存在
Step 2: 若不存在 → 搜索 _archive/ 和 _drafts_archive/
Step 3: 若在归档目录中找到 → 更新 queue 条目为 status=archived, reason=ghost_entry_cleanup
Step 4: 若完全不存在 → 标记 status=archived, reason=missing
Step 5: 记录清理日志到 queue notes（ghost_cleanup_YYYY-MM-DD）
```

**实战数据（2026-06-19）**：6 篇幽灵条目发现并清理：
| Paper ID | 目录位置 | 旧 qs/gate |
|:----------|:---------|:-----------|
| 3d-pupil-localization | _archive/ | qs=55, PASS |
| 3wd-framework-trustworthy-clinical-ai | _archive/ | qs=25, FAIL |
| intraocular-pressure-ODE | _archive/ | qs=75, HARD_FAIL |
| eye-tracking-4d | _drafts_archive/ | qs=68, CONDITIONAL |
| cuteye-model | _drafts_archive/ | qs=78, CONDITIONAL |
| automated-label-production-pipeline-for-eye-tracking | missing | qs=0, PASS |

**与 Trap #28 的区别**：
| 维度 | Trap #28（未注册孤儿） | Trap #41（幽灵条目） |
|:-----|:----------------------|:---------------------|
| 方向 | disk → queue（纸在盘不在队） | queue → disk（队在盘不在） |
| 磁盘位置 | papers/ 根目录下 | _archive/ 或 _drafts_archive/ |
| 目录状态 | 存在且有 paper.tex + state.json | 已归档或已删除 |
| 修复动作 | 添加到 paper-queue.json | 标记 queue 条目为 archived |

**规范化标准流程（参照3d-eyeball-iris-segmentation）**：
```
Step 1: 清理根目录——删除不属于当前Bib的所有文件
  - 删除旧PDF（grep bib key匹配，不在Bib中的直接删除）
  - 删除旧元数据（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md）
  - 删除bak备份文件
Step 2: 从pdfs子目录提取与当前Bib匹配的PDF到根目录
  - 对每个bib key，在pdfs/中查找case-insensitive匹配的PDF
  - 匹配的PDF复制到根目录
  - 名称不匹配的PDF创建符号链接（如Collins2015TRIPOD.pdf -> Collins2015.pdf）
Step 3: 删除不需要的子目录
  - 如果pdfs/不再被使用 → 删除
  - 如果pdfs_md/不再被使用 → 删除
  - 根目录应保持扁平：PDF + .bib + 空pdfs/子目录（可选）
Step 4: 处理名称不匹配
  - Bib key与PDF文件名不一致时，创建符号链接
  - 记录映射关系到pdfs目录（保留作为历史记录）
Step 5: 对缺失PDF的bib key——标记并尝试下载
  - 记录缺少的PDF列表
  - 尝试通过publisher开放获取URL下载
  - 付费墙/版权保护PDF标记为"需手动获取"
```

**命名规范**：
- PDF文件名应与Bib key大小写一致（如 `Chawla2002.pdf`）
- Bib key含多部分时（如 `Collins2015TRIPOD`），PDF可简化为 `Collins2015.pdf`，通过符号链接映射
- 符号链接：`ln -sf Collins2015.pdf Collins2015TRIPOD.pdf`

**常见陷阱**：
- 不要假设pdfs子目录中的PDF都与当前Bib对应——旧管线PDF可能完全不相关
- 名称不匹配（如 `Shams2025.pdf` vs `Shams2023BRFSS` Bib key）需要检查内容而非仅看文件名
- pdfs子目录中可能有非当前Bib的PDF，删除前需确认
- 符号链接创建后，用 `ls -la *.pdf` 验证，确保链接正确

**实战数据（pima-crispdm 2026-06-18）**：
| 操作 | 数量 |
|------|------|
| 根目录删除旧PDF | 7个 |
| 根目录删除旧元数据 | 3个（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md） |
| 删除bak文件 | 5个 |
| 从pdfs复制匹配PDF到根目录 | 8个 |
| 创建符号链接 | 2个（Collins2015TRIPOD→Collins2015, Lundberg2017SHAP→Lundberg2017） |
| 规范化后根目录PDF/链接 | 18个 |
| Bib总数 | 29个 |
| 仍有缺失PDF | 14个（需下载） |

### 🟡 Bib清理后的.tex引用清理顺序陷阱（2026-06-18 实战）

清理 Bib 中的无效条目只是第一步。如果 `.tex` 文件中仍引用了已删除的 bibkey，编译仍会产生 undefined citation 警告。

**正确顺序**：

```
Step 1: 从 references.bib 删除无效/虚假/错误条目
Step 2: 从 paper.tex 中删除对已删除 bibkey 的 \cite{} 引用
Step 3: 重新编译 — pdflatex → bibtex → pdflatex × 2 → pdflatex × 1
Step 4: 验证 — 0 undefined citation warnings, 0 errors
```

**⚠️ 错误做法**：只清理 Bib 不清理 .tex → 编译仍有 undefined citation 警告 → 看起来"引用没修好"→ 但实际上问题已部分解决，只是 .tex 残留。

**检测残留引用**：
```bash
# 清理后检查 .tex 中是否还有已删除的 bibkey
deleted_keys="Wen2024Leakage Chang2024 Deepalakshmi2025"
for key in $deleted_keys; do
    grep -n "$key" paper.tex && echo "REMAINING: $key" || echo "CLEAN: $key"
done
```

**修复**：找到 .tex 中引用这些 key 的行，删除或替换为正确引用。

**付费墙/下载失败模式**：
- BMJ论文（Riley2020SampleSize, Vollmer2020Machine）：Cloudflare防护，curl返回HTML挑战页面
- MDPI论文（Sali2025）：403拒绝
- Semantic Scholar API：429 Too Many Requests（限流）
- Sci-Hub：403 Forbidden
- 处理策略：DOI验证通过后，PDF缺失不计入质量扣分，在报告中注明"付费墙PDF缺失"

34. **🟡 引用计数 > Bib条目数不等于异常（2026-06-18 实战）**: 扫描论文库时，`\\cite{}` 计数经常超过 Bib 条目数——这不是 bug，而是正常现象。同一文献在引言（方法概述）+ 方法（算法细节）+ 讨论（对比分析）中可能被多次引用，每个引用都产生一个 `\\cite{}`。

**正确处理**：
- **D10a 计算**：对每个 `\\cite{key1, key2}` 中的每个 key 去重后统计（unique cite keys），而非 `\\cite` 出现次数
- **引用总数（Total Citations）**：所有 `\\cite` 出现次数（含重复），用于评估论文引用丰富度
- **D10a**：unique_cite_keys ∩ bib_keys / len(bib_keys)，只计算不重复的键
- **D10a > 100%**：当 unique_cite_keys 数量超过 bib 条目时可能出现（如同一 bibkey 在 bib 文件中出现多次，或引用计数方式不一致），这不表示问题

**扫描论文库成熟度的关键指标**（2026-06-18 实战总结）：
- **成熟论文特征**：有编译PDF (>500KB)、有07-quality/quality_check.md、有05-figures/含3+张图、有Graphical Abstract、有index.md、引用数 ≥30、D10a ≥80%
- **唯一成熟论文示例**：3d-eyeball-iris-segmentation — D10a=100%、75个引用、50篇Bib、2.7MB PDF、3张Figure、Graphical Abstract、quality_check.md
- **次成熟候选**：pima-crispdm — 78个引用、66篇Bib、有PDF但有status.json无quality_check.md、无Figure
- **脚本化扫描**：使用 `scripts/paper-maturity-scan.py` 自动排序所有论文的成熟度评分
- **成熟度分级标准**（2026-06-18 实战）：76篇论文扫描结果如下：

| 等级 | 评分 | 特征 | 实战数据（2026-06-18） |
|:-----|:----:|:-----|:----------------------|
| L5 成熟投稿级 | ≥90 | 全量结构(01-07)+index+QC+PDF(>500KB)+3+图+GA+D10a≥80% | 1篇: 3d-eyeball-iris-segmentation |
| L4 准投稿级 | 70-89 | 有编译PDF+index+QC+引用完整，缺GA或2+图表 | 0篇 |
| L3 可投稿级 | 50-69 | 有编译PDF+引用完整+实验代码，缺QC或index | 1篇: pima-crispdm (80/100) |
| L2 草稿级 | 20-49 | 有paper.tex可编译，缺PDF或引用不完整 | 3-5篇 |
| L1 骨架级 | <20 | 有paper.tex但无法编译，或仅有目录结构 | 69+篇 |

**成熟论文核心特征**：
- 有编译PDF（>500KB，3d-eyeball=2.7MB, pima-crispdm=372KB）
- 有完整7子目录结构
- 有index.md（元数据+作者+状态+质量评分）
- 有quality_check.md（G1-G7审计记录）
- 有state.json（stage+status+quality_score+gate_status）
- D10a ≥80%（成熟论文通常100%）
- 0孤儿, 0僵尸引用
- Clean编译（0 errors, 0 undefined warnings）

**PDF vs Bib 不匹配模式**（2026-06-18 实战）：参考文献PDF数量可能远超Bib条目数（pima-crispdm: 51 PDF vs 33 Bib）。多出的PDF是NotebookLM导入时的历史残留，不在bib中。处理策略：只要bib条目全部正确引用在正文中、D10a=100%，PDF历史残留不影响论文质量——保留它们无害，删除需逐个确认是否被引用。