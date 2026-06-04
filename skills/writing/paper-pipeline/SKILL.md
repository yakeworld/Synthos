---
name: paper-pipeline
description: "主skill | SCI论文全流程编排器。核心原理：声明与执行分离、逐问收束、节点闸门、闭环进化。v3.9新增模板层：按论文类型预选实验模板(CRISP-DM/消融/对比/理论)。v3.10新增：批量双质检工作流、NotebookLM_唯一命名规范、引用PDF就绪检查。v3.10.1修复：paper-manager搜索导入错误、更新DOI批量下载策略。调用子skill: notebooklm-cli, sci-paper-standard-structure, research-paper-search, sci-paper-quality-review"
signature: "paper_name: str -> pipeline_report: dict, next_actions: list"
related_skills: [latex-output, notebooklm-writing-workflow, political-proposal, scc-paper-writing-norms, sci-paper-standard-structure]
allowed-tools: [terminal, read_file, write_file, search_files]
version: 3.12.0
author: "Synthos + 临床科研设计与论文写作 + 用户杨晓凯"
license: MIT
metadata:
  hermes:
    tags: [writing, paper, pipeline, orchestrator]
    related_skills: [notebooklm-cli, sci-paper-standard-structure, research-paper-search, sci-paper-quality-review]
---

# Paper Pipeline — 科研全流程编排器（哲学驱动版）

## 原理层 · 文言

| 概念 | 文言 | 义 |
|:-----|:-----|:---|
| 声明与执行分离 | **先立后行，不混不乱** | 写好全文再编译，不边写边编 |
| 逐问收束 | **一问一答，渐次收窄** | 每轮NotebookLM问一个具体问题，答案逐轮收敛 |
| 节点闸门 | **节不过则停，门不通则返** | 每阶段完成必经质量门，不通过不前进 |
| 闭环进化 | **投完不弃，检之改之** | 投稿后仍可自检修订，为下轮迭代储备 |
| 论文即验证 | **文以验法，技乃所产** | 论文不是终极目标——它验证系统是否工作；可复用的技能才是真正产出 |
| 自我进化 | **一气流注，不假再生** | 从方向到投稿全流程自动化，连续运行，高质量科研自然涌现 |

> **文以验法，技乃所产。自进化是唯一目标，论文是验证手段，技能是系统产物。**

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
bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib))

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
    key=$(basename "$f" .pdf)
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

### 🔴 工作目录统一铁律 — 所有论文在 Synthos/outputs/papers/ 下

> **2026-06-04 用户明确要求**：所有论文的工作目录统一为 `/media/yakeworld/sda2/Synthos/outputs/papers/{paper-name}/`。不得在多个路径下分散存放同一篇论文。

### 统一规则

| 规则 | 说明 |
|:-----|:------|
| **唯一工作目录** | 每篇论文只在一个目录下工作：`Synthos/outputs/papers/{paper-name}/` |
| **09-子目录体系** | 必须使用标准化结构：01-manuscript / 02-submission / 03-code / 04-data / 05-figures / 06-references / 07-quality / 08-records / 09-background |
| **PDF存储** | 引用PDF统一在 `06-references/pdfs/`，不在其他路径保留副本 |
| **外部源→合并** | 其他路径下的论文（如 `投稿文件汇总/crispdm-pima/`）发现后立即合并到 Synthos outputs，合并后该路径废弃 |
| **合并步骤** | ① 拷贝最新 paper.tex+references.bib 到 `01-manuscript/` 和 `06-references/` ② 拷贝实验代码到 `03-code/experiment/` ③ 拷贝分析文档到 `09-background/` ④ 更新符号链接 ⑤ 验证编译通过 ⑥ 通知用户统一完成 |

### 已知外部源目录（需持续排查）

| 外部源 | 当前状态 | 处理 |
|:-------|:---------|:-----|
| `投稿文件汇总/{paper-name}/` | Pima已合并 ✅ | 发现新论文即合并 |
| `~/桌面/article_todo/` | 8篇待写（6眼动+2前庭） | 启动前先迁入 Synthos outputs |
| `~/桌面/synthos_paper.tex` | 单文件草稿 | repo版更成熟：outputs/papers/synthos-system-paper/ |

### 合并操作参考（含完整步骤）

具体合并操作的详细步骤、编译验证、实战记录见 `references/paper-dir-unification-workflow.md`。包含：扫描外部源 → 创建09目录 → 拷贝文件 → 建立symlink → 编译验证 → 通知用户的完整闭环。

**合并检测脚本**：

```bash
# 检查是否有论文在 Synthos outputs 之外有副本
EXTERNAL_BASE="/media/yakeworld/sda2/投稿文件汇总"
for d in "$EXTERNAL_BASE"/*/; do
    name=$(basename "$d")
    if [ -d "/media/yakeworld/sda2/Synthos/outputs/papers/$name" ]; then
        echo "⚠️  重复: $name — 已存在于 Synthos outputs"
    else
        echo "🆕 未纳入: $name — 需迁移"
    fi
done
```

## 📁 论文草稿来源管理

除 `outputs/papers/` 下的已编排论文外，用户还有两处草稿来源：

1. **`~/桌面/article_todo/`** — 8篇待写论文（6眼动+2前庭），详见 `references/article-todo-inventory.md`
2. **`~/桌面/synthos_paper.tex`** — Synthos系统论文早期草稿（repo版更成熟：`outputs/papers/synthos-system-paper/synthos-paper.tex`）

**启动一篇todo论文前**：先查阅 `article-todo-inventory.md` 了解结构和成熟度，再决定是全文重写还是直接编译已有LaTeX。对于已有初稿的论文优化，使用 `todo-paper-optimization-workflow.md` 三步法。

### 已知陷阱

17. **🔴 定量实验中的 benchmark 降级（Quantitative Eval without Benchmark Datasets）**：当基准数据集（BSDS500、KITTI等）因安全扫描器阻断/付费墙/网络不可达而无法下载时，使用 `skimage.data` 内置标准测试图像做原理验证性定量实验。详见 `references/quantitative-evaluation-with-builtin-data.md`。

