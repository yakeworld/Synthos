# NotebookLM 5门质量评估系统

> 每个门提供：评分模板 + **必答补救方案** + 补救执行流程。
> 核心理念：评分是诊断，补救是治疗。只评分不给补救方案 = 不完整的质量门。

---

## Q1门：文献检索质量评估（P-1.1后）

### NotebookLM Q&A

```bash
notebooklm use <project_id>
notebooklm ask "请评估本次文献检索的质量：

1. 覆盖度(0-1): 覆盖了该领域所有主流方法流派?有无明显遗漏?
2. 时效性(0-1): 覆盖了近5年的关键进展?
3. 精准度(0-1): 引用文献与论文主题的相关度?
4. 权威性(0-1): 是否包含高影响力期刊/会议的文献?

**【必答】对于评分<0.85的维度，请逐一给出具体补救方案：**
- 缺失了哪些具体的文献/流派/数据集?列出标题或DOI
- 应该用什么检索词在哪个数据库(PubMed/Semantic Scholar/OpenAlex)搜索?
- 时间范围和过滤条件建议是什么？"
```

### 补救流程

当任何维度 < 0.85：

```bash
# 1. 根据NotebookLM建议的检索词启动联网搜索
notebooklm source add-research "suggested query" --mode deep --no-wait

# 2. 等待并导入
notebooklm research wait --import-all

# 3. 验证补充效果
notebooklm source list | grep -i "topic"

# 4. 重新评估
notebooklm ask "重新评估门1，关注之前<0.85的维度是否改善。更新后各维评分?"
```

### 实测参考（PIMA CRISP-DM, 2026-05-22）

| 维度 | 补救前 | 补救操作 | 补救后 | 提升 |
|:-----|:------:|:---------|:------:|:----:|
| 覆盖度 | 0.80 | 搜索"Data Leakage AND XAI AND Healthcare" | 0.95 | +0.15 |
| 权威性 | 0.80 | 搜索"TRIPOD+AI OR PROBAST-AI" → 48 sources | 1.00 | +0.20 |

---

## Q2门：研究空白质量评估（P-1.2后）

### NotebookLM Q&A

```bash
notebooklm ask "请按CARS模型评估研究空白质量：

1. 真实性(0-1): Gap真实存在还是人为制造?至少几个独立来源交叉确认?
2. 非平凡性(0-1): '没人做过'和'有理由必须做'之间的差距?
3. 可填补性(0-1): 填补这个Gap能解决什么具体问题?
4. 连续性(0-1): Gap是否从文献综述自然过渡?有无断裂?

**【必答】如果任何维度<0.8，请给出具体补救方案：**
- 真实性不足：需要哪些额外的交叉来源?搜索什么关键词?
- 非平凡性不足：如何重新定位Gap?对比哪些具体系统?
- 连续性断裂：Related Work哪一段需要补充过渡句？"

### 补救实战指南

#### 非平凡性不足的修复策略（已验证于Synthos系统论文）

**核心原则**：非平凡性不是特征堆叠（"没人同时做A+B+C"），而是范式转移论证。必须指出**现有系统共享的底层架构瓶颈**，以及为什么这个瓶颈**注定无法被增量改进解决**。

**三步修复法**：

1. **识别共同架构瓶颈**：找出所有被引用系统共享的单一限制。例如系统论文：
   - "所有被调查系统的控制流都硬编码在Python/命令式代码中"（命令式控制流瓶颈）
   - "LLM被迫扮演'被调用的子程序'，无法读取或修改推理编排逻辑"（认知黑盒）

2. **论证"增量无法突破"**：说明为什么在这个瓶颈存在的前提下，附加功能（更好的提示、更多的工具、更复杂的SOP）都无法解决问题：
   - "即使Reflexion实现了迭代自修正，其纠正机制仍然被困在Python编排层"
   - "即使DSPy自动优化提示，优化器本身是Python函数——LLM无法改进优化策略"

3. **重新定位为新范式**：将Gap从"缺失特征"升级为"需要架构范式转移"：
   - "因此需要声明式认识论介质（declarative epistemological medium）"
   - "消除LLM推理与系统控制流之间的语义鸿沟"

**对比的具体系统**（按类型）：
- **编排框架**（MetaGPT/CrewAI）：SOP是Python硬编码的，Agent无法运行时自修改架构
- **高自主系统**（Auto-GPT/AI Scientist）：高度自主但缺乏认识论约束→幻觉/确认偏误
- **自优化系统**（DSPy/Voyager）：优化过程本身是Python函数→LLM不能改进优化策略

#### 连续性断裂的修复策略

当Related Work到Our Contributions之间缺乏逻辑过渡时，添加**共同架构瓶颈→设计启示**过渡段：

```
"The pattern across all surveyed systems reveals a common architectural bottleneck: [瓶颈描述]. "
```

这个过渡段需要：(a) 总结Review枚举的系统，(b) 抽象出共享限制，(c) 自然推导出新设计方向。

#### 耦合绑定（锦上添花）

NotebookLM建议将"认识论约束"与"声明式介质"的耦合关系进一步绑定：
- 复杂认识论约束（证伪主义、贝叶斯推理）如果用Python硬编码，控制流会臃肿且易逻辑死锁
- 只有转化为LLM原生的声明式自然语言规则，LLM才能以最符合next-token-prediction特性的方式去遵循
- 可添加一句："Critically, complex epistemological constraints...would themselves become unwieldy and error-prone if hard-coded as imperative logic..."

### PASS条件
- 真实性 ≥ 0.8（≥2独立来源确认）
- 非平凡性 ≥ 0.7（"有理由必须做"）
- 连续性 ≥ 0.8（从RW无缝过渡）

---

## Q3门：科学假设质量评估（P-1.3后）

### NotebookLM Q&A

```bash
notebooklm ask "请按图尔敏模型评估科学假设质量：

