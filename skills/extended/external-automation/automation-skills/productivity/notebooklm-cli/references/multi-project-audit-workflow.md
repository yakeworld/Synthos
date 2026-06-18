# Multi-Project NotebookLM Research Audit Workflow

> 2026-05-25 实战验证：62个笔记本的系统化扫描和评估
> 2026-05-26 升级：增加研究空白/假设/论文/数据挖掘完成度四维评估框架

## Trigger

当用户要求"查看 NotebookLM 中所有项目"、"分析研究项目"、"整理研究空白和论文计划"时。

## Workflow

### Phase 0: Source Count Inventory（前置摸底）

先快速获取每个核心项目的源文件数量，评估数据底座厚度：

```bash
# 获取所有核心项目的source count
for pid in <project_id_1> <project_id_2> ...; do
  notebooklm source list -n "$pid" --json 2>&1 | grep '"count"' | head -1
done
```

**经验阈值：**
| 源文件数 | 评估 | 数据挖掘潜力 |
|:---------|:-----|:-------------|
| ≥100 | 🔥 厚资料库 | 可深入挖掘多个子方向 |
| 30-99 | ✅ 中等底座 | 可支持1-2篇论文 |
| 5-29 | ⚠️ 薄底座 | 需补充源或探索性分析 |
| 0-4 | ⏳ 刚起步 | 仅作方向记录 |

### Phase 1: Full Scan & Domain Categorization

```bash
notebooklm list
```

Categorize notebooks into research domains (e.g., BPPV/Vestibular, 3D Eye Tracking, VOR Digital Twin, PD, Medical AI, Teaching).

**Priority: focus on Owner notebooks first** (they contain user's original work). Shared notebooks may contain reference papers only.

### Phase 2: Structured Project Probe（核心四问）

对每个核心项目，用**标准化模板**探查。**不同项目可并行执行**（NotebookLM不同项目有独立会话）：

```bash
# 并行安全：每个notebook有独立会话，不会串话
notebooklm use <id_A> && notebooklm ask "..."   # 项目A
notebooklm use <id_B> && notebooklm ask "..."   # 项目B（可同时跑）
```

#### 标准探针模板（Gap→Hypothesis→Papers→DataMining→TeachingValue）

```bash
notebooklm use <project_id>
notebooklm ask "分析此笔记本。请逐项回答：

1. 研究空白（Research Gaps）：从源文件中提炼出了哪些核心Gap？是否存在尚未解决的瓶颈？
2. 科学假设（Falsifiable Hypotheses）：形成了哪些可证伪的假设？(If X then Y + 淘汰标准)
3. 论文产出（Papers）：已产出了哪些论文和手稿？逐篇列出(标题+状态：已发表/已投稿/已完稿/策划中)
4. 数据挖掘完成状态（Data Mining Status）：哪些部分已充分分析？哪些部分仅初步探索？哪些待补充？
5. 教学示范价值（Teaching Value）：这个项目适合作为教学案例吗？理由？

简明分点列表，每点控制在2-3句。"
```

> **注意**：共享（Shared）笔记本中的论文列表**包含参考文献**，必须过滤作者。详见Phase 3的Author Filter。但研究空白和假设分析可以直接用，不依赖作者过滤。

### Phase 3: Author Filter（论文归属确权）

**Gemini reports ALL papers in a notebook, including references — not just the user's own.** Each project MUST be filtered by author.

Standard filter:

```bash
notebooklm ask "逐个检查笔记本中每个源文件的作者字段。只列出作者明确包含 Xiaokai Yang 或 杨晓凯 的论文。没有的话说无。"
```

**三字符串搜索法：**
1. `Xiaokai Yang`（全名）
2. `Xiao-kai Yang`（连字符格式）
3. `Yang XK`（缩写格式）
4. 加机构名交叉验证：`Wenzhou People's Hospital`

### Phase 4: Paper vs Document-Section Distinction

After author matching, verify:

```
Distinguish:
(1) Published/submitted papers
(2) Completed manuscripts (full IMRaD)
(3) Patent document sections (NOT independent papers)
(4) Research directions only (not written yet)
Do NOT count multiple sections of the same patent as multiple papers.
```

### Phase 5: Multi-Paper Potential Matrix（每项目不限于一篇论文）

评估每个项目可衍生的论文数量：

| 场景 | 可衍生篇数 | 典型模式 |
|:-----|:----------:|:---------|
| 厚资料库+充分挖掘 | 3-5+篇 | 方法论1篇 + 实证1篇 + 综述1篇 + 教学1篇 |
| 中等底座+充分挖掘 | 1-3篇 | 核心方法1篇 + 拓展应用1篇 |
| 薄底座+初步探索 | 0-1篇 | 综述/视角论文1篇 |
| 教学项目 | 1-2篇 | 教学设计+成效评估 |

### Phase 6: Teaching/Demonstration Value Assessment（教学示范价值评估）

评估每个项目是否适合作为教学案例，关键维度：

| 维度 | 高(⭐⭐⭐) | 中(⭐⭐) | 低(⭐) |
|:-----|:---------|:--------|:------|
| 数据完整性 | 完整全流程可复现 | 部分流程可复现 | 仅理论框架 |
| 教学大纲 | 有完整学时分配 | 有框架无分配 | 无教学设计 |
| AI融合度 | 展示人机协作+伦理 | 仅工具使用 | 无AI集成 |
| 学科覆盖面 | 跨多学科 | 单学科 | 单一技巧 |

## Research Project Audit Report Template

完成全部探查后，按以下模板汇总：

```
### Domain 1: [领域名称]（成熟度评估）

| 项目 | 源文件 | 数据挖掘状态 | 教学价值 |
|:-----|:------:|:-----------:|:--------:|
| [名称] | N | ✅🔥/⏳ | ⭐⭐⭐ |

**已产出论文：N篇已发表 + N篇投稿中 + N篇完稿待投 + N篇策划**

**核心Gap已攻克：** [清单]

**待深入方向：** [清单]

**核心假设：** [清单]
```

### Data Mining Completion Level（统一分级标准）

| 标记 | 完成度 | 含义 | 典型特征 |
|:----:|:------:|:-----|:---------|
| 🔥 | ≥95% | **数据挖掘完成** | 核心算法已验证、多数据集充分分析、论文已产出 |
| ✅ | 70-94% | **充分挖掘** | 主要算法就绪、部分数据已处理、有待补充维度 |
| ⚠️ | 30-69% | **部分挖掘** | 理论框架完整、代码就绪、关键临床数据待采集 |
| ⏳ | <30% | **待挖掘** | 仅论文设计/申报书阶段、尚无实际数据 |

## Known Pitfalls

| Pitfall | Fix |
|:--------|:-----|
| Reference papers reported as user's | Always specify author name in filter |
| Abbreviation confusion (Yang X) | Cross-verify with institution (Wenzhou People's Hospital) |
| Document sections counted as papers | Instruct Gemini to distinguish patent sections vs standalone papers |
| Same preprint in multiple notebooks | Deduplicate by title |
| **Shared笔记本不含用户创新** | Shared项目可能仅引用，核心创新在Owner笔记本中 |
| **单项目可衍多篇论文** | 不要将"一个Notebook"等同于"一篇论文"；厚资料库可多篇 |
| **教学项目需要源文件支撑** | 教学示范需要足够源文件（>30个）才有说服力 |