21. **先搜数据再跑实验**: P2阶段撰写跨数据集验证/Discussion增强节前，先搜索已有实验数据而非立即重跑。实验输出常存于 `outputs/papers/{paper}/`、`synthos_data/`、或旧会话日志。`session_search()` + `find` 快过重新运行整个pipeline。2026-05-31实战教训：用户纠正了"数据肯定是保留在哪里的找一下"，应优先查现有结果。
2. **批量DOI下载不可行** — 论文引用的大多是付费期刊DOI（Springer、Elsevier等），99%无法通过OA/arXiv下载。正确做法：只下载arXiv论文，其余在manifest中标记为 `paywalled`。
3. **Semantic Scholar API的openAccessPdf字段** — 多数返回空（`"status": "CLOSED"`），不是API错误，而是论文确实无OA版。
4. **PDF提取质量差异大** — markitdown、pandoc、pdfminer对不同PDF的提取质量差异显著。部分PDF（扫描版/数学论文）提取为乱码。优先用原生PDF格式上传NotebookLM。
5. **NotebookLM上传限流** — 连续上传 > 30个PDF可能触发限流（超时）。建议分批（每次20个，间隔30秒）。
6. **DOIs vs arXiv IDs** — 同一论文可能同时有DOI和arXiv ID。优先用arXiv下载（免费、稳定、快速）。`10.48550/arXiv.xxxx` 格式的DOI是arXiv代理，不需要Sci-Hub。

### 🧹 论文完成后的目录清理协议（2026-06-04 Pima实战）

论文通过双质检后，根目录常残留大量垃圾文件。执行以下清理步骤：

```bash
# Step 1: 移动文件到正确子目录
mv notebooklm-review.md notebooklm-sources.json 09-background/ 2>/dev/null
mv QUALITY.md qc-*.md quality-report.md 07-quality/ 2>/dev/null
mv REFERENCE_MANIFEST.md 06-references/ 2>/dev/null
mv fig_architecture.pdf Fig_Architecture.* 05-figures/ 2>/dev/null
mv crisp-dm-pima.ipynb 03-code/ 2>/dev/null
mv sections/* 09-background/ 2>/dev/null; rmdir sections 2>/dev/null

# Step 2: 删除垃圾文件
rm -f enhanced-bibtex-*.bib references.bib.bak* bibkey-map.json
rm -f paper-synthos-v*.tex pima-crispdm-v*.pdf pima-crispdm-v*.tex
rm -f paper.aux paper.bbl paper.blg paper.log paper.out paper.spl
rm -rf analysis-submission paper-submission elsarticle pdfs

# Step 3: 同步根目录 bib → 06-references/
ln -sf 06-references/references.bib references.bib  # 取代根目录独立文件

# Step 4: 清理 01-manuscript/ 中的编译产物
rm -f 01-manuscript/paper.aux 01-manuscript/paper.bbl 01-manuscript/paper.log
rm -f 01-manuscript/old-version-*.tex
```

**判断标准**：论文根目录只保留 `01-09` 九个子目录 + `references.bib`（symlink）。无其他独立文件。

**Pima实战成果**：清理前 ~60个文件（含140条垃圾bib的references.bib），清理后干净目录结构。

---

## 论文项目组织铁律（2026-05-30用户明确 + 2026-05-31研究空白审计补充）

每次论文优化/投稿准备完成后，必须执行以下操作：

1. **目录标准化** — 主论文目录按 09-子目录 体系重排
2. **过程文档化** — 在 `08-records/optimization-logs/` 下生成：
   - `CHANGE_LOG.md` — 做了什么（6阶段追踪）
   - `TODO.md` — 待办清单（投前→投后→后续研究）
3. **研究空白审计（RESEARCH_GAPS.md）** — 从完成的论文中系统性推导后续研究方向，**必须放在论文自身的 `09-background/` 目录中**，不得放在外部 `~/桌面/article_todo/` 等独立位置。这使得研究空白随论文版本管理，与其他论文的空白互不干扰。
4. **外部版本同步** — article_todo、桌面等外部副本归入 `09-background/`
5. **提交包同步** — 确保 `02-submission/` 与当前手稿一致

模板与详细方法论见 `references/research-gap-audit-template.md`。

## 数据来源引用追溯（2026-05-30新增）

> 当论文使用实验/影像数据（μCT、MRI、ICT、临床CT等）时，**必须追溯实际数据来源**并验证引用覆盖率。数据来源的原始出版物必须被论文引用，不能仅引处理方法论文。

### 触发条件

论文目录包含实验数据文件，符合以下任一：
- `04-data/` 目录有 `.csv`/`.json` 拟合参数文件
- `code/data/` 目录有标注数据（`.mrk.json`、`.nii.gz`、`.stl`）
- NFS 数据目录（`/mnt/nfs/inner_ear_data/`）被引用
- 论文 Methods 段提及特定扫描设备、数据集名称、或图像来源

### 追溯方法

**Step 1: 查用户研究笔记**

搜索 `yakeworld` 笔记目录（Obsidian vault）中与论文主题相关的文件：
```bash
grep -rli "μCT\|microct\|数据来源\|dataset.*source\|s16885\|HBL\|OpenEar" /media/yakeworld/sda1/yakeworld/
```

笔记中通常记录了每个数据集的来源URL、DOI、原始文献引用。

**Step 2: 定位实际数据文件**

检查 NFS 数据目录和本地数据目录，识别所使用的数据集：
- `/mnt/nfs/inner_ear_data/Human_Bony_Labyrinth/` — F01-F14 + T01-T08
- `/mnt/nfs/inner_ear_data/OpenEar/` — Greek-letter specimens
- `/mnt/nfs/inner_ear_data/david_ct/` — Human S16885 (UNC Henson lab)
- 本地 `03-code/data/sp*_microct/`、`sp*_mrn/`、`sp*_ict/`

**Step 3: 比对论文引用**

对每个识别的数据集，检查论文bibliography是否包含原始出版物：

| 数据源 | 原始引用 | 检查方法 |
|:-------|:---------|:---------|
| Human S16885 (UNC) | David2016 (Sci. Rep.) | `grep David2016 v4-paper.tex` |
| Human_Bony_Labyrinth (F+Т系列) | Wimmer2019 (Data in Brief) | `grep Wimmer2019 v4-paper.tex` |
| OpenEar (Greek letters) | Sieber2019 (Sci. Data) | `grep Sieber2019 v4-paper.tex` |

**Step 4: 补全缺失引用**

将缺失的数据源引用添加到 `thebibliography` 中，关键信息：
- 作者, 标题, 期刊(年份), 卷号, 页码/文章号
- DOI 可选（pdflatex + thebibliography不需要）

**验证**：
```bash
# 编译 → 确认0未定义引用
pdflatex paper.tex && pdflatex paper.tex
grep -i "undefined" paper.log   # 应无输出
```