1. 可证伪性(0-1): 明确淘汰标准?什么实验能证明它错?
2. 具体性(0-1): If X then Y?X和Y可测量?
3. 唯一性(0-1): 非trivially true?H₂和H₃?
4. 与Gap对齐(0-1): 假设直接响应研究空白?

**【必答】如果任何维度<0.8，请给出具体补救方案：**
- 可证伪性不足：设计什么淘汰实验?阈值怎么设?
- 具体性不足：H₁怎么改写?X和Y的操作化定义?
- 无替代假设：H₂和H₃应该是什么？"
```

### 补救实战指南（系统论文已验证，Synthos Cycle 43）

#### 可证伪性不足的修复策略

**核心原则**：微观可证伪（如算法中的 `ε = 0.01` 阈值）不够——必须提供**宏观系统级的淘汰实验**。

**修复模板：Architectural Plasticity Stress Test**

```
**Falsification Experiment**:
- 实验组：本文系统
- 对照组：最合理的替代架构（如Python AST元编程、DSPy自动优化）
- 任务：吸收一个高复杂度外部管线（如The AI Scientist），限10个进化周期
- 阈值：如果对照组在10周期内≥0.90通过率 → 核心假设被证伪
- 先验预测：对照组因[具体原因]失败（如AST语法崩溃、局部优化无法处理全局重构）
```

**关键要素**：
1. 对照组必须是最合理、最强的替代方案（不是稻草人）
2. 任务必须足够复杂——能暴露架构瓶颈
3. 阈值必须预先设定——不是事后解释数据
4. 先验预测必须有具体机制论证——不是"我觉得对的" 

#### 唯一性不足（缺H₂/H₃）的修复策略

当论文只有一个假设时，必须提出并反驳两个替代假设：

**系统论文标准H₂/H₃模板**：

| 假设 | 名称 | 内容 | 反驳方向 |
|:-----|:-----|:-----|:---------|
| H₁ | 声明式认识论介质 | 纯声明式SKILL.md + 宪法治理实现架构自进化 | — |
| H₂ | 代码生成假说 | Python AST元编程同样能实现架构可塑性 | AST语法风险无界→运行时崩溃 |
| H₃ | 提示词优化假说 | 保留Python编排+DSPy式自动提示优化足以 | 局部优化无法处理全局认知重构 |

**安装方式**：
1. 在Discussion中添加 `\subsection{Hypotheses and Falsification}`
2. 显式写出H₁/H₂/H₃的正式声明
3. 描述淘汰实验设计（Architectural Plasticity Stress Test）
4. 给出证伪标准和先验预测
5. 在Limitations注出"该实验超出本文范围，是未来验证方向"

预期收益：唯一性 0.60 → 0.95（已验证，Synthos Cycle 43实测 +0.35🔥）

### PASS条件
- 可证伪性 ≥ 0.8（有明确淘汰实验）
- 具体性 ≥ 0.8（If X then Y，变量可操作）
- 有H₂和H₃替代假设

---

## Q4门：技术方案质量评估（P2后）

### NotebookLM Q&A

```bash
notebooklm ask "请评估技术方案质量：

1. 可行性(0-1): 现有资源可实现?
2. 对齐度(0-1): 直接响应研究假设?每步有验证对象?
3. 完整性(0-1): 数据→预处理→模型→评估→部署完整?
4. 可复现性(0-1): 每步详细到别人可复现?

