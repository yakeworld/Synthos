---
name: post-compile-dual-quality-check
description: "⚡ 论文编译后的自动双质量检查流程。编译成功→自动触发L0.5+L1-L4双质检。强制流程，不等用户问。"
version: 1.3.0
author: Hermes Agent
priority: P0
execution_rule: "论文编译成功后自动触发，不可跳过。先skill_view()加载quality-gate和sci-paper-quality-review确认可用。"
---

---

## 原理层·文言

> 「苟日新，日日新，又日新。」编成即检，不问即行。
> 「诚者，物之终始。」L0.5查数据之真伪，Layer A验引用之完备，Layer B审七维之高下。
> 不达标则修，修完再检。有患即除，不待下轮。# 论文编译后自动双质量检查

> 编译乃节点，不检不过。不待用户问，自修自证。
> **资料齐全再评** — D7引用评估前，必须先上传或检索导入参考文献全文。无全文的D7评分不可信。

## 触发条件

论文 LaTeX 编译成功（`Output written on paper.pdf` 出现）**后自动触发**，不等用户提问。

### 🔴 前置步骤：定位论文源文件（多仓库策略）

**致命陷阱：论文源文件可能不在默认路径。** 2026-05-27 Synthos paper 双质检实战发现

**🔴 预检：重复 bibliography** — 编译成功不等同于 bibliography 正确。必须检查 `\bibliography{}` 出现次数：`grep -c '\\bibliography{' paper.tex`。若 ≥2，先删除靠前的重复组（只保留 `\end{document}` 前那一组），清空 .aux/.bbl，重新运行完整编译链（pdflatex → bibtex → pdflatex × 2）后再继续后续质检。详见 `paper-pipeline` skill 的陷阱 #11 和 `references/duplicate-bibliography-fix-2026-05-30.md`。

在执行任何质检步骤前，必须检查以下所有位置的论文目录：

```bash
# 检查候选路径
for dir in \
  /home/yakeworld/Synthos/outputs/papers \
  /media/yakeworld/sd*/Synthos/outputs/papers \
  /home/yakeworld/桌面/article_todo; do
  [ -d "$dir" ] && echo "📁 $dir ($(ls -d "$dir"/*/ 2>/dev/null | wc -l) 篇)"
done
```

若论文未在本地找到，检查 NotebookLM：
- `b54348f4` = Synthos系统论文笔记本（含完整 LaTeX + PDF + 已编译质检报告）
- `460fbd4c` = Synthos 论文库 (papers-md, 8篇Markdown版)

**定位优先级**：
1. `/media/yakeworld/sda2/Synthos/` > `~/Synthos/`（sda2 包含完整 evolution 数据和 CONSTITUTION）
2. 若本地存在，优先使用本地文件（可编译、可追溯进化数据）
3. 若仅 NotebookLM 有，下载 fulltext → 保存本地 → 修复格式（`\cite` 反斜杠常缺失）

### 修复 NotebookLM 下载的 LaTeX 格式

NotebookLM `source fulltext` 提取的 LaTeX 会丢失反斜杠（`\cite{...}` → `cite{...}`）。下载后必须修复：

```bash
# 用 sed 批量恢复常用 LaTeX 命令的反斜杠
sed -i 's/^cite{/\\\\cite{/g; s/^section{/\\\\section{/g; s/^subsection{/\\\\subsection{/g' paper.tex
# 或使用更全面的 Python 正则修复（见实战教训）
```

### 检查已有质检报告

重复执行质检前，先检查论文目录下是否已有 `quality-report.md`：
```bash
ls paper-dir/quality-report.md 2>/dev/null && echo "⚠️ 已有质检报告，确认是否覆盖"
```
若已有报告，比较版本号或问用户是否重新运行。

## L0.5 数据诚实门 — 逐条验证

## Cron/Offline 模式（Layer B 不可用时）

当运行在 cron 上下文或无 NotebookLM 认证时，Steps 3-4（NotebookLM 上传 + Layer B Gemini 评审）**不可执行**。不要阻塞或重试——直接跳过它们：

```
论文编译成功
  ↓ 自动触发
Step 1: L0.5 数据诚实门          ← 必做
Step 2: Layer A 本地7维评审       ← 必做
Step 3+: NotebookLM 不可用 → 跳过
Step 5: 仅用 Layer A 判定         ← 校准分 = Layer A 分（无 Layer B 可 min）
Step 6: 产出双质检报告            ← 标注 "Layer B: N/A (offline mode)"
```

**判定规则**（无 Layer B 时）：
| Layer A 平均分 | 判定 | 行动 |
|:--------------:|:-----|:-----|
| ≥0.85 | T1 PASS | 标记完成 |
| ≥0.80 | T2 PASS | 标记完成 |
| ≥0.75 | T3 PASS | 标记完成 |
| <0.75 | FAIL | 修订循环 |

**报告格式变体**：在双质量校准表中，Layer B 列填写 "N/A (cron/offline)"，校准分列直接取 Layer A 值。添加备注："Layer B 未执行——NotebookLM 在 cron 上下文中不可用。校准分退化为 Layer A 单一评分。下周期有 NotebookLM 时补 Layer B。"

**交叉引用**：此降级策略由 `autonomous-core-researcher` skill 的 Step 2b 节授权（"若 NotebookLM 不可用，仅做 Layer A 本地评审并在报告中标注 'Layer B: N/A'"）。post-compile-dual-quality-check 是本策略的技术执行者。

## 强制流程

```
论文编译成功
  ↓ 🔴 铁律: 先 L0.5，再报任何结果
  Step 1: L0.5 数据诚实门
    提取论文中所有数值声明 → 追溯源文件
    └─ 无源代码的实验值（ensemble/voting/ablation）→ 必须写实验代码跑出真实值
  ↓ 通过后
  Step 2: Layer A 本地7维评审
    基于实际读到的 paper.tex 逐维评分
  ↓ 完成
  Step 3: 上传PDF到NotebookLM
    notebooklm source add paper.pdf
  ↓
  Step 4: Layer B Gemini 7维评审
    notebooklm ask "7维SCI评审，每维0-1，【必答】给修复建议"
  ↓
  Step 5: 校准与判定
    校准分 = min(Layer A, Layer B)
    校准分 ≥ 阈值 → PASS
    校准分 < 阈值 → 自动进入修订循环
  ↓
  Step 6: 产出双质检报告
    写入 paper-dir/quality-report.md
```

### 🔴 铁律：编译后先做 L0.5，不先报结果

编译成功后，**必须先执行 L0.5 数据诚实门，再向用户报告任何结果**。
不得出现以下模式：
  1. 编译成功 → 报"24页/0错误" → 用户问"数据都检查了？" → 才做 L0.5
  2. 编译成功 → 直接进入 Layer A/B → 跳过 L0.5

正确模式：
  编译成功 → L0.5 审计 → 报告（含 L0.5 结果）→ 继续 Layer A/B

用户问"所有的实验数据都经过检查了吗？"说明 L0.5 未执行或执行不充分。
这是触发条件本身的问题，不是用户额外要求。

## 执行细则

### 🔴 前置验证：进化数据直查（替代信任论文自述）

**致命陷阱：论文中的进化/性能声明必须从源文件验证，不可信任论文自述。**
2026-05-27 Synthos paper 实战：论文声称 composite score 0.982，但 evolution/_INDEX.md 记录 95/100（偏差 0.032），evolution-state.json 无 0.982 字段。此偏差未被任何一轮评审发现。

**验证清单**（执行 L0.5 前先跑）：

| 声明 | 源文件 | 验证命令 |
|:-----|:-------|:---------|
| 进化周期 | `evolution-state.json` | `python3 -c "import json; print(json.load(open('evolution-state.json'))['evolution_count'])"` |
| 引擎版本 | `evolution-state.json` | `python3 -c "import json; print(json.load(open('evolution-state.json'))['engine_version'])"` |
| 原子分数 | `evolution-state.json` → `quality_metrics.*.trust_score` | `python3 -c "import json; d=json.load(open('evolution-state.json')); [print(k,v['trust_score']) for k,v in d.get('quality_metrics',{}).items()]"` |
| 综合评分 | `evolution/_INDEX.md` | `grep -oP '\d+/\d+|\d\.\d{3}' evolution/_INDEX.md` |
| 吸收数量 | `evolution-log.md` | `grep -c '吸收\|吸收' evolution-log.md` |
| 论文产出 | `outputs/papers/` | `ls -d outputs/papers/*/ 2>/dev/null \| wc -l` |

**进化数据优先搜索路径**：`/media/yakeworld/sda2/Synthos/` > `~/Synthos/`

### Step 1: L0.5 数据诚实门

```bash
# 提取论文中所有数值声明
grep -oP '[\\d]+(\\.[\\d]+)?%' paper.tex | sort -u
# 对每个数值追源代码输出
# 格式：数值 → 源文件路径 → 行号
```

### 🔴 L0.5 子检查：形态学/解剖学论文的特殊处理（2026-06-01 新增）

**情景**：论文是形态学/解剖学测量研究（如半规管3D重建、角度测量），数据来自影像分割软件（Avizo、3D Slicer、VMTK），而非可执行的实验代码。

**与实验论文的区别**：

| 维度 | 实验论文 | 形态学论文 |
|:-----|:---------|:-----------|
| 03-code/ | 应有实验脚本 | 可能为空或仅有分析脚本 |
| 数据来源 | 代码运行输出 | 影像分割 `.mrk.json`/`.fcsv` 中心线文件 |
| L0.5验证 | 运行代码验证数值 | 检查 Table 数值 vs 原始测量数据一致性 |
| 统计推断 | 可做 t-test/ANOVA | n=1/模态时禁止推断统计，仅纯描述性 |

**L0.5验证路径**（形态学论文）：