### 常见缺失引用模式（实战记录）

| 场景 | 表现 | 修复 |
|:-----|:-----|:-----|
| 公开μCT数据集引了方法而非原始论文 | 论文使用 Human_Bony_Labyrinth 数据仅引 Smith2021 | +Wimmer2019, Data in Brief (2019) |
| OpenEar数据未引原始论文 | 论文使用 Greek-letter 标本但引了无关文献 | +Sieber2019, Sci. Data (2019) |
| UNC μCT 标本仅引自身在手稿 | 论文使用 Human S16885 仅引 Yang2025 (in prep) | +David2016, Sci. Rep. (2016) |

### 引用PDF就绪度检查

双质检有效的**前置条件1**：论文的引用文献必须在对应的 NotebookLM 项目中作为 source 存在。Gemini 需要引用 source 来验证论文中的每个引文和声明。

**前置条件2（v3.12新增）**：bibitem 完整性与数据来源引用覆盖率。详见 `paper-reference-pipeline` 技能 Step 7-8 及 `quality-gate` 技能的 `references/ref-citation-audit-protocol.md` 和 `references/bibitem-integrity-verification.md`。
引用PDF就绪度检查 是 **第二层**（下载实际PDF供NotebookLM验证）;
两层次必须先后通过才能进入质量门评审。

### 引用PDF就绪度检查

双质检有效的**前置条件1**：论文的引用文献必须在对应的 NotebookLM 项目中作为 source 存在。Gemini 需要引用 source 来验证论文中的每个引文和声明。

**前置条件2（v3.12新增）**：bibitem 完整性与数据来源引用覆盖率。详见 `paper-reference-pipeline` 技能 Step 7-8 及 `quality-gate` 技能的 `references/ref-citation-audit-protocol.md` 和 `references/bibitem-integrity-verification.md`。

**2026-05-27 确认：Markdown 优于 PDF 上传 NotebookLM。**
- PDF 经常因无可提取文本层导致 error 状态
- Markdown 纯文本格式 100% 成功，Gemini 检索效果相同
- 方法：`note create --title 名称 --content "$(cat paper.md)"`
- 详见 `notebooklm-cli` 技能陷阱 #00

**检查方法**：
```bash
# 检查论文目录中是否有 pdfs/ 引用PDF
ls paper-dir/pdfs/*.pdf 2>/dev/null | wc -l

# 检查 NotebookLM 项目 source 数（大的项目 = 参考文献丰富）
notebooklm source list -n <project_id> 2>/dev/null | grep -c "│.*│.*│"
```

**就绪度判定**：
- ✅ >50 sources + pdfs/ 有引用PDF → 参考文献就绪，QC有效
- ⚠️ 10-50 sources → 部分就绪，QC结果可能偏保守
- ❌ <10 sources → 参考文献不足，先补充 source 再跑 QC

### 引用补充：低文献项目的回退策略

当 NotebookLM 项目 source <10 篇时，需要补充参考文献。**不要试图批量下载论文 .bib 文件中的所有 DOI**（实践中几乎全部失败——论文引用的大多是付费期刊DOI，Sci-Hub不收录）。正确做法：

**Step 1: 确认项目范围**
```bash
# 查看当前项目有多少 source
notebooklm source list -n <project_id> 2>/dev/null | grep -c "pdf\|PDF"
```

**Step 2: 论文自身上传确认**
检查项目中的 PDF 是论文自身还是真正的参考文献。只有 1-3 篇 PDF 且文件名含论文名 → 说明缺参考文献 source。

**Step 3: 定向搜索关键参考文献（避开 paper-manager search）**

`paper-manager search` 的学术搜索可能卡住（>120s 无输出即死锁）。改用直连搜索：

```bash
# 方案A: arXiv搜索 — 最稳定
python3 -c "
import requests, json
r = requests.get('http://export.arxiv.org/api/query?search_query=all:keyword&max_results=3')
# 解析 atom feed，提取 PDF 链接
"

# 方案B: Semantic Scholar API（简单搜索，不开 paper-manager）
curl -s 'https://api.semanticscholar.org/graph/v1/paper/search?query=keyword&limit=3' \
  | python3 -c "import sys,json; [print(p['paperId'],p.get('title','')) for p in json.load(sys.stdin).get('data',[])]"
```

**Step 4: 下载 + 上传到 NotebookLM**
```bash
# 找到可下载的 PDF 后
notebooklm source add /path/to/paper.pdf --title "ref-topic-description" -n <project_id>
```

**Step 5: 高优补充顺序**
| 优先级 | 项目 | 当前源 | 目标 |
|:-------|:-----|:-------|:-----|
| P0 | BPPV (95509a49) | 5 PDFs | >=15 |
| P1 | 3D眼球 (b6698e12) | 9篇 | >=15 |
| P2 | CutEye (468528f8) | 1篇 | >=10 |

详细操作流程见 `references/ref-supplement-workflow.md`。

### 已知陷阱

1. **pdflatex UnicodeDecodeError**: 当 .tex 含中文或 smart quotes 时，`subprocess.run(..., text=True)` 可能因编码错误崩溃。**修复**: 用 `text=False` 捕获 bytes，手动 decode('utf-8', errors='replace')。
2. **delegate_task 的 50 次工具调用限制**: 批量任务很容易达到上限。使用 Python 脚本在 single `execute_code` 中完成，避免每次操作触发独立工具调用。
3. **已上传的 PDF 用 --title 区分**: 同一个 NotebookLM 项目内多个 paper.pdf 无法区分。统一用 `{dir-name}-v{N}.pdf` 格式加 `--title` 参数。
4. **Shared 项目无法通过 CLI 删除 source**: "Deleted source" 成功消息后 source 仍存在。需用户在网页端手动删除。
5. **引文验证提示**: 在 Layer B 评审 prompt 中附加 `"For each citation in the paper, verify it matches a source in this notebook."` 让 Gemini 做引用验证。
5b. **凭证硬编码审计（2026-05-31）**: 发现 `batch_refresh.sh`、`batch_meddata_all.py`、`batch_enhance_all.py`、`auto_fix_d8.py` 中硬编码了 MEDDATA_USERNAME/PASSWORD。已全部改为读环境变量。运行这些脚本前须确保 `MEDDATA_USERNAME` 和 `MEDDATA_PASSWORD` 已设。详见 `references/credential-envvar-audit.md`。下次使用 paper-manager 工具前可先运行审计检测是否有其他硬编码残留。