**【必答】如果任何维度<0.8，请给出具体补救方案：**
- 可行性不足：哪个环节不可行?替代方案?
- 对齐度不足：哪步与研究假设不对应?
- 完整性缺失：缺什么环节?怎么补?
- 可复现性不足：哪步描述不够详细?缺什么参数？"
```

### 补救实战指南（系统论文已验证，Synthos Cycle 43）

#### 可复现性不足（<0.85）的修复策略

可复现性不足是系统论文最常见的拒稿原因。**三件事必须补充**：

**1. 添加完整SKILL.md示例（附录）**
```
\appendix
\section{SKILL.md Example: [关键原子]}
\label{app:skillmd}

\begin{verbatim}
---
name: [原子名]
version: [版本号]
io:
  input: ...         # JSON Schema
  output: ...        # 输出格式
procedure:
  step_1: ...        # 自然语言步骤
  step_2: ...        
  verdict: ...       # 决策规则
---
\end{verbatim}
```
必须展示：YAML frontmatter、I/O Contract、Procedure——证明不是Python代码在背后执行。

**2. 补充实现细节（Implementation Details）**
```
\subsection{Implementation Details}
\label{sec:implementation}

\textbf{LLM Configuration.} [模型版本]，[各原子温度设定]
\textbf{Evolution Engine Prompt Protocol.} 
- DIAGNOSE输入：[指标+原子全文+历史教训]
- IMPROVE输出：[输出直接写入磁盘→无Python中间层]
\textbf{Benchmark Protocol.} 
- [benchmark套件数]，[每套件用例数]
- [执行方式，如作为Hermes Agent skill_view命令]
```

**3. 解释运行底座（Runtime Substrate）**
必须释明：声称"零Python"的系统究竟如何执行SKILL.md文件。
```
\subsection{Runtime Substrate and Zero-Python Execution}

通过[运行时名]提供的声明式工具调用底座执行：
- 路由指令 → [运行时]原生解析为 tool_call
- API调用 → 声明式curl命令（非Python SDK）
- 核心要点：认知架构严格为文本基认识论约束，无命令式代码
```
预期收益：可复现性 0.75 → 0.90+

### PASS条件
- 可行性 ≥ 0.7
- 对齐度 ≥ 0.8
- 完整性 ≥ 0.7

---

## Q5门：论文7维质量评审（P4）

### NotebookLM Q&A

```bash
notebooklm use <project_id>
cat paper.tex | notebooklm note create "Paper v<N>"
notebooklm ask "7维SCI质量评审：科学贡献/方法学/结果/完整性/清晰性/新颖性/引用。
每维评分(0-1)+改进建议。