```bash
# 1. 检查中心线数据文件是否存在
find . -name "*.mrk.json" -o -name "*.fcsv" 2>/dev/null | head -5

# 2. 验证 Table 数值与原始数据的一致性
# 例如：角度偏差 = arccos(n_MEM · n_BONY)
# 如果 Table 中有法向量，可以直接计算验证

# 3. 检查是否有校准误差分析
grep -n "registration\|calibration\|error" paper.tex | head -10

# 4. 检查统计推断是否适当（n=1时不应有ANOVA/t-test）
grep -n "ANOVA\|t-test\|p <\|p =" paper.tex
# 若找到 → 标注为不适当推断，需删除
```

**关键铁律**：n=1 per modality → 只做描述性统计（mean $\pm$ SD），不得使用 inferential statistics（ANOVA, t-test, p-value）。发现即修，不等用户问。

### 🔴 L0.5 子检查：实验数值必须有实验代码（2026-06-01 新增）

**致命陷阱：论文中的核心实验数值可能无任何源代码支撑，为 LLM 编造。**
2026-06-01 Pima CRISP-DM 论文实战：Voting Ensemble F1=0.7541 和消融实验全部数值均无对应实验代码，
benchmark 中实际最优模型仅 F1=0.6678，虚高 0.0842。

**触发条件**：论文包含以下任意一项时，必须执行此子检查：
- Voting / Soft Voting / Hard Voting 集成模型性能声明
- 消融实验 / Ablation Study 表格含多个场景的对比数值
- 声称"最佳集成模型"但无对应实验脚本
- 任何声称的 F1 ≥ 0.75（对 PIDD 等小数据集，真实 Helix 隔离 F1 不会超过 0.68）

**检查流程**：
```bash
# 1. 列出论文中所有实验数值
grep -oP 'F1[=:]\s*[\d.]+' paper.tex | sort -u

# 2. 对每个数值，确认对应的实验代码文件存在
#    格式：实验脚本 → 输出 JSON → 论文数值
#    若某数值无代码路径 → 必须标记为 LLM 编造

# 3. 特别检查 ensemble/voting 声明
grep -n 'ensemble\|voting\|Voting\|Ensemble' paper.tex
#    ensemble 必须有独立的 .py 文件产生该输出

# 4. 特别检查 ablation/消融声明
grep -n 'ablation\|Ablation\|No Leakage\|Severe Leak' paper.tex
#    ablation 表每一行必须有对应实验代码

# 5. 检查实验目录
ls 03-code/experiments/*.py  # 所有实验脚本
ls 03-code/experiments/*.json  # 所有实验输出
#    对比：论文中所有数值是否都能映射到一个 JSON 文件的具体字段
```

**发现无源文件数值时的处理流程**：
```
发现编造数值
  ↓
写实验代码（最少工作量：只跑论文声称的实验配置）
  ↓
运行实验 → 获取真实值 JSON
  ↓
对比真实值与编造值的差异
  ↓
更新论文 → 重新编译 → 重新 L0.5 验证
  ↓
保存实验代码+输出到 03-code/experiments/（痕迹保留）
```

**典型案例**（2026-06-01 Pima）：
| 论文声称 | 实验证实 | 偏差 |
|:---------|:---------|:----:|
| Ensemble F1=0.7541 | 0.6699 | -0.0842 |
| Ablation No Leakage F1=0.6759 | 0.6647 | -0.0112 |
| Ablation Severe Leak F1=0.7338 | 0.7290 | -0.0048 |
| GBC standalone F1=0.6857 | 0.6379 | -0.0478 |

**预防**：所有实验数值在写入论文前必须有对应的代码运行日志或 JSON 文件。
LLM 写作时倾向于为"听起来最好"的数值写句子——这是编造信号，不是优化目标。

### Step 2: Layer A 本地7维评分标准

| 维度 | 评分依据 | 证据要求 |
|:-----|:---------|:---------|
| D1 科学贡献 | Gap定位、贡献列表 | Introduction末段、贡献枚举 |
| D2 方法学严谨性 | 形式化定义、算法、CV协议 | Section 2、Algorithm块 |
| D3 结果可信度 | 表格数值可追溯、实验日志存在 | Tables、实验代码输出 |
| D4 完整性 | 所有IMRaD节存在、引用数 | 结构检查、引用计数 |
| D5 清晰性 | CARS模型、金字塔原理 | Introduction结构 |
| D6 新颖性 | 与已有工作的差异声明 | Related Work/Limitations |
| D7 引用质量 | 元数据完整性、自引率 | 每条bibitem检查 |

### Step 3: NotebookLM 上传（论文PDF + 参考文献PDF）

#### Step 3a: 上传论文PDF

```bash
# 删除旧版（如果有）
notebooklm source list | grep -i "paper" | head -1
# 上传新版
notebooklm source add paper.pdf --title "Paper v$VERSION"
```

#### Step 3b: 获取参考文献全文（⚠️ D7引用验证的关键前置条件）

**两种方式**：

**方式A（网页检索）：** 用 `notebooklm source add-research` 搜索参考文献**元数据**（从网页中提取引用信息）。注意：此方式导入的是**网页源文件**，**不是PDF全文**。适用于快速获取引用信息而非精确全文验证。

```bash
# 搜索论文信息（导入为网页源，非PDF）
notebooklm source add-research --mode deep --no-wait "PaperQA2 PubMedQA 99.3 percent accuracy Lala 2023"

# 等待检索完成
notebooklm research wait --import-all --timeout 300
```

**方式B（精确PDF上传）：** 维护 `notebooklm-sources.json` 清单 + `bibkey-map.json` 命名映射，避免重复上传：

使用配套脚本 `notebooklm-sources-sync.py` 实现：
```bash
python3 /media/yakeworld/sda2/Synthos/skills/notebooklm-sources-sync.py ./paper-dir/
```

**方式C（推荐：BibTeX→PDF管线）：** — 完整流程见 `notebooklm-cli` skill 的 `references/reference-pdf-workflow.md`
1. NotebookLM生成BibTeX元数据（含DOI/arXiv ID）
2. 用DOI/arXiv独立下载PDF到 `pdfs/{bibkey}.pdf`
3. 用bibkey命名上传到NotebookLM

配套工具：
- `notebooklm-cli/scripts/validate-pdfs.py` — PDF校验+命名规范
- `notebooklm-cli/scripts/upload-pdfs.sh` — 批量上传（可后台运行）

```bash
# Step 1: NotebookLM生成BibTeX
notebooklm ask "为每个源文件生成BibTeX条目，含DOI或arXiv ID"

# Step 2: 用arXiv ID下载PDF
wget -O pdfs/lala2023paperqa.pdf "https://arxiv.org/pdf/2305.00000.pdf"

# Step 3: 用bibkey命名上传
notebooklm source add pdfs/lala2023paperqa.pdf --title "lala2023paperqa"
```

**清单文件格式**（`notebooklm-sources.json`，存放于论文目录）：
```json
{
  "version": "1.0",
  "notebook_id": "b54348f4-...",
  "notebook_title": "论文标题",
  "last_synced": "2026-05-26T17:00:00",
  "sources": [
    {
      "local_path": "pdfs/Lala2023.pdf",
      "notebooklm_title": "Lala2023",
      "notebooklm_id": "2fd1b772-dfd8-...",
      "type": "pdf",
      "status": "ready"
    },
    {
      "notebooklm_title": "nature-skills GitHub",
      "notebooklm_id": "af6934fd-...",
      "type": "research",
      "status": "ready"
    }
  ]
}
```

**脚本自动完成**：
1. 读取本地 `pdfs/` 目录 → 获取所有PDF列表
2. 查询 NotebookLM 当前源文件 → 获取已上传清单
3. 比较 → 只上传缺失的PDF，跳过已有的
4. 更新 `notebooklm-sources.json` → 记录上传状态

**模板文件**：`outputs/papers/notebooklm-sources.template.json`

**如果pdfs/目录为空或PDF不全**（常见于付费期刊论文无法自动下载）：

在质量报告中标注：
```
D7参考全文验证：⚠️ 部分参考PDF未获取（pdfs/目录不全）
受影响的引用数：N篇
D7校准分置信度：降低30%——仅基于bib元数据的浅层评估
```
**上传范围**（不需要所有30+篇，但必须覆盖关键引用）：

| 优先级 | 参考文献类型 | 原因 | 示例 |
|:-------|:------------|:-----|:-----|
| **P0** | 论文中引用了**数值**的文献 | 验证数值真实性，防引用链传播 | baseline对比表(如EllSeg IoU 0.9618) |
| **P0** | 论文核心claim依赖的文献 | 验证claim是否准确反映原文 | "据X报告Y"类声明 |
| **P1** | Related Work中的核心引用 | 验证分类/归因是否正确 | "X属于方法A" |
| **P2** | 其余引用 | 可选，有则传 | — |

**操作流程**：

```bash
# 0. 确认bibtex_pdfs目录是否存在及可用PDF数量
ls bibtex_pdfs/pdfs/*.pdf 2>/dev/null | wc -l

# 1. 从论文中提取所有key引用——识别数值引用和core claim引用
#    方法：在results/discussion节中找伴随数值的引用
grep -nP 'cite[tp]?\{[^}]+\}.*\d+\.\d+' sections/results.tex sections/discussion.tex 2>/dev/null
grep -nP '\d+\.\d+.*cite[tp]?\{[^}]+\}' sections/results.tex sections/discussion.tex 2>/dev/null

# 2. 对每个关键引用key，查找对应PDF并上传
#    常用转换：bibkey → bibtex_pdfs/pdfs/bibkey.pdf 或 pdfs/bibkey.pdf
for key in kothari2021ellseg jia2024condseg palmero2021; do
  pdf_path=""
  for dir in "bibtex_pdfs/pdfs" "pdfs"; do
    [ -f "$dir/$key.pdf" ] && pdf_path="$dir/$key.pdf" && break
  done
  if [ -n "$pdf_path" ]; then
    notebooklm source add "$pdf_path" --title "$key"
    echo "✅ 已上传: $key.pdf"
  else
    echo "⚠️ 未找到PDF: $key.pdf — 在质量报告中标注为'参考全文未获取'，D7扣减0.05"
  fi
done

# 3. 等待所有source处理完成
notebooklm source list | grep -E "pending|processing"
# 若显示pending，等待几秒后重试
sleep 5
notebooklm source list
```

