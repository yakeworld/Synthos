# 写作管线质量闸门规范 (v2.0)

> 验证 SynthOS 写作管线是否按规程执行，而非"模拟输出"。
> **每原子执行后必过对应闸门，不过不放行。**
> 用于 quality-gate 的「规程遵从性」维度，以及 evolution 的「写作管线 BENCHMARK」。

## 核心原则

**"按规程执行" ≠ "产生正确输出"**。前者是过程正确，后者是结果正确。过程正确是结果正确的必要但不充分条件。

| 情形 | 判定 |
|:-----|:-----|
| 原子输出正确但未加载SKILL.md | ❌ 不合格 — 这是模拟，不是调用 |
| 原子加载了SKILL.md但步骤执行有偏差 | 🟡 部分合格 — 需记录偏差 |
| 原子加载SKILL.md、按步骤执行、保存输出 | ✅ 合格 |

## 导则：管线 + 闸门总览

```
ACQ ──[G1]──→ EXT ──[G2]──→ ASC ──[G3]──→ HYP ──[G4]──→ ARG ──[G5]──→ VER ──[G6]──→ latex ──[G7]──→ ✅
```

每个闸门(G1-G7)是**二元的**：通过才放行，不通过就回退修复。

**一次一件事规则**：不跳步、不并行。不过前一门，不进下一阶段。

```
G1通过 → 只做EXT → G2通过 → 只做ASC → G3通过 → 只做HYP → G4通过 → 只做ARG → G5通过 → 只做VER → G6通过 → 只做latex → G7通过 → ✅
```

---

## G1: ACQ → EXT 闸门（搜索+PDF质量门）

### 检查清单

> **⚠️ 阈值按论文类型调整**: 系统综述/meta分析用以下标准。方法学论文(如新算法、新架构)只需 ≥5篇竞争对手论文建立对比矩阵，无需60篇候选。临床研究需≥30候选/≥20PDF。

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 1.1 | 搜索是否真实 | API调用记录存在 (S2/PubMed/Crossref) | 至少1个API有返回 |
| 1.2 | 多关键词搜索 | ≥3个变体 | 核心词+同义词+方法学 |
| 1.3 | 候选论文数 | ≥60篇 | 去重后真实候选数 |
| 1.4 | PDF下载数 | **≥30篇成功**（>5KB有效PDF） | 检查 `pdfs/` 目录 |
| 1.5 | DOI覆盖率 | **被引用的论文100%有DOI** | `cited_doi_ratio = 100%` |
| 1.6 | PDF命名规范 | 全部为 `{BibKey}.pdf` | 检查文件名 |
| 1.7 | 候选信息完整 | 每篇有 bibkey/title/DOI/venue | raw_papers.json |

**不通过修复**：
- PDF < 30篇 → 补搜arXiv/OA期刊
- DOI覆盖率<80% → 补充PubMed/S2搜索
- 候选<60篇 → 补充关键词变体

---

## G2: EXT → ASC 闸门

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 2.1 | 输出文件存在 | `extraction_output.json` | 文件非空 |
| 2.2 | 覆盖度 | 至少覆盖60%有PDF的候选 | 提取条目≥22篇 |
| 2.3 | 结构完整 | 每篇有摘要/方法/结论 | json结构完整 |
| 2.4 | 关键发现 | 每篇至少1个关键发现 | 发现字段非空 |

---

## G3: ASC → HYP 闸门

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 3.1 | 输出文件存在 | `association_output.json` | 文件非空 |
| 3.2 | 关联类型丰富 | ≥3种类型边（主题/方法/引用） | 类型字段存在 |
| 3.3 | 有聚类/分组 | 论文被分组到≥3个主题簇 | cluster字段存在 |
| 3.4 | 关键差距识别 | 至少指出1个研究空白 | 空白描述非空 |

---

## G4: HYP → ARG 闸门

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 4.1 | 输出文件存在 | `hypothesis_output.json` | 文件非空 |
| 4.2 | 可证伪性 | 假设有明确预测+证伪条件 | prediction + falsification字段 |
| 4.3 | 基于文献 | 假设引用至少3篇支持的文献 | evidence字段非空 |
| 4.4 | 新颖性 | 非简单重复已有工作 | 与现有工作有区别描述 |

---

