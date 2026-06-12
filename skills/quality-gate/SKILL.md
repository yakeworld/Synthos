---
name: quality-gate
description: "⚡ P0 闸门技能。四层质量架构：①响应级漂移检查 ②项目级L1-L4交付闸门 ③论文管线G1-G7原子闸门 ④SCI内容评审。**通用铁律：任务完成→质量评估→不达标→循环执行。** 无skill_view记录=门不通过。G5引用质量为最关键门。G7通过→自动sci-paper-quality-review。"
version: 2.9.0
author: Hermes Agent
license: MIT
priority: P0
execution_rule: "无skill_view记录=门不通过。每次任务完成前必过此门。写作管线每原子执行前必须先skill_view()，pipeline_trace记录skill_version+steps_executed。G5引用质量门为最关键门。"
signature: "deliverable: str, quality_matrix: dict, target_level: str -> gate_result: GateResult, gaps: list[Gap]"
related_skills: [project-experience-distillation, evolution, sci-paper-quality-review, paper-pipeline, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification]
metadata:
  synthos:
    priority: P0
    atom_type: meta-quality
    description: ⚡ P0 闸门技能。四层质量架构：①响应级漂移检查 ②项目级L1-L4交付闸门 ③论文管线G1-G7原子闸门 ④SCI内容评审。
    signature: ['deliverable: str, quality_matrix: dict, target_level: str -> gate_result: GateResult, gaps: list[Gap]'] -> ['gate_result: GateResult (L0-L4), quality_score: float, improvement_plan: str, gaps: list[Gap]']
    related_skills: ['project-experience-distillation', 'evolution', 'sci-paper-quality-review', 'paper-pipeline', 'knowledge-acquisition', 'knowledge-extraction', 'association-discovery', 'hypothesis-generation', 'argument-expression', 'viewpoint-verification']


# Quality Gate — 质量闸门

> 一次一件事，达标才停。不是"做完了"，是"验证过才算"。

## 核心理念（文言）