**如果pdfs/目录为空或PDF不全**（常见于付费期刊论文无法自动下载）：

在质量报告中标注：
```
D7参考全文验证：⚠️ 部分参考PDF未获取（pdfs/目录不全）
受影响的引用数：N篇
D7校准分置信度：降低30%——仅基于bib元数据的浅层评估
```

#### Step 3c: 验证source处理完成

```bash
notebooklm source list | head -20
```

> **为什么必须传参考文献全文？** — 没有参考文献PDF，Layer B 无法验证：
> - 论文中声称的数值（如"Method X achieves IoU 0.9618"）是否真的出自被引的原始论文？
> - 引用链传播错误（论文引用了原始论文A，但数值实际来自复现论文B的Table 2）？
> - 论文是否准确反映了所引文献的结论/贡献？
> - 筛选偏倚——论文是否故意忽略了与自己结果矛盾的文献？
> 
> **没有全文，D7 评分就是凭标题和摘要猜，不可信。** 2026-05-26 Synthos论文实战已验证：PaperQA2声称99.3%实际仅86.3%（Lala2023.pdf），nature-skills stars 5,625→12.3k（GitHub检索），外部对比表全为虚构数据。

### Step 4: G5d 空假一致性检查（前置门）

> 🔴 新增：Layer B前必须执行G5d空假一致性门。验证论文的gap/hypothesis相对于关键参考文献的定位正确性。

详见 `quality-gate` skill 的 `references/gap-hypothesis-congruence.md`。

通过条件：
- ✅ 全部关键文献定位正确 → 直接进入Layer B
- 🟡 1-2篇贡献声明略强 → 降级措辞后进入Layer B
- 🔴 gap已填/contribution冲突 → 先修订论文再进入Layer B

### Step 5: Layer B Gemini 7维评审（含引用全文交叉验证）

**🔴 硬闸门：D7评分前必须已上传≥3篇参考文献PDF**
```bash
# 检查是否有参考PDF已上传（排除论文PDF自身）
ref_count=$(notebooklm source list | grep -c '\.pdf')
paper_count=$(notebooklm source list | grep -c 'synthos-paper\|paper.pdf')
if [ $((ref_count - paper_count)) -lt 3 ]; then
    echo "🔴 硬闸门拦截：参考文献PDF不足（需≥3篇，实际仅$((ref_count - paper_count))篇）"
    echo "   D7评分无法执行——无全文则无验证"
    echo "   请先执行 Step 3b 上传/检索参考文献"
    echo "   强制跳过标记：quality-report.md中D7=[不可信，需重评]"
fi
```

```bash
notebooklm ask "请对论文进行7维SCI质量评审（0-1分）：
1. D1 科学贡献
2. D2 方法学严谨性
3. D3 结果可信度
4. D4 完整性
5. D5 清晰性
6. D6 新颖性
7. D7 引用质量

**【🔴 引用全文验证——必答】** 我已在NotebookLM中上传了论文PDF和部分关键参考文献的PDF作为源文件。请在评估D7时：

1. **数值核对**：论文中每次声称'Method X achieves metric Y'并引用了某文献时——检查该文献的PDF中是否真的包含这个数值
2. **引用链传播检测**：检查是否存在论文引用了原始论文A，但数值实际来自复现论文B的Table 2
3. **归因准确性**：检查论文是否准确反映了所引文献的结论（而非断章取义或过度推广）
4. **覆盖完整性**：检查论文遗漏了哪些必须引用的关键文献
5. **对每个发现的引用问题，指明：** 论文中的哪个声明 → 引用了哪个key → 参考PDF中实际内容是什么

**【必答】评分<0.80的维度，给出具体可操作的修复方案。**"
```

### 分段中心线数据修复

当ICT数据中膜性半规管被分为两段标注(AC_MEM1/2, PC_MEM1/2):

1. 端点分析: 两段共享相同终点(中点)说明从两端向中点标注
2. 合并: `merged = np.vstack([seq1, seq2[-2::-1]])`
3. 验证: 合并间隙<0.2mm, 端点与源数据一致
4. 更新gen_composite_figure.py和fit_all_three.py使用合并文件
5. 重新拟合后对比: 分段数据产生伪b值(0.5或-0.9), 合并后回到正常(0.01-0.2)
6. 同步更新论文Table 1中受影响参数范围

### Step 5: 校准与判定

#### 🔴 铁律：不得提问，立即修订

> **2026-05-28 实战教训**：校准分0.791(<T2阈值0.80)时，Agent报了分然后问"要不要现在动手"——这是错的。必须一条消息内完成：报分 + 判定 + 初始修订计划。不得分两步走。

**强制执行规则**：
1. 校准分计算完成后 **立即** 与阈值比较
2. 校准分 < 阈值 → **不得提问用户** → **立即进入修订循环**
3. 修订计划必须与质量报告在同一消息中给出
4. 只有在校准分 ≥ 阈值时，才可询问用户是否继续提升

**格式模板**（一条消息内完成）：
```markdown
## 双质检结果
校准平均分: 0.791 (T3通过, T2未过)

## 自动启动修订轮次 #1
薄弱维度: D7引用质量(0.72) — 补参考文献19→35篇
具体计划: 搜索发育生物学文献12篇 + 跨物种文献3篇 + ...
```

**违反后果**：分两步走（先报分等回复 → 再修）消耗用户注意力，被用户批评"阈值判断又没有调用"。

---

校准分 = min(Layer A, Layer B)，**但有以下例外**：

| 场景 | 规则 | 原因 |
|:-----|:-----|:------|
| D5 < 0.80 且 PDF提取伪影已确认 | 取 Layer A 的 D5 分 | NotebookLM PDF伪影导致假阳性 |
| D7 < 0.80 且原因仅为 "et al." 截断 | 取 Layer A 的 D7 分 | elsarticle-num.bst 默认行为，非错误 |
| 其他维度 | min(Layer A, Layer B) | 标准规则 |

### Step 4.5: 验证方法论调研（🔴 系统/架构论文必做）

当被评审论文是系统描述类（描述AI/架构/框架而非实验发现），且D3（结果可信度）存在以下情况之一时，必须执行此步骤：

**触发条件**：
- D3 < 0.80 且原因是"缺乏外部对比"或"只有内部指标"
- 论文原本有虚构的外部对比表（已被删除）
- 论文声称"我们比现有系统更好"但无实验证据

**方法**：利用已上传的参考文献PDF，用 NotebookLM 查询同类论文的验证方法论：

```bash
notebooklm ask "在NotebookLM的源文件中，有AI Scientist、PaperQA等论文。请分析这些论文如何验证系统性能：
1. 每个系统用什么指标/基准？
2. 用什么对比基线？
3. 是否使用人工评估？样本量(N)是多少？
4. 是否有外部第三方基准？
5. 是否报告了局限性？"
```

**将调研结果应用于论文**：

| 常见场景 | 参考论文做法 | 推荐行动 |
|:---------|:------------|:---------|
| 论文有虚构对比数据 | AI Scientist 无同类系统可比 → 跨模型对比 | 删除虚构数据，用**真实管线产出**作验证 |
| 论文只有内部指标 | PaperQA 自建评估基准(LitQA 50问) + 人工基线 | 用已有的管线论文质量分数做统计分布表 |
| 论文声称架构创新 | 所有系统论文都报告局限性 | 引用局限性部分说明"缺乏外部对比是普适挑战" |
| 论文缺引用 | AI Scientist 诚实报告自己的Bug和失败 | 保持诚实声明，不隐瞒局限性 |

**关键原则**（从 AI Scientist 和 PaperQA 论文验证）：同类系统论文的D3验证通常使用：
1. **内部指标**（如进化曲线、基准通过率）— Synthos有48 cycles/0.98 composite ✅
2. **跨模型/跨配置对比**（不同LLM基座对比）— 非虚构跨系统对比
3. **自建评估基准**（如PaperQA的LitQA）— 双质检分数就是你的自建基准
4. **诚实报告局限性** — AI Scientist 详细报告了高成本/代码Bug/幻觉
5. **不需要虚构数据** — 没有同类端到端系统可比较是行业常态

**实战案例**（2026-05-26 Synthos论文）：删除了虚构的N=30对比表（Citation F1 78.3%±2.15%, p<0.01），替换为**22篇管线论文的真实质量分布**（6 T1, 10 T2, 均分0.812）。同时引用AI Scientist自身"无同类系统可比较"的声明作为方法论锚点。

**验证步骤**：
```bash
# D5伪影验证
grep -rn "acting\|re﹨u001de x\|speci﹨u001ccity\|direntiating\|﹨u001celd" sections/*.tex paper.tex 2>/dev/null
# 若无匹配→伪影确认
# D7 "et al." 验证
grep -c "et al" references.bib  # 确认是否为.bst默认截断
```

| 校准平均分 | 判定 | 行动 |
|:----------:|:-----|:-----|
| ≥0.85 | T1 PASS | 可投顶刊 |
| ≥0.80 | T2 PASS | 可投高水平期刊 |
| ≥0.75 | T3 PASS | 可投标准期刊 |
| <0.75 | FAIL | 自动修订循环 |

### Step 8: P6 技能提炼与进化触发

当校准分 ≥ 阈值（PASS判定）后，自动触发：

1. 提炼可复用技能（使用 project-experience-distillation skill）
2. 记录进化周期
3. 研究空白写入论文 09-background/（P2阶段已完成）

详见 paper-pipeline 的 P6 节。

### Step 9: 产出最终双质检报告

校准分 < 阈值 → 自动进入修订循环，不等用户问。