6. **paper-manager search 导入错误（已修复 2026-05-27）**: 曾因 `src/` 结构下的相对导入错误（`from ..racing_engine import` / `from .sources.xxx import`）导致 PDF 下载阶段崩溃。表现为搜索成功→进入下载→崩溃→fallback到旧Sci-Hub循环→"卡死"。
   **修复**：`pdf_downloader.py`、`racing_engine.py`、`scihub_racing.py` 中的相对导入全部改为绝对导入。
   **现状**：`paper-manager search` 可用（3.2s搜索3篇），`download_one.py` 可用（206KB PDF下载成功）。
   **仍然慢**：Sci-Hub 域探测每次约8-12s + 实际下载超时。不是卡死，是慢。
   **替代**：如果只需要参考文献项（不下载PDF），用 `--no-download` 参数跳过下载阶段，搜索+BibTeX导出通常3秒内完成。

7. **批量DOI下载不可行**: `batch_ref_download.py` 从 .bib 文件提取所有 DOI 后逐个调用 `download_one.py` 下载。实践中几乎全部失败——论文 .bib 里引用的多是付费期刊 DOI（Springer、Elsevier、Taylor & Francis等），Sci-Hub 不收录，LibGen也不收录。`batch_ref_download.py` 的正确用途不是批量下载——是**审计哪些DOI不可获取**。如果一个项目的 .bib 里>80% DOI下载失败，说明该项目需要定向找 OpenAccess 替代引用。

## 七原子 → 科学流程 → NotebookLM 映射

本管线的每一阶段都对应一个认知原子，由哲学模型驱动，通过 NotebookLM Gemini 执行。

### 特殊管道：3D对数螺旋形态学分析（2026-05-29新增）

对于需要对解剖结构中心线进行数学建模的论文（如半规管、血管、气道等），使用专门的3D对数螺旋拟合管道。详见 `references/3d-logspiral-scc-analysis.md`。包含两阶段拟合策略（平面螺旋→面外正弦扭转）、批量处理脚本 `scripts/batch-3d-logspiral-fit.py`、以及典型参数解读。

该管道包含：6种候选模型拟合 → AIC/BIC模型选择 → 配对组织对比（Wilcoxon符号秩检验+Cohen d效应量）→ Bootstrap置信区间 → Frenet-Serret曲率/挠率分析 → Stokes流流体力学理论推导。

### 推荐模型：3D对数螺旋（3D Logarithmic Spiral, 7参数）

方程：
```
r(θ) = O + R · (a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))^T
```

优势：比HSMM-2（10参数）少3个参数，AIC/BIC更优，且与耳蜗对数螺旋共享数学形式——可提出发育同源性假说。

### 候选模型对比库

| | 模型 | 参数 | 优势 | 劣势 |
|:-----|:-----|:----:|:-----|:-----|
| | 平面圆 | 6 | 经典基线 | RMSE最高 |
| | 平面椭圆 | 8 | 改进拟合 | 无面外分量 |
| | **3D对数螺旋** | **8** | **最优平衡** | 需两阶段拟合 |
| | HSMM-2正弦椭圆 | 8 | 高精度 | 参数同数 |
| | Fourier级数 | 27-39 | 理论精度上限 | 严重过拟合 |
| | 螺旋线 | 7 | 负对照 | 不适合SCC |

### 跨结构比较协议
SCC与耳蜗的螺旋率b比较需补充：
1. **Bootstrap 95% CI**（10,000次重采样）量化SCC b分布
2. **Cohen's d**检验左右耳对称性（作为方法稳健性证据）
3. 引用文献的耳蜗b值作为参考，禁止声称「发现二者共享同一螺旋率」

### 配对组织比较（如骨vs膜）
- Wilcoxon符号秩检验（配对数据）
- Cohen's d / rank-biserial r
- 方向对齐：nearest-neighbor path检测两组织中心线的对应关系

### 实验代码与数据管理铁律（2026-05-31）

> **用户明确要求**:
> 1. 所有实验代码必须保存到 `03-code/experiments/`（不存 /tmp）
> 2. 推荐通过Docker执行ML实验，避免 `--break-system-packages`

### D6增强：跨数据集验证模式

> **实战验证**（2026-05-31 Pima论文）: D6从0.72→0.80 (+0.08)，核心手法是跨数据集验证。2026-06-03进一步增加文献汇聚证据后预期D6达到0.82-0.84。

**两步强化策略**：
1. **实验级**：跑Helix vs Leaky对比在2+外部数据集 → 见下文协议
2. **文献级**：下载OA PDF → 定位泄漏原文 → 提取基线性能 → 写Discussion独立验证段 → 见 `references/literature-convergent-evidence-workflow.md`

当D6（新颖性）因"结论已在文献中建立"而不及格时：

**Step 1: 找出文献的缺口**
- 文献说了"X有害"但没量化 → 你的量化就是新发现
- 文献说了"X有害"但只在单数据集验证 → 你的跨数据集验证就是新发现

**Step 2: 选择验证数据集**
- 至少3个数据集，覆盖不同：样本量（小/中/大）、患病率（高/中/低）、特征维度
- 确保对比维度（如患病率）有足够跨度以揭示单调关系

**Step 3: 统一实验协议**
- 所有数据集用同一代码管线（Helix隔离）
- 同一评价指标（F1为主）
- 记录每个数据集的Helix F1 vs Leaky F1

**Step 4: 发现规律**
- 建立序列: 患病率13.8%→+73.2%, 34.9%→+11.1%, 61.5%→−1.6%
- 结论: X的损伤与Y呈单调关系（而非二元有无）

**Step 5: 论文集成**
- Abstract加一句话概括跨数据集发现
- Contributions列中展开
- Discussion新增独立子节（含表）
- Conclusion提及跨数据集验证
- Limitations更新：承认单数据集局限，但跨数据集已缓解

#### 代码持久化规则

| 资源类型 | 目标路径 | 示例 |
|:---------|:---------|:-----|
| 实验脚本 | `03-code/experiments/run_*.py` | `run_helix_benchmark.py` |
| 实验结果JSON | `03-code/experiments/*_results.json` | `cross_dataset_results.json` |
| 实验说明 | `03-code/experiments/README.md` | 数据集/方法/运行方式 |
| Docker命令 | README.md中注明 | 标准模板见下 |

#### Docker执行标准模板

