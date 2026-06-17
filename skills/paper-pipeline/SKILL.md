---
name: paper-pipeline
description: "主skill | SCI论文全流程编排器。核心原理：声明与执行分离、逐问收束、节点闸门、闭环进化。v3.9新增模板层：按论文类型预选实验模板(CRISP-DM/消融/对比/理论)。v3.10新增：批量双质检工作流、NotebookLM_唯一命名规范、引用PDF就绪检查。v3.10.1修复：paper-manager搜索导入错误、更新DOI批量下载策略。v3.14新增：论文管线双轨制（轨道A论文管线/轨道B知识库）、空壳清理协议。调用子skill: notebooklm-cli, sci-paper-standard-structure, research-paper-search, sci-paper-quality-review"
version: 3.14.0
author: "Synthos + 临床科研设计与论文写作 + 用户杨晓凯"
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: SCI论文全流程编排器。核心原理：声明与执行分离、逐问收束、节点闸门、闭环进化。v3.14新增：论文管线双轨制、空壳清理协议。
    signature: |
      paper_name: str -> pipeline_report: dict | pipeline_report: dict (stage, status, quality_score, next_step)
    related_skills: [quality-gate, evolution, project-experience-distillation, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification, sci-paper-quality-review, conversation-to-memory, knowledge-extraction, knowledge-acquisition, academic-atom-architecture]

---

## IO_CONTRACT

- **input**: `paper_name: str` — 论文目录名，相对于 papers/ 目录
- **output**: `pipeline_report: dict` — 包含 stage, status, quality_score, next_step 的流水线报告
- **side_effects**: 更新论文目录下的 state.json、quality_check.md、LaTeX 源文件及编译产物

# Paper Pipeline — 科研全流程编排器（哲学驱动版）

## 原理层 · 文言

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

### 轨道B：知识库
- 进入条件：无paper.tex但有研究内容（有step_*.md、参考文献、代码、目录）
- 流程：知识条目生成（cron产出直接走轨道B）
- 输出：knowledge_entry_*.md

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

```python
import re

with open('paper.tex') as f: tex = f.read()
with open('references.bib') as f: bib = f.read()

# 提取cite键
tex_cites = set()
for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', tex):
    for k in m.group(1).split(','): tex_cites.add(k.strip())

# 提取bib键
bib_keys = set(re.findall(r'@\w+\{[^,]+,', bib))

# 计算
orphan = tex_cites - bib_keys   # tex有但bib无 → 零容忍
zombie = bib_keys - tex_cites   # bib有但tex无 → 需清理
print(f"正被引用: {len(tex_cites & bib_keys)}")
print(f"孤儿: {len(orphan)} — 必须修复")
print(f"僵尸: {len(zombie)} — 建议删除")
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

## 已知陷阱

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