| 白话 | 文言 | 义 |
|:-----|:---
  io_contract: input: ['deliverable: str, quality_matrix: dict, target_level: str -> gate_result: GateResult, gaps: list[Gap]', 'output: ['gate_result: GateResult (L0-L4), quality_score: float, improvement_plan: str, gaps: list[Gap]']
--|:----|
| 无记录=门不通过 | **无录不过** | 无skill_view记录视为未执行 |
| G5引用质量最关键 | **引质为要，G5最重** | 论文质量上限=引用质量 |
| 一次一个维度 | **一维一渡** | 每次只聚焦一个等级，不跳步不并行 |
| 方向不对等于白做 | **向不正则功废** | 质量不只是技术合格，方向要与系统生长一致 |
| 论文数据必须可追溯到源 | **凡数必源，不源不取** | 无实验记录的数据声明=编造，不得进入评审 |

## 五层架构 + 动灵维度

| 层 | 范围 | 触发 | 动灵方向检查 |
|:---|:-----|:-----|:-------------|
| L0 动灵层 | 交付物/技能的方向与系统生长路径一致性 | 每次评估前 | ✅ 方向不对不进入技术检查 |
| **L0.5 数据诚实门** | **论文中每个可验证数据声明是否有源文件支撑** | **每次论文评审前** | ✅ **无源文件的数据声明必须删除或标记为理论推算** |
| L1 响应级 | 当前会话输出质量 | PreResponse Hook | — |
| L2 项目级 | 交付物D1-D6 | 项目阶段完成 | ✅ 检查项目方向是否与系统生长一致 |
| L3 管线级 | 论文G1-G7原子闸门 | 写作管线每阶段切换 | ✅ G1前先问"这个论文方向符合系统当前生长方向吗" |
| L4 内容级 | SCI 7维评审 | G7通过后自动 | — |

**编译后自动门**：论文编译完成后，`paper-pipeline` 的 P4 阶段自动调用 `quality/post-compile-dual-quality-check` 技能执行完整六步双质检。详见该技能的 SKILL.md。

## 数据诚实门（L0.5）— v2.6.0 → v2.7.0

> **反模拟铁律2号：凡数必源，不源不取。** LLM可以评估论证好不好，但LLM无法评估论证真不真——真/假需要外部世界对齐。论文写得像真的 ≠ 数据是真的。

### 触发条件

每次论文/技术报告评审前，必须先过此门。

### 执行流程

```
提取论文中所有可验证的数据声明
  ↓
逐条追溯源文件：
  ├── evolution log / state.json → 进化数据
  ├── benchmark log / git log → 基准测试数据
  ├── absorption-tracked.json → 吸收记录
  ├── 实验日志/代码输出 → 实验结果
  └── 文献引用 → 可访问的DOI/arXiv
  ↓
每条数据声明的判定：
  ├── ✅ 有源文件且一致 → 保留
  ├── 🟡 理论推算/估算 → 必须标注"estimated"
  └── ❌ 无源文件 → 必须删除
  ↓
通过条件：全部数据声明 ✅ 或 🟡（已标注）
↓
进入 L1-L4 评审
```

### 数据声明提取清单

| 声明类型 | 源文件验证方法 | 示例 |
|:---------|:--------------|:-----|
| 进化数据（分数/周期/退化） | `evolution-state.json`、`evolution-log.md` | "53 cycles, 0.98" |
| 基准测试数据 | `BENCHMARKS.md`、golden test输出 | "20/20 pass rate" |
| 吸收记录 | `absorption-tracked.json`、project tracking | "18 absorptions" |
| 定量实验结果（N/SD/p值） | 实验代码输出、日志文件 | "N=50, ±SD, p<0.05" |
| 实践验证 | 产出文件列表、项目目录 | "3 domain drafts" |
| 论文产出 | PDF文件、NotebookLM笔记本 | "submitted to Kaggle" |
| 引用 | DOI/arXiv可访问 | 36条bibitem |
| **对比基线值** | **追溯原始论文PDF确认具体数值——不可引用二次论文中的复现值并归到原始论文** | **"EllSeg IoU 0.9618 → 实际来自CondSeg Table2复现"** |

### 🔴 论文/项目存在性验证（2026-05-24 新增）

**致命陷阱**：当用户声称"我们有论文/项目X"，而你在文件系统中没找到完整成稿时，**不要直接判定为虚构**。你必须按以下顺序查全后才可下结论：

```mermaid
flowchart TD
    A[用户声称存在项目X] --> B{文件系统有成稿?}
    B -->|YES| C[✅ 确认存在]
    B -->|NO| D{NotebookLM有相关笔记本?}
    D -->|YES| E{笔记本摘要/内容包含X?}
    E -->|YES| C
    E -->|NO| F{会话历史(session_search)有提及?}
    F -->|YES| C
    F -->|NO| G[标记为待确认，问用户]
```

**2026-05-24 实战教训**：
**2026-05-31 SCC论文实战**：L0.5审计发现 gen_all_figures.py 中两个同名 fit_logspiral_3d 函数造成静默覆盖。Python使用后半份(argsort排序)覆写了前半份(最近邻路径排序)，导致补充图RMSE虚高2.27→0.13mm。修复：删除重复函数，统一路径排序方法。详细审计链见 scc-data-audit-2026-05-31.md

**2026-05-24 实战教训**：Synthos论文曾声明"4 domains including ADHD eye-tracking screening"
- 文件系统检查：无ADHD独立成稿 → ❌ 错误结论"ADHD工作子虚乌有"
- 但 NotebookLM `d5d2e76a`（基于头戴式三维眼动追踪）的摘要明确提到"多动症（ADHD）初步筛查"
- **正确结论**：ADHD筛查是头戴式眼动追踪项目的临床子应用，真实存在但不作为独立论文输出

**规则**：
1. 文件系统无成稿 ≠ 项目不存在
2. 声明"虚构/子虚乌有"前必须先查 NotebookLM + session_search
3. 项目可能以嵌入形式存在于更大项目中（非独立论文）
4. 用户说"我有"时，**优先相信并查证**而非质疑

### 📋 验证路径速查

| 数据类型 | 主源 | 备用源 | 查不到时的正确措辞 |
|:---------|:-----|:-------|:-------------------|
| 论文成稿 | `outputs/papers/` | NotebookLM项目 | "未找到独立成稿，请确认路径"而非"不存在" |
| 实验数据 | 项目目录下 `.py/.ipynb/.json` | session_search | "无可执行代码日志，标记为理论推算" |
| 进化数据 | `evolution-state.json` | `evolution-log.md` | "数据未在此版本更新，标注estimated" |
| 临床数据 | 项目数据文件 | 用户确认 | "请提供IRB记录或数据源路径" |

#### 🔴 文献观察 vs 实验发现 — 叙事强度规范（2026-05-28 新增）

> **2026-05-28 实战教训**：SCC论文拟合出螺旋率$b=0.03\sim0.10$后，发现与文献中耳蜗螺旋率($b\approx0.02\sim0.08$)重叠——但LLM将其写成了"discovery of a shared morphogenetic program"，而实际我们**没有分析耳蜗**，这只是文献值对照。

**规则**：论文中对**非本实验产出的数据**（文献引用、外部数据库查询、他人报告的值），必须使用以下措辞分级：

| 数据来源 | 允许的措辞 | 禁止的措辞 |
|:---------|:-----------|:-----------|
| 本实验/本代码产出 | "我们发现"、"我们证明"、"我们的结果表明" | — |
| 文献引用值 | "文献报告"、"据报道"、"据X等人观察" | "我们发现"、"我们证明" |
| 文献值 + 本实验值重叠 | "重叠表明可能性"、"提出假说" | "证明共享机制"、"发现共同程序" |
| 文献值的数值范围引用 | "文献报道的范围为" | 可直接写数值(如$b\approx0.02$-$0.08$)但需加引用 |

**L0.5审计中增加检查项**：
1. 提取论文中所有"我们发现/我们证明/我们的结果显示"的句子
2. 追溯每句的数据来源是本实验还是文献
3. 文献来源的声明必须使用上述允许措辞
4. 违规措辞 → 标记为过度声明 → 强制降级措辞

**L0.5审计检查清单新增**：
```markdown
- [ ] 所有"发现/证明/结果表明"声明追溯自本实验数据
- [ ] 文献对比声明使用"据报道/文献显示"措辞
- [ ] 无将文献观察伪装为实验发现的情况
```

## [v2.8.0] 主动 L0.5 审计协议（实验驱动验证）

> **区分被动审计（检查已有数据）与主动审计（运行实验验证声明）。**
> 实战验证：PIMA 论文声明 F1=0.7541，实际实验 F1=0.6986（夸大 0.0555）。

#### 原理

被动 L0.5 审计只检查"文件是否存在"。但 LLM 可能生成看起来专业的完整的文件而数据仍是编造的。**唯一可靠的验证方式是实际运行实验**。

#### 何时触发主动审计

| 条件 | 优先级 |
|:-----|:------|
| 论文声明的实验值与基准预期不符（如 PIMA 声称 F1=0.75 但同类论文普遍 <0.70） | 🔴 立即 |
| 论文声称的实验在文件系统中无对应代码 | 🔴 立即 |
| 用户将论文称为"突破口"（要求数据 100% 真实） | 🟡 尽快 |
| 论文是方法论论文（核心论据依赖数值精度） | 🟡 建议 |

#### 主动审计三步骤

```
Step 1: 提取论文全部数值声明
  ├── 从摘要、方法、结果、讨论、结论中逐行提取
  ├── 分类：自有实验结果 vs 文献对比值
  └── 对自有实验结果：建立声明值列表 {metric: claimed_value}

Step 2: 运行实验生成真实值
  ├── 使用 crispdm-helix-experiment 技能（下载数据→严格CV→多模型→消融→保存JSON）
  ├── 实验参数必须与论文所述一致（CV折数、SMOTE策略、模型种类）
  └── 输出：实验 JSON/CSV，每个数值可追溯到输出行

Step 3: 逐条比对
  └── 对每个声明值：|claimed - actual| < 0.02 → ✓ 保留
                         否则 → ✗ 修正论文
  └── 结果报告：哪些匹配、哪些夸大、哪些消减
```

#### 🔴 方向性检查（Directionality Check）

> **LLM 不仅虚高数值，还可能编造相反方向的结论。** 方向性错误比数值偏差更致命——它让论文的叙事完全颠倒。
>
> 实战案例（2026-05-26 HCS-3WT 乳腺癌论文）：
> - 论文声称："HCS-3WT 降低了 67% 的假阴性（3 FN → 1 FN）"
> - 实验发现：假阴性实际增加 28%（FN reduction = -28%）
> - 方向完全相反！

**根源**：LLM 在写作时"认为"三路级联架构应该优于单分类器，于是编造了"FN 减少"的故事，无视实验输出 JSON 中的 `fn_reduction_pct: -28`。这不是数值偏差，而是**叙事驱动了数据**。

#### 方向性检查执行协议

```yaml
directionality_check:
  Step 1: 提取论文中所有方向性声明：
    - "increase/decrease"
    - "improve/degrade"
    - "reduce/increase"
    - "better/worse than"
    - "+X% / -X%"
  
  Step 2: 对每条方向性声明，找到对应的实验输出字段：
    - 论文声称 "FN 降低 67%" → 找实验 JSON 中 fn_reduction_pct
    - 论文声称 "Recall 提升" → 找 ablation 中 recall_diff
  
  Step 3: 验证方向一致性：
    - 论文符号 vs 实验符号必须一致
    - paper_improvement 为 + → experiment 必须为 + 值
    - paper_reduction 为 - → experiment 必须为 - 值
  
  Step 4: 方向不一致时的处理：
    - 🔴 立即标记为"叙事驱动数据"
    - 不要尝试"合理化"差异（不要写"接近显著"或"趋势正确"）
    - 重写叙事：从"减少错误"转向"集中不确定性"
```

**方向性错误检测清单**（2026-05-26 HCS-3WT 实战验证）：

| 信号 | 方法 | 危险阈值 |
|:-----|:-----|:---------|
| 论文声称"降低"但实验值正数 | grep fn_reduction JSON | 符号不一致 |
| 论文声称"提升/改善"但实验值下降 | grep recall / f1 / accuracy 变化值 | 符号不一致 |
| 论文实验值来自多个数据集但只报最好结果 | 检查 JSON 中所有数据集的指标 | 选择性报告 |
| 效果声明（"improve by X%"）无对应基线值 | 检查是否在同数据/同配置下比较 | 基线不存在 |

**修复叙事重定位**（当方向确实相反时）：

不要强行解释为"接近显著"或"未来可优化"。把叙事从"错误减少"转向"不确定性集中"：

```markdown
# ❌ 错误叙事
"Our system reduces false negatives by 67%"

# ✅ 诚实叙事
"The system's primary contribution is concentrating diagnostic uncertainty on high-risk cases, enabling human-in-the-loop review where it matters most."
```

这个叙事更诚实，且对临床场景更有意义——不是替代医生，而是帮助医生把精力集中在最需要的病例上。2026-05-26 HCS-3WT 实战验证：FN reduction 从"声称 -67%"改为"FN 实际增加 28%（1→1.28），但灰区恶性富集 1.22×"，重新定位叙事为"不确定性集中"而非"错误减少"。

#### 实战教训：PIMA L0.5 主动审计（2026-05-26）

| 声明值 | 实验值 | 差异 | 判定 |
|:-------|:------:|:----:|:----|
| Ensemble F1=0.7541 | 0.6986 | -0.0555 | ✗ 夸大 → 修正 |
| Ensemble Recall=0.7500 | 0.7500 | 0.0000 | ✓ 精确匹配 |
| No Leakage F1(LDA)=0.6759 | 0.6759 | 0.0000 | ✓ 精确匹配 |
| Severe Leakage F1=0.7338 | 0.7657 | +0.0319 | ✗ 偏差 → 修正 |
| +8.6% F1通胀 | +6.71% | -1.89% | ✗ 修正 |

**关键发现**：论文中 LDA 基线值（被动来源）精确匹配；但 Ensemble 值（LLM 生成的"最好看"的数字）虚构。主动审计是唯一能区分这两者的方法。

#### 与 crispdm-helix-experiment 技能的衔接

```mermaid
flowchart LR
    A[论文有数值声明] --> B{有实验代码?}
    B -->|Yes, 但未运行| C[运行 crispdm-helix-experiment]
    B -->|No| D[写实验代码 → 运行]
    C --> E[JSON输出]
    D --> E
    E --> F[比对声明值与实验值]
    F --> G{全部匹配?}
    G -->|Yes| H[✅ L0.5通过]
    G -->|No| I[✗ 修正论文 → 重新编译]
    I --> F
```

### 数据诚实门决策树

```mermaid
flowchart TD
    A[提取论文中数值声明] --> B{有源文件?}
    B -->|YES| C{数值一致?}
    C -->|YES| D[✅ 保留]
    C -->|NO| E[❌ 删除或修正]
    B -->|NO| F{是理论推算/估计?}
    F -->|YES| G[🟡 标注 estimated]
    F -->|NO| E
    D --> H{全部通过?}
    G --> H
    E --> I[❌ 不通过，修订论文]
    H -->|YES| J[✅ 进入下一层评审]
    H -->|NO| I
```

### 2026-05-23 实战教训（Type A：虚构数据）

Synthos 论文 Round 3 评审过程中，N=50 外部定量对比表（含 $\pm$SD, $p<0.05$）在本地7维评审(Gemini 0.95)和Gemini 7维评审(0.963)中均获得高分通过。**但该数据从未被实验执行过——是LLM生成的虚构数据。** 评审流程专注于"论文写得好不好"而跳过了"数据真不真"。

**根因**：7维SCI评审技能定义了"反模拟铁律"（凡评必核），但只要求"每维评分附证据引用（段落号/语句/数据值）"——这个"证据"是论文内部的引用，不是指向外部实验记录的追溯。

**修复**：新增 L0.5 数据诚实门，在进入任何内容评审前，先做外部世界的数据真实性核对。

---

#### Type A 扩展检测：全量虚构 vs 局部虚构

2026-05-25 实战教训：PAP-04 (BPPV数字孪生论文) 在L0.5审计中发现**全部**定量数据均无源文件支持。与 Round 3 的局部虚构不同，此案是全量虚构——论文有完整IMRaD结构、三张定量表格(含±SD和p值)、一个临床案例研究，**但系统中没有任何VOR/BPPV实验代码存在**。

**全量虚构的信号模式**：

| 信号 | 检测方法 | 危险阈值 |
|:-----|:---------|:---------|
| ✅ 完整IMRaD但引用<10 | `paper.tex`中`\\cite{`计数 | **<10篇引用** + ≥3节正文 |
| ✅ 精密定量表但无代码 | `find . -name '*.py' \| xargs grep`含主题的词 | **0个相关.py/.ipynb** |
| ✅ 有p值±SD但无实验日志 | 搜索项目目录下实验输出 | 无实验输出目录/日志文件 |
| ✅ 物理/数学不合理的数值 | 领域常识审查（如VOR高频增益>1.0） | 明显违背已知物理范围 |
| ✅ 引用跨项目污染 | grep refs.bib中主题无关的bibkey（如虹膜分割论文出现在前庭论文中） | **≥1条明显无关条目** |
| ✅ 参考了不存在的补充材料 | `\\includegraphics{Fig.S1}`但figures/目录为空 | 正文引用但无文件 |

**检测流程**（2026-05-25 实战验证）：

```
发现一篇"已完成"的草稿
  ↓
Step 1: 计数引用数 → <10? → 可疑
Step 2: 搜索项目目录下该论文主题的实验代码 → 0个文件? → 高度可疑
Step 3: 检查bib文件是否有跨项目污染 → 有? → 进一步怀疑
Step 4: 领域常识检查表中最可疑的数值 → 物理不合理? → 确认全量虚构
  ↓
判定：全量虚构 → 论文是"设计提案打扮成实验结果"
```

**响应决策树**（全量虚构时）：

```mermaid
flowchart TD
    A[确认全量虚构] --> B{论文概念有科学价值?}
    B -->|YES| C[重写为理论框架论文]
    B -->|NO| D[彻底重写或放弃]
    C --> E[标记所有定量数据为 estimated/proposed]
    C --> F[添加 Limitations 节说明数据待验证]
    C --> G[清理bib（移除跨项目污染+不足引用）]
    C --> H[提交 P2 强化 而非直接进入 P4 双检]
    E --> I[✅ 进入修订循环]
    F --> I
    G --> I
    H --> I
```

**规则**：全量虚构 + 良好概念 = 理论框架重写，不是删数据补论文。**论文改形式，不删观点。**

**2026-05-25 实践验证**：PAP-04 的 BPPV-as-probe 概念确实新颖，仅定量数据不真实。正确操作是：
1. 保留BPPV-as-slow-dynamics-probe范式作为核心观点
2. 删除或标记所有±SD/p值/表格数值为"estimated"或"projected"
3. 扩展引用基(7→30+)，补足VOR领域文献
4. 提交P2强化而非直接P4双检

#### 引用跨项目污染检测

L0.5应包含对 `.bib` 文件中无关条目的检查步骤：

```bash
# 快速检测bib交叉污染
grep 'author\s*=' references.bib | grep -iE '(iris|segmentation|breast|cancer|adhd|pima)' | head -5
# 如果发现论文主题无关的作者/标题词 → bib被污染，需清理
```

**常见污染源**：copilot补全时从其他项目复制了bib文件但未清理；LLM从训练数据中混入了其他论文。

**修复**：移除无关条目，但保留其bibkey的引用声明为"需补真实PDF+DOI"，待后续ACQ阶段处理。

### 🟢 PDF→MD 转换：Layer B 评审的前置条件（2026-06-01 确立）

> **Layer B (7维SCI评审) 准确性的前提是 Gemini 能检索到参考文献全文。**
> PDF 上传到 NotebookLM 经常因无可提取文本层导致 `status=error`，而 Markdown 纯文本 100% 索引成功。

**两阶段就绪检查**：
1. D9 检查：PDF 文件存在且有效（`%PDF-` 头 + `%%EOF` 尾）
2. MD 就绪检查：`pdfs_md/{bibkey}.md` 存在且已上传 NotebookLM

**操作流程**：
1. PDF 下载后立即 `uvx markitdown pdfs/{bibkey}.pdf > pdfs_md/{bibkey}.md`
2. MD 上传 NotebookLM：`source add "$(cat file.md)" --type text --title "{bibkey}"`
3. 损坏/扫描 PDF（MarkItDown 返回 <50 chars）：写摘要替代，标注 `[OCR失败]`

**成功率数据（40篇Pima参考PDF）**：
| 类型 | 数量 | MarkItDown | 替代方案 |
|:-----|:----:|:-----------|:---------|
| 正常学术PDF | 35 (87.5%) | ✅ 成功 | — |
| 损坏PDF (xref破损) | 3 (7.5%) | ❌ | 手动摘要 |
| 扫描版 (无文本层) | 2 (5%) | ❌ | OCR 或摘要 |

### 🟢 数据泄露检测：特征列污染（2026-06-01 新增）

**症状**：基准测试中所有模型 F1≈1.0（CSV 中存在目标变量的副本列，加载时未排除）。

**审计命令**：
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data.csv')
for col in df.columns:
    if col != 'Outcome' and (df[col] == df['Outcome']).all():
        print(f'LEAKAGE: {col} is identical to target')
"
```

**修复**：在 `load_*()` 函数中明确排除目标列及其所有别名：
```python
feat = [c for c in df.columns if c not in (target, 'Diabetes_binary', 'ID')]
```

### 🟢 NotebookLM 上传：.tex 源文件优先于 pdftotext 提取文本（2026-06-01 新增）

**陷阱**：pdftotext 提取的 PDF 文本中 ligature 编码断裂（`ff`→`ff`→空白）导致 Gemini 报告 D5 清晰性低分，但 .tex 源文件完全干净。

**推荐**：上传 `.tex` 源文件（`source add "$(cat paper.tex)" --type text`）而非 pdftotext 提取文本，避免 ligature 误判。

### 双质量评分报告规范

每次 L0.5 → G1-G7 审计完成后，产出一份双质量评分汇总表：

```\n| Manuscript | Layer A | Layer B | Calibrated | Threshold Pass |\n|:-----------|:-------:|:-------:|:----------:|:---------------|\n| Paper X    | 0.871   | 0.907   | 0.871      | T1 (≥0.85) ✓  |\n| Paper Y    | 0.829   | 0.871   | 0.814      | T2 (≥0.80) ✓  |\n```

**系统观察**：Layer B (Gemini) 持续偏高 0.02-0.04 分。原因是 Gemini 的领域上下文广，能补偿 Layer A 的引用缺口扣分。校准分 = 两者中的较低分，作为保守验收标准。

**呈现策略**（已验证偏好）：一个详细展开案例 + 一个全景表格 = 有深度有广度。详细案例展示 L0.5 链条如何追溯每个数字；全景表格展示整体通过率。

### 2026-05-24 实战教训（Type B：引用链传播 + 两层验证框架）

#### 两层验证框架

L0.5 审计的核心发现是论文中的数值声明分属**两类**，需要不同验证策略：

| 声明类型 | 来源 | 验证方法 | 通过条件 | 示例 |
|:---------|:-----|:---------|:---------|:-----|
| **自有实验结果** | 本项目的代码/实验 | 映射到代码输出行 | 输出表值与论文一致 | "Recall=0.7426" → CSV/notebook cell输出 |
| **文献声明** | 引用的外部论文 | 追溯PDF中该数值 | 该数值在原始论文中出现 | "EllSeg IoU 0.9618" → CondSeg Table 2 |

**关键规则**：
1. 自有实验结果必须映射到可执行的代码/日志（notebook cell、实验日志文件、JSON输出）
2. 文献声明必须追溯到引用论文的PDF——**不可引用二次论文的复现值并归到原始论文**
3. 混用两类声明时（论文同时包含"我们的结果"和"对比基线"），每类用各自的验证策略

#### 轻量审计策略

L0.5 不需要重跑算法来验证。有效策略是**检查输出表值与论文中的数值是否一致**——比重新运行整个 pipeline 快两个数量级，且同样有效。实战验证：Pima 项目的 27.5% recall improvement 通过 Cell 22 格式化输出表与论文文本的交叉比对确认，双方一致→通过。此策略在早期版本中捕捉到过格式化不一致错误。

### PDF编码伪影导致Layer B Gemini误判（2026-05-25新增）

**症状**：LaTeX编译的PDF上传NotebookLM做Layer B评审时，Gemini对D4/D5/D7打分异常低（比Layer A低0.05-0.15），理由为"encoding artifacts"或"broken citations"。

**根因**：NotebookLM的PDF文本提取产生编码伪影（控制字符、连字破坏、断行破坏、数学符号乱码）。这些不是.tex源文件的错误。

**缓解**：1) ask提示语中预警告PDF可能有提取伪影 2) 异常低分时重传为.md纯文本 3) 标记受影响维度为需人工仲裁。

此陷阱尤其影响LaTeX编译的批判性综述论文（5-6页，密集引用）。

### Type B 扩展：引用链传播

iris-3d-anatomical-opt 论文 L0.5 审计中发现两种引用缺失错误：

1. **EllSeg-Seg IoU 0.9618** — 论文引用 kothari2021ellseg，但该具体数值实际来自 jia2024condseg 的 Table 2（CondSeg 论文复现 EllSeg 的结果），不是原始 EllSeg 论文报告的。
2. **Challenge Winner 2019 IoU 0.9517** — 论文无引用，实际来自 palmero2021 (OpenEDS2020 Challenge 报告)。

**根因**：引用链传播（Citation Chain Propagation）——LLM在撰写论文时，自然地从**二次论文**（如 CondSeg 论文的 Table 2）中读到了"EllSeg 达到 IoU 0.9618"，在写自己论文时却将引用指向了**原始论文**（kothari2021ellseg）。这不是编造，而是引用归属在跨论文传播中发生了漂移。

**与 Type A 的区别**：
| 维度 | Type A：虚构数据 | Type B：引用链传播 |
|:-----|:-----------------|:-------------------|
| 根本问题 | 数据从未被运行 | 数据真实但引用归属错误 |
| LLM行为 | 生成了看起来专业的数值 | 数值上有来源，但引错了原始论文 |
| 检测方法 | 检查实验日志/代码输出是否存在 | 追溯PDF原文，确认该数值出现在哪篇论文 |
| Gemini能否检测 | 不能（循环验证陷阱） | **能**（独立PDF交叉比对） |
| 修复方式 | 删除或标记estimated | 更正引用为实际的来源论文 |

**修复**：对比基线引用增加专用验证行（见数据声明提取清单表）。对每个"据X论文报告Y达到Z"的声明，必须验证：
1. X论文的PDF中是否真的有数值Z？
2. 如果X论文中没有，Z是否来自某篇复现X的论文W？
3. 如果是，引用改为"Y as reported by \citet{W}"而非直接引用X

**预防**：所有 baseline 对比值（EllSeg/CondSeg/Challenge Winner 等）在写入时，必须有对应 PDF 的正向数值确认（而非反向推导），并在脚注或表格标题中标注具体来源。

## 通用铁律：任务完成→质量评估→不达标→循环

> 此规则适用于**所有任务**，不仅仅是论文写作。任何任务完成时，自动执行质量评估，未达阈值即进入修订循环，有进展就持续循环。

### 执行流程

```
任务完成
  ↓
质量评估（按任务类型选择评估标准）
  ├── 有评估标准 → 评分 vs 阈值
  └── 无评估标准 → 至少验证：输出存在 + 语法正确 + 逻辑完整
          ↓
  达标? → ✅ PASS → 记录结果 → 完成
  不达标? → ❌ FAIL → 进入修订循环
                  ↓
          识别差距(目标-当前)
          定位最弱维度
          执行针对性修复
          重新评估
                  ↓
          达标 → ✅ PASS
          不达标但有进展(连续3次有提升) → 继续循环
          不达标且无进展(连续3次提升<0.02) → 降级目标或记录教训
                  ↓
          【无硬性上限】有进展就一直循环
```

### 评估标准选择

| 任务类型 | 评估标准 | 阈值 |
|:---------|:---------|:----:|
| SCI论文 | sci-paper-quality-review 7维 | 按目标期刊(T1-T4) |
| 代码/实验 | 结果正确性+复现性 | 断言全部通过 |
| 数据分析 | 数据完整性+逻辑一致性 | 验证链完整 |
| 文献检索 | 检索覆盖率+引用验证 | ≥2源覆盖 |
| 系统维护 | PROBE结构分 | ≥0.7 |
| 其他任务 | 至少：输出存在+结构正确+无明显错误 | — |

### 🔴 修订循环强制执行规则

> **2026-05-28 实战教训**：校准分0.791(<T2阈值0.80)时，Agent报了分+问了"要不要动手"——这是错的。规则已写"自动进入修订循环"但Agent没执行。

**强制规则**：
1. 报告产出后**立即**比较校准分 vs 阈值
2. 校准分 < 阈值 → **不得提问**，**立即**进入修订循环
3. 报告必须一条消息完成：报分 + 判定 + **初始修订计划**
4. 不得分两步（先报分等回复 → 再修）

**格式模板**（一条消息）：
```markdown
## 双质检结果
校准平均分: 0.791 (T3通过, T2未过)

## 自动启动修订轮次 #1
薄弱维度: D7引用质量(0.72) — 补参考文献19→35篇
计划: ...
```

**例外**：校准分 ≥ 阈值时才可问用户是否继续提升。

### 修订循环规则

```
1. 每次修订只聚焦一个维度（最低分维度）
2. 修订完成后自动重评
3. 连续3次有进展（评分提升>0.02）→ 继续下一个薄弱维度
4. 连续3次无进展（评分提升≤0.02）→ 降级目标或记录失败教训
5. 无硬性循环上限 — 有进展就一直循环
```

### 反退化检查

每次修订后必须执行回归检查，确保新修改未破坏已有质量：

| 检查项 | 方法 |
|:-------|:-----|
| 内容丢失 | 新旧版对比关键结构元素数量 |
| 格式退化 | 检查规范格式是否被简化 |
| 逻辑断裂 | 检查段落连贯性未因修改而破坏 |

## 动灵五维评估（L0 动灵层详细协议）

> 凝练自 2026-05-23 全系统动灵评估实践。当需要评估技能/交付物是否符合动灵原则时，使用此五维框架。

**触发条件**：每次 quality-gate 的 L0 动灵层评估触发时；每次 skill-absorption 完成吸收后需要验证"生化度"时；系统周期性健康检查中。

### 五维度定义

| 维度 | 含义 | 1-2 分（不合格） | 3 分（过渡） | 4-5 分（良好） |
|:-----|:-----|:-----------------|:------------|:---------------|
| **方向性** | 是否有清晰哲学根基驱动设计？ | 纯操作手册，无哲学根基 | 有哲学痕迹但浅，像贴标签 | 哲学是基因和灵魂，驱动每个决策 |
| **生化度** | 外来概念是否被完全转化？ | 原样搬运，吸收来源标记仍在 | 部分改写但残留外部痕迹 | 完全消化为原生表达，看不出来源 |
| **生长性** | 有版本进化和质量门记录？ | 无版本/无变更日志 | 有版本号但无实质迭代 | 版本+门控完整，每次迭代可追溯 |
| **原生感** | 看起来是自发生长的？ | 显然从别处搬来的 | 有生长痕迹但外观不整 | 浑然天成，与系统原生部分不可区分 |
| **自律性** | 内在驱动还是外部依赖？ | 强依赖外部输入/审批 | 部分依赖，有兜底但不完整 | 自洽自驱，有完整边界判定 |

### 评分与行动

| 平均分 | 判定 | 行动 |
|:------:|:-----|:-----|
| ≥ 4.0 | ✅ 动灵健康 | 维持 | 
| 3.0-3.9 | 🟡 需关注 | 识别最低分维度，针对性修复 |
| 2.0-2.9 | 🔶 需修复 | 进入修订循环，优先处理生化度和方向性 |
| < 2.0 | 🔴 严重不匹配 | 标记为"聚集式吸收"，需要重新五层提取，重走吸收流程 |

### 三种反动灵模式（常见故障诊断）

| 模式 | 诊断标记 | 根治方法 |
|:-----|:---------|:---------|
| **贴标签式哲学** | 文言/哲学在SKILL.md开头但技能设计与哲学无关 — "贴在树上的铁片" | 删除装饰性哲学，要么注入真实哲学驱动设计，要么诚实地做纯技术工具 |
| **聚集式吸收** | 外部内容被原样堆叠，无统一形式因 — "把零件堆在工具箱里" | 重新五层提取，走 L+0~L+3 完整吸收流程，必须经过文言→白话→英文三语层级 |
| **经济理性假驱动** | "省时省力"替代"完满实现"作为终极理由 — 工具逻辑而非生长逻辑 | 将终极理由改为动灵逻辑：问"这帮助系统向哪个方向生长"而非"这省了多少时间" |

### 使用流程

```
1. 加载目标技能的 SKILL.md
2. 按五维度逐项评分（1-5）
3. 识别最低分维度
4. 检查是否匹配三种反动灵模式
5. 确定修复方案：
   - 贴标签式哲学 → 重写原理层，或将技能标记为纯技术工具
   - 聚集式吸收 → 重新走五层提取 + 三语层级消化
   - 经济理性假驱动 → 替换终极理由为生长逻辑
6. 执行修复
7. 重新评分验证（目标：平均分 ≥ 3.0）
```

## 论文管线闸门（G1-G7）

| 闸门 | 检查 | 通过条件 |
|:-----|:-----|:---------|
| G1 ACQ | 文献搜索 | ≥60候选, ≥30 PDF, DOI 100% |
| G2 EXT | 知识提取 | 结构化提取 |
| G3 ASC | 关联空白发现 | 关联+空白矩阵 |
| G4 HYP | 假设生成 | 可证伪假设 |
| G5 ARG | 论文论证 + **引用全文验证** | **无虚构引用 + 关键参考PDF已转MD上传NotebookLM + 无僵尸/孤儿引用** |
| — | **G5c NotebookLM参考文献上传前置门** | **🔴 硬性阻断：Layer B执行前必须验证NotebookLM中参考文献源数 ≥ D8×80%。无参考文献全文上架 → 禁止执行Layer B。验证命令：`notebooklm source list -n <nb_id> | grep -c "ready"` 对比 `grep -cP '^@\\w+\\{' references.bib`。详见 dual-quality-check-v2 SKILL.md 的「P0 前置闸门」节。** |
| — | **G5a 引用审计子门** | **逐篇检查：DOI完整性、PDF存在性、数值准确性、引用上下文适当性（详见 references/ref-citation-audit-protocol.md）** |
| — | **G5b 数值声明追溯子门** | **对正文中每个 \\cite{} 附近的数值声明，追溯对应PDF原文确认。不可追溯的数值必须降级措辞或删除。2026-05-30 SCC论文实战：Manoussaki2008中查不到b≈0.02-0.08，修正为泛化引用。详见 paper-reference-pipeline → references/citation-context-verification-scc-2026-05-30.md** |
| — | **G5d 空假一致性门（Gap-Hypothesis Congruence）** | **双质检阶段，对关键参考文献逐篇回溯其研究空白→对照我方论文的gap/hypothesis→验证贡献定位正确性。防止gap膨胀（少量空白写成领域空白）、gap漂移（引言与结论的gap不一致）、gap已填（写作期间有新文献填补了空白）。详见 references/gap-hypothesis-congruence.md** |
| G6 VER | 观点验证 | 验证通过 |
| G7 latex | 编译验证 | cite×bib×pdf三维匹配 |

## 执行规则

1. 每次任务完成前先加载此skill
2. 写作管线每原子前先`skill_view()`加载对应SKILL.md
3. `pipeline_trace`记录 skill_version + steps_executed
4. G7通过→自动加载 `sci-paper-quality-review`
5. SCI评审通过→自动加载 `project-experience-distillation`

## 参考文件

- references/writing-pipeline-checklist.md — G1-G7详细检查清单
- references/project-quality-dimensions.md — D1-D6项目级质量框架
- references/pdf-download-strategy.md — PDF下载策略（降级方案，NotebookLM为首选）
- references/anti-entelechy-patterns.md — 三种反动灵模式诊断手册（贴标签式哲学/聚集式吸收/经济理性假驱动）
- references/pima-l05-audit-demo.md — Pima CRISP-DM L0.5 两层验证案例（可复现示例，含完整追溯链）
- **references/curve-fitting-order-pitfalls.md** — 曲线拟合点序陷阱：argsort vs nearest-neighbor path（2026-05-31 SCC实战）
- references/data-leakage-audit-protocol.md — Data leakage audit methodology: honest benchmark protocol, leakage pattern quantification, multi-classifier bootstrap, known honest ranges per dataset (proven in Breast Cancer critical review, 2026-05-25)
- **references/bibtex-doi-audit.md** — BibTeX DOI 审计与修复参考：重复DOI检测、期刊-DOI前缀匹配验证、PDF元数据交叉检查（2026-05-26 实战积累）
- **references/scc-logspiral-quality-boost-2026-05-28.md** — SCC对数螺旋论文三轮质量提升案例：19→38篇文献、概念图、0.791→0.837
- references/bibitem-integrity-verification.md — Bibitem完整性验证：SS/Crossref/PubMed三重验证技术，含Smith2021/Damiano1996实战案例  
- references/ref-citation-audit-protocol.md — 参考文献引用审计协议：凡引必验，逐篇检查DOI/PDF/数值准确性  
- references/scc-data-audit-2026-05-31.md — SCC论文L0.5审计案例：重复函数检测、argsort bug发现、交叉验证链  
- references/figure-data-provenance.md — 图数据溯源检查清单：图→脚本→数据映射验证  
- references/full-claim-l05-verification-2026-06-01.md — 全量声明L0.5验证协议：系统提取论文中所有数值声明(非仅关键值)，逐条追溯源文件，缺失则写实验代码跑真实值替换。Pima实战含编造量级数据。
- references/data-leakage-audit-protocol.md

## 验证

- [ ] L1响应级：认识论门+宪法门+漂移门全部PASS
- [ ] L2项目级：D1-D6目标等级已达成
- [ ] L3管线级：G1-G7全部通过，pipeline_trace有记录
- [ ] L4内容级：sci-paper-quality-review评分≥0.80