### Step 7: 自动 D7 引用元数据修复（新增）

双质检报告生成后，若 D7 < 0.80 且原因涉及客观引用元数据错误，**不等用户确认，直接修复**：

| D7扣分原因 | 自动修复动作 |
|:-----------|:------------|
| 重复DOI | `grep -oP 'doi\s*=\s*\{[^}]+\}' refs.bib \| sort \| uniq -d` 找出重复 |
| 期刊-DOI前缀不匹配 | 检查DOI前缀（10.1109/=IEEE, 10.1016/=Elsevier, 10.1155/=Hindawi）与期刊出版商是否一致，不一致则移除后补充正确DOI |
| 缺失DOI | 根据论文作者+标题查找补充 |
| PDF文件与bib条目不符 | 用 `pdfinfo` 检查文件元数据，若标题/作者不匹配则删除 `file=` 行 |

**检测和修复流程**：

1. **找出重复 DOI**：
```bash
# 找到所有使用相同DOI的条目
grep -oP 'doi\s*=\s*\{[^}]+\}' reference4.bib | sort | uniq -d
# 输出示例: doi={10.1016/j.imavis.2009.03.003} — 如果出现在两个不同条目中，就是错误的
```

2. **确认哪个条目的 PDF/DOI 匹配错误**（实战案例：`wang2002study` vs `proencca2010iris`）：
```bash
# 对比两个PDF的元数据，确认哪个文件是错的
pdfinfo bibtex_pdfs/pdfs/wang2002study.pdf | grep -E 'Title|Author'
pdfinfo bibtex_pdfs/pdfs/proencca2010iris.pdf | grep -E 'Title|Author'
# 如果两者输出完全相同（同一篇论文），则其中一个PDF文件放错了
# 修复：删除错误条目的 file= 行和错误的 doi= 行
```

3. **期刊-DOI前缀不匹配检测**（实战案例：`li2019efficient` 期刊 Mobile Information Systems 但 DOI 前缀为 10.1109/，属于 IEEE）：
```bash
# 从bib中提取条目名和DOI
grep -B2 -A6 'doi\s*=\s*{10\.1109/' reference4.bib | grep -E 'journal|booktitle'
# 如果 journal 不是 IEEE 出版物（如 Mobile Information Systems, Hindawi），则 DOI 贴错了
# 因为 10.1109/ 前缀属于 IEEE Xplore，只匹配 IEEE 期刊/会议
# 正确的 Hindawi DOI 前缀是 10.1155/
```

**DOI前缀速查表**：
| 前缀 | 出版商 | 匹配期刊/会议 |
|:-----|:-------|:-------------|
| 10.1016/ | Elsevier | Image and Vision Computing, Biomedical Signal Processing and Control 等 |
| 10.1109/ | IEEE | IEEE Trans., ISMAR, CVPR 等 |
| 10.1155/ | Hindawi | Mobile Information Systems 等 |
| 10.1007/ | Springer | LNCS, Machine Vision and Applications 等 |
| 10.1038/ | Nature | Nature MI, Scientific Reports 等 |

4. **修复后重新编译**：
```bash
bibtex article20250830 2>&1  # 确认无错误（特别注意 bibtex 不支持 % 注释）
pdflatex article20250830     # 两次编译确保引用解析
pdflatex article20250830
```

**🔴 BibTeX 陷阱：注释行（%开头）在 bib 条目内会导致解析失败**
```bibtex
% ❌ 错误——BibTeX 会把 % 当作条目的一部分，导致解析错误
@Article{wang2002study,
  author = {Wang, J. and Sung, E.},
  % NOTE: DOI needs verification ← 这行会触发 bibtex 报错
}
```
BibTeX 不像 LaTeX 那样支持条目内的注释。所有注释必须放在条目**外部**：
```bibtex
% ✅ 正确——注释在条目外部
% NOTE: DOI needs verification
@Article{wang2002study,
  author = {Wang, J. and Sung, E.},
}
```

**修复后**：重新编译（bibtex + pdflatex×2）→ 重新上传PDF到NotebookLM → 重新做Layer B评审确认D7已修复。

**注意**：此步仅限于**客观元数据错误**（重复DOI、期刊-DOI不匹配、缺失DOI、文件错配）。不涉及引用覆盖度、自引率等主观判断。
# 双质量检查报告
## 论文：[标题]

### L0.5 数据诚实门 ✅/❌
逐条列出声明验证状态。

### 双质量校准

| 维度 | Layer A | Layer B | 校准分 |
|:-----|:-------:|:-------:|:------:|
| D1 | X.XX | X.XX | X.XX |
| ... | ... | ... | ... |
| **平均** | **X.XX** | **X.XX** | **X.XX** |

### 期刊感知判定
- T2 (≥0.80): ✅/❌
- 修订决策: PASS/循环
```

### 🔴 致命陷阱：D7评估无参考文献全文 = 盲猜（2026-05-26 实战验证）

**症状**：仅上传论文PDF到NotebookLM，未上传或搜索导入参考文献全文，Gemini评估D7评分时只能看参考文献标题和摘要。这会导致：

- **引用数值捏造**：论文声称"PaperQA2 achieves 99.3% on PubMedQA"，实际参考PDF显示PaperQA achieves 86.3% — 评分0.95 vs 真实0.50
- **引用链传播错误**：论文引用了原始论文A，但数值实际来自复现论文B
- **归因混淆**：论文将Constitutional AI的RLAIF方法与本身的符号层级混为一谈，无参考PDF无法发现
- **漏引奠基文献**：论文自称"认知操作系统"但不引用SOAR/ACT-R

**影响**：无参考PDF的D7评分平均虚高0.20-0.30，且会连带降低D3（结果可信度）的信任度——一处引用捏造会导致审稿人全盘否定所有定量结果。

**预防**：D7评估前必须执行Step 3b，可通过 `add-research` 检索导入或手动上传参考PDF。

实战案例参见 `references/d7-citation-verification-case-synthos.md`——该案例详细记录了参考PDF发现D7问题导致校准分从0.81降至0.74的完整过程。

### 🔴 `add-research` 研究检索可能超时（2026-05-26 实战）

当使用 `notebooklm source add-research --no-wait` 启动多个研究任务时：
- `research wait --import-all` 可能超时（deep research需要60-180秒）
- 超时后部分任务的状态可能卡在"completed"但"Add sources?"弹窗未确认
- `research status` 本身也可能超时

**缓解**：
1. 对每个研究任务单独 `research wait --import-all` 而非一次性等待所有
2. 设置 `--timeout 300`（默认1800可能太长）
3. 如果超时，手动检查：`notebooklm source list | grep -i <topic>` 确认是否已导入
4. 备选方案：直接上传PDF（方式B）——更可靠但更慢
5. 关键数值核对应优先使用方式B（上传PDF），星数等生态数据可用方式A（检索）

### 🔴 .tex文件操作陷阱：patch工具双转义 + read_file/write_file行号污染

这是修改LaTeX文件时最常犯的错误，两种路径皆可破坏.tex文件：

**路径A：patch工具双转义** — 当patch的新字符串中包含`\textbf`、`\begin{tikzpicture}`等LaTeX命令时，patch工具会将其转义为`\\textbf`、`\\begin{tikzpicture}`（多一层反斜杠）。当写入文件后，LaTeX编译报`Missing \begin{document}`。

**预防**：每次patch后立即验证：`sed -n 'LINE' paper.tex | od -c | head -1`，检查反斜杠数量。单反斜杠应为`\   b   e   g   i  n`；双反斜杠为`\   \   b   e   g   i  n`。若发现双反斜杠，在execute_code中用Python修正而非sed修补：若发现`\\textbf`，执行：
```bash
sed -i 's/\\\\textbf{/\\textbf{/g; s/\\\\section{/\\section{/g; s/\\\\begin{/\\begin{/g; s/\\\\end{/\\end{/g}' paper.tex
```

**路径B：execute_code中read_file→write_file行号污染** — 当使用Python的`read_file()`读取.tex文件时，返回的内容包含行号前缀（如` 139|Most notably...`）。若将其直接`write_file()`回写，文件被污染为：
```
 139|   139|Most notably...