```bash
# 对任何需要pip安装的实验
docker run --rm \
  -v /home/yakeworld/synthos_data:/data \
  -v $(pwd)/03-code/experiments:/code \
  python:3.11-slim \
  bash -c "pip install -q pandas scikit-learn imbalanced-learn xgboost && python3 /code/run_xxx.py"
```

使用 `terminal(background=true)` + `notify_on_complete=true` 避免阻塞主会话。

#### 跨数据集实验管理

当论文需要多数据集验证时：
1. 实验代码统一放在 `03-code/experiments/`
2. 每个实验有独立脚本（如 `run_helix_benchmark.py`）
3. 结果合并为一个JSON
4. `README.md` 记录实验矩阵（哪些数据集×哪些模型）

### 🔴 用户工作流偏好：NotebookLM 逐问法优先于直接写作

**2026-05-28 用户明确纠正**：不得跳过 NotebookLM 直接写论文节。所有论文节必须通过 `notebooklm ask` 逐节由 Gemini 从源文件提取生成，而非依赖 AI 自身知识库写作。

正确流程：
```
1. NotebookLM 文献检索导入（add-research）→ 源文件就绪
2. 逐问法 Round 1：提取关键文献信息（Bradshaw/Rabbitt/Santina等）
3. 逐问法 Round 2：空白定位（Gap确认）  
4. 逐问法 Round 3-5：逐节生成内容（Introduction/Methods/Results/Discussion）
5. 提取 LaTeX 输出 → 编译 → 双质检
```

每个 Q&A 问题的输出保存到 `{paper_dir}/tmp/qa_r{N}_{topic}.txt` 作为可追溯记录。

**禁止**：直接在 execute_code 或 terminal 中写论文 LaTeX 正文（即便有源文件内容记忆也不行）。必须让 Gemini 基于其源文件库生成内容并引用。

对比模型库（按参数复杂度递增）：
1. 平面圆 (6参数) — 经典基线
2. 平面椭圆 (8参数)
3. **3D对数螺旋 (7参数)** — 当前最优
4. 非平面正弦椭圆HSMM-2 (10参数) — 对比基线
5. Fourier级数 (27/39参数) — 过拟合参考
6. 螺旋线 (7参数) — 负对照

模型选择：AIC/BIC。跨结构比较（如SCC vs 耳蜗）需补充Bootstrap置信区间。配对组织（骨vs膜）需做方向对齐（nearest-neighbor path检测）。

该管道包含：6种候选模型拟合 → AIC/BIC模型选择 → 配对组织对比（方向对齐+Wilcoxon检验）→ Frenet-Serret曲率/挠率分析 → 跨结构Bootstrap比较 → Stokes流流体力学理论推导。

```
认知原子         科学步骤          驱动哲学              NotebookLM操作
────────         ────────          ────────              ──────────────
ACQ              文献检索          CARS Move1           逐问法Q1-Q3
EXT              知识提取          格物通理              source guide + 提取Q&A
ASC              关联发现          取象通变·天人合一     交叉Q&A
GAP              空白定位          CARS Move2           聚焦Q&A
HYP              假设形成          CARS Move3           结构化Q&A
ARG              论文写作          图尔敏·金字塔·沙漏    逐节ask→extract→compile→verify
VER              质量验证          双质量检查            Layer B: Gemini 7维评审
```

- `references/credential-envvar-audit.md` — 凭证硬编码审计清单，paper-manager 工具凭证环境变量化改造记录
- `references/legacy-paper-rescue-workflow.md` — 抢救遗落/废弃论文的工作流（Markdown→LaTeX转换、从零构建references.bib、OpenAlex DOI验证、D8/D10a验证）
- `references/paper-project-optimization-cycle.md` — 6阶段论文项目优化循环：质量评估→自动修复→提交包同步→目录标准化→过程文档→研究空白与假设。每次投稿前执行完整循环。

## P2 论文构建

**🔴 铁律：不得跳过NotebookLM直接写论文节。所有论文节必须通过 `notebooklm ask` 逐节由Gemini生成或验证。**

> 2026-05-28 实战教训：用户明确要求"不是直接写文章，应该是问题引导，文献检索"。
> 正确的写作流程：NotebookLM add-research 文献检索 → 逐问法Q&A知识提取 → 提取回答组合为LaTeX → 编译。
> 跳过NotebookLM直接手写LaTeX = 违规流程，审稿时会被发现文献引用不准确。

写作顺序：Results→Methods→Discussion→Introduction→Abstract。

各节Q&A模板见 `notebooklm-cli` skill 的 `references/paper-section-generation.md`。

### 组合编译

编译前先确定论文的引用管理方式。两种模式：

```
模式A — BibTeX (.bib文件 + \\bibliography{...}):
  pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex

模式B — thebibliography (\\begin{thebibliography}...\\bibitem{...}):
  pdflatex paper.tex && pdflatex paper.tex
```

### LaTeX图/表排版坑（2026-05-28）

| 问题 | 表现 | 修复 |
|:-----|:-----|:-----|
| 大图(6×3面板)漂到末尾 | 用 `[t]` 时大图被推到文档最后 | `[t]` → `[htbp]` |
| 图标题与下文间距不足 | 图caption后紧接subsection | `\\end{figure}` 后加 `\\vspace{12pt}` |
| 多列表格超宽 | Overfull hbox警告 | `\\setlength{\\tabcolsep}{4pt}` 缩小列间距 |
| 图layout描述过时 | caption描述3×6layout但实际是6×3 | 每次改layout同步更新caption |

### 模型参数计数：必须说明包涵/排除规则

**2026-05-28 实战教训**：论文声称 HSMM-2 有10参数、3D对数螺线有7参数，但用户指出从公式计数均为11（R(3)+c(3)+a,b,A,ω,φ(5)=11）。问题出在计数口径不一致——R和c的某些自由度由数据决定（SVD平面法线、数据质心），不独立拟合。

**铁律**：
1. 参数计数 = 实际通过优化/最小二乘独立调整的自由参数数
2. 必须明确说明哪些自由度由数据固定（SVD平面法线=2、数据质心=3），哪些是独立可调
3. 3D对数螺线与HSMM-2若共享相同的定位+旋转变换策略（SVD+质心），则参数数应相同

