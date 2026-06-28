---
name: research-output-evaluation
description: "科研产出评估 — 评估研究者的实际发表论文数量/质量分布、管线产出效率、临床功底与计算建模的平衡。核心发现：管线产量≠质量（中位数55/100，55.7%条件通过）。覆盖论文库扫描、质量分层、产出效率分析、临床vs合成数据审计。"
version: 1.0.0
priority: P1
execution_rule: "当用户要求'评估我''评估论文管线''分析产出质量'或类似查询时执行。"
signature: "paper_directory/ + quality_reports/ -> evaluation_report.md (publication_count, quality_distribution, production_efficiency, clinical_depth, synthetic_data_ratio)"
related_skills: [paper-pipeline, quality-gate, paper-numerical-integrity-audit, paperjury, project-experience-distillation, evolution, sci-paper-quality-review]
---

# Research Output Evaluation — 科研产出评估

> **核心哲学：产量不等于质量。100篇管线论文 ≠ 1篇SCI。临床功底是核心壁垒，计算建模是放大工具。**

## 原理

评估科研产出不是简单地数"写了几篇论文"。必须从三个维度交叉验证：

1. **数量维度**：管线论文数、已完成数、已发表数
2. **质量维度**：质量分分布、质量门通过率、引用健康度
3. **深度维度**：临床数据真实性、合成数据占比、方法论创新度

**关键发现（2026-06-20）：** 一个典型的"产量幻觉"场景——管线产出98篇论文，56篇"已完成"，但质量分中位数仅55/100，55.7%仅为"条件通过"，23.9%直接FAIL。绝大多数论文仅有合成数据验证，无真实患者数据。

## 触发条件

- 用户要求"评估我"、"评估论文管线"、"分析我的产出"
- 用户要求"哪篇论文最好"、"我应该发表哪篇"
- 周期性审计（cron运行）需要产出效率报告

## 核心流程（五步）

```
论文库扫描 → 质量分层 → 效率分析 → 数据真实性 → 综合评估
 (10m)       (5m)      (10m)       (15m)        (5m)
```

### Step 1: 论文库全景扫描

从 `outputs/papers/` 目录扫描：

```bash
# 统计目录数量
ls outputs/papers/ | grep -v '^_' | wc -l  # 排除 _docs _drafts _knowledge_only

# 统计有.tex的论文
find outputs/papers -name "*.tex" -not -path "*/_*" | wc -l

# 统计有PDF的论文
find outputs/papers -name "*.pdf" -not -path "*/_*" | wc -l

# 统计有state.json的论文
find outputs/papers -name "state.json" -not -path "*/_*" | wc -l
```

### Step 2: 质量分层

读取所有 `state.json` 中的 `quality_score`：

```python
import json, os

qs_scores = []
for d in os.listdir('outputs/papers/'):
    if d.startswith('_'): continue
    state = f'outputs/papers/{d}/state.json'
    if os.path.exists(state):
        with open(state) as f:
            qs = json.load(f).get('quality_score', 0)
            qs_scores.append((d, qs))

# 分层
t1 = [(d,q) for d,q in qs_scores if q >= 90]  # T1: Nature MI/PAMI
t2 = [(d,q) for d,q in qs_scores if 70 <= q < 90]  # T2: CBM/IEEE
t3 = [(d,q) for d,q in qs_scores if 50 <= q < 70]  # T3: Standard
t4 = [(d,q) for d,q in qs_scores if q < 50]  # T4: 需要大修

print(f"总数: {len(qs_scores)}")
print(f"T1 (≥90): {len(t1)}")
print(f"T2 (70-89): {len(t2)}")
print(f"T3 (50-69): {len(t3)}")
print(f"T4 (<50): {len(t4)}")
```

**关键阈值**：
| 等级 | QS范围 | 建议 |
|------|--------|------|
| T1 | ≥90 | 可投T1期刊（Nature MI/PAMI） |
| T2 | 70-89 | 可投T2期刊（CBM/IEEE TBME） |
| T3 | 50-69 | 需进一步修订 |
| T4 | <50 | 大修或归档 |

### Step 3: 管线效率分析

计算关键效率指标：

| 指标 | 公式 | 正常范围 |
|------|------|----------|
| 管线产出效率 | completed_papers / total_paper_dirs | >0.5 |
| 质量门通过率 | pass_count / (pass+conditional+fail) | >0.4 |
| T1+T2占比 | (len(t1)+len(t2)) / total | >0.3 |
| 质量分中位数 | median(qs_scores) | >70 |

**效率低下的信号**：
- 质量门通过率 <30% → 管线产出的论文大多需要返工
- T1+T2占比 <15% → 绝大多数论文达不到发表水平
- 质量分中位数 <50 → 一半以上论文低于及格线

### Step 4: 数据真实性审计

这是评估中最关键的步骤——区分"有临床数据的论文"和"有合成数据验证的论文"：

```bash
# 检查论文是否使用真实临床数据
for dir in outputs/papers/*/; do
    # 搜索临床数据相关关键词
    clinical=$(grep -rl "patient data\|clinical data\|IRB\|ethics\|hospital\|clinical trial" "$dir" 2>/dev/null | wc -l)
    synthetic=$(grep -rl "synthetic data\|simulated\|generated data\|no real data" "$dir" 2>/dev/null | wc -l)
    
    echo "$(basename $dir): clinical=$clinical, synthetic=$synthetic"
done
```

**⚠️ 合成数据陷阱**：大量ODE/PINN论文声称"临床验证"，实际仅使用合成数据验证。其"验证"过程为：
1. 用已知参数的ODE生成合成数据
2. 用PINN从合成数据恢复参数
3. 对比恢复参数和已知参数