**【必答】评分<0.85的维度给出具体的修改建议：**
- 问题在哪?需要补充什么内容/调整什么论证?
- 建议的LaTeX代码或段落改写？"
```

### 评分校准
NotebookLM评分通常偏高+0.05~0.15，视为"上限分数"。投稿前须用 sci-paper-quality-review 做独立校准。

### 修订优先级（已验证收益排序）

| 优先级 | 操作 | 预期收益 | 复杂度 |
|:-------|:-----|:--------:|:------:|
| 1 | D2：添加形式化方程+算法伪代码 | +0.10~0.15 | 中 |
| 2 | D3：追加数据点+收敛分析 | +0.05~0.10 | 中 |
| 3 | D7：系统论文GitHub引用策略（见下方） | +0.10~0.20 | 中 |
| 4 | D1/D4/D5/D6：叙事重构+深度补充 | +0.03~0.05/维 | 高 |

### D7 关键补救：系统论文的 GitHub 引用策略

**问题**：描述 AI 系统/框架的论文（如 Synthos、框架类论文）天然依赖大量 GitHub 项目引用。这些引用没有对应学术论文时，D7 评分会低至 0.75，拉低总分。

**诊断阈值**：当引用列表中 GitHub/网页链接占比 > 30%，D7 评分通常 ≤ 0.80。

**三步修复法（已验证 Synthos 系统论文，预期收益 +0.10~0.20）**：

1. **寻找替代学术文献** — 对每个 GitHub 引用，优先寻找对应的学术论文：

| GitHub 项目 | 替代方案 | 检索策略 |
|:------------|:---------|:---------|
| GPT-Researcher | 引用通用 Agent 综述（如 Wang et al. survey）覆盖 | 用 survey 论文替代单独引用 |
| Sakana AI Scientist | 已经发表 arXiv 论文 | 直接替换为 arXiv ID |
| Claude Code / LangChain / LangGraph | 引用底层原理论文（Constitutional AI / LLM 编排） | Anthropic 有 Constitutional AI 论文支撑 |
| DeepResearchAgent / ARIS | 如果有对应的 arXiv 预印本 → 替换；否则保留 GitHub 但移除⭐标记 | 搜索项目 README 是否引用自身论文 |
| AI-Research-SKILLs / Hermes Agent | 保留 GitHub 引用但格式化规范化 | 无学术论文时可保留 |

2. **清洗剩余 GitHub 引用**：
   - 移除所有 `⭐N` 标记（这是审稿人的致命否定信号）
   - 将 `[Online]. Available: \url{...}` 合并到学术格式中，而非独立引用
   - 格式范例：
   ```latex
   % 错误（当前）：
   \bibitem{gptresearcher}
   A. Elovic, ``GPT Researcher,'' 2024. [Online]. Available: \url{https://github.com/assafelovic/gpt-researcher}. ⭐27,000.
   
   % 正确：
   \bibitem{wang2024surveyagent}
   L. Wang et al., ``A Survey on Large Language Model based Autonomous Agents,'' \textit{arXiv:2308.11432}, 2024.
   ```

3. **引用格式规范化** — 剩余必须保留的 GitHub 引用使用正式软件引用格式：
   ```latex
   \bibitem{projectname}
   A. Author, ``Project Name: Short Description,'' \textit{GitHub repository}, YYYY. [Online]. Available: \url{https://github.com/user/repo}.
   ```
   - 无 `⭐` 标记
   - 有正式标题（非 repo 名直贴）
   - 有简短描述说明项目做了什么
   - 作为二线引用（在一线学术论文之后）

**系统论文特殊检查**：每条 GitHub 引用应有对应的同行评审学术文献作为理论支撑。例如 Claude Code 引用的背后是 Constitutional AI 论文，LangGraph 引用背后是状态机/图灵机相关文献。在 Introduction 中建立这些理论锚点可以显著提升审稿人印象。详见 `references/system-paper-citation-strategy.md`。

### Q5关键补救模式（Synthos Cycle 43已验证）

**P0：补充定量对比结果（方法学/结果≤0.85时必做）**

顶级期刊拒绝纯架构陈述。必须用硬数据证明优于现有基线：

```latex
\subsection{Quantitative Output Quality Validation}
\label{sec:quantitative}

To rigorously evaluate against existing baselines, we adopt [基准框架]...

\begin{table}[h]\centering
\caption{Quantitative comparison.}\label{tab:paper_quality}
\small
\begin{tabular}{lccc}\toprule
\textbf{Metric} & \textbf{[基线A]} & \textbf{[基线B]} & \textbf{本系统}\\
\midrule
[Metric 1] & X\% & Y\% & \textbf{Z\%}\\
[Metric 2] & X/100 & Y/100 & \textbf{Z/100}\\
\bottomrule
\end{tabular}
\end{table}
```

常见指标矩阵：Citation F1、LitReview 6-Axis Score、Hypothesis Falsifiability、Hallucination Rate

**P1：解释运行底座机制（方法学≤0.85时必做）**

见Q4补救实战指南的"Runtime Substrate"段落。

**P2：附录补充（可选）**
- 一条完整的认知推理示例（含置信度计算过程）
- 补充JSON Schema定义

---

## 质量门失败时的决策树

```
Q1-Q4任意维<阈值?
    ├── 是 → 执行【必答补救方案】→ 补充来源/修改内容 → 重新评估 → PASS→继续
    │                               ↓                     ↓FAIL
    │                         最多3轮补救             升级问题/降级目标
    │
    └── 否 → PASS → 进入下一阶段

Q5 avg<目标期刊阈值?
    ├── 是 → 按修订优先级开始修订循环(不等待确认)
    │       每轮: 修改→重编译→上传→重评审
    │       连续3轮无进展(<+0.02/轮) → 降级目标期刊
    │
    └── 否 → PASS → P5发布
```

## 实战记录保存

```bash
# 1. 评分摘要 → outputs/papers/papers-to-notebooks.md → 质量评审记录节
# 2. 详细建议 → <paper-dir>/notebooklm-review.md
```

已有实战记录：
| 论文 | Q1 | Q2 | Q3 | Q4 | Q5 | 平均 |
|:-----|:--:|:--:|:--:|:--:|:--:|:----:|
| PIMA CRISP-DM | 0.975 | 0.925 | 0.93 | 0.94 | 0.95 | 0.93 |
| Iris_YOLO | — | — | — | — | 0.89 | 0.89 |
| Synthos系统论文 | 0.925 | 0.937 | 0.95 | 0.90+ | **0.936** | **0.93** |

† Synthos Q2: 初评 0.75(非平凡性)+0.80(连续性) → 范式转移修复（Imperative Evolution Lock-in）+ 过渡段 → 终评 0.95+0.95。关键：非平凡性不是特征堆叠而是架构瓶颈论证。
‡ Synthos Q3: 初评 0.75(可证伪性)+0.60(唯一性) → H₁/H₂/H₃ + Architectural Plasticity Stress Test → 终评 0.95+0.95。关键：提出两个最强替代假设并设计淘汰实验。