**正确做法**（以SCC论文为模板）：
```
在方法中写明：'Note that both Model 3 and Model 4 are fitted with 8 
independent parameters: the in-plane center coordinates (c_x, c_y) and 
in-plane rotation θ₀ are determined by direct optimization, while the 
shape parameters and torsion parameters (A, ω, φ) are fitted via least-squares.
The 3D rotation matrix R and translation O/c are not independent—the
canal plane normal is obtained from SVD of the data points, and the 3D 
center is set to the data centroid.'
```

### 🧩 多版本论文编辑协议

**场景**：论文目录中同时存在 `paper.tex` 和 `*v2.tex` / `*v{N}.tex` 等版本文件。

**铁律**：编辑 `paper.tex` 前，先检查所有版本化 `.tex` 文件的内容，尤其是：
- `ls *v*.tex` — 列出所有版本文件
- 对比版本文件的摘要/作者/方法等关键段
- 将 `*v2.tex` 中的正确内容移植到 `paper.tex`，而非从头重写

**坑**（2026-05-28实战）：编辑 `paper.tex` 时覆盖了 `v2.tex` 中已有的正确作者信息。用户纠正后才补回。

**原因**：版本文件包含已通过用户审核的内容，`paper.tex` 是最终工作版本但可能落后于版本文件。版本文件是用户认可的状态，不应丢弃。

### D2提升：Always Add Algorithm Pseudocode

When fitting mathematical models to data (curve fitting, optimization), include a numbered algorithm block (`algorithm` environment + `enumerate`) in the Methods section. This directly boosts D2 (Methodological Rigor) score by 0.02-0.05.