这个过程验证的是**数值算法的自洽性**，不是**临床模型的准确性**。论文不能据此声称任何临床相关性。

### Step 5: 综合评估报告

输出包含以下维度：

1. **论文库全景**：总数、已完成的、有PDF的、有quality_check的
2. **质量分布**：T1/T2/T3/T4分层、中位数、均值、最高分
3. **效率指标**：质量门通过率、T1+T2占比、完成效率
4. **数据真实性**：使用真实临床数据的论文数 vs 仅合成数据验证的论文数
5. **临床深度评估**：作者的真实临床身份/经验 vs 论文中声称的临床贡献
6. **建议**：优先发表的论文列表、需要归档的论文、需要补充数据的论文

## 产出效率分析的陷阱

### 陷阱1: 流水线产量幻觉

> **核心发现（2026-06-20）**：管线产出98篇论文、56篇"已完成"，但：
> - 质量分中位数 55/100
> - 55.7%仅为"条件通过"
> - 23.9%直接FAIL
> - 仅21.6%通过质量门
>
> **结论**：流水线产出的是**论文骨架**，不是**可发表成果**。98篇中真正接近可发表水平的可能不足10篇（T1+T2）。

**正确评估方式**：不要数"管线产出多少篇"，而要看"有多少篇质量分≥80且有真实数据支撑"。

### 陷阱2: 合成数据≠临床数据

> 大量ODE/PINN论文使用合成数据验证，声称"临床相关性"。**合成数据验证只能证明数值方法的自洽性，不能证明模型对真实世界的描述能力。**

**正确评估方式**：对每篇论文检查是否包含真实患者数据、IRB声明、临床设备采集记录。若无，论文不能声称任何临床相关性。

### 陷阱3: 质量门通过率虚高

> "条件通过"（CONDITIONAL）不等于"通过"。质量门报告中49篇条件通过（55.7%），这些论文需要至少1-3个维度修复后才能投稿。

**正确评估方式**：将条件通过视为"未完成"，只计算绝对通过（PASS）的论文为"完成"。

### 陷阱4: 临床身份与论文产出不匹配

> 用户是**眩晕病实验室负责人、前庭医学专家**，拥有深厚的临床解剖学功底。但多数论文是通用计算建模方法（ODE/PINN），与临床深度脱节。

**正确评估方式**：优先评估与用户临床身份直接相关的论文（BPPV、VOR、眼动追踪、前庭功能评估），这些论文的临床贡献最可信。通用方法论文（如breast cancer ML、stroke prediction）需要外部验证。

## 推荐优先发表的论文选择标准

| 标准 | 权重 | 说明 |
|------|------|------|
| 质量分≥80 | 0.30 | 已通过质量门，有结构完整性 |
| 使用真实临床数据 | 0.25 | 有患者数据、IRB、临床设备 |
| 与临床身份直接相关 | 0.20 | BPPV/VOR/眼动追踪/前庭功能 |
| 引用健康度D10a≥90% | 0.15 | 引用完整、无孤儿僵尸 |
| 有可复现代码 | 0.10 | 有实验代码和输出 |

## 产出质量诊断框架

评估一篇论文的"可发表性"时，按以下维度打分：

```
临床深度 (0-100) × 计算创新性 (0-100) × 数据真实性 (0-100)
```

- **临床深度**：论文是否利用了作者的专业知识？是否对临床实践有实际指导意义？
- **计算创新性**：ODE/PINN方法是否有理论贡献？还是仅仅是现有方法的简单应用？
- **数据真实性**：是否有真实数据支撑？合成数据验证能说明什么？

**三者缺一不可**。一篇论文若临床深度高但计算创新性低 → 可投临床期刊。若计算创新性强但临床深度低 → 可投方法学期刊。若数据真实性为零 → 不可发表。

## 与 quality-gate 的关系

- `quality-gate` 检查**单篇论文**的结构完整性（G1-G7）
- `paper-numerical-integrity-audit` 检查**单篇论文**的数值一致性
- `research-output-evaluation` 检查**整个论文库**的质量分布和效率

三者互补：quality-gate 是手术刀，paper-numerical-integrity-audit 是显微镜，research-output-evaluation 是体检报告。

## 支持文件

- `references/output-evaluation-checklist.md` — 评估清单和评分表模板
- `references/synthetic-vs-clinical-data-guide.md` — 合成数据 vs 临床数据评估方法

## 实战数据（2026-06-20）

基于 `outputs/papers/` 和 `agent-tracker.json` 的实际数据：

| 指标 | 值 |
|------|----|
| 总论文目录数 | 98 |
| 有.tex的论文 | 71 |
| 有PDF的论文 | 59 |
| 有quality_score的论文 | 88 |
| 质量门PASS | 19 (21.6%) |
| 质量门CONDITIONAL | 49 (55.7%) |
| 质量门FAIL | 21 (23.9%) |
| 质量分中位数 | 55 |
| 质量分均值 | 55.3 |
| 质量分最高 | 96 (7篇) |
| T1 (≥90) | 32 |
| T2 (70-89) | 94 |
| T3 (50-69) | 4 |
| T4 (<50) | 2 |
| 已完成论文 | 56 |
| 僵尸引用总数 | 1063 |
| D8≥30的论文 | 29.9% |
| D10a≥95%的论文 | 91.6% |

**关键洞察**：98篇论文中，真正接近可发表水平的（T1+T2且D10a≥95%）约10-15篇。其中使用真实临床数据的可能不到5篇。其余80+篇需要大量修订或归档。

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