## G5: ARG → VER 闸门（**最关键的门——引用质量**）

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 5.1 | 输出文件存在 | `argument-expression_output.json` | 文件非空 |
| **5.2** | **每篇引用都有PDF** | 所有 `\\cite{}` 有对应 `.pdf` | `cited_keys ⊆ pdf_bibkeys` |
| **5.2b** | **PDF文件类型验证** | `file pdfs/*.pdf` 全部返回"PDF document" | 无JavaScript/HTML伪文件 |
| **5.3** | **引用数量** | ≥30篇（全部有PDF） | count(citations) ≥ 30 |
| 5.4 | 引用真实性 | BibTeX的DOI/URL可解析 | 全部有真实DOI前缀 |
| **5.5** | **无虚构引用** | 所有bibkey在ACQ候选列表中 | `cited_keys ⊆ candidate_bibkeys` |
| 5.6 | 引用分布平衡 | 不集中在单一来源 | arXiv + OA期刊 ≥ 2种 |
| 5.7 | 引用必要性 | 每篇引用被讨论，非凑数 | 文中对每篇有描述 |

**不通过→必须重写引用部分**。虚假引用(不在候选) → 找到真实DOI或删除。无PDF引用 → 补下或删。

---

## G6: VER → latex-output 闸门

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 6.1 | 输出文件存在 | `viewpoint-verification_output.json` | 文件非空 |
| 6.2 | 6维评分 | 每维有明确分数 | 6个score字段 |
| 6.3 | 阈值 | 平均分 ≥ 0.85 | avg_score ≥ 0.85 |
| 6.4 | 引用验证 | 验证了引用完整性 | 有引用检查结果 |
| 6.5 | 逻辑连贯性 | 论文论点链完整 | coherence ≥ 0.8 |

---

## G7: latex-output → 完成（最终输出闸门）

| # | 检查项 | 判定标准 | 通过条件 |
|:-:|:-------|:---------|:---------|
| 7.1 | paper.tex存在 | ≥5000字符 | 文件大小 |
| 7.2 | references.bib存在 | ≥30条目 | 条目数 |
| 7.3 | 引用-条目匹配 | 每个 `\cite{}` 有对应BibTeX | bibkeys ⊇ cited_keys |
| 7.4 | 引用-条目1:1 | 无未使用条目 | cited_keys = bibkeys |
| 7.5 | 引用-PDF匹配 | 每篇引用有PDF文件 | cited_keys ⊆ pdf_bibkeys |
| **7.6a** | **唯一引用数=bib条目数** | 所有bib条目都被引用 | cited_keys == bib_keys |
| **7.6b** | **无未用条目** | 每篇引用在文中有对应论述 | `comm -23 bib_all cited_cited`为空 |
| 7.6 | LaTeX语法 | 无括号不匹配等 | 可解析 |
| 7.7 | pipeline_trace.json | 存在且完整 | 记录所有原子 |

---

## 反模拟铁律（v2.1 新增 — 最高优先级）

> 本节的优先级高于所有其他检查项。**模拟执行 = 闸门自动不通过，不论产出质量如何。**

### 定义

| 行为 | 判定 | 后果 |
|:-----|:-----|:------|
| 未调用 skill_view() 但输出了该原子的产物 | ❌ 模拟执行 | 闸门不通过，全管线标记为"模拟"，不记录到 CHANGELOG |
| 调用 skill_view() 但执行步骤与 SKILL.md 不一致 | 🟡 偏差执行 | 记录偏差，修复后重检 |
| 调用 skill_view() + 按 SKILL.md 步骤执行 + 输出到正确路径 | ✅ 合规执行 | 可过闸门 |

### 证据要求

**pipeline_trace.json 必须为每个原子记录：**

```json
{
  "atoms": [
    {
      "name": "knowledge-acquisition",
      "skill_view_called": true,
      "skill_version": "1.5.0",
      "skill_view_path": "/media/yakeworld/sda2/Synthos/skills/knowledge-acquisition/SKILL.md",
      "steps_executed": ["Step 1: 多关键词搜索", "Step 2: API回退链", "Step 3: PDF下载"],
      "gate_passed": "G1",
      "gate_result": "pass"
    }
  ]
}
```

### 闸门检查项（每原子专属）