```
编译报`Missing \begin{document}`，文件体积增大10-15%。

**修复**：
```bash
sed -i 's/^[[:space:]]*[0-9]*|//' paper.tex
```
然后检查git是否跟踪该文件（若跟踪则`git checkout paper.tex`更高效）：
```bash
git ls-files paper.tex && git checkout paper.tex
```

**预防**：编辑LaTeX文件优先使用`execute_code`中的纯Python字符串操作（open/read/write而非read_file/write_file），或使用`terminal`命令调用sed/patch。

### 🔴 TikZ+pgfplots 陷阱（2026-05-25 实战积累）

系统综述论文添加TikZ图时，以下5个陷阱会逐个出现：

**1. `%`百分号在caption中触发"Runaway argument"**
症状：`! File ended while scanning use of \caption@xdblarg`
根因：caption中的`95\%`被patch工具转义为`95\\%`。LaTeX将`\\%`解析为`\` + `%`(注释符)，`%`注释掉剩余caption和`}`。
修复：用"95 percent"替代`95\%`；或修复反斜杠再编译。
预防：TikZ caption中避免`%`；若必须，patch后用`od -c`验证反斜杠为单层。

**2. TikZ坐标算术需`{...}`包裹（无calc库时）**
症状：`! Package pgf Error: No shape named (74 is known.`
根因：TikZ将`(74.3*0.06,0.35)`解析为节点坐标引用而非算术。
修复：用`({74.3*0.06},0.35)`包裹算术。多重运算：`({(74.3+16.2)*0.04},2.2)`。
预防：所有涉及乘/加/除的TikZ坐标必须用`{...}`包裹。

**3. pgfplots用`ln()`而非`log()`求自然对数**
症状：`! Package PGF Math Error: Unknown function 'log'`
根因：pgfplots数学引擎的自然对数函数是`ln`。
修复：`log(x)` → `ln(x)`。
预防：pgfplots中自然对数用`ln`，常用对数用`log10`。

**4. `\foreach`中双重`{{`引发"Missing number"**
症状：`! Missing number, treated as zero.`
根因：`({{\x}*0.04},-3.7)`的双重`{{`被解析为嵌套问题。
修复：用`({\x*0.04},-3.7)`。
预防：`\foreach`坐标算术只用单层`{...}`包裹。

**5. `\foreach`内`%`仍是注释符**
症状：`\foreach`循环中文本被截断。
根因：`{\x\%}`中`\%`在循环上下文中被解析为`\`+注释开始。
修复：用"100 percent"替代`\x%`。
预防：TikZ节点文本中避免`%`。

**6. `label={[options]text_with_colon}`引发"Unknown function"**
症状：`! Package PGF Math Error: Unknown function 'Layer' (in 'Layer 3: Clinical Translation')`
根因：TikZ的`label`选项语法`label={[options]text}`中，如果`text`包含冒号`:`，TikZ将冒号解析为数学模式分隔符，试图将"Layer 3: Clinical Translation"整体解析为数学表达式。
修复：将label文本用额外花括号包裹，或将label文本写在`\node`内容中：
```latex
% 错误：
\node[layer, label={[above,font=\bfseries]Layer 3: Name}] at (0,0) {};
% 正确方案A：花括号包裹
\node[layer, label={[above,font=\bfseries]{Layer 3: Name}}] at (0,0) {};
% 正确方案B：裸\node作标签（更可靠，避免其他特殊字符问题）
\node[layer] (L3) at (0,0) {};
\node[above, font=\bfseries] at (0,0.5) {Layer 3: Name};
```
预防：涉及冒号、连字符、斜杠等特殊字符的标签文本，优先使用方案B（独立\node），而非`label`选项。多层架构图尤其容易出现此问题，因为节点名天然包含"Layer N:"等带冒号的标签。
实测：2026-05-25 pd-dysphagia-2026 v4架构图中，`\node[layer, label={[above,font=\bfseries]Layer 3: Clinical Translation}]`产生15个PGF数学错误。切换到方案B后0错误。

**7. TikZ PRISMA flow diagram: `\n` is NOT a LaTeX line break**
When writing PRISMA 2020 flow diagrams in TikZ, Python's `\n` newline escape does NOT work inside LaTeX/TikZ node text. Using `\\n` (or actual `\n` from Python multi-line strings) causes: `! Undefined control sequence` errors repeated for each node line.

**根因**: LaTeX's TikZ `\node` text does not recognize `\n` as a newline. The correct LaTeX line break inside TikZ nodes is `\\` (double backslash), combined with `align=center` and `text width=` styles.

**Fix**: Replace all `\n` in TikZ node text with `\\`:
```latex
% ❌ 错误——Python的\n在TikZ中无效
Records identified\\nthrough database\\nsearching

% ✅ 正确——LaTeX双反斜杠换行
Records identified\\\\through database\\\\searching
```
Requires `align=center` and a `text width=` / `minimum width=` style on the node.

**Detection**: grep for `Undefined control sequence` in paper.log. If all 16+ errors are in the TikZ figure section with `\n` in the argument, this is the root cause.

**Prevention**: Always use Python triple-quoted raw strings with explicit `\\` when constructing TikZ node text with line breaks. Never use `\n` inside TikZ code.

**8. TikZ calc library `$...$` syntax fails inside `\node at (...) {};` coordinates**
When using the calc library's interpolation syntax `$(A)!.5!(B)$` as a TikZ coordinate inside `\node at (...) {};`, LaTeX interprets the `$` as math mode markers, causing: `! Package PGF Math Error: Unknown function 'south'`, `! Missing \endcsname inserted`, `! LaTeX Error: \begin{document} ended by \end{figure}`.

**根因**: In `\node[box] at ($(id1.south)!.5!(id2.south)$) {};`, the `$...$` calc syntax collides with LaTeX's math mode. The `\node at (...)` coordinate is processed in LaTeX's coordinate parser, which doesn't expect math mode markers here.

**Fix 1 (preferred — absolute coordinates)**: Use explicit X coordinates instead of calc midpoints:
```latex
% ❌ 错误——calc语法在at-coordinate中失败
\node[box] at ($(id1.south)!.5!(id2.south)$) {...};

% ✅ 正确——显式绝对坐标
\node[box] at (0,-1.2) {...};
% Y坐标 = (id1.y + id2.y)/2 - node_height
```

**Fix 2 (calc with braces — when midpoint truly needed)**: Works on some tikz versions:
```latex
\node[box] at ({$(id1.south)!.5!(id2.south)$}) {...};
```

**Detection**: If paper.log shows both `! Missing \endcsname inserted` AND `! Extra \endcsname` AND `! Package PGF Math Error: Unknown function 'south'` simultaneously, the PRISMA flow diagram has a calc syntax issue.

**Prevention**: For PRISMA 2020 flow diagrams (which are simple four-level structures), always use absolute coordinates. The layout is standard and the Y positions are easily computed: Level 1 at y=0, Level 2 at y=-1.5, Level 3 at y=-3.0, Level 4 at y=-4.5, with identification/screening/eligibility/included labels in the left margin. This avoids all calc library issues entirely. See `references/tikz-systematic-review-templates.md` for a working PRISMA template.

**9. Figure/table environment balance verification after string replacement**
After any Python string replacement (`str.replace()`) that modifies TikZ figures or LaTeX tables, the environment counts can become unbalanced if the replacement boundaries are wrong. Leftover duplicate `\end{figure}` blocks cause cascading errors: `! LaTeX Error: \begin{document} ended by \end{figure}`, `! Too many }'s`, `! Extra \endgroup`.

**Prevention**: Before compiling, always verify:
```python
import re
figs = len(re.findall(r'\\begin{figure}', content))
end_figs = len(re.findall(r'\\end{figure}', content))
tabs = len(re.findall(r'\\begin{table}', content))
end_tabs = len(re.findall(r'\\end{table}', content))
algs = len(re.findall(r'\\begin{algorithm}', content))
end_algs = len(re.findall(r'\\end{algorithm}', content))
print(f"Figure: {figs}/{end_figs} {'OK' if figs==end_figs else 'MISMATCH!'}")
print(f"Table: {tabs}/{end_tabs} {'OK' if tabs==end_tabs else 'MISMATCH!'}")
```

**修复**: Count the extra `\end{figure}` lines and remove them. The extras are always at the boundary where the old content was replaced — look immediately after the new replacement for leftover original `\end{figure}` / `\caption` / `\label` lines.

**实战**: 2026-05-26 kappa-vor-calibration v2 — Python `str.replace()` left 2 extra `\end{figure}` + duplicate `\caption`/`\label` after the PRISMA insertion. Detected via `\begin{figure}=1, \end{figure}=3` mismatch check.

### 10. TikZ `font=` 选项中的 `\textcolor` 导致 brace 匹配错误

当在 TikZ 节点样式中用 `font=` 键设置文字颜色时，不要用 `\textcolor` 包裹文字：

```latex
% ❌ 错误——\textcolor 会消耗节点文本的 { 作为其参数
\node[right, font=\small\textcolor{red!80}] {Records excluded\\$(n = 556)$};
```

**根因**：TikZ 的 `font=` 键将后面的所有内容视为字体命令。`\textcolor{red!80}` 是一个带参数的 LaTeX 命令——它期望 `{text}` 作为参数。但在 `font=` 上下文中，`\textcolor{red!80}` 会消耗节点文本的起始 `{` 作为其第三个参数，导致 brace 不匹配。

**症状**：`! LaTeX Error: Something's wrong--perhaps a missing \item.` 发生在 `\end{tikzpicture}}` 处。PDF 虽然生成，但 TikZ 图渲染可能异常。

**修复**：使用 TikZ 的 `text=` 键而非 `\textcolor` 命令：
```latex
% ✅ 正确——使用独立的 text= 样式键
\node[right, font=\small, text=red!80] {Records excluded\\$(n = 556)$};
```

**检测**：如果 `paper.log` 中的 `Something's wrong--perhaps a missing \item` 错误恰好发生在 `\end{tikzpicture}}` 行，且 TikZ 节点使用了 `font=\small\textcolor{...}` 语法，则 99% 是此问题。

**预防**：在 TikZ 节点样式中，永远用 `text=<color>` 代替 `\textcolor{<color>}{...}`。

**实战**：2026-05-26 kappa-bppv-nystagmus v2 — PRISMA 流程图的排除数字标签 `\small\textcolor{red!80}` 导致 `\end{tikzpicture}}` 处 2 个非致命错误。修复为 `\small, text=red!80` 后通过。

### 11. 🔴 TikZ node text starting with `\n`/`\no`/`\non` after `\\` line break

When a TikZ node with `align=center` (or any node using `\\` line breaks) has text starting with `\n` after the break, LaTeX interprets `\n` as a control sequence command. This causes `! Undefined control sequence` errors that block PDF generation entirely.

**Root cause**: After `\\` (TikZ line break), LaTeX re-enters text mode. If the very next character is a backslash-triggered sequence, it's parsed as a command. `\n` is not a defined LaTeX command, so `no`, `non-PD`, `not-available` etc. all trigger "Undefined control sequence" starting with `\n`.

**Symptoms**:
```
! Undefined control sequence.
<recently read> \no
l.123 ...{Excluded(n=341)\\\no
                         calibration...
```

**Fix**: Use `\hspace{2mm}` or `\mbox{}` to protect the `n`:
```latex
% ❌ Error — \n interpreted as command
\node[box] (...) {Excluded (n = 341)\\\no calibration parameters};

% ✅ Fix A — \hspace before text
\node[box] (...) {Excluded (n = 341)\\\\hspace{2mm}no calibration parameters};

% ✅ Fix B — \mbox protection
\node[box] (...) {Excluded (n = 341)\\\mbox{}no calibration parameters};

% ✅ Fix C — rephrase to avoid n-initial word
\node[box] (...) {Excluded (n = 341)\\\\hspace{2mm}0 calibration reports: 156};
```

**All at-risk `\n`-prefix words** (after `\\` in TikZ node):
- `\no` (no, not, none, non-PD, normal)
- `\nu` (number, null)
- `\ne` (near, needs, never)
- `\ni` (nil, nine)
- `\na` (namely, named)

**Detection**: grep `\no` in paper.tex lines between `\begin{tikzpicture}` and `\end{tikzpicture}`:
```bash
grep -n '\\\\no\|\\\\non\|\\\\not\|\\\\nu' paper.tex | grep -A5 'begin{tikzpicture}' 
```

**Prevention**: In any TikZ PRISMA or flow-chart node text where a line after `\\` starts with a word beginning with `n`, prefix with `\hspace{2mm}` or `\mbox{}`. This is especially common in exclusion-category lists ("no calibration reported", "non-PD focus", "not relevant to topic").

**Related but distinct from pitfall #7**: 
- Pitfall #7 is about `\n` from Python's newline escape being embedded in TikZ code (`\\n` → `\` + `n` literal). 
- Pitfall #11 is about legitimate text after a `\\` line break starting with a word beginning with `n`, where `\n` is innocently part of the word but LaTeX treats it as a command. Both produce `! Undefined control sequence` but have different root causes and fixes.

**实战**: 2026-05-28 kappa-pd-calibration-artifacts v2 — PRISMA 流程图 `{Excluded (n = 341)\\\\no calibration parameters}` 触发 `! Undefined control sequence \\no`。修复为 `\\\\\\\\hspace{2mm}no calibration parameters` 后编译 0 错误通过.

### 13. pgfplots `\exp(\pgfmathprintnumber{\tick})` for log-axis labels (2026-05-26)

When displaying funnel plot DOR values on a log-transformed x-axis, use `xticklabel={$\exp(\pgfmathprintnumber{\tick})$}` to show the actual DOR values at log-spaced tick positions:

```latex
\begin{axis}[
    ...
    xticklabel={$\exp(\pgfmathprintnumber{\tick})$},
    ...
]
```

This renders tick labels like "0.14", "0.37", "1.0", "2.72", "7.39", "20.1", "54.6" corresponding to log(DOR) values -2, -1, 0, 1, 2, 3, 4.

**实战**: kappa-vor-calibration v4 — funnel plot with Egger's test annotation.

### 14. Yellow-filled annotation nodes on TikZ plots (2026-05-26)

For Egger's test p-value or other statistical annotations inside a pgfplots axis:

```latex
\node[draw, fill=yellow!10, rounded corners=2pt, font=\small] 
    at (axis cs:-0.5,5.5) {Egger's $p = 0.41$};
```

Note `axis cs:` coordinate system — must be used inside `{axis}` environment.

### 15. Float too large by Npt — resizebox reduction (2026-05-26)

When `pdflatex` reports "Float too large for page by NN.NNNNpt", reduce the `\resizebox{...\textwidth}` fraction. The float size scales linearly with the resizebox factor:

| Original | Float warning | Fixed to | Result |
|:---------|:-------------|:---------|:-------|
| `0.7\textwidth` | 79.17pt overflow | `0.55\textwidth` | 0 errors |

The warning does not affect PDF generation but may cause the float to appear on an isolated page. From kappa-vor-calibration v4 funnel plot fix.

**16. 🔴 `\\%` 在 pgfplots axis 选项中触发注释截断（2026-05-28 新增）**

### 17. 🔴 RMSE定义陷阱：Z分量 vs 全3D几何误差（2026-05-28 SCC论文实战）

当论文声称模型RMSE为0.08-0.16mm但视觉上曲线与数据明显不吻合时，检查RMSE计算方法：

**症状**：论文\u5b63称RMSE极小但肉眼可见拟合偏差大。

**根因**：常见的HSMM型模型（平面椭圆+正弦扭转）可能只计算了Z(out-of-plane)分量的拟合误差，忽略了平面椭圆本身0.7-1.5mm的几何误差。总3D RMSE = sqrt(平面误差² + Z误差²)，可能比声称值大3.5-6×。

**检测流程**：
```bash
# 提取论文中所有数值声明
grep -oP 'RMSE[=:]\s*[\d.]+' paper.tex | sort -u

# 对每个RMSE声明，回溯代码确认定义
grep -n 'rmse =' code/*.py
# 检查rmse计算是否只用了Z分量：
# rmse = sqrt(mean((z - z_fit)²)) → 只有分量
# rmse = sqrt(mean(Σ(x-x_fit)²)) → 全3D
```

**修复**：
1. 在代码中明确计算全3D几何RMSE（每个数据点到拟合曲线最近点的欧氏距离）
2. 或改用B-spline自由曲线（Level 3）实现0.05-0.13mm真3D精度
3. 在论文中明确说明RMSE定义（全3D几何距离 vs 代数距离 vs Z分量）

**预防**：任何涉及3D曲线拟合的论文，在L0.5数据门中必须额外检查RMSE的定义域——数字小不代表拟合好。

当在包含 pgfplots 的 LaTeX 文档中定义 TikZ 样式时，切勿使用以下保留名：

| 冲突名 | pgfplots 内置用途 | 替代名 |
|:-------|:------------------|:-------|
| `domain` | `\addplot[domain=0:1]` 定义绘图定义域 | `dbox` |
| `layer` | `\pgfplotsset{layers=...}` 图层管理 | `lbox` |
| `arr` | 无直接冲突但过于泛用，多个 TikZ 图共用时需全局注册 | `myarr` |

**症状**：编译时出现多个 `! Package pgfkeys Error: I do not know the key '/tikz/domain'` 错误，即使样式在 `tikzpicture[]` 选项中已定义。实际是 pgfplots 的内置 `domain` 键被 TikZ 的 `domain/.style={...}` 覆盖，pgfplots 尝试解析 `\addplot[domain=0:1]` 时找不到原生的 `domain` 键。

**根因**：TikZ 的 `\begin{tikzpicture}[domain/.style={...}]` 将 `domain` 注册为 TikZ 样式。pgfplots 的 `\addplot[domain=0:1]` 依赖 `domain` 作为轴坐标的 key。当 TikZ 先注册了 `domain` 样式，pgfplots 的 key 被覆盖，导致 `\addplot[domain=0:1]` 触发 "I do not know the key" 错误。

**检测**：
```bash
grep -n 'domain/' paper.tex        # 检查是否定义了 domain/.style
grep -n '\\\\addplot.*domain=' paper.tex  # 检查是否有 pgfplots 使用 domain= 键
grep -c 'do not know the key.*domain' paper.log  # >0 表示冲突已触发
```

**修复**：重命名 TikZ 样式：
```latex
% ❌ 冲突
\begin{tikzpicture}[
  domain/.style={rectangle, draw, fill=blue!10},  # 破坏了 pgfplots
  ...
]

% ✅ 正确
\begin{tikzpicture}[
  dbox/.style={rectangle, draw, fill=blue!10},    # 安全命名
  ...
]
```

**预防**：在包含 pgfplots 的文档中定义 TikZ 样式时，避免 `domain`、`axis`、`tick`、`grid`、`legend`、`label`、`title`、`colorbar` 等 pgfplots 内置键名。使用带前缀的命名方案：`dbox`、`bspot`、`rbox`、`lbox`。

**全局样式与局部样式**：当 `myarr`（或类似替代名）在多个独立的 `tikzpicture` 环境中使用时，必须在文档导言区全局注册：
```latex
\tikzset{myarr/.style={->, >=stealth, thick}}
```
否则每个 `\draw[myarr]` 在独立的 `tikzpicture[]` 选项中会重复注册，且跨 tikzpicture 不共享。

**实战**：2026-05-27 vor-bppv-diagnosis v6 — 收敛框架架构图中使用 `domain/.style=` 导致 7 个 pgfkeys 错误。重命名为 `dbox` 并从全局 `\tikzset` 注册 `myarr` 后 0 错误通过。

当用 Python 生成 pgfplots 柱状图代码时，axis 标签中的 `%` 字符是常见需求（如 "Proportion of Studies (%)"）。但 Python 字符串中 `\\%` 和 `\\%` 的微小差别导致截然不同的 LaTeX 结果：

```python
# Python string → 文件输出 → LaTeX解析
"\\%"       →  \%    → 渲染为 `%` 字符 ✅
"\\\\%"    →  \\%   →  `\\`(换行命令) + `%`(注释符) → 注释掉行尾剩余部分 ❌
```

**症状**: LaTeX Error: `Something's wrong--perhaps a missing \item.` 或 `! You can't use '\end' in internal vertical mode`。`\end{axis}` 无法正确闭合。`paper.log` 中 axis 选项行不完整。

**根因**: 在 pgfplots axis 选项行中（如 `ylabel={...}`），LaTeX 读入整行作为选项参数。当这行包含 `\\%` 时，`\\` 被解析为换行命令，然后 `%` 开始注释——`)` 和 `}` 等闭合字符被忽略，axis 选项解析到不完整的参数就停了下来。`\end{axis}` 找不到匹配的 `\begin{axis}`，触发环境未闭合错误。

**检测**:
```bash
grep -n '\\\\%' paper.tex                          # 找出所有 \\% 位置
python3 -c "print(open('paper.tex').read().count('\\\\\\\\%%'))"  # 准确计数
# 对照检查: 期望 \% (单反斜杠+%) 而非 \\% (双反斜杠+%)
```

**修复**:
```latex
% ❌ 错误——\\\\% 在 Python 字符串中 → 文件写入 \\% → LaTeX解析为 换行+注释
width=0.95\\textwidth, ylabel={Proportion of Studies (\\\\%)},

% ✅ 正确——\\% 在 Python 字符串中 → 文件写入 \% → LaTeX渲染为 `%`
width=0.95\\textwidth, ylabel={Proportion of Studies (\\%)},

% ✅ 更安全——用纯英文替代，彻底避免 %
width=0.95\\textwidth, ylabel={Proportion of Studies (percent)},
```

**预防**:
- 在 Python 字符串中生成 pgfplots axis 标签时，永远用 `\\%`（单个 backslash-escape）而非 `\\\\%`
- 对于 axis label 中不需要 `%` 符号的场合，直接用 "percent" 或 "percentage" 替代
- caption 中使用 `%` 时同理——`\\%` 而非 `\\\\%`，或改写为 "percent"
- 在编译前运行 grep 检查：`grep -cP '[^\\\\\\\\]\\\\\\\\%' paper.tex` — 非预置命令后的 `\\%` 标记潜在问题点
- 在 execute_code 的 `write_file()` 执行后、pdflatex 编译前，添加 axis 标签检查：

```python
# 编译前检查：axis 标签中不应有 \\%
import re
for i, line in enumerate(open('paper.tex').readlines(), 1):
    if re.search(r'ylabel|xlabel|legend|title', line) and '\\\\%' in line:
        print(f"⚠️  Line {i}: axis label contains \\\\% — may cause comment truncation")
```

**实战**: 2026-05-28 kappa-3d-eye-tracking v3 — QUADAS-2 bar chart `ylabel={Proportion of Studies (\\\\%)}` 导致 `! Something's wrong--perhaps a missing \item` 和 `! \begin{tikzpicture} on input line 99 ended by \end{document}`。修复为 `\\%` 后编译 0 错误通过。

---

- 导言区加：`\usepackage{tikz}` + `\usetikzlibrary{shapes.geometric, arrows, positioning, calc, fit, backgrounds, patterns}`
- 用pgfplots额外加：`\usepackage{pgfplots}` + `\pgfplotsset{compat=1.18}`
- 编译前做 axis 标签检查：grep `\\\\%` 在 ylabel/xlabel/legend/title 行
- 每个TikZ图插入后先单次编译验证
- elsarticle双栏用`\resizebox{\textwidth}{!}{...}`包裹tikzpicture
- 系统综述标准四件套（典型D3+D4提升+0.06）：PRISMA流程图 + SROC曲线 + 漏斗图 + QUADAS-2柱状图
- 参考文件 `references/tikz-systematic-review-templates.md` 含已验证代码
- 参考文件 `references/d7-citation-verification-case-synthos.md` — D7引用验证实战案例（含问题发现、修复流程、D7扣分矩阵）
- 参考文件 `references/system-paper-pipeline-validation-case.md` — 系统论文管线验证方法（用真实产出数据替代虚构对比表）
### 🔴 D7 `[?]` 假阳性：PDF提取伪影 vs 真实编译错误

当 Layer B (Gemini) 报告 D7 存在 `[?]` 占位符时，**必须用 `pdftotext` 验证 PDF 文本层**：

```bash
pdftotext paper.pdf - | grep -c '\[?\]'
# 输出 0 = PDF 中无占位符，Layer B 报告为提取伪影
# 输出 >0 = 真实编译错误，需修复
```

**已知现象**：NotebookLM 的 PDF 提取器有时会将 elsarticle 的 `[1]` 格式引用误读为 `[?]`。如果 pdf-to-text 确认 PDF 中零 `[?]`，则 D7 评分应校正（取 Layer A 的 D7 分，在质量报告中标注"Gemini 报告为提取伪影"）。

**判定规则**：
| pdftotext 结果 | Layer B D7 声明 | 结论 |
|:--------------|:---------------|:-----|
| 0 `[?]` | 报告有 `[?]` | PDF 提取伪影，取 Layer A D7 |
| >0 `[?]` | 报告有 `[?]` | 真实编译错误，需修复后重评 |

**实战**：pd-torsion-review 论文双质检时 Layer B 返回全 0 分（7维都是 0.00）。表面上看论文质量极差，但实际原因是 NotebookLM Gemini 的解析层报 `WARNING: No marked answer found; falling back to longest unmarked text`——Gemini 还在澄清评分流程，从未解析论文内容。

**检测流程**：
```bash
# 1. 检查 quality-report.md 中 Layer B 是否全零
grep -c '0.00' quality-report.md

# 2. 检查先前的 NotebookLM ask 日志（如有）
grep -i 'no marked answer\|WARNING.*notebooklm' /path/to/logs/*.log

# 3. 做 Layer A 独立评分（不依赖 Layer B）——如果 Layer A 正常得分而 Layer B 全零，则判定为 API 解析错误
```

**判定规则**：
| Layer A 平均分 | Layer B 模式 | 判定 |
|:--------------:|:-------------|:-----|
| ≥0.70 | 全0.00 | 🔴 API解析错误，取 Layer A 分 |
| ≥0.50 | 全0.00 | 🟡 可能API错误，需人工审核 |
| <0.50 | 全0.00 | ✅ 真0分，论文确实质量差 |

**修复**：重新用 `notebooklm ask` 提交评审，提示语中明确要求"对论文本身进行评分，不要解释评分标准"。

**预防**：Layer B 评审提示语开头加一句前置约束：`请直接打分，不要解释评分标准或要求澄清。输出格式：｛维度: 分数, 理由｝`

### 其他陷阱

1. **🔴 `\resizebox` 包裹 `\begin{table}` 触发"Not in outer par mode"** — 当用 `\resizebox{\textwidth}{!}{%` 包裹整个 `\begin{table}...\end{table}` 环境（而非仅 `tabular`）时，LaTeX 报错 `! LaTeX Error: Not in outer par mode` 和 `! Package graphics Error: Division by 0`。PDF 虽然生成但表格可能渲染异常（D4评分受损）。

   **根因**: `\resizebox` 是一个水平盒子命令，而 `table` 是一个浮动体环境（float），浮动体不允许出现在水平盒子内。LaTeX 无法将浮动体嵌入 `\resizebox`，导致外层环境解析失败。

   **修复**:
   ```latex
   % ❌ 错误——\resizebox 包裹整个 table 环境
   \resizebox{\textwidth}{!}{%
   \begin{table}[htbp]
   \centering
   \caption{...}
   \begin{tabular}{...}
   ...
   \end{tabular}
   \end{table}}

   % ✅ 正确——\resizebox 只包裹 tabular
   \begin{table}[htbp]
   \centering
   \caption{...}
   \resizebox{\textwidth}{!}{%
   \begin{tabular}{...}
   ...
   \end{tabular}}
   \end{table}
   ```

   **检测**: 编译日志中如果出现 `Not in outer par mode` + `Division by 0` 同时出现，99% 是 `\resizebox` 包裹了浮动体环境。grep 命令：
   ```bash
   grep -c 'Not in outer par mode' paper.log     # >0 → 有浮动体嵌入问题
   grep -n '\\\\resizebox.*\\\\begin{table}' paper.tex  # 找到错误行
   ```

   **预防**: 永远只用 `\resizebox` 包裹 `tabular`/`tikzpicture`，不包裹 `table`/`figure` 环境。

   实战：2026-05-25 vor-pd-systematic-review v2 — 比较表和外层 `\resizebox` 导致5个编译错误。修复后0错误通过。

2. **Layer B不能替代Layer A** — Gemini评分偏高+0.05~0.15，必须取两方最低分

3. **🔴 `\usepackage[table]{xcolor}` 与 elsarticle 的 array 包冲突，导致 `p{}` 列类型编译失败** — 当 elsarticle 文档类已内建加载 `array` 包时，额外引入 `\usepackage[table]{xcolor}` 会通过 `colortbl` 包重新注入 `array` 包，导致 LaTeX 内核的 `\insert@pcolumn` 宏未定义。症状：
   ```
   ! Undefined control sequence.
   <argument> ...rtpbox {\@nextchar }\insert@pcolumn \@endpbox ...
   l.70 \begin{tabular}{p{2.5cm}cccccc}
   ```
   该错误不会阻止 PDF 生成，但所有使用 `p{}` 列类型的 tabular 环境会呈现空白列或排版异常。

   **根因**: `\usepackage[table]{xcolor}` 加载 `colortbl`，后者依赖 `array` 包。由于 `elsarticle.cls` 已加载 `array`，`colortbl` 的二次加载序列破坏了 LaTeX 内核中 `p{}` 列类型的解析管道。当不使用 `[table]` 选项时（仅 `\usepackage{xcolor}`），`colortbl` 不被加载，即使已有 `array` 包也不会冲突。

   **修复**: 移除 `[table]` 选项，改用纯色 `\usepackage{xcolor}`。如果论文不需要 `\rowcolor` 或 `\cellcolor` 等表格着色命令，这是最简单的修复。若确实需要表格行着色：
   ```latex
   % ❌ 错误——会触发 elsarticle + array 冲突
   \usepackage[table]{xcolor}
   
   % ✅ 正确——无冲突
   \usepackage{xcolor}
   % 然后手动用 TikZ 或 \color 替代 \rowcolor
   ```
   替代方案：用 TikZ 独立绘制带颜色的表格，或用 `\textcolor{<color>}{<cell content>}` 逐格着色。

   **检测**:
   ```bash
   grep -n 'usepackage\[table\]' paper.tex     # 是否使用了冲突的 option
   grep 'insert@pcolumn' paper.log             # 确认是否触发该错误
   ```
   若 `insert@pcolumn` 出现在 `paper.log` 且 `paper.tex` 导言区有 `\usepackage[table]{xcolor}`，则 100% 是此问题。

   **预防**: 在 elsarticle 文档中，永远用 `\usepackage{xcolor}` 代替 `\usepackage[table]{xcolor}`。表格颜色用 `colortbl` 之外的方式实现（TikZ、\textcolor）。`\usepackage[table]{xcolor}` 在与 `booktabs`、`multirow` 等常见表格包联用时通常是安全的，但 elsarticle 的 array 加载序列有特殊性。

   **实战**: 2026-05-26 pd-ocular-biomarkers v4 — 添加 `\usepackage[table]{xcolor}` 后，所有使用 `p{}` 列类型的 tabular 报 `\insert@pcolumn` 错误。移除 `[table]` 选项后编译 0 错误通过。
4. **NotebookLM PDF提取有伪影 → D5假阳性** — elsarticle字体会在PDF中产生连字伪影，NotebookLM常报告"acting"→"affecting", "re\u001dex"→"reflex", "speci\u001ccity"→"specificity"等乱码。**必须验证**：当Layer B的D5 < 0.80时，grep TeX源确认：

   ```bash
   # 验证NotebookLM报的每个"乱码词"是否实际存在于TeX源
   for word in "acting" "re\u001dex" "speci\u001ccity" "direntiating" "\u001celd"; do
     if grep -rn "$word" sections/*.tex paper.tex 2>/dev/null; then
       echo "⚠️ 确认: '$word' 确实在TeX源中存在，需要修复"
     else
       echo "✅ '$word' 在TeX源中不存在，为PDF提取伪影，D5评分无效"
     fi
   done
   ```

   若TeX源中的正确拼写存在而伪影不存在 → D5评分取Layer A（否决Layer B的伪影评分）。
   
5. **L0.5在首次编译时可能无源文件** — 对理论/方法论论文，数值声明的验证路径为代码输出
6. **引用数统计** — 用`grep -cP '\\\\\\\\\\\\cite[tp]?\\\\{'`而非视觉估计。注意：elsarticle 论文使用 `\\\\citep{...}` 和 `\\\\citet{...}` 而非标准 `\\\\cite{...}`，必须同时处理三种格式：`grep -oP '\\\\\\\\cite[tp]?\\\\{[^}]+\\\\}' paper.tex | tr ',' '\\\\n' | wc -l`
7. **修订循环无限** — 有进展就继续，连续3轮无进展(avg提升<0.02)则降级目标期刊

8. **`\makecell` not bundled in elsarticle** — When adding tables with `\makecell[c]{...}` column headers, elsarticle does not automatically load the `makecell` package. Compilation fails with `! Undefined control sequence. \makecell [...]`. Fix: add `\usepackage{makecell}` explicitly in the preamble. This is safe — makecell has no known conflicts with elsarticle, booktabs, or array packages. 2026-05-28 kappa-pd-calibration-artifacts v2 fix.

### 🔴 Synthos 系统论文特有陷阱：数据不一致性

对 Synthos 自身系统描述论文进行双质检时，最常见的发现是 **摘要/正文/表格/结论之间的数据不一致**：

| 常见不一致模式 | 检测方法 | 修复 |
|:--------------|:---------|:-----|
| 摘要说"48 cycles"但结论说"55" | `grep -nP '\\b\\d+\\b.*(cycle|Cycle)'` 全文扫描 | 统一为 `evolution-state.json` 的 `evolution_count` |
| 表格标题"Cycle~51"但正文说"Over 55" | `grep 'Cycle~'` 检查表格与正文 | 表格保留代表性快照,正文引用更新 |
| 吸收数在不同位置不一致 | `grep "absorbed"` 检查各位置 | 以 evolution-log.md 中 `✅ 完全吸收` 计数为准 |
| engine版本过时 | `grep -i "engine.*v"` | 更新为 `evolution-state.json` 的 `engine_version` |

**数据源优先级**（从高到低）：
1. `evolution-state.json` — 权威的 `evolution_count`, `engine_version`, `trust_score`
2. `evolution/_INDEX.md` — `综合评分`（注意口径可能不同）
3. `evolution-log.md` — 吸收记录
4. `CONSTITUTION.md` 首行 — 宪法版本

**实战案例**：2026-05-27 Synthos论文Round 2双质检发现摘要报48 cycles而evolution-state.json记录55，差7轮。Table 2仍标Cycle 51。自动修复后校准分从0.793提至0.81+。

## Cron 批量全库质量扫描

> **自动看门狗模式** — 每6小时扫描45+篇论文，只在新论文或状态变化时报警。

### 架构

```
qc_batch_scan.py (no_agent=True, 纯脚本)
  ↓ 每6小时触发
  ↓
1. 扫描 outputs/papers/ 下所有论文目录
2. 对每篇论文运行 D8/D9/D10a 机械检查
3. 与上次状态比较，检测变化
4. 有变化→输出报告发到用户对话
5. 无变化→静默 (空stdout, no_agent=True不发送)
```

### 安装位置

- 脚本: `~/.hermes/scripts/qc_batch_scan.py`
- 状态文件: `~/.hermes/qc_last_scan.json`（自动维护）
- Cron: `hermes cron` → `qc-batch-scan`（每6小时）

### 检查内容

| 维度 | 方法 | 阈值 |
|:-----|:-----|:-----|
| D8 | `\\bibitem` / `.bib` 条目计数 | ≥30 |
| D9 | `pdfs/` + `bibtex_pdfs/pdfs/` PDF 计数 | ≥80% 条目标 |
| D10a | `\\cite{}` vs `\\bibitem` 正则匹配 | ≥80% 覆盖率 |

### 输出示例（变化时）

```
📋 [qc-batch] 05-30 08:03 — 45篇 | D8达标 35 | D10a达标 24 | 双达标 22
  🆕 eye-tracking-4d: 新论文
  ⚡ D8不足: 3d-sobel-edge-detection (16/30)
  🔗 D10a低: iris-yolo (0%)
```

### 与 post-compile 联动

| 模式 | 覆盖 | 局限 |
|:-----|:------|:------|
| post-compile（会话内） | 全量 D1-D10 + Layer B Gemini | 需 NotebookLM |
| Cron 批量（6h） | D8/D9/D10a + 变化检测 | 无 Layer A/B 语义评分，需人工补Layer B |

**推荐工作流**：
1. Cron 自动扫描 → 发现新论文 / D8不足 / D10a低
2. 用户收到通知 → 决定是否做 Layer A 完整评审
3. 用手工补 Layer B（NotebookLM）

## 自驱Cron Agent模式

当需要长时间自主推进科研任务时，使用持久工作跟踪器实现状态化cron：

**agent-tracker.json**（存放在 outputs/ 目录）：
```json
{
  "phase": "scanning | working | discovery",
  "current_paper": "paper-dir-name",
  "current_task": "当前具体任务",
  "progress_log": ["时间戳: 完成内容"],
  "completed_papers": ["dir-name1"],
  "next_action": "下一步描述"
}
```

**cron prompt铁律**：
- 每次运行在全新上下文（无历史记忆）
- 所有状态通过agent-tracker.json持久化
- 每次结束更新tracker + 追加agent-log.md
- 一次只做一件事（修一个维度/写一个节/跑一次质检）
- 同一论文最多5轮修订

**被忽略论文的自动修复模式**：
Agent会扫描 outputs/papers/ 下所有目录，自动发现未过双质检的论文并逐轮修复。常见自动修复路径：
- D2提升：增加形式化数学定义、算法伪代码、定理（2026-05-25 Iris-YOLO v3实战证明D2 +0.16）
- D4提升：补全引用元数据、添加实现细节节、**添加TikZ流程图/架构图**（PRISMA流程图、六阶段管线图等）
  
  **D4 TikZ图技巧**（详见 `references/tikz-systematic-review-templates.md` 含5个已验证模板）：
  - PRISMA 2020 流程图：用 TikZ `box/.style` + 绝对坐标定位，每个阶段标注排除数
  - SROC曲线：用 pgfplots + `ln()`（非`log()`），标注汇总估计+置信椭圆+散点
  - Deeks漏斗图：用 pgfplots，DOR vs Precision 回归线+p值
  - QUADAS-2柱状图：用 TikZ 原生 `\fill` + 坐标 `{...}` 算术包裹
  - 架构图：用 TikZ `stage/.style` + 水平排列 + `\resizebox{\textwidth}{!}`
  - 导言区需添加：`\usepackage{tikz}` + `\usetikzlibrary{shapes.geometric, arrows, positioning, calc, fit, backgrounds}`
  - 用pgfplots额外加：`\usepackage{pgfplots}` + `\pgfplotsset{compat=1.18}`
  
  **三层架构图模板**（理论框架/系统论文通用，实测D4 +0.06）：
  ```latex
  \\begin{figure}[htbp]
  \\centering
  \\resizebox{\\textwidth}{!}{%
  \\begin{tikzpicture}[
    node distance=0.8cm and 0.6cm,
    atom/.style={rectangle, draw, fill=blue!10, rounded corners=2mm, minimum width=1.8cm, minimum height=0.6cm, font=\\small},
    layer/.style={rectangle, draw, fill=gray!5, dashed, rounded corners=3mm, inner sep=4mm},
  ]
  % Layer 3 (top)
  \\node[layer, label={[above,font=\\bfseries]Layer 3: Name}] (L3) at (0,4.5) {};
  \\node[atom] (C1) at (-3.2,4.5) {Component 1};
  \\node[atom] (C2) at (0,4.5) {Component 2};
  \\node[atom] (C3) at (3.2,4.5) {Component 3};
  % Vertical arrows
  \\draw[<->, >=stealth, dashed, red!50] (L3.south) -- (L2.north);
  \\draw[<->, >=stealth, dashed, red!50] (L2.south) -- (L1.north);
  \\end{tikzpicture}}
  \\caption{Three-layer architecture description}
  \\label{fig:architecture}
  \\end{figure}
  ```
  要点：Layer 3在最上方（安全机制/元规则），Layer 2居中（流程/循环），Layer 1在底部（原子/组件）。每层用dashed矩形框包住区域内的节点。层间用dashed + red!50双向箭头显示依赖关系。用`resizebox{\\textwidth}{!}`包裹全部tikzpicture。
  
- D7提升：展开"et al."为全作者名、补卷期页码