Minimum content: input, step-by-step fitting procedure, output parameters. Use `elsarticle`-compatible `algorithm` environment with plain `enumerate` (avoid `algpseudocode` which conflicts with elsarticle's math mode).

```latex
\\begin{algorithm}[htbp]
\\caption{Fitting Procedure}\\label{alg:fit}
\\begin{enumerate}
  \\item Step description with math notation...
\\end{enumerate}
\\end{algorithm}
```

## P4 质量门+递归进化

**强制流程**：编译后自动触发双质量检查。论文 `pdflatex` 编译成功后，不等用户问，立即执行 `post-compile-dual-quality-check` 技能。

### 🔴 P4前置闸门：参考文献NotebookLM就绪检查

**在执行任何Layer B评审之前，必须先通过此闸门。** 

**流程**：
1. 确认论文NotebookLM项目ID（`notebooklm list | grep "论文关键词"`）
2. 执行 `dual-quality-check-v2` 技能的「P0前置闸门」步骤（Step 1-6）
3. 仅当 `源数 ≥ D8 × 80%` 时允许进入Layer B
4. 未通过时：先补充参考文献上传，再继续

**2026-06-01实战教训**：膜性SCC重建论文的Layer B评审在0篇参考文献上传的情况下执行，评审结果（校准分0.81）可能因缺乏全文上下文而不准确。此闸门确保类似情况不再发生。

### 双质量评分汇总表

| Manuscript | Layer A | Layer B | Calibrated | Threshold Pass |
|:-----------|:-------:|:-------:|:----------:|:---------------|
| Paper X    | 0.871   | 0.907   | 0.871      | T1 (>=0.85) ✓  |
| Paper Y    | 0.829   | 0.871   | 0.814      | T2 (>=0.80) ✓  |

### NotebookLM 版本管理

**命名约定**：当一个NotebookLM项目服务多篇论文时，上传文件必须使用唯一命名：
- 格式：`{paper-dir-name}-v{N}.pdf`（如 `hcs3wt-breast-cancer-v2.pdf`）
- 不上传通用名 `paper.pdf` 到共享项目
- 用 `--title` 参数标注论文全称和版本

**更新流程**：
1. 删除旧版：`notebooklm source delete <old_id> -y`
2. 上传新版：`notebooklm source add {dir}-v{N}.pdf --title "..." -n <project_id>`
3. 验证：`notebooklm source list` 确认只有新版

### 已知陷阱

9. **🔴 膜性标注文件分裂陷阱（2026-05-29发现）**: 当分析配对组织结构（如骨vs膜、左vs右）时，同一结构的标注可能被意外分割为多个文件（如sp3 ICT的AC_MEM1+AC_MEM2、sp1 microCT的lc_mem+lc_mem2）。表现为弧比（膜/骨）<1.0 或弧长明显短于同一标本的其他管型。检查方法：进入数据目录后先 `ls *mem* *MEM*` 看是否有多个膜性文件。对每对文件计算4种端点连接的间距，最小间距<3mm即可合并。合并后弧比参考：膜性半规管应比骨性长10-40%（AC:1.10-1.22, PC:1.11-1.20, LC:1.26-1.39）。详见 `bony-to-memb-scc-mapping` 技能的 `references/DATA_MERGING_PROTOCOL.md`。

11. **🔴 重复 bibliography 陷阱（2026-05-30 发现）**

12. **🔴 派生值不同步陷阱（Derived Value Staleness，2026-06-03 发现）**：L0.5审计或手动修正实验数值后，派生值（百分比、比率、delta值、relative improvement）**不会被自动同步**。这是LLM修复的典型模式错误——LLM精准更新了每个独立数值（F1 0.6759→0.6986, 0.7338→0.7657），但依赖这些数值的计算结果（`+8.6%`, `+6.71%`）保持旧值不变。

13. **🔴 消融表模型混用陷阱（2026-06-03）**：消融表的**所有行必须来自同一模型管线**。Pima案Table 2的No/Minor/Medium三行用Ensemble值，但Severe行F1=0.7657**既非Ensemble(0.8140)也非LR(0.7338)**——完全虚构。导致"Recall从0.7500降至0.6364"这个结论是编造的。**检测**：逐行对比实验JSON所有5个指标，不可只看F1/Recall。**铁律**：若Ensemble下Recall不降反升→诚实用LR做消融或报告双升。

    **检测方法**：找出论文中所有「对比性数值声明」（'improved by X%'、'increase of Y%'、'Z times higher'、'W-fold'），人工核查其计算公式中的原始数值是否与当前论文表中的值一致。

    ```bash
    # 批量检查：提取所有 X% 声明，定位其引用的原始值
    grep -oP '(\\+|-)?\\d+\\.?\\d*\\%' paper.tex | sort -u
    # 然后逐条核对计算公式
    ```

    **修复**：对每个派生值，重新计算：
    ```python
    # Pima实战: (0.7657-0.6986)/0.6986 = 9.6% (旧值8.6%错误)
    # 修复流程
    import re
    tex = open('paper.tex').read()
    old_pcts = {'+8.6\\%': '+9.6\\%', '+6.71\\%': '+9.6\\%'}
    for old, new in old_pcts.items():
        tex = tex.replace(old, new)
    with open('paper.tex', 'w') as f: f.write(tex)
    ```

    **Pima实战数字**（2026-06-03）：
    | 位置 | 旧值 | 新值 | 根因 |
    |:-----|:----:|:----:|:-----|
    | Abstract (1处) | +8.6% | +9.6% | 数字更新后未重算 |
    | Figure 1 (1处) | +8.6% F1 | +9.6% F1 | 同上 |
    | Contribution #2 (1处) | +8.6% | +9.6% | 同上 |
    | Results (1处) | +8.6% | +9.6% | 同上 |
    | Discussion Grounds (1处) | +6.71% | +9.6% | 旧版本残留 |
    | Discussion Backing (1处) | +8.6% | +9.6% | 同上 |
    | Conclusion (1处) | +8.6% | +9.6% | 同上 |
    | **共8处** | — | — | — |

    **预防**：L0.5审计/数据修正完成后，自动执行 `grep -oP '\\+?-?\\d+\\.?\\d*\\%'` 扫描全文，对所有百分比声明做公式一致性检查。

11. **🔴 重复 bibliography 陷阱（2026-05-30 发现）**: 当论文经过多轮跨周期编辑后， `grep -oP '\\+?-?\\d+\\.?\\d*\\%'` 扫描全文，对所有百分比声明做公式一致性检查。: 当论文经过多轮跨周期编辑后，`\\bibliography{}` 命令可能被意外重复——一个在附录前，一个在附录后，导致参考文献列表打印两次（PDF 页数虚增 1-2 页）。根因：跨周期编辑时，旧 bibliography 被保留为新段落的前导内容，新 bibliography 又被追加到 `\\end{document}` 前。检测方法：
```bash
# 检查 \\bibliography{} 出现次数
grep -c '\\\\bibliography{' paper.tex
# 若 ≥2 → 重复！仅需保留最后一个（紧邻 \\end{document} 之前）
```
修复：删除靠前的 `\\bibliography{}` + `\\bibliographystyle{}`，只保留 `\\end{document}` 前那一组。**编译链验证**：删除后需清空 .aux/.bbl 后完整运行 pdflatex → bibtex → pdflatex × 2（否则残留交叉引用会导致 undefined citation）。2026-05-30 实战：3d-sobel-edge-detection 删除重复 bibliography 后编译从 11 页（含重复 bibliography）恢复为 12 页（正常）。完整工作流见 `references/duplicate-bibliography-fix-2026-05-30.md`。

## P6: 技能提炼与系统进化（新增 — 闭环的最后一环）

> **P5之前的全部阶段，最终汇入这里。论文完成+双质检通过 ≠ 结束。真正的产出是提炼出可复用的技能，驱动系统进化。**

### 核心哲学

```
论文完成 & 双质检通过
      ↓
P6a: 提炼可复用技能
      ↓
P6b: 修补已有skill的误区/陷阱
      ↓
P6c: 喂入进化引擎
      ↓
P6d: 同步到OpenCode规则（如有编码技能）
      ↓
系统能力提升 — 下一轮论文更少人工介入
```

**每一篇论文的目的**：让下一篇论文更容易、更自动、更高质。

### P6a: 提炼可复用技能

使用 `project-experience-distillation` skill，从本论文中提取：

| 提取内容 | 示例 | 去向 |
|:---------|:-----|:------|
| **新方法/协议** | B-spline骨膜偏差分析协议 | 新skill → `hermes skills create` |
| **流程步骤** | 论文全流程编排（P0→P5） | 已存在 → 更新paper-pipeline |
| **轨迹/误区** | argsort vs nearest-neighbor path | 更新quality-gate的curve-fitting-pitfalls |
| **数据来源** | OpenEar/UNC数据集的引用要求 | 更新paper-pipeline的数据溯源节 |
| **自动化触发** | 编译后自动双质检 | 已有(post-compile-dual-quality-check) |
| **未解决的问题** | G1-G7研究空白 | 写进论文的09-background/ |

**判断标准**：一个协议/方法在论文中出现2次以上 → 应提炼为skill。

### P6b: 修补已有skill

双质检过程中发现的每个陷阱/误区，都必须回馈到相关skill：

```bash
# 每发现一个重复踩坑 → 记录到对应skill的陷阱列表
# 例：SCC论文发现模型RMSE > 生物信号时不适用
hermes skill patch quality-gate \
  --add-pitfall "模型RMSE不应大于待测生物信号量级"
```

**无需用户提醒**：发现问题→skill patch在P6阶段一次性完成。

### P6c: 喂入进化引擎

将论文的进化数据（周期数、评分变化、关键转折点）记录到 `evolution` 中：

```bash
# 记录论文作为一次进化周期
evolution record-cycle \
  --paper "membranous-scc-reconstruction" \
  --cycle-vitals "v1→v3: 校准分0.79→0.81, G5d加入质量门" \
  --new-skills "0 (G5d门已注入quality-gate)" \
  --skills-patched "quality-gate, dual-quality-check-v2, paper-pipeline" \
  --exit-criteria "投稿包就绪+技能已提炼"
```

### P6d: 同步到OpenCode规则（如适用）

如果提炼的技能涉及编码实践（文件命名、实验管线、数据管理），同步到 `.opencode/rules.md`：

```bash
echo "- $(basename $paper_dir): $(提炼的技能摘要)" >> .opencode/rules.md
```

### 执行清单（P6退出条件）

- [ ] 提炼了≥1个可复用技能（新skill或skill更新）
- [ ] 所有新发现的陷阱已patch到相关skill
- [ ] 研究空白已写入 `09-background/SCC-Research-Gaps.md`
- [ ] 论文的进化周期已记录
- [ ] 下一轮的起点已明确（G1-G7中哪个先做）

### 与现存skill的关系

| Skill | 在P6中的角色 |
|:------|:-------------|
| `project-experience-distillation` | **主执行者** — 从经验到skill的标准流程 |
| `evolution` | **收数据** — 接收论文进化周期记录 |
| `quality-gate` | **被修补** — 吸收新陷阱 |
| `dual-quality-check-v2` | **被修补** — 吸收新检查项（如G5d） |
| `paper-pipeline`（自身） | **被修补** — 吸收新阶段/新流程 |

## P5: 手稿反馈分类与验证（Manuscript Feedback Triage）

> 当收到审稿人/同行/用户的书面反馈（word文档、邮件、评审意见表）时，不能直接照单回复。必须先逐条**溯源验证**——将每条反馈映射到源文件（.tex行、.bib条目、数据文件、代码输出），交叉核对其数值和声称，然后给出分级的修复方案。

### 核心流程

```
收到反馈文档
  ↓
Step 1: 反馈分类
  ├── 🔴 数据/代码问题（RMSE矛盾、引用不可用、数据源错误）
  ├── 🟡 表述问题（术语混用、描述不准确、fig caption不完整）
  └── 🟢 格式/风格问题（优化项）
  ↓
Step 2: 逐条溯源
  ├── 数值声明 → 查 .tex / Table / Figure caption / 数据CSV
  ├── 引用声明 → 查 references.bib + ref-pdfs 内容是否匹配
  └── 方法声明 → 查代码管线是否实际产生声称的输出
  ↓
Step 3: 交叉验证
  ├── 摘要RMSE → Fig 1 RMSE → Table 2 RMSE → 原始数据CSV 四步一致？
  ├── |b|值 → |b| from CT vs uCT vs 3-specimen micro-CT 三数据源一致？
  └── Fig caption 描述 → 实际figure内容一致？
  ↓
Step 4: 产出
  ├── 每条的核实状态（✅已修复 / 🟡需验证 / ❌确认问题）
  ├── 优先级标签（P0/P1/P2/P3）
  └── 具体修复操作（改.tex行、换术语、补充数据来源说明）
```

### 交叉验证规则表

| 检查类型 | 操作方法 | 正确条件 |
|:---------|:---------|:---------|
| RMSE跨段一致 | 摘录Abstract/§Results/Table/Fig caption中的RMSE值→逐一比对 | 只有一种模型（对数螺旋）的RMSE应在0.07-0.17；其他模型的值可不同但需明确标注 |
| | b值跨数据源 | 从 uct_vs_ct_stats.txt 提取CT/uCT/MRI的mean b和|b| → 与Table中的mean |b|验证 | b有正负，|b| < 0.1 正常；若mean b与|b|差异大，说明正负号抵消，属正常 |
| 数据集称呼 | 全文grep "micro-CT\\|µCT\\|uCT\\|high-resolution" → 标注每个出现位置对应的数据集 | 三个数据集各有统一种呼，不在同一段混用 |
| Fig数据来源 | 检查Fig生成代码 → 确定数据来自本文还是文献 | 若为文献数据，caption必须标明来源引用 |
| 引用真实性 | 核实「in preparation」/「unpublished」条目 → 必须在.tex中无\cite | 零容忍。未发表作品不能作为引用 |
| 术语统一 | 检查全文对同一对象是否用同一名词 | Dataset 1 ≠ Dataset 3，不应都叫micro-CT |

### 实战案例：SCC论文6问题分类

完整案例见 `references/manuscript-feedback-triage-example-scc.md`，这里摘要优先级模式：

| 优先级 | 发现类型 | SCC论文示例 | 修复操作 |
|:------:|:---------|:------------|:---------|
| 🔴 P0 | 数据管线一致性 | 两套拟合混用（已验证当前v4无此问题） | 全管线重跑验证 |
| 🔴 P0 | 数据集描述不清 | Dataset 1的3标本是各自1种模态，非3种模态 | §2.1加一句澄清 |
| 🟡 P1 | 术语未统一 | Dataset 1/3都被叫 "micro-CT" | 分用不同名称 |
| 🟡 P1 | Fig caption缺失数据来源 | Fig 4C未标注SCC/耳蜗数据来源 | caption加引用标注 |
| 🟡 P1 | Fig描述与实际内容偏差 | Fig 1 caption说"6种模型"但Fourier系列未在图中 | caption加排除说明 |
| 🟢 P2 | 数值澄清 | Abstract 0.07-0.17 vs Fig 1 0.271（非Log Spiral的值） | 加一句话明确 |

### 黄金原则

1. **数值声明三地一致**：Abstract/正文/Table中出现的同一模型同一指标，必须数值相同或明确说明差异原因
2. **数据源透明**：Fig中涉及的数据必须标注来源（本文实验 / 文献引用 / 混合对比）
3. **术语唯一**：全文对同一对象使用同一名称
4. **引用可验证**：所有引用的文献必须在 .bib 中有条目，且非 "in preparation" / "unpublished"
5. **不改对响应**：每条反馈给出「已核实 / 已修复 / 确认需修」的明确判定，不回避不掩盖

### 参考文件

- `references/manuscript-feedback-triage-example-scc.md` — SCC论文6问题的完整溯源过程与修复方案
- `references/openml-benchmark-insights.md` — OpenML论文研读要点（Feurer2025）：标准化拆分防泄漏 + 泄漏在OpenML上仍存在 + 基准套件引用方法。2026-06-04 Pima论文吸收实战。

10. **🔴 L0.5 数据诚实门**
- **代码审查先于代码运行**: 即使 `experiment/*.json` 文件已存在，也要先审查代码逻辑再运行。HCS-3WT代码发现3个bug（变量名错误、SMOTE应用到错误子集、FN计算指向最后一个模型）。
- **叙事重定位**: 当实验数据不支持论文预期时，不要强行解释。把叙事从「错误减少」转向「不确定性集中」，更诚实且对临床场景更有意义。
- **🔴 将文献观察称为「发现」(Experimental Claim vs Literature Observation)**: 2026-05-28 SCC论文实战教训——3D对数螺旋拟合发现螺旋率|b|=0.03-0.10后，论文写了「discovery that SCCs and cochlea share a common spiral growth class」。但**我们没有分析耳蜗，这个「重叠」是引用Manoussaki2008的文献观察，不是实验发现。** 用户指出后修正了6处措辞。
  | 声明类型 | 允许措辞 | 禁止措辞 |
  |:---------|:---------|:---------|
  | 自己的实验/拟合数据 | 我们发现、我们的结果显示 | — |
  | 文献中引用的数值 | 文献报告、据X报道、与文献值一致 | 我们发现、这是一个发现 |
  | 基于文献比对的推论 | 提出假设、推测、一致的可能性 | 证实、揭示、这证明 |
  **执行检查**：L0.5数据门增加「声明分类」步骤——提取所有带发现/discovery/揭示/reveal的句子，逐一问：基于我们的数据还是文献引用？文献引用类一律降级。只有拟合/实验/代码直接输出的数值才能用发现。