| 检查 | 如何验证 | 判定 |
|:-----|:---------|:-----|
| SKILL.md 已加载 | pipeline_trace 中有 `skill_view_called: true` | ✅/❌ |
| SKILL.md 版本记录 | pipeline_trace 中有 `skill_version` 字段 | ✅/❌ |
| 执行步骤已记录 | pipeline_trace 中有 `steps_executed` 数组 | ✅/❌ |
| 输出文件符合IO契约 | 检查输出 json 的字段名与 SKILL.md 的 output contract 一致 | ✅/❌ |

### 铁律

1. **无 skill_view 记录 = 门不通过，即使输出正确。** 不设例外。
2. 每次调用 skill_view() 后，立即在 pipeline_trace 追加记录（不是等全部完成再补）。
3. 如果原子不需要 SKILL.md（如纯机械操作），在 trace 中标注 `skill_view_required: false` 并写明原因。
4. 被用户抓到一次模拟 → 修复方式：重做该原子（不是补 trace 记录）。
5. 累计3次模拟被抓 → 全管线判定 FAIL。

## 加载/执行/输出阶段（所有原子通用）

### 加载阶段
- [ ] 该原子的 SKILL.md 已加载（通过 `head -5 <path>` 或 `skill_view(name)` 确认）
- [ ] 加载的版本号与 evolution-state 记录一致

### 执行阶段
- [ ] 上游输出文件已读取（非手动构造输入）
- [ ] 执行步骤遵循 SKILL.md 定义的流程（Step 1 → Step 2 → ...）
- [ ] 未跳过任何必选步骤
- [ ] 未添加 SKILL.md 未定义的替代路径

### 输出阶段
- [ ] 输出文件保存到 `<run_dir>/<atom-name>_output.json`
- [ ] 文件格式符合 SKILL.md 定义的 IO 契约
- [ ] `pipeline_trace.json` 已更新（atoms_executed + 时间戳）

---

## ACQ 原子专项检查（v1.5.0+ 铁律）

### 检索规范
- [ ] 使用了至少 **3 个不同关键词变体**（核心词 + 同义词 + 方法学 + 中英文 + 拓展词）
- [ ] 结果 < 5 篇时自动补搜（多关键词回退策略）
- [ ] 去重合并后的文献数量如实报告

### 速率限制
- [ ] S2 API: 每次 curl 调用后 sleep 1s（1次/秒）
- [ ] PubMed: sleep 0.5s 间隔（无key时3次/秒）
- [ ] 429 响应时 sleep 1s 后重试 1 次

### PDF 下载与命名
- [ ] PDF 已从arXiv/OA/PMC路径批量下载（优先arXiv直链→Frontiers→MDPI→F1000→JMIR→其他OA）
- [ ] PDF 文件名 = BibTeX key + `.pdf`（如 MLGym2025.pdf）
- [ ] 无法下载时标记 `pdf_status = "unavailable"` + 记录原因，**不纳入引用候选**
- [ ] 已下载有效PDF ≥ 30篇才进入下一步（G1闸门）
- [ ] BibTeX 保存到单一 `latex/references.bib`（非多个零散文件）

### 模拟防护（零容忍）
- [ ] 所有文献来源可追溯（真实 API 调用记录）
- [ ] 无虚构 DOI/标题/作者/摘要
- [ ] 0 篇结果不是错误——如实报告

---

## 常见失败模式

| 模式 | 表现 | 修复 |
|:-----|:-----|:-----|
| **候选有DOI但PDF=0** | ACQ搜出82篇，但pdfs/为空 | G1卡住 → 批量arXiv直链下载 |
| **引用虚构文献** | `\cite{SomePaper}` 不在raw_papers中 | G5卡住 → 查真实DOI或删除 |
| **引用数达标但无PDF** | 45篇引用，0篇PDF | G5卡住 → 必须PDF≥引用 |
| **PDF下载失败未标记** | 付费墙页面存为5KB.pdf | G1验证实际大小>5KB |
| **引用-条目不匹配** | bib有45条目，只引了37个 | G7卡住 → 清理未引用条目 |
| **汇编引用替代真实搜索** | 模型凭知识写BibTeX而非真实API | 无G1通过 = 管线不启动 |

## 使用方式
1. 完成每次原子执行后 → 运行对应闸门(G1-G7)
2. 闸门不通过 = 原子未完成 → 修复后再过门
3. 全部7门通过 = 管线完成
4. 4. **G7通过后 → 加载 sci-paper-quality-review 进行SCI内容评审**
5. 任何 FAIL 标记为质量缺口，在本轮修复而非推迟
