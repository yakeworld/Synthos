---
name: quality-gate
description: "⚡ P0 闸门技能。四层质量架构：①响应级漂移检查 ②项目级L1-L4交付闸门 ③论文管线G1-G7原子闸门 ④SCI内容评审。通用铁律：任务完成→质量评估→不达标→循环执行。无skill_view记录=门不通过。G5引用质量为最关键门。G7通过→自动sci-paper-quality-review。"
version: 2.23.0
priority: P0
signature: "deliverable: dict, context: dict -> quality_report: dict (L0-L4 scores + gate_pass: bool + fix_suggestions: list) -> trigger-loop signal"
related_skills: [project-experience-distillation, evolution, sci-paper-quality-review, paper-pipeline, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification, paperjury, citation-appropriateness-verification]
---

# Quality Gate — 质量闸门

> 一次一件事，达标才停。不是"做完了"，是"验证过才算"。

## 契约层 · BOUNDARY

**边界**：quality-gate 负责所有交付物和产出的质量验证。它不生产内容，只检查内容。
**范围**：L0 动灵层、L0.5 数据诚实门、L1 响应级、L2 项目级、L3 管线级、L4 内容级。
**不覆盖**：内容生产（由对应技能负责）、语义论证站得住脚（paperjury 负责）、引用实质恰当性（citation-appropriateness-verification 负责）。
**触发**：每次任务完成、每次管线阶段切换、每次提交前。
**退出**：所有检查通过（score ≥ 0.85），或循环修复后达到阈值。

## 契约层 · IO_CONTRACT

**输入**：交付物（论文/技能/代码/文档）、上下文（任务描述、阶段信息）。
**输出**：质量评估报告（L0-L4各层评分+通过/不通过判定+修复建议）、循环触发信号。

## 契约层 · EVIDENCE_SCHEMA

| 证据类型 | 来源 | 验证方式 |
|----------|------|----------|
| 形式正确性 | 编译日志、bib统计 | 自动扫描 |
| 引用恰当性 | 参考文献全文 | PDF内容校验+语义比对 |
| 数据可追溯 | 实验记录、代码、JSON输出 | 源文件检查 |
| 方向一致性 | 系统生长路径、进化日志 | 人工判断+方向检查 |

## 契约层 · CHANGE_LOG

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-18 | 2.9.2 | 新增L0.5数据诚实门；新增citation-appropriateness-verification引用检查两层法；新增submission-materials.md |
| 2026-06-18 | 2.9.3 | 技能审计发现质量闸门结构完整性仅20%，补齐BOUNDARY/EVIDENCE_SCHEMA/golden/CHANGE_LOG |
| 2026-06-22 | 2.9.4 | 新增三项铁律(凡引必验/凡数必源/代码必核)为L0.5执行前置；新增Codex-tmux调度协议；强化PDF不可达文献的处理策略：经典保留+标注，可替换用OA替代 |
| 2026-06-23 | 2.9.5 | 新增BBL/bib/tex同步检查陷阱；新增G2门后重新编译步骤；新增图真实性和数值一致性检查 |
| 2026-06-23 | 2.9.6 | 新增多源交叉验证铁律；新增消融值来自不同实验配置的检测模式；新增政府申报方案检查告警 |
| 2026-06-24 | 2.13.0 | 新增 state.json 内部不一致检测（top-level vs gates_result quality_score）；新增多JSON源 ensemble 成员交叉比对；新增 comprehensive-quality-report-template.md 参考文件 |
| 2026-06-24 | 2.13.2 | 新增单栏排版陷阱（表格超宽、图宽过大、对比表列溢出）；新增 references/single-column-layout-pitfalls.md | 新增通用tmux后台脚本协议（替代jupyter nbconvert等复杂编排）；新增Top-1模型主导Ensemble规则；新增LaTeX patch双转义反斜杠陷阱；扩充state.json内部不一致检测；保存comprehensive-quality-report-template.md |
| 2026-06-24 | 2.15.1 | 新增自主修复不问原则（用户纠正：自己做主不待批准）；新增 OpenML 基准对比作为 G4 数据完整性检查的扩展；新增 EuropePMC 作为 PDF 下载备用通道（Kapoor2023 实战验证）
| 2026-06-24 | 2.16.0 | 新增 OpenML Claim-Only 检测（G2.5子项）；新增统计量可追溯性检查（p-value/Cohen's d 需在代码中记录）；新增 PDF-bib DOI 不匹配检测（G5子项）；新增 JSON-to-JSON ensemble 三角校验（横向对比所有 JSON 的 ensemble 成员）；新增 references/codex-comprehensive-quality-report-workflow.md |
| 2026-06-24 | 2.17.0 | 新增 自主修复闭环协议（codex-comprehensive-quality-report-workflow.md Step 5）；新增 修复决策矩阵（可自主修复 vs 需人工）；新增 fix-log.md 模板；扩充 comprehensive-quality-report-template.md 增加"报告生成后的必做动作"警告
| 2026-06-24 | 2.18.0 | 新增 G6 论文约束系统检查框架：同实体跨位约束、声明-证据对齐约束、比较-基准对齐约束、叙事-数据比例约束。四种约束类型独立于具体论文领域。
| 2026-06-24 | 2.19.0 | 新增审稿人评价框架（Q1-Q6六问）：假说问、空白问、解法问、实验问、结论问、价值问。六问不取代G1-G7，而是将G1-G7发现组织到审稿人视角下。新增六问评分标准（60分制）与投稿判定。新增 references/skill-design-abstraction-levels.md 记录抽象层次方法论。
| 2026-06-24 | 2.20.0 | 调研 12 个建立已久的审稿框架（PROBAST/TRIPOD/Cochrane/AMSTAR2/EQUATOR 等），提取三项结构性改进待后续版本落地：领域级判定取代总分（Cochrane RoB2）、关键项一票否决（AMSTAR2）、论文类型识别→不同模板（EQUATOR Network）。新增 references/established-review-frameworks.md 和 references/paper-constraint-system.md。
| 2026-06-24 | 2.21.0 | 新增多模板多报告机制：每篇论文出多份独立报告（通用六域 + 类型专项 + 参考文献审查 + 检查员）。L0分类器根据标题/关键词分论文类型，加载对应模板。取消总分制，改为六域 PASS/SOFT/HARD 判定 + 关键项(L0.5)一票否决。新增四份报告并行输出结构。参考 established-review-frameworks.md。\n| 2026-06-24 | 2.22.0 | 新增检查员报告（第四份报告）：凡数必源矩阵 → 逐数值追踪源文件；凡引必查清单 → PDF存在性+DOI匹配+体裁验证三检；代码诚实验证 → 独立复现关键数字；虚构检测扫描 → 7种LLM虚构模式扫描。四条铁律在检查员报告中聚合成独立报告，不再作为L0.5门的附属项。报告模板全面重构为四报告并行格式。\n| 2026-06-25 | 2.23.0 | 从 ~/.hermes/skills/ 迁移到 Synthos/skills/core/；补 GOLDEN_SET.md + cases/expected/；更新 skill_registry.json。认知同步协议：任务文件不再嵌入技能内容→指向 Synthos 路径让 Codex 自主加载。七份参考文件整理到 Synthos 路径下。
## 三项铁律（L0.5 前置检查）

每次论文/交付物评估前，先过这三项基础铁律：

| # | 铁律 | 文言 | 检查方法 | 违反后果 |
|:-:|:-----|:----|:---------|:---------|
| 1 | **凡引必验** | 引不验则废 | 每篇引用须有可打开的全文字PDF。PDF不可达时：经典/核心文献保留并标注"需手动获取"；可替换文献必须用开放获取版本替代 | G5门不通过 |
| 2 | **凡数必源** | 数不源则诬 | 每个数值声明须映射到可执行代码的具体输出行(JSON/CSV/cell output)，不可仅凭论文文本信任 | L0.5门不通过 |
| 3 | **代码必核** | 码不核则妄 | 论文声称的实验必须实际运行验证，仅检查代码是否存在不够。独立复现差异>5%标记DATA_SUSPECT | 论文不进入投稿流程 |

**执行顺序**：L0.5 数据诚实门 → 先过三项铁律 → 再进入G1-G7闸门 → 最后L4内容评审。

**2026-06-22 实战教训**：PIMA论文参考文献27/37无PDF全文（72%缺失），未在第一时间触发"凡引必验"自动检查，导致后续引用替换工作被动。此为指导原则，非可选项。

## Codex 调度协议（与三项铁律并列）

> **User preference (2026-06-22)**: Codex 必须通过 tmux 后台运行，不得使用 delegate_task 等阻塞方式。理由：tmux 不阻塞主会话对话，delegate_task 超时600s且中间不可交互。

### 标准流程

bash
```
# 1. 创建会话
tmux new-session -d -s codex-<task_name> -c <workdir>
# 2. 启动 Codex（分两步send-keys：先文本，后Enter）
tmux send-keys -t codex-<task_name> 'codex --yolo'
tmux send-keys -t codex-<task_name> Enter
sleep 30
# 3. 发送指令（分两步：先文本，后Enter）
tmux send-keys -t codex-<task_name> '<one-line instruction>'
tmux send-keys -t codex-<task_name> Enter
# 4. 读取响应
tmux capture-pane -t codex-<task_name> -p | tail -30
# 5. 继续主会话对话，Codex在后台运行
```

### 何时用 Codex tmux vs 直接终端

| 场景 | 方式 | 理由 |
|:-----|:-----|:------|
| PDF批量下载 | Codex tmux | 非阻塞，边聊天边下载 |
| 论文质量检查 | Codex tmux | 长任务不打断对话 |
| 简单文件操作 | 直接 terminal | 一次调用即可 |
| 数据下载 | 直接 terminal | 可用 curl/wget |

详见 `codex-tmux-control` 技能。

### 通用 tmux 后台脚本协议（2026-06-24 新增）

**适用范围**：任何需要后台运行的实验/编译/下载任务。**优先于** delegate_task、jupyter nbconvert 等复杂编排。

**原则**：写最小独立脚本 → tmux 后台跑 → 继续对话。

```bash
# 标准模式
tmux new-session -d -s <task> -c <workdir>
tmux send-keys -t <task> "python3 /path/to/script.py" Enter
# 继续对话，之后回来检查
sleep 60 && tmux capture-pane -t <task> -p | tail -20
```

**用户偏好（2026-06-24）**：
> "能简单的就不要复杂；确保流程可重复；做事情要有方法学指导；具体工作用tmux放到后台去跑"

| 场景 | 推荐方式 | 理由 |
|:-----|:---------|:------|
| 单模型/Ensemble实验 | tmux + standalone .py | 3分钟，不阻塞 |
| 跨数据集扫描 | tmux + standalone .py | 批量，可查日志 |
| Notebook Run All | ❌ 避免 | jupyter依赖多，易失败 |
| LaTeX编译 | 直接 terminal | 30秒出结果 |

## 核心理念

| 白话 | 文言 | 义 |
|:-----|:---|:---|
| 无记录=门不通过 | **无录不过** | 无skill_view记录视为未执行 |
| G5引用质量最关键 | **引质为要，G5最重** | 论文质量上限=引用质量 |
| 一次一个维度 | **一维一渡** | 每次只聚焦一个等级，不跳步不并行 |
| 方向不对等于白做 | **向不正则功废** | 质量不只是技术合格，方向要与系统生长一致 |
| 论文数据必须可追溯到源 | **凡数必源，不源不取** | 无实验记录的数据声明=编造，不得进入评审 |
| 发现问题立即修复 | **发觉即修，不待问** | 质量审计发现的每个P0-P1问题必须立即修复，不可仅报告。修复优先级：数据诚实 > 引用完整性 > 图表真实性 > 格式优化。用户明确要求：发现问题的同时给出修改方案并执行，不要只写检查报告。所谓"质量检查"应当输出「已修复的版本」而非「待修复的问题清单」。如ROC/SHAP图缺失 → 用实验数据生成实际图并替换paper.tex；如数值不一致 → 找到正确数据源并修正论文；如CatBoost>Ensemble → 直接更新论文正文和结论中的表述，不做报告等用户指示。**能装的库直接装不问，代码逻辑错直接修不问，paper.tex直接改不问。** |
| 自主修复不问 | **自己做主，不待批准** | 质量报告出具后，P0/P1问题能修的自己动手修。用户明确纠正：不要写完报告等用户指示，自己去修 bib、改数字、清理残留文件、重编译。Kapoor2023 PDF 不对 → 下载正确的；OpenML 缺数据 → 查 API 补报告；bib orphan → 直接清理。修完发 PDF。**核心哲学：质量审查的输出是「已修复的论文」，不是「待修复清单」。** |

## 五层架构 + 动灵维度

| 层 | 范围 | 触发 | 动灵方向检查 |
|:---|:-----|:-----|:-------------|
| L0 动灵层 | 交付物/技能的方向与系统生长路径一致性 | 每次评估前 | ✅ 方向不对不进入技术检查 |
| **L0.5 数据诚实门** | **论文中每个可验证数据声明是否有源文件支撑** | **每次论文评审前** | ✅ 无源文件的数据声明必须删除或标记为理论推算 |
| **G2.5 实验完整性门** | **实验设计与数据可溯源的系统性检查** | **L0.5通过后 → L2评审前** | ✅ 实验流程设计完整才能进入项目级交付 |
| L1 响应级 | 当前会话输出质量 | PreResponse Hook | — |
| L2 项目级 | 交付物D1-D6 | 项目阶段完成 | ✅ 检查项目方向是否与系统生长一致 |
| L3 管线级 | 论文G1-G7原子闸门 | 写作管线每阶段切换 | ✅ G1前先问"这个论文方向符合系统当前生长方向吗" |
| L4 内容级 | SCI 7维评审 | G7通过后自动 | — |

**执行顺序**: L0 → L0.5 数据诚实门 → G2.5 实验完整性门 → **三要素评价（科学性/创新性/可行性）** → L1/L2/L3 → G1-G7闸门 → L4 内容评审。G2.5不通过则总评分上限50/100，不可标记"可投稿"。三要素不通过则论文价值判定为"方向不适合发表"。

## G5 引用质量评估（最新扫描数据 2026-06-18）

| 子门 | 阈值 | 通过情况 | 评价 |
|------|------|----------|------|
| D10a ≥ 95% | 95% | 70/72 (97.2%) | ✅ 优秀 |
| D10a = 100% | 100% | 70/72 (97.2%) | ✅ 优秀 |
| DOI ≥ 90% | 90% | 4/68 (5.9%) | ❌ 严重薄弱 |
| DOI ≥ 70% | 70% | 7/68 (10.3%) | ❌ 严重薄弱 |

**关键发现**: DOI覆盖率是G5引用质量的最薄弱环节。86.8%的论文bib条目无DOI元数据，使得参考文献不可追踪、不可验证。所有ODE/PINN论文系列（0xx/1xx命名）均无DOI。

**G5修复优先级**: 1) 为所有高D8论文补充DOI → 2) 修复D10a<95%的论文 → 3) 清理orphan/zombie引用

### PDF-参考文献DOI不匹配检测（2026-06-24 新增）

**问题**：references.bib 中的 DOI 与本地 PDF 文件的元数据（XMP/PDF header）中的 DOI 可能不同。当 PDF 从 Semantic Scholar 下载时，文件名可能是原文的 DOI 缩写，但实际内容可能来自不同期刊或同一作者的另一篇论文。

**检测方法**：

```bash
# 对每个 bib entry 中的 DOI，检查本地 PDF 元数据是否匹配
bib_file="01-manuscript/references.bib"
pdf_dir="06-references/"

# 方法1：检查 PDF 文件名中的 DOI 是否与 bib DOI 匹配
# 如果文件名是 Kapoor2024Leakage.pdf 但 bib entry journal 是 Patterns (doi:10.1016/j.patter.2023.100804)
# 而 PDF 元数据 Subject 字段显示 Nature Communications DOI → 不匹配

# 方法2：用 pdftotext + strings 检查 PDF 首页的关键词
for bibkey in $(grep '^@' "$bib_file" | grep -v '@comment' | sed 's/.*{//;s/,.*//'); do
    pdf=$(find "$pdf_dir" -name "${bibkey}*" -o -name "*${bibkey}*" 2>/dev/null | head -1)
    if [ -n "$pdf" ]; then
        bib_doi=$(grep -A 3 "${bibkey}" "$bib_file" | grep 'doi' | sed 's/.*{//;s/}.*//')
        pdf_doi=$(strings "$pdf" | grep -i 'doi' | head -3)
        if [ -n "$bib_doi" ] && [ -n "$pdf_doi" ]; then
            if echo "$pdf_doi" | grep -q "$bib_doi"; then
                echo "✅ $bibkey: bib DOi 在 PDF 元数据中"
            else
                echo "⚠️ $bibkey: bib DOI=$bib_doi, PDF 元数据含=$pdf_doi"
            fi
        fi
    fi
done
```

**PIMA实战案例（2026-06-24）**：
| 条目 | bib DOI | PDF 元数据 DOI | 来源 |
|:-----|:--------|:---------------|:-----|
| Kapoor2023Leakage | 10.1016/j.patter.2023.100804 (Patterns) | 10.1038/s41467-024-46150-w (Nature Communications) | ❌ 不匹配 |
| 其他 28 篇 | 匹配 | 匹配 | ✅ |

**修复**：
- 若 PDF 内容正确但 bib 的 DOI/journal 错误 → 修正 bib entry 以匹配加载的 PDF
- 若 PDF 内容完全是另一篇文章 → 重新下载正确 PDF

**规则**：G5 引用真实性检查必须包含 PDF 文件与 bib entry 之间的 DOI 交叉验证，不限于 D10a 覆盖率检查。

引用检查有**两个层次**，必须区分：

| 层次 | 检查内容 | 工具/方法 | 自动化程度 |
|------|----------|-----------|------------|
| **形式检查** | D10a覆盖率、孤儿引用、僵尸引用、DOI存在性、格式正确性 | `paper-references-scanning` + `reference-verification` | ✅ 全自动 |
| **实质检查** | 引用是否得当——文献是否真的支持论文中的论断 | `citation-appropriateness-verification` | ⚠️ 半自动 |

**G5检查流程**:
0. **第零步（新增 — 引用存在性验证）**: 在进入任何引用质量检查前，必须先验证参考论文**是否真实存在**。LLM常虚构参考文献，尤其文献综述表（Table 1）。三步过滤器：
   - Level 1: 查本地 PDF 目录（`enhanced_bibtex/pdfs/`）— 有 PDF 则高可信，无 PDF 则高危
   - Level 2: SS/Crossref API 查询 — 无记录则标记虚构 ❌
   - Level 3: `pdftotext` 读 PDF 首页确认期刊名 + DOI + 实际指标 — 防止下载到同名不同内容的论文
   - **保留策略**: 只保留有 PDF + SS 可验证的论文。3-4 篇即可，不必填满表。被 PLOS ONE 发 Expression of Concern 的论文需标注或删除。
   - **虚构信号**: Acc>95%(PIDD)、Acc=100%、所有指标同时最优、SS无记录、多篇同主题无PDF。
1. 第一步（自动）：`paper-references-scanning` 检查 D10a≥95%、孤儿=0、僵尸=0、DOI≥90%
2. 第二步（自动）：`reference-verification` 验证DOI存在性和格式正确性
3. 第三步（半自动）：`reference-verification` PDF内容校验 + 错误PDF修复
4. **第四步（引用实质恰当性 — 必经）**：`citation-appropriateness-verification` 逐篇阅读PDF全文 → 引用功能分类（背景/方法/支撑/争辩/装饰）+ 引文性能基准提取 + 引文网络分析 → 逐篇审查报告。**引用恰当率 ≥ 80% 且装饰引用 ≤ 10% 方可通过。**
5. **重编译步骤**（P0 — 引用清理后必须执行，否则审查的是过期PDF）：
   a. 清理辅助文件：`rm -f *.aux *.bbl *.blg *.out *.spl`
   b. 执行 `pdflatex → bibtex → pdflatex → pdflatex` 三轮编译
   c. 交叉验证新 BBL 与当前 bib 一致性（命令见 BBL/bib/tex 同步陷阱）
6. 第五步（验证）：重新运行 `paper-references-scanning` 确认 D10a ≥ 95%
7. **判定**：G5通过条件 = D10a ≥ 95% AND 引用恰当率 ≥ 80% AND 装饰引用 ≤ 10%

**PDF文件错误陷阱**: DOI-based下载可能匹配错误内容。ICCVW论文中因DOI相似性下载到OLED/光纤传感器文章而非虹膜分割论文。**修复方案**：①批量下载后用`strings`搜索论文主题关键词快速验证 ②优先通过Semantic Scholar查询openAccessPdf ③从arXiv下载开放获取版本。详见 `reference-verification/references/pdf-corruption-fix-workflow.md`。

**2026-06-18教训**: 形式检查全部通过后，用户指出"引用是否得当"需要**逐篇阅读文献全文再核对论断**。这是质的要求，不是量的要求。**由此创建新技能 `citation-appropriateness-verification`**。详见 `citation-appropriateness-verification/SKILL.md`。

**BBL/bib/tex同步陷阱 （2026-06-23实战教训）**: 编辑 `references.bib`后（增删条目），若不重新编译LaTeX，`paper.bbl`（BibTeX输出）**保持旧版本**。这导致：
  - paper.pdf 的参考文献列表包含**已被删除的虚构条目**（如 Amri2025, Saeedi2019 WITHDRAWN）
  - paper.pdf 的引用号/内容与实际 bib 失步
  - 审稿人检查PDF引用列表时会看到当前 bib 中不存在的条目

**检测方法**：
```
1. grep '^@' references.bib | sed 's/.*{//;s/,.*//' | sort -u > /tmp/bib_keys
2. grep 'bibitem{' paper.bbl | sed 's/.*{//;s/}.*//' | sort -u > /tmp/bbl_keys
3. comm -23 /tmp/bbl_keys /tmp/bib_keys   # BBL有但bib已无→删除残留
4. comm -13 /tmp/bbl_keys /tmp/bib_keys   # Bib有但BBL无→需重编
```

**修复**: 每次完成引用增删后，清理辅助文件（`rm -f *.aux *.bbl *.blg *.out *.spl`），重跑 2-3 轮 `pdflatex → bibtex → pdflatex → pdflatex`。

**注意**: 引用得当性检查无法用脚本完全替代。API能找文献，但无法读全文判断论断一致性。PDF内容校验可用`strings`快速抽查。**用户将引用检查定为铁律，不可跳过。**

### LaTeX 编译陷阱：`\\\\\\\\%` 导致数学模式被截断（2026-06-24 新增）

**问题**：Python/NotebookLM 生成 LaTeX 时，`$...%$`（数学模式内的百分号）常被双转义为 `$...\\\\\\\\%$`。

**检测方法**：grep 反斜杠模式。

**修复**：用 Python 而非 sed。

**Pitfall: patch 工具双转义 LaTeX 反斜杠（2026-06-24 新增）**

编辑 LaTeX 文件时，patch 工具可能将 `\cite` 双转义为 `\\cite`、`\texttt` 双转义为 `\\texttt`、`\Phi` 双转义为 `\\Phi`。这是因为 patch 的模糊匹配对反斜杠的处理与 LaTeX 解释器不一致。

**检测**：patch 后重新编译，或用 `grep '\\\\\\\\cite' paper.tex` 检查是否有双写反斜杠。

**修复**：
```bash
# 全局修复：\\\\X → \\X
python3 -c "
with open('paper.tex') as f:
    c = f.read()
# 修复双转义的反斜杠命令
import re
# 找到 \\\\ 后面跟字母的情况（\\cite, \\texttt 等）
c = re.sub(r'\\\\\\\\([a-zA-Z])', r'\\\\\1', c)
with open('paper.tex', 'w') as f:
    f.write(c)
"
# 然后重新编译
rm -f *.aux *.bbl *.blg *.out
pdflatex ... bibtex ... pdflatex ... pdflatex
```

**PIMA案例（2026-06-24）**：patch SHAP分析段落时 `\cite{Lundberg2017SHAP}` 被双转义为 `\\cite{Lundberg2017SHAP}`，导致编译报未定义的引用。

**PIMA案例（2026-06-24）**：paper.tex 的 abstract、contributions、ablation 等 11 处 `\\\\\\\\%` 全部引发数学模式截断，修复后编译通过。

### 单栏排版陷阱（2026-06-24 新增）

**问题**：将论文从 elsarticle 双栏(`3p,twocolumn`)改为单栏(`3p`)后，表格可能溢出列宽，图也可能过大。

**检查列表**：

| 检查项 | 方法 | 
|:-------|:-----|
| 多列表格溢出 | `strings paper.log \| grep "Overfull.*hbox"` |
| 无resizebox的保护表格 | `grep -c '\\\\begin{tabular}' paper.tex` 与 `grep -c '\\\\resizebox' paper.tex` 对比 |
| 单栏图宽过大 | `grep 'includegraphics\[width=0.9' paper.tex` |
| 新增指标列导致表格超宽 | 缩短列标题，用`—`替代长文本 |

**修复**：
- 5列以上表格包 `\resizebox{\columnwidth}{!}{% ... %}`
- 单栏图宽：ROC曲线用 `0.70\columnwidth`，柱状图用 `0.60\columnwidth`
- 缩短列标题（"Claimed Accuracy"→"Accuracy"；"Leakage Prevention"→"Leakage"）
- 对比表中其他研究的F1值用 `—` 标记（非 "N/R"）

详见 `references/single-column-layout-pitfalls.md`。

### 重编译后检查：`\\node` 变成 `\\\\node`（2026-06-24 新增）

**问题**：TikZ 图的 `\node` 命令在行首可能因文本处理被双写为 `\\node`。`\\node` 被解析为 `\\`（换行）+ 文本 `node`，而非 `\node` 命令，导致 TikZ 解析失败。

**检测**：`grep -n '^\\\\node' paper.tex` — 命令在行首应为 `\node`（单个反斜杠）。

**修复**：`sed -i 's/^\\\\node/\\node/' paper.tex`

### Ensemble 成员一致性检查（2026-06-24 新增, 2026-06-24 更新: Top-1主导规则）

**问题**：验证数值一致性时，仅检查 F1 值不足以发现隐患。

**检测方法**：对比 JSON 与 paper.tex 中的 ensemble 成员列表。

**Top-1 模型主导规则（2026-06-24 新增）**：如果单模型基准中 CatBoost（或任一外部框架）的 F1 显著高于所有 sklearn 模型（如 CatBoost F1=0.7067 > GBC 0.6868, +2.9%），则 Ensemble 必须以该模型主导，除非有明确理由（如LDA的线性互补性）。禁止论文声称的 Ensemble 成员与实验 JSON 中不一致。

**检查步骤**：
1. 从 experimental JSON 获取 top-1 单模型
2. 提取论文声称的 Ensemble 成员
3. 若 top-1 不在 Ensemble 中 → 标记 ⚠️ ENSEMBLE_MISSING_BEST
4. 若论文 Ensemble 成员与 JSON 中运行的任何 Ensemble 不匹配 → 标记 ⚠️ ENSEMBLE_MEMBER_MISMATCH
5. 如有不匹配 → 必须重新运行实验验证（用 tmux + 独立脚本，不要手工改数字）若 `all_results.json` 的 ensemble 由 `[GBC, LDA, LR]` 组成，但论文声称 `[CatBoost, GBC, LR]`，即使 F1 相近（0.6857 vs 0.6993），这两个"ensemble"是不同的实验产物——不能互相作为数值验证源。

**检测方法**：
```python
# 对比 JSON 中 ensemble member 与论文 claim 是否一致
json_models = results['ensemble_soft_voting']['models']  # ['GBC', 'LDA', 'LR']
paper_claims = 'CatBoost+GBC+LR'  # 从 paper.tex 提取
if set(json_models) != set(paper_claims.split('+')):
    print('⚠️ ENSEMBLE_MEMBER_MISMATCH:')
    print(f'  JSON: {json_models}')
    print(f'  Paper: {paper_claims}')
```

**规则**：L0.5 数值检查必须包含 **成员组成** 的比对，不仅是数值比对。组成不同则数值比对无意义。

**多JSON源交叉比对陷阱（2026-06-24 新增, 2026-06-24 更新: JSON-to-JSON 三角校验）**: 实验代码目录下可能有多个 JSON 文件（comprehensive_results.json, definitive_ablation.json, notebook_trace_final.json, catboost_ensemble.json 等），不同 JSON 可能定义了不同的 ensemble 成员。即使两个 JSON 的 F1 值相近（如 0.6986 vs 0.6878），若成员不同（GBC+LDA+SVC vs LDA+GBC+LR），则不能互相作为数值验证源。此外，paper.tex 可能声称第三种成员组合（如 CatBoost+GBC+LR）。**检测方法：**

```bash
# 从所有 JSON 文件中提取 ensemble 成员信息并进行两两对比
python3 << 'EOF'
import json, os, glob
from itertools import combinations

def find_ensembles(obj, path='', results=None):
    if results is None:
        results = {}
    if isinstance(obj, dict):
        if 'models' in obj and isinstance(obj['models'], list):
            results[f"{path}.models"] = obj['models']
        if 'ensemble' in obj and isinstance(obj['ensemble'], dict):
            if 'models' in obj['ensemble']:
                results[f"{path}.ensemble.models"] = obj['ensemble']['models']
        for k, v in obj.items():
            find_ensembles(v, f'{path}.{k}', results)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_ensembles(v, f'{path}[{i}]', results)
    return results

all_ensembles = {}
for f in sorted(glob.glob('03-code/**/*.json', recursive=True)):
    try:
        with open(f) as fh:
            d = json.load(fh)
        ensembles = find_ensembles(d)
        for path, members in ensembles.items():
            key = f"{f}/{path}"
            all_ensembles[key] = members
    except: pass

# 输出所有发现的 ensemble 成员
print(f"找到 {len(all_ensembles)} 个 ensemble 定义:")
for src, members in all_ensembles.items():
    print(f"  {src}: {members}")

# 两两对比
sources = list(all_ensembles.keys())
for i, j in combinations(range(len(sources)), 2):
    m1, m2 = set(all_ensembles[sources[i]]), set(all_ensembles[sources[j]])
    if m1 != m2:
        print(f"\n⚠️ ENSEMBLE_MEMBER_MISMATCH:")
        print(f"  源1: {sources[i]} → {m1}")
        print(f"  源2: {sources[j]} → {m2}")

# 检查 paper.tex 中的 ensemble 声称
import re
with open('01-manuscript/paper.tex') as f:
    tex = f.read()
paper_ensemble = re.findall(r'(?:Ensemble|Voting|ensemble)[^.]*?(?:of|\[|\()([^)]+?)(?:\]|\))', tex)
if paper_ensemble:
    print(f"\npaper.tex ensemble 声称: {paper_ensemble}")
EOF
```

**PIMA实战案例（2026-06-24）**：跨 JSON 三角校验发现 3 种不同成员组合：
| 源 | 成员 | F1 |
|:---|:-----|:--:|
| catboost_ensemble.json | [CatBoost, GBC, LR] | 0.6973 |
| definitive_ablation.json | [GBC, LDA, SVC] | 0.6986 |
| comprehensive_results.json | [LDA, GBC, LR] | 未明确报告 |

即使 F1 值相近，这三个 ensemble 是不同的实验产物。paper.tex 引用的是 CatBoost+GBC+LR (F1=0.6973)，但 definitive_ablation.json 中被定义为 GBC+LDA+SVC (F1=0.6986)。**根因**：实验迭代过程中产生了多个不同版本的 ensemble 脚本，残留的 JSON 文件未被清理。

然后比对论文声称的 ensemble 成员（从 paper.tex 提取 `Ensemble(` 或 `VotingClassifier(` 所在行）。任意两个来源的成员不一致 → 标记 ⚠️ ENSEMBLE_MEMBER_MISMATCH。

## 与 paperjury 的协作关系

**quality-gate** 负责结构化质量门（G1-G7，编译、引用、格式等可量化检查）。**paperjury** 负责语义审查（claim 是否站得住、实验是否真正支撑结论、论证链条完整性）。

集成路径：
1. quality-gate L1-L3 → paperjury 快速 triage（可选）
2. quality-gate L4 → paperjury review 作为内容审查工具
3. quality-gate L5-L7 → paperjury edit-safety（编译 + 合规）

典型流程：论文完成 → quality-gate L1-L2 → paperjury review → 修复 → quality-gate L3-L4 → paperjury auto loop → quality-gate L5-L7 → 投稿。

详见 `paperjury` 技能的"与 Synthos 现有能力的集成点"章节。

## 提交材料准备（G7通过后）

论文通过G7后，需准备投稿材料：

1. **Cover Letter** — 说明贡献概述、期刊匹配度、关键指标、无发表承诺、利益冲突
2. **Highlights** — 5条要点，每条85字符以内（Elsevier要求）
3. **Graphical Abstract** — 设计规范的PDF，展示问题→方法→结果→应用
4. **Author Info** — 作者简历、ORCID、推荐审稿人
5. **Submission Checklist** — 完整的提交清单

详见 `references/submission-materials.md`。

详见 `paper-pipeline/references/submission-preparation.md`（Elsevier/BSPC 投稿清单）。

## G4 数据完整性检查扩展：OpenML 基准对比（2026-06-24 新增）

对使用 OpenML 托管的数据集的论文，L0.5 数据诚实门应增加 OpenML 基准对比：

### 检查流程

```python
import openml

# 1. 获取 Task ID（PIDD = Task 37）
evals = openml.evaluations.list_evaluations('f_measure', tasks=[37], size=1000)

# 2. 提取统计数据
all_f1 = [e.value for e in evals.values() if e.value > 0.1]
max_f1, mean_f1, med_f1 = max(all_f1), np.mean(all_f1), np.median(all_f1)

# 3. 计算论文排名
rank = sum(1 for f in all_f1 if f > our_f1) + 1
pctile = 100 * sum(1 for f in all_f1 if f < our_f1) / len(all_f1)
```

### 数据可提供的论文核心论据

| 数据 | 论文使用场景 |
|:-----|:------------|
| AUC 排名 | 如果论文 AUC 是 OpenML 第一 → 论文核心亮点 |
| Accuracy Top% | 如果 Top 1-5% → 方法论有效证据 |
| F1 排名 | 解释框架差异（Weka vs sklearn, SMOTE 拖累等） |
| 方法差异表 | 论文的严格隔离协议 vs OpenML 多数 runs 的无隔离 |

### 实战：PIDD Task 37（2026-06-24）

| 指标 | Our CatBoost | OpenML 排名 |
|:-----|:-----------:|:----------:|
| AUC | 0.8422 | **1/1000** 🥇 |
| Accuracy | 0.7759 | **5/1000** (Top 0.5%) |
| F1 | 0.7067 | 753/1000 (sklearn: 294/490, Top 60%) |

**Weka vs sklearn 差异**：Weka 508 runs 平均 F1=0.7405，sklearn 490 runs 平均 F1=0.6449。论文的 F1=0.7067 高于 sklearn 平均 +0.062。

### 注意事项
- `list_evaluations` 返回 `{run_id: OpenMLEvaluation}` dict，不是 list
- evaluation.value 可直接读取
- 性能指标在 evaluation 对象中，不在 run.predictive_accuracy（返回 None）
- API 超时问题：size=1000 可能较慢，建议分批

L0.5 数据诚实门增加两个子检查：

| 子门 | 检查内容 | 方法 |
|:-----|:---------|:-----|
| 独立复现验证 | 论文声明的数值结果是否可独立复现 | 相同数据 + 相同模型 + 相同预处理 + 相同 CV → 比较 F1/Acc/Prec/Rec/AUC |
| 引用键匹配 | Tex 中所有 cite keys 是否都在 .bib entry 中 | `re.findall(r'@\\w+\\{(\\w+?),', bib)` vs tex 逐行提取 cite keys |
| **Notebook 多配置一致性** | **Notebook 是否含多个冲突配置，论文是否 cherry-pick 最佳值** | **遍历 notebook 所有 code cell outputs，提取所有 metric 值 → 与论文声称对比 → 差异 >5% 标记 DATA_SUSPECT** |
| **数字可溯源** | **论文每个数值是否能对应到 notebook 中的具体 cell** | **每个数字在 notebook output 中找到精确匹配或 <1% 浮点误差** |

**触发条件**：所有论文在进入 L4 内容级评审前必须通过。若 F1 差异 > 10% 或 Prec/Rec 方向相反 → DATA_SUSPECT，不进入投稿流程。

## G2.5 实验完整性门（2026-06-24 新增）

### 核心原则

**实验设计与数据完整性是论文质量的最终保障。** 论文的每个数值必须能追溯到可执行的代码输出，且每个代码块的设计意图必须清晰可循。未经此检查的论文不可标记为"可投稿"。

### 检查项（权重 30/100）

| 子项 | 权重 | 检查内容 | 通过标准 |
|:-----|:----:|:---------|:---------|
| 数值可追溯 | 10分 | 论文每个数字声明对应到代码输出JSON/CSV/cell output | 数字精确匹配或 <1% 浮点偏差 |
| fold-level detail | 8分 | 实验输出JSON包含每折（fold）的详细指标，不只是均值 | 有 fold_id / fold_0..9 的完整记录 |
| 自动验证Cell | 7分 | Notebook有最终验证cell，自动比对论文数字与JSON差异 | 输出PASS/FAIL报告，差异>2%即FAIL |
| EDA可视化证据 | 5分 | 论文/Notebook包含EDA可视化（分布图、相关性、缺失模式等） | 至少3张实质性EDA图 |

### G2.5 新增：实验声明真实性检查（2026-06-24 新增）

### ① OpenML/数据库实验 Claim-Only 检测

**问题**：论文 Methods 节声称使用 OpenML leaderboard 分数作为 benchmark baseline，或声称从 OpenML/UCI/Kaggle 下载了数据集，但代码中无对应的 `fetch_openml`、`pd.read_csv(URL)` 或 API 调用。这种"声明性引用"（Claim Only）不符合"凡数必源"原则。

### G6 逻辑完整性 — 论文约束系统检查

**核心原则**：论文是由多个组件（表格、正文、图、代码、JSON、bib）组成的**约束系统**。组件的孤立正确性（数值→JSON匹配）是必要条件，但不够——**组件之间的关系**也必须满足约束。

#### 四种普适约束类型

| 约束类型 | 核心问题 | 违反后果 |
|:---------|:---------|:---------|
| **同实体跨位约束** | 同一实体在不同位置出现时，值是否一致或有解释？ | P1 |
| **声明-证据对齐约束** | 每个声明是否有对应的证据片段直接支撑？ | P1 |
| **比较-基准对齐约束** | 声称的对比是否基于相同协议/度量/设置？ | P0 |
| **叙事-数据比例约束** | 叙事的语气强度是否与数值差异大小成比例？ | P0 |

#### 1. 同实体跨位约束（Cross-position Same-entity Constraint）

**本质**：论文中同一个实体（数据集/模型/指标）出现在 ≥2 个位置时，必须满足：值相同 OR 差异有显式解释。

**普适性**：任何包含多个表格或正文+表格的论文都可能触发。不依赖特定数据集名或指标名。

**检测方法**：
```python
import re

with open('paper.tex') as f:
    tex = f.read()

# 步骤1：提取所有 (实体, 属性, 值) 三元组
# 实体 = 数据集名/模型名/方法名
# 属性 = 指标名
# 值 = 数值

# 从表格中提取
entities = {}  # {(entity, attr): [(value, table_name, line_num)]}
tables = re.split(r'\\begin\{table\*?\}', tex)
for i, tbl in enumerate(tables):
    caption = re.search(r'\\caption\{([^}]+)\}', tbl)
    cap = caption.group(1)[:60] if caption else f'Table_{i}'
    
    # 提取所有 实体+指标+数值 的组合
    # 通用模式：任何文本 + 指标名 + 分隔符 + 数值
    for match in re.finditer(
        r'([A-Z][A-Za-z0-9\s]+?)\s*[&:]\s*'
        r'(F1[-\s]?[Ss]core|Accuracy|AUC|Recall|Precision|Sensitivity|Specificity)'
        r'\s*[=:≈]\s*([\d.]+)',
        tbl, re.I
    ):
        entity = match.group(1).strip()[:30]
        attr = match.group(2).lower()
        val = float(match.group(3))
        key = (entity, attr)
        if key not in entities:
            entities[key] = []
        entities[key].append((val, cap, 'table'))

# 从正文中提取（abstract, results, discussion等）
for match in re.finditer(
    r'([A-Z][A-Za-z\s]+?)\s*(?:F1[-\s]?[Ss]core|Accuracy|AUC|Recall|Precision)'
    r'\s*(?:of|is|=|:)\s*([\d.]+)',
    tex, re.I
):
    entity = match.group(1).strip()[:30]
    val = float(match.group(2))
    # 判断在哪个section
    pos = match.start()
    # ... 通过位置判断section

# 步骤2：对同一 (entity, attr) 检查跨位差异
THRESHOLD = 0.05
for (entity, attr), occurences in entities.items():
    if len(occurences) >= 2:
        values = [o[0] for o in occurences]
        max_diff = max(values) - min(values)
        if max_diff > THRESHOLD:
            # 检查附近是否有解释（不同CV/不同模型/不同预处理）
            # 搜索 "different|varies|due to|note|protocol" 等关键词
            print(f'⚠️ {entity}.{attr}: 跨位差异 {max_diff:.3f}')
            for v, src, typ in occurences:
                print(f'   {src}({typ}): {v}')
```

**阈值**（通用，不依赖具体数值范围）：
| 差异幅度 | 处理 |
|:---------|:-----|
| > 0.10 或 > 10% 的相对差异 | 🔴 P0 — 必须解释或修正 |
| 0.05~0.10 或 5%~10% | 🟡 P1 — 建议加脚注 |
| < 0.05 或 < 5% | ⚪ 可接受 |

**修复**：在差异位置添加说明"此值来自[不同实验设置]，与Table X的[值]因[协议差异]而不同"。

#### 2. 声明-证据对齐约束（Claim-evidence Alignment Constraint）

**本质**：论文中每个实质性声明（claim）必须能在表格/图/代码中找到直接支撑数据。

**普适性**：任何有 claim 的论文都适用。不依赖具体领域。

**检测流程**：
```
[提取声明]             [定位证据]           [验证对齐]
  ├── Abstract claims     ├── Table cells       ├── 数值匹配？
  ├── Contribution list   ├── Figure values     ├── 统计显著？
  ├── Discussion claims   ├── Code output       └── 逻辑直接？
  └── Conclusion claims   └── JSON values
```

**常见断裂模式**（通用）：
| 模式 | 信号 | 示例 |
|:-----|:-----|:------|
| 无证据声明 | 声明无对应 table/figure 引用 | "模型表现卓越" 但无对应表 |
| 证据不足声明 | 声明需要多个数据点但只提供一个 | "全面超越" 但只比了一个指标 |
| 证据错位声明 | 引用的是 A 实验但实际支撑 B 实验 | "跨数据集验证" 但只在一个数据集上做了 |
| 统计缺失声明 | "显著优于" 但无 p-value 或 confidence interval | "性能提升明显" 但无检验 |

#### 3. 比较-基准对齐约束（Comparison-baseline Alignment Constraint）

**本质**：论文声称"优于"、"可比"、"超越"其他方法时，比较必须基于相同的评估协议（相同CV、相同度量、相同预处理），或者必须显式讨论不公平性。

**普适性**：任何包含方法比较的论文都可能触发。

**检测清单**：
```
□ 声称 "优于 OpenML 平均" → 是否用了相同 CV 协议？
□ 声称 "超越 Weka 结果" → CV fold 数相同？预处理一致？
□ 声称 "与 SOTA 可比" → 数据集完全相同？评估指标一致？
□ 声称 "跨数据集一致" → 各数据集用了相同模型和 CV 方案？
```

**规则**：
- 比较涉及不同评估协议 → 必须显式说明差异并评估影响
- 无说明的比较偏差 → 标记 ⚠️ COMPARISON_MISALIGNMENT (P1)
- 明知协议不同仍声称"超越" → 标记 🔴 COMPARISON_MISLEADING (P0)

#### 4. 叙事-数据比例约束（Narrative-to-data Proportionality Constraint）

**本质**：叙事的语气强度必须与定量差异的大小成比例。论文中"剧烈"、"崩溃"、"灾难性"、"轻微"、"可接受"等语气词必须对应合理量级的数值差异。

**普适性**：任何带有评价性语言的论文都适用。

**校准指南**：
| 语气词 | 应对应的定量差异 |
|:-------|:----------------|
| "collapse/崩溃/catastrophic/灾难性" | > 30% 下降 |
| "dramatic/剧烈/severe/严重" | 15-30% 变化 |
| "significant/显著/substantial/实质性" | 5-15% 变化或 p<0.05 |
| "modest/适度/mild/轻微" | 1-5% 变化 |
| "negligible/可忽略/minimal/极小" | < 1% 变化 |

**检测方法**：
```python
# 搜索语气词及其附近的数值
import re
with open('paper.tex') as f:
    tex = f.read()

tone_words = {
    'catastrophic|collapse|崩溃|灾难性': 0.30,
    'dramatic|plummet|剧烈|严重': 0.15,
    'significant|substantial|显著|实质性': 0.05,
    'modest|mild|轻微|适度': 0.01,
    'negligible|minimal|可忽略|极小': 0.001,
}

for pattern, threshold in tone_words.items():
    for match in re.finditer(pattern, tex, re.I):
        # 提取语气词前后 50 字符内的数值
        start = max(0, match.start() - 50)
        end = min(len(tex), match.end() + 50)
        context = tex[start:end]
        numbers = re.findall(r'[\d.]+%|[\d.]+', context)
        if numbers:
            print(f'  "{match.group()}" 附近数值: {numbers[:3]}')
```

**修复**：将语气词替换为与数值量级匹配的词汇。2% 差异不应称为"drastic collapse"。

---

**集成方法**：在 G6 逻辑完整门中执行约束系统检查。对每种约束类型：

1. 自动扫描 paper.tex 提取实体/声明/比较/语气
2. 与 JSON/代码数据源交叉验证
3. 输出约束违反清单（按 P0/P1 分类）
4. 修复建议：如跨位差异需加说明、声明需补证据索引、比较需补协议说明、语气需降级

**检测方法**：
```bash
# 搜索代码中是否有实际的数据获取操作
for pattern in "fetch_openml" "kagglehub" "pd.read_csv" "ucimlrepo" "load_diabetes" "load_breast"; do
    count=$(grep -r "$pattern" 03-code/ --include='*.py' --include='*.ipynb' 2>/dev/null | wc -l)
    echo "$pattern: $count 次出现"
done
```

| 论文声称 | 代码中对应的 fetch 调用 | 判定 |
|:---------|:------------------------|:----:|
| "从 OpenML 获取 PIDD" | `fetch_openml(\"pima-indians-diabetes\")` 存在 | ✅ 真实实验 |
| "与 OpenML leaderboard 对比" | 无 fetch 操作 + 无 leaderboard 数据文件 | ❌ Claim Only |
| "跨数据集验证包括 NHANES" | 读取 NHANES CSV 或 API 调用的代码存在 | ✅ 真实实验 |

**规则**：
- 论文中每个数据相关声明（\"我们从 XXX 获取数据\"、\"与 YYY benchmark 对比\"）必须能在代码中找到对应的数据加载/API调用操作
- 仅引用了数据来源的原始文献但无实际数据操作的 → 标记 ⚠️ DATA_CLAIM_ONLY
- 修复：要么从代码中删除该声明（如果未实际使用），要么补充实际数据操作代码

**PIMA实战案例（2026-06-24）**：
- 论文 L128 Methods 段说 \"Leveraging OpenML's curated benchmarking suites... leaderboard scores on standardized tasks provide a reliable, leakage-free baseline for comparing Helix results against established benchmarks\"
- 代码中 `grep -r "fetch_openml" 03-code/` 返回 0 次
- PIDD 数据来自本地 `pima_raw.csv` 文件
- 结论：❌ Claim Only → 需删除或补充代码

### ② 统计量可追溯性检查（p-value, Cohen's d 等）

**问题**：论文正文报告了统计显著性检验结果（如 \"p=0.59, Cohen's d=0.28\" 或 \"F1 difference not significant (p<0.05)\"），但实验代码/JSON 输出中无对应记录。这些数字一旦在论文文本中漂移，无法通过 JSON 回溯验证。

**常见统计声明示例**：
| 论文声明 | 应来自 | 可追溯方式 |
|:---------|:-------|:----------|
| p=0.59 | SciPy `ttest_rel()` 输出 | 代码 cell 保存 p-value 到 JSON 或直接打印 |
| Cohen's d=0.28 | `compute_effsize()` 计算 | 代码保存 d 值 |
| \"not significantly different (p>0.05)\" | 统计检验结果 | 在代码中运行检验并输出结果 |
| \"F1 improved by 2.9%\" | 两列 F1 数组的均值差 | JSON 中保存两个数组值 |

**检测方法**：
```python
# 搜索论文中的统计量
import re
with open('paper.tex') as f:
    tex = f.read()
stats = re.findall(r'p\s*[=<>]\s*0\.\d+|Cohen.*?d\s*[=:]\s*[\d.]+|not\s+significant|significantly', tex)
print(f'论文中统计声明: {stats}')

# 检查代码中是否有对应计算
# 搜索 ttest, mannwhitney, effect_size, cohen_d 等
```

**规则**：
- 论文报告的每个 p-value、Cohen's d、效应量必须能在代码/JSON 中找到原始计算
- 无法在代码中找到的统计量 → 标记 ⚠️ STAT_UNTRACEABLE (P1)
- 论文声称显著差异但代码无统计检验 → 标记 ⚠️ STAT_CLAIM_ONLY (P0)
- 修复：在 Notebook 中添加统计检验 cell，保存结果到 JSON，或从论文中移除无法追溯的统计声明

**PIMA实战案例（2026-06-24）**：
- paper.tex L259: \"A paired t-test confirms no significant difference between the two (p=0.59, Cohen's d=0.28)\"
- `grep -r "ttest\|pvalue\|0\.59" 03-code/` → 无结果
- Cohen's d=0.28 也无法在 JSON 中找到
- 结论：⚠️ STAT_UNTRACEABLE — 需在代码中补充统计检验 cell 并保存结果

### 不通过后果

- G2.5 FAIL → 总评分上限 = 50/100
- G2.5 FAIL → 不可标记"可投稿"、"gate=PASS"、"quality_score≥70"
- 整改后必须重新做G2.5审计，不可自报通过

### 单一权威Notebook原则

**背景问题**（PIMA案例）：实验代码分散在 Notebook + 多个独立脚本（run_ablation.py, run_ensemble.py, run_cross_dataset.py, pima_definitive.py）中，导致同一实验产生多个不一致的JSON输出文件（definitive_ablation.json vs definitive_experiment.json 对相同指标给出不同数值），读者无法通过单一入口复现论文数字。

**原则**：
1. 论文的所有实验必须**在一个单一权威Notebook中完成**，产生所有论文数字
2. 独立脚本仅用于**无法在Notebook中完成的任务**（如大规模跨数据集扫描），且必须被Notebook中的一个cell引用和验证
3. Notebook同时承担**教学叙事**（step-by-step解释）和**计算证据**（产生论文数字）双重角色
4. Notebook达到"Kaggle Run All"即可完整复现论文全部数字

**陷阱：Notebook 缺失外部框架（2026-06-24 实战教训）**。在 PIMA 案例中，Notebook (`crisp-dm-pima.ipynb`) 包含 27 个 sklearn 模型（通过 `all_estimators()`），但 **CatBoost、XGBoost、LightGBM 三个外部框架仅在 `crisp_dm_pima_unified.py` 脚本中有，不在 Notebook 中**。论文声称"evaluated 30 models"但 Notebook 只能复现 27 个。CatBoost 被论文列为最优模型（F1=0.7067），但其复现代码不在 Notebook 内→违反了原则1。

**检测方法**：
```python
# 检查 notebook 中是否包含论文声称的所有外部框架
import json
with open('crisp-dm-pima.ipynb') as f:
    nb = json.load(f)
all_code = ' '.join([''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code'])
for ext in ['CatBoost', 'XGBoost', 'LightGBM']:
    if ext not in all_code:
        print(f'⚠️ {ext} 不在 notebook 中！')
```

**修复**：将外部模型的 import + pipeline 代码补入 notebook 的 30-model benchmark cell 中。重新执行 notebook 验证所有数字一致。

详见 `references/notebook-script-reconciliation-workflow.md`（发现多源矛盾时的具体操作步骤）。

### EDA最低标准

数据探索（EDA）是实验设计的前提。每个论文项目在进入预处理前，Notebook必须包含：

| EDA组件 | 要求 | 输出 |
|:--------|:-----|:-----|
| 描述统计 | 均值/中位数/标准差/四分位/偏度 | `.describe()` 表 |
| 零值/缺失分析 | 每特征零值/缺失计数+比例+可视化 | **零值比例柱状图** |
| 分布可视化 | 直方图+KDE，按目标类别着色 | **8特征分布面板（2×4或3×3）** |
| 类别对比 | 箱线图/小提琴图按Outcome分组 | **箱线图对比面板** |
| 相关性分析 | Pearson + Spearman | **双热图** |
| 缺失模式诊断 | 零值特征的联合缺失模式 | UpSet图或热图 |

**"每个数据集都不同，必须先了解分布才能设计预处理策略。"** 无EDA可视化支撑的论文，G2.5自动FAIL。

### 多源交叉验证铁律（2026-06-23 新增）

**问题**：审计交付物中的"数字声明"（如"BPPV相关论文已发表14篇"、"已完稿64项成果"）时，容易仅检查本地管线而忽略外部数据库（PubMed、CNIPA等），得出"数据夸大"的错误结论。

**规则**：当审计任何可量化声明时，必须同时检查**两个数据源**：

| 声明类型 | 本地源 | 外部源 |
|:---------|:-------|:-------|
| 已发表论文数 | `outputs/papers/` 管线 | PubMed搜索（邮箱/姓名） |
| 发明专利数 | 研究者面貌/技能库 | CNIPA / 3deyes.top |
| 被引次数 | local BibTeX | Crossref / Google Scholar |
| 数据集使用 | 实验代码 | OpenML / UCI / Kaggle |

**实战案例**（2026-06-23 BCI申报方案审计）：
- 初始结论：⚠️ "BPPV论文仅5篇，文档称14篇，夸大180%"
- 真实结论：✅ "PubMed搜索Yang Xiaokai[Author] AND BPPV 得到14篇，管线存档另有10篇，文档数据准确"
- **教训**：仅查管线不查PubMed，得出完全错误的结论。

**执行流程**：先查本地管线，其次查PubMed/CNIPA（外部数据库），最后综合判定。不可仅在本地数据上做出结论。

**参考案例**：pima-crispdm — Notebook 含 4+ 个不同 pipeline 配置（Cell 24: F1=0.6878, Cell 26: F1=0.6420, Cell 27: F1=0.6330, Cell 28: F1=0.6907, Cell 31: F1=0.6522），论文声称 F1=0.6857 无法对应任何 cell 输出，独立复现 F1=0.6177（-11.3%）。**根因：notebook 不是确定性管线，有多个"调参"cell 但论文选了最佳而非最稳定的输出。**

**修复原则**：
1. 若 notebook 有多个配置 → 论文必须明确说明选了哪个（及为什么）
2. 若论文数字无法对应 notebook → 要么重写数字，要么补充代码
3. 独立复现差异 >5% → 必须检查随机种子、数据预处理、CV 策略是否一致
4. **多配置 notebook 的论文不适合投稿**——要么精简为单一确定管线，要么用独立脚本替代 notebook

### 科学性/创新性/可行性三要素评价（2026-06-24 新增）

这是论文质量评估的**最基础维度**，独立于G1-G7技术闸门。所有论文在完成G2.5实验完整性检查后，必须进行三要素评价方可进入投稿流程。

## 审稿人评价框架（2026-06-24 新增）

> 现有 G1-G7 闸门和三要素评价是"检查员"视角——查数据完整性、引用格式、编译正确。
> 本框架提供**审稿人**视角——问六个审稿人拿到论文时第一个想问的问题。
> 本框架不取代 G1-G7，而是将 G1-G7 的所有发现组织到审稿人关心的六个问题下。

### 多模板多报告机制

**核心设计**：一篇论文出**四份独立报告**，每份从不同模板/视角评估。四份报告分工明确，互不重叠：

```
论文
 ├─ ① 通用六域报告（所有论文必出）        ← 审稿人视角：Q1-Q6 + 整体判定
 ├─ ② 类型专项报告（根据论文类型加载）     ← 方法学专家：PROBAST/AMSTAR2对齐
 ├─ ③ 参考文献审查专项报告（所有论文必出）  ← 引用审查员：功能分类+引文网络+恰当率
 └─ ④ 检查员报告（所有论文必出）           ← L0.5铁律：凡数必源+凡引必查
```

**四份报告不做可比性判断**——每份独立给出PASS/SOFT/HARD，最终判定取最严格的。

**L0 分类器**：扫描标题/关键词/摘要，判断论文类型，加载对应模板。

| 信号词 | 论文类型 | 额外模板 |
|:-------|:---------|:---------|
| "ODE"、"PINN"、"differential equation"、"dynamical system"、"parameter estimation" | 计算建模 | ODE/PINN + 通用 |
| "prediction"、"classification"、"AUC"、"ROC"、"logistic regression"、"machine learning"、"dataset" | 临床 ML | Clinical ML + 通用 |
| "systematic review"、"meta-analysis"、"literature review"、"PRISMA" | 综述/系统评价 | 综述 + 通用 |
| 无明确信号 | 通用 | 仅通用 |

---

### 检查员报告（所有论文必出）

> **文言**：凡数必源，凡引必查。数不源则诬，引不验则废。
> **角色**：检查员是审稿流程里最不受待见又最不可或缺的人——不看故事好不好，只看每个数字能不能追踪到代码、每篇引用能不能找到PDF。

```markdown
═══════════════════════════════════════════════
  检查员报告
═══════════════════════════════════════════════

【第一块 · 凡数必源矩阵】

▸ 提取论文中所有数值声明 → 逐条追踪到源文件（JSON/CSV/Notebook cell）
▸ 源要求：精确匹配或 <1% 浮点偏差；>5% 标记 DATA_SUSPECT
▸ 路径要求：代码绝对路径 + 行号/键名

| # | 论文位置 | 声明值 | 源文件 | 行/键 | 匹配 | 偏差 |
|:-:|:--------|:------:|:------|:-----:|:----:|:----:|
| 1 | Abstract L3 | F1=0.707 | ../03-code/ablation/results.json | severe_leakage_f1 | ✅ | — |
| 2 | Table 1 CatBoost | Acc=77.59 | ../03-code/catboost.json | accuracy | ✅ | — |
| 3 | Methods L243 | p=0.59 | — | — | ❌ | — |
| … | | | | | | |

▸ 结果：XX/XX 个数值可追溯（可追溯率 XX%）
  - 可追溯 ≥ 95%  → ✅ PASS（数据诚信）
  - 可追溯 80-95% → ⚠️ SOFT（需补交源文件）
  - 可追溯 < 80%  → ❌ FAIL（数据不诚实）
  - 存在 paper_claims/actual_values 双结构 → 🔴 FABRICATION_DETECTED

【第二块 · 凡引必查清单】

▸ 对每篇参考文献，检查三项：
  ① PDF 存在性：本地是否有可打开的 PDF
  ② 格式一致性：PDF 元数据的 DOI/journal 与 bib entry 匹配
  ③ 体裁验证：PDF 首页含论文主题关键词（非同名无关文献）

| 引用键 | 作者(年) | PDF? | DOI匹配? | 体裁验证 | 整体 |
|:------|:---------|:----:|:---------:|:--------:|:----:|
| Smith1988 | Smith (1988) | ✅ | ✅ | ✅ | ✅ |
| Akbar2020 | Akbar (2020) | ✅ | ✅ | ✅ | ✅ |
| Kapoor2023 | Kapoor (2023) | ✅ | ✅ | ✅ | ✅ |
| … | | | | | |

▸ 结果：XX/XX 篇通过（通过率 XX%）
  - 通过率 ≥ 90% → ✅ PASS
  - 通过率 80-90% → ⚠️ SOFT
  - 通过率 < 80% → ❌ FAIL
  - 任意 PDF 内容与 bib 声明不一致 → 🔴 PDF_BIB_MISMATCH

【第三块 · 代码诚实验证】

▸ 对论文声称的关键结果，用实验代码独立复现：
| 声称 | 论文值 | 代码输出 | 差异 | 判定 |
|:-----|:------:|:--------:|:----:|:----:|
| CatBoost F1 | 0.7067 | 0.7067 | 0% | ✅ |
| Severe Leakage Rec | 0.6232 | 0.6232 | 0% | ✅ |
| Cross-dataset Early Diabetes F1 | 0.930 | 0.698 | -33% | 🔴 |

【第四块 · 虚构检测扫描】

▸ 对以下虚构信号进行全局扫描：
  □ paper_claims/actual_values 双结构 → 存在? 差异?
  □ Ensemble 成员在 JSON 间不一致 → 三源比对结果
  □ F1/Acc 绝对值异常（>95%） → 条目数
  □ 所有指标同时最优 → 条目数
  □ 引用键在 bib 中但无 PDF → 条目数
  □ 统计量（p/Cohen's d）在代码中无记录 → 条目数
  □ 叙事-数据比例失调（如 <5% 差称"catastrophic"）→ 条目数

═══════════════════════════════════════════════
检查员判定:  ✅ 数据诚信 / ⚠️ 需补源 / ❌ 数据不诚实
═══════════════════════════════════════════════
```

### 通用六域报告（所有论文标配）

```
═══════════════════════════════════════════════
  通用六域检查报告
═══════════════════════════════════════════════

Q1 假说问:   PASS / ⚠️ SOFT / 🔴 HARD    (假设清晰可证伪)
Q2 空白问:   PASS / ⚠️ SOFT / 🔴 HARD    (空白真实有支撑)
Q3 解法问:   PASS / ⚠️ SOFT / 🔴 HARD    (方法-问题匹配)
Q4 实验问:   PASS / ⚠️ SOFT / 🔴 HARD    (数据可追溯+实验设计)
Q5 结论问:   PASS / ⚠️ SOFT / 🔴 HARD    (结论-证据闭环)
Q6 价值问:   PASS / ⚠️ SOFT / 🔴 HARD    (可复现+可迁移+可行动)
───────────────────────────────────────────
关键项(L0.5)一票否决:  PASS
整体判定:              ⚠️ 有条件发表 (修4个SOFT FAIL)
═══════════════════════════════════════════════
```

### 临床 ML 专项报告（PROBAST 对齐）

针对临床预测模型论文的专项检查，与通用六域**并行输出**：

```
═══════════════════════════════════════════════
  临床 ML 专项报告 (PROBAST 对齐)
═══════════════════════════════════════════════

域1 参与者(P):  PASS                 (样本量>100, 纳入/排除标准明确)
域2 预测因子(P): PASS                 (特征定义清晰, 测量方法报告)
域3 结果(O):    PASS                 (结局定义明确, 盲法评估)
域4 分析(A):
  ├── 数据泄露      PASS             (fold内预处理已验证)
  ├── 基线公平性    ⚠️ SOFT FAIL      (OpenML最大F1=0.776, 论文0.707, 需解释差距)
  ├── 指标适当性    PASS             (分类指标用于分类输出)
  ├── 缺失值处理    PASS             (0→NaN→中位数, 有消融验证)
  └── 统计检验      ⚠️ SOFT FAIL      (Cohen's d=0.28未在代码中记录)
─────────────────────────────────────────────
PROBAST整体偏倚风险: ⚠️ LOW-MODERATE
TRIPOD报告完整性:    19/22 (缺3项: 注册号、样本量计算、模型更新策略)
═══════════════════════════════════════════════
```

### ODE/PINN 专项报告

针对计算建模/微分方程论文：

```
═══════════════════════════════════════════════
  ODE/PINN 专项报告
═══════════════════════════════════════════════

1. 数学推导正确性:     ✅ / ⚠️ / ❌
2. 参数可辨识性:      ✅ / ⚠️ / ❌    
3. 初值/边界条件:     ✅ / ⚠️ / ❌
4. 数值求解器稳定性:  ✅ / ⚠️ / ❌
5. 指标适当性:        ✅ / ⚠️ / ❌   (分类指标不用于回归输出)
6. 多初始值报告:      ✅ / ⚠️ / ❌   (multi-seed需报告mean±std)
7. 代码可复现:        ✅ / ⚠️ / ❌
─────────────────────────────────────────────
整体判定:  ✅ 可投稿 / ⚠️ 修问题 / ❌ 拒稿
═══════════════════════════════════════════════
```

### 综述/系统评价专项报告

```
═══════════════════════════════════════════════
  综述/系统评价专项报告 (AMSTAR 2 对齐)
═══════════════════════════════════════════════

关键项(Key Domains):
  1. 研究问题+PICO明确:   ✅ / ⚠️ / ❌
  2. 检索策略可复现:     ✅ / ⚠️ / ❌
  3. 纳入/排除标准:      ✅ / ⚠️ / ❌
  4. 偏倚风险评估:       ✅ / ⚠️ / ❌
  5. 发表偏倚检测:       ✅ / ⚠️ / ❌
─────────────────────────────────────────────
整体可信度:  HIGH / MODERATE / LOW / CRITICALLY LOW
═══════════════════════════════════════════════
```

### 集成方案

在 comprehensive-quality-report-template 中，结构改为：

```markdown
# [论文名] — 质量检查报告集

> 生成日期: ...
> 论文类型: [Clinical ML | ODE-PINN | Review | General]
> 加载模板: [通用六域] + [Clinical ML专项]

## 报告一：通用六域报告
[Q1-Q6 判定 + 关键项一票否决 + 整体判定]

## 报告二：临床 ML 专项报告
[PROBAST 四域 + TRIPOD 完整性]

## 报告三：复现性审计报告
[代码复现步骤 + 每个数字的JSON源 + 编译状态]

## 附录：所有P0/P1问题清单
[合并所有报告中的问题，按严重度排序]
```

### PIMA 实战示例

PIMA 论文会出两份报告：

**报告一：通用六域** → 47/60 → ⚠️ 有条件发表（Q4 统计记录 + Q5 跨数据集机制）
**报告二：临床 ML 专项** → PROBAST Low-Moderate Risk，TRIPOD 19/22
**两份报告独立判定，互不影响。**

### 六问与现有质量门的对应关系

```
收到论文
  │
  ├─ Q1 假说问：这篇论文想证明什么？        ← 从 Abstract/贡献中提取假设
  ├─ Q2 空白问：这个研究真的有必要吗？      ← 从 Introduction 提取研究空白
  ├─ Q3 解法问：这个方法对路吗？            ← 从 Methods 评估问题-方法匹配
  ├─ Q4 实验问：数据和实验可信吗？          ← 从 Results + JSON 验证
  ├─ Q5 结论问：结论真的从实验中来吗？      ← Conclusion → Results 逆向追溯
  └─ Q6 价值问：谁会在乎这个工作？          ← 从 Discussion + Limitations 评估
```

---

### Q1 假说问：这篇论文想证明什么？

**审稿人心理模型**：拿到论文先看标题和摘要，试图用一句话回答"这篇论文的核心论点是什么"。

**现有覆盖**：G1 结构检查检查了 IMRaD 完整性，G6 检查了逻辑链。但**没有主动提取假设并验证**。

**执行方法**：
```python
with open('paper.tex') as f:
    tex = f.read()

# 步骤1：提取明示的假设/贡献声明
# 找 "we hypothesize|we propose|our hypothesis|this paper shows|we demonstrate"
import re
hypothesis_signals = re.findall(
    r'(?:We|This paper|Our|The proposed)\s*(?:hypothesize|propose|introduce|demonstrate|show|argue|present|contribute)'
    r'[^.]*\.', tex, re.I
)
print('假设声明:', hypothesis_signals[:3])

# 如果 > 3 个句子中都没出现假设关键词 → ⚠️ HYPOTHESIS_IMPLICIT
```

| 结果 | 含义 | 处理 |
|:-----|:-----|:-----|
| 假设显式声明在 Abstract 开头 | ✅ 清晰 | 正常通过 |
| 假设隐式在 Introduction 末尾 | 🟡 可接受 | 建议显式化 |
| 全文无假设声明 | 🔴 P2 | 审稿人会追问"所以呢？" |

**PIMA实战**：Abstract L30 明确声明 "leakage does not uniformly inflate but selectively distorts Precision-Recall" → ✅ 假设清晰

---

### Q2 空白问：这个研究真的有必要吗？

**审稿人心理模型**："你说的这个空白我确认一下——你引的那些文献真的没覆盖到？这是真空白还是你编的？"

**现有覆盖**：G5 验证了引用真实性（有 PDF，DOI 有效）。但没问"你声称的空白，那些引用真的支撑吗？"

**执行方法**：
```python
# 步骤1：从 Introduction 提取研究空白声明
gap_section = extract_section(tex, 'introduction')
gap_claims = re.findall(
    r'(?:gap|lack|missing|absence|no study|few studies|not been addressed|remains unknown)'
    r'[^.]*\.', gap_section, re.I
)

# 步骤2：对每个空白声明，找到它引用的文献
for gap in gap_claims:
    cited_keys = re.findall(r'\\cite\{([^}]+)\}', gap)
    print(f'空白: {gap[:80]}...')
    print(f'  引用: {cited_keys}')

# 步骤3：对每个引用，验证它是否真的支撑该空白
# (用 citation-appropriateness-verification 技能逐篇读 PDF)
```

| 结果 | 含义 | 处理 |
|:-----|:-----|:-----|
| 空白声明有 ≥2 篇引用直接支持 | ✅ 真实空白 | 通过 |
| 空白声明有引用但引用主题不匹配 | ⚠️ GAP_SUSPECT (P1) | 需检查 PDF 原文 |
| 空白声明无引用（自我宣称） | 🔴 GAP_UNSUPPORTED (P0) | 必须补充引用或删除 |

**陷阱**：LLM 常生成这样的伪空白 "Existing methods achieve high accuracy but lack interpretability"——这也太通用了，审稿人一眼看出不是真空白。检测：空白声明如果可以用在 10 篇不同论文上 → ⚠️ GENERIC_GAP。

---

### Q3 解法问：这个方法对路吗？

**审稿人心理模型**："你提出的方法真的能解决你说的那个问题吗？还是说方法 X 很好但跟你的问题没啥关系？"

**现有覆盖**：三要素中的"方法论适当性"（方法选择与问题匹配）。但缺乏**问题→方法→指标**的显式映射。

**执行方法**：
```
[研究问题] ──→ [提出的方法] ──→ [验证指标]
                                           
  "Seletive Metric        CRISP-DM Helix      Recall, F1, AUC
   Inflation"             协议                在 4 级消融上验证

检查：指标是否测量了方法声称解决的问题？
  - 问题：泄漏导致 Recall 受抑制 → 指标：Recall 在泄漏增大时是否下降？ ✓
  - 问题：需要可审计协议 → 验证：Algorithm 1 是否形式化定义了隔离？ ✓
  - 问题：通用性 → 验证：是否在 ≥2 数据集上测试？ ✓
```

**关键判断**：一个好的审稿人会问"为什么不用更简单的方法"。如果论文用复杂框架解决了一个简单问题 → ⚠️ OVERENGINEERED。

| 信号 | 判定 |
|:-----|:------|
| 方法复杂度远高于问题复杂度 | ⚠️ OVERENGINEERED (P2)。修复：在 Discussion 中 justify 方法选择 |
| 指标不测量声明的问题 | ⚠️ METRIC_MISMATCH (P1)。修复：增加缺失指标 |
| 方法-问题映射清晰 | ✅ 通过 |

**PIMA 实战**：CRISP-DM Helix 用 5-tuple 形式化和 Algorithm 1 算法来确保数据隔离。问题是"泄漏导致指标失真"，方法是用隔离协议+消融实验来量化失真，指标是 Recall/Precision 在各级泄漏下的变化方向。 ✅ 方法-问题映射清晰。

---

### Q4 实验问：数据和实验可信吗？

**审稿人心理模型**："这个数字是真的吗？实验是公平的吗？指标选得对吗？"

**现有覆盖**：这是目前最强的一层。L0.5 数据诚实门（数值→JSON匹配）+ G2.5 实验完整性门 + OpenML 基准对比。

**TODO**：在现有 L0.5/G2.5 之上增加两小项：

#### 4a. 指标适当性检查（审稿人敏感）

**问题**：分类指标（AUC/Accuracy）用在回归输出上。ODE/PINN 论文用 AUC 评价连续ODE输出是常见陷阱。

**检测**：如果论文标题/关键词含 "ODE"、"PINN"、"regression"、"dynamics" 但 Results 用 AUC 评价 → 🔴 METRIC_INAPPROPRIATE (P0)。

#### 技能设计原则（2026-06-24 用户校正）

**不能"缺什么补什么"——必须提取普适性原则。**

错误模式：发现 Early Diabetes F1 矛盾 → 加一个"跨表一致性检查"；发现 CDC 讨论浅 → 加一个"讨论深度检查"。这是打补丁，不是设计系统。

正确模式：发现跨表矛盾 → 抽象出"同实体跨位约束"（任何实体在论文中跨位置出现时必须一致或有解释）。发现讨论浅 → 抽象出"约束系统检查框架"（声明-证据对齐、比较-基准对齐、叙事-数据比例）。四类约束**独立于具体论文领域**，下次不同主题的论文仍然适用。

**信号检测**：如果新加的检查项名包含论文特有实体（"Early Diabetes"、"CDC BRFSS"、"CatBoost"）→ 不对，应抽象到"数据集"、"模型"、"实验设置"层面。

**问题**：论文声称 "优于 SOTA" 但基线用的是默认参数未调优。

**检测**：
```python
# 搜索基线的超参数说明
baseline_section = extract_section(tex, 'baseline|compared method|competitor')
has_default_param = 'default' in baseline_section.lower()
has_tuned_param = 'grid search' in baseline_section.lower() or 'tuned' in baseline_section.lower()
if not has_tuned_param and has_comparison_claim:
    print('⚠️ BASELINE_MAYBE_UNFAIR — 基线似乎用了默认超参')
```

---

### Q5 结论问：结论真的从实验中来吗？

**审稿人心理模型**："你说 A 导致了 B，怎么证明不是你实验里的 C 导致的？"

**现有覆盖**：G6 逻辑完整性检查了 IMRaD 结构完整性。但缺少**结论→结果**的逆向追溯。

**执行方法**：对 Conclusion 段的每个句子，反向查找它在 Results/Discussion 中的证据。

```python
# 步骤1：提取 Conclusion 段的所有声明
conclusion = extract_section(tex, 'conclusion')
claims = re.findall(r'(?:We|Our|The|This)\s*(?:show|demonstrate|find|conclude|provide|establish|confirm)[^.]*\.', conclusion)

# 步骤2：对每个声明，追溯它在 Results 中的对应实验
for claim in claims:
    # 提取声明中的关键词（数据集名、方法名、指标名）
    keywords = extract_keywords(claim)
    # 在 Results 中搜索这些关键词
    evidence = search_in_results(tex, keywords)
    if not evidence:
        print(f'⚠️ 声明 "{claim[:60]}..." 在 Results 中无对应实验')
    else:
        # 检查声明的语气是否与实验数据匹配
        print(f'✅ 声明在 Results 中有对应')
```

| 结果 | 含义 | 处理 |
|:-----|:-----|:-----|
| 每个结论句在 Results 中有 ≥1 个对应实验 | ✅ 闭环完整 | 通过 |
| 结论句引用了 Results 外的内容 | ⚠️ CONCLUSION_DRIFT (P1) | 检查是否合理 |
| 结论声称 > 数据支撑（如 3% 差说成"显著超越"） | 🔴 CONCLUSION_OVERCLAIM (P0) | 见"叙事-数据比例约束" |

**PIMA 实战**：Conclusion 段（L419-425）每句话都能追踪到 Results 的实验 → ✅ 闭环完整。

---

### Q6 价值问：谁会在乎这个工作？

**审稿人心理模型**："就算你说的都对，但这篇论文对谁有用？能改变什么？"

**现有覆盖**：三要素中的"可行性"（可复现性、可获取性、可迁移性）。但缺乏**应用场景**检查。

**执行方法**：

| 维度 | 检查项 | PIMA 实例 |
|:-----|:-------|:----------|
| **可复现** | 代码公开？Kaggle URL 有效？ | ✅ Kaggle |
| **可理解** | 方法描述是否能让另一个实验室复现？ | ✅ Algorithm 1 |
| **可迁移** | 框架是否依赖特定数据/硬件？ | ✅ 独立于模型和数据 |
| **可行动** | 审稿人读完后能不能改变自己的实践？ | ✅ Dataset Baseline Registry 提案 |
| **可验证** | 结论是否能被独立验证？ | ✅ PIDD 公开 + 开源代码 |

**底线**：如果一篇论文通过了 Q1-Q5 但 Q6 全 × → ⚠️ NO_PRACTICAL_VALUE，不建议发表。

---

### 六问与现有质量门的对应关系

```
Q1 假说问 → G1 元数据（假设必须在 Abstract 开头）+ 三要素·创新性
Q2 空白问 → G5 引用质量（引用真实性→空白真实性）+ 三要素·科学性  
Q3 解法问 → G6 逻辑完整性（方法-问题匹配）+ 三要素·科学性
Q4 实验问 → L0.5 数据诚实门 + G2.5 实验完整性门 + OpenML 基准
Q5 结论问 → G6（逆向追溯）+ 三要素·科学性（证据链完整性）
Q6 价值问 → 三要素·可行性 + 三要素·创新性
```

**六问不是新门，是新透镜**——用同一个数据，问出审稿人才会问的问题。

---

### 六问评分标准（总分 60 = 六问各 10 分）

| 问题 | 0-3分 | 4-6分 | 7-10分 |
|:-----|:------|:------|:-------|
| Q1 假设 | 假设隐式/不存在 | 假设存在但不可证伪 | 假设清晰 + 可证伪 |
| Q2 空白 | 无空白声明/虚构 | 空白存在但弱 | 空白真实 + 重要 |
| Q3 解法 | 方法不解决提出的问题 | 部分匹配 | 方法-问题精确匹配 |
| Q4 实验 | 数据不可追溯/数值矛盾 | 部分可验证 | 全部可独立复现 |
| Q5 结论 | 结论与实验脱节 | 部分有证据链 | 每个结论可追溯 |
| Q6 价值 | 无应用场景 | 理论价值但缺实践 | 可复现 + 可迁移 + 可行动 |

**判定**：
- ≥ 48/60 (平均 8 分) → 强烈推荐发表
- 36-47/60 → 有条件发表（修 Q4/Q5 问题）
- 24-35/60 → 大修
- < 24/60 → 拒稿

**PIMA 实战评分**：
| 问题 | 评分 | 理由 |
|:-----|:----:|:------|
| Q1 假设 | 9/10 | "泄漏不是统一膨胀而是选择性扭曲"——清晰、可证伪（消融实验 4 级可验） |
| Q2 空白 | 7/10 | 空白真实（无标准化隔离协议）但文献引用 Kapoor2023 足够支撑 |
| Q3 解法 | 8/10 | CRISP-DM Helix 精确对准数据隔离问题 |
| Q4 实验 | 8/10 | 数值全部可追溯 JSON。OpenML AUC 第一。但 p-value 未在代码中记录 |
| Q5 结论 | 8/10 | 每个结论可追踪到实验。但跨数据集分析缺机制解释 |
| Q6 价值 | 7/10 | Kaggle 开源，Baseline Registry 提案有启发性但尚未实现 |
| **总分** | **47/60** | ⚠️ 有条件发表（修 Q4 统计记录 + Q5 跨数据集机制 + Q6 实现步骤） |

**比纯粹的三要素评分更贴近审稿人的实际决策过程。**

---

### 计划改进（2026-06-24 调研建议）

从 12 个建立已久的审稿框架（PROBAST、TRIPOD、Cochrane RoB 2.0、AMSTAR 2、EQUATOR 等）中提取以下三项结构性改进，待后续版本落地：

| 改进 | 来源 | 当前问题 | 计划方案 |
|:-----|:------|:---------|:---------|
| **领域级判定取代总分** | Cochrane RoB 2.0 | 输出 "72/100" 对审稿人无用 | 改为 {数据诚实, 实验设计, 引用质量, 论证完整性, 报告完整性, 价值} 六域，每域判 PASS / ⚠️ SOFT / 🔴 HARD |
| **关键项一票否决** | AMSTAR 2 | L0.5 FAIL 仍进入 G1-G7 评分 | 如果 L0.5 = FAIL → 整篇不进入后续评分，直接标记 "需修正数据后再评估" |
| **论文类型识别 → 不同模板** | EQUATOR Network | 一套 G1-G7 打天下 | L0 层扫描标题/关键词识论文类型（Clinical ML / ODE-PINN / Review / RCT），加载对应检查模板 |

详见 `references/established-review-frameworks.md`。

### 科学性 (Scientific Soundness) — 权重 25%

| 子项 | 满分 | 检查内容 |
|:-----|:----:|:---------|
| 研究问题明确性 | 5 | PICO/FRAM框架清晰，CARS引论结构完整 |
| 方法论适当性 | 5 | 方法选择与问题匹配，参数设置合理 |
| 证据链完整性 | 5 | 从实验设计→结果→讨论→结论的推理链条完整 |
| 统计严谨性 | 5 | 假设检验正确，多重比较校正，效应量报告 |
| 可证伪性 | 5 | 结论可被后续独立研究验证或推翻 |

**典型风险**：
- Ensemble性能低于CatBoost单模型但论文声称"ensemble超越所有单模型" → 必须诚实讨论
- Medium Leakage与No Leakage差异很小 → 需做统计显著性检验
- 缺少模型间pairwise对比（如McNemar检验）

### 创新性 (Innovation/Novelty) — 权重 25%

| 子项 | 满分 | 检查内容 |
|:-----|:----:|:---------|
| 概念新颖性 | 5 | 是否提出新概念/命名/分类 |
| 方法论创新 | 5 | 是否是现有方法的实质性扩展或组合 |
| 洞察深度 | 5 | 发现是否改变了领域内已有认知 |
| 实用性创新 | 5 | 可被其他研究者直接采用 |
| 对比已有文献 | 5 | 与SOTA的差异化清晰 |

**典型信号**：
- 新发现：泄漏非均匀扭曲Precision-Recall关系（而非"整体膨胀"）→ 创新
- 新概念：Selective Metric Inflation → 创新
- 新框架：CRISP-DM Helix作为形式化5元组 → 增量创新
- 新工具：Dataset Baseline Registry提案 → 创新
- 框架本身非新（CRISP-DM=2000年），但扩展是可接受的增量贡献

### 可行性 (Feasibility/Practicality) — 权重 10%

| 子项 | 满分 | 检查内容 |
|:-----|:----:|:---------|
| 代码可复现性 | 5 | Run All即可复现全部结果 |
| 数据可获取性 | 3 | 数据公开/可申请/可替代 |
| 方法可迁移性 | 2 | 框架可迁移到其他数据集/场景 |

**典型优势**：低计算成本（30模型~15min）、无API依赖、无硬件限制、Kaggle+GitHub双渠道。

### 三要素评分与投稿判定

| 三要素总分 | 判定 |
|:----------|:-----|
| ≥ 42/60 | ✅ 可投稿 |
| 30-41/60 | ⚠️ 修正后投稿 |
| < 30/60 | ❌ 不可投稿 |

**注意**：三要素评价是**方向性判定**（这篇论文值不值得发），不是**技术性检查**（格式/引用/复现）。三要素通过不等于G1-G7全过，反之亦然。两者必须同时满足。

### PIMA案例三要素评分（参考）

| 维度 | 评分 | 关键发现 |
|:-----|:----:|:---------|
| 科学性 | 22/25 | 方法严谨但Ensemble<CatBoost需讨论 |
| 创新性 | 18/25 | Selective Metric Inflation是亮点，但整体增量贡献 |
| 可行性 | 10/10 | 完全可复现，低计算成本 |
| **三要素总分** | **50/60** | **✅ 可投稿** |

## sklearn 版本差异+外部框架陷阱（2026-06-24 新增, 2026-06-24 更新: 加入外部框架CatBoost最佳发现）

**问题**：`all_estimators(type_filter='classifier')` 返回的模型数随 sklearn 版本变化。

| sklearn 版本 | sklearn 模型数 | 外部框架 | 总模型数 | 说明 |
|:------------|:--------------:|:--------:|:-------:|:------|
| 1.5.x | 27 | - | 27 | 含 PassiveAggressiveClassifier |
| 1.9.0 | 27 | XGBoost v3.3.0 + LightGBM v4.6.0 + CatBoost v1.2.10 | **30** | AdaBoost/HistGBC 正确包含（非 meta-wrapper） |
| 1.10+ | 可能更少 | - | - | PassiveAggressiveClassifier 已移除 |

**影响**：论文声称"evaluated 27 baseline models"，但新环境只跑出 25 个，或未包含 CatBoost 导致遗漏最佳模型。

**修复**：
1. 动态获取模型数：`len(all_estimators())` 在 Notebook 中自动计算
2. 外部框架（XGBoost/LightGBM/CatBoost）单独声明版本号并说明"alongside"
3. 论文 Methods 写"30 models (27 sklearn + 3 external)"而非固定数字
4. **AdaBoostClassifier 和 HistGradientBoostingClassifier 不是 meta-wrapper**，不要放入 meta_wrappers 跳过列表
5. CatBoost 可能在特定数据集上超越所有 sklearn 模型——PIMA 案例中 CatBoost F1=0.7067 > GBC 0.6882
  6. **CatBoost + SMOTE 过拟合陷阱**：在 <1000 样本的数据集上，CatBoost + SMOTE 管道可能产生 F1=1.0 的完美分数。原因是 SMOTE 在小样本上生成与真实样本极接近的合成点，CatBoost 的强梯度提升能力可以"记忆"这些边界。验证时须使用 `cross_validate` + `ImbPipeline`（确保 SMOTE 在 fold 内），并 check 每折结果的 std——若 std=0 且 F1=1.0 则标记 CATASTROPHIC_OVERFIT。详见 `references/catboost-smote-overfit-detection.md`。

**检测方法**：对比论文声称的模型数与当前环境实际输出。差异 ≥ 2 则标记 ⚠️ MODEL_COUNT_MISMATCH。同时检查是否漏装了 CatBoost/LightGBM/XGBoost。同时检查 Notebook 中是否包含这些外部框架（见"单一权威Notebook原则"下的 Notebook 缺失外部框架陷阱）。

### state.json 自评不可靠陷阱（2026-06-23 新增, 2026-06-24 更新: 内部不一致检测）

**核心问题**：`state.json` 中的 `quality_score` 和 `gate_status` 是**自报告**值，可能比实际独立审计结果高 2 倍。

**内部不一致检测（2026-06-24 新增）**：同一 state.json 中 top-level `quality_score` 可能与 `gates_result.quality_score` 不同。

```bash
python3 -c "
import json
with open('state.json') as f:
    d = json.load(f)
top = d.get('quality_score')
gate = d.get('gates_result', {}).get('quality_score')
print(f'  top-level: {top}, gates_result: {gate}')
if top and gate and abs(top - gate) > 5:
    print('⚠️ STATE_INTERNAL_INCONSISTENCY — 相差 >5 分，需同步')
"
```

**核心问题**：`state.json` 中的 `quality_score` 和 `gate_status` 是**自报告**值，可能比实际独立审计结果高 2 倍。

### 实战案例：pima-crispdm 审计

| 指标 | state.json 自报 | 独立审计结果 | 差异 |
|:-----|:---------------:|:-----------:|:----:|
| quality_score | 80 | **40** | 高估 100% |
| gate_status | PASS | **FAIL** | 完全相反 |
| D10a | 100% | **无法计算**（BBL过期） | 引用失步 |
| 数据完整性 | PASS | **CRITICAL FAIL**（数值虚构） | 完全相反 |

### 根因

1. **state.json 是自动化管线产物**，数值在管线运行的最后一步被写入，不会在后续被重新验证
2. **quality_score 的计算逻辑可能包含乐观偏差**（如仅检查文件是否存在，不检查内容正确性）
3. **gate_status=PASS 不代表当前状态通过**——因为 gate_timestamp 可能早于后续修改

### 检测方法

```bash
# 检测内部不一致：top-level quality_score vs gates_result.quality_score
python3 -c "
import json
with open('state.json') as f:
    d = json.load(f)
top = d.get('quality_score')
gate = d.get('gates_result', {}).get('quality_score')
print(f'  top-level: {top}, gates_result: {gate}')
if top and gate and abs(top - gate) > 5:
    print('⚠️ STATE_INTERNAL_INCONSISTENCY')
" 2>/dev/null || echo 'Cannot parse state.json — may not have gates_result field'
```

**2026-06-24 实战案例（pima-crispdm 审计）**: state.json 的 top-level quality_score=96, 但 gates_result.quality_score=85（相差 11 分），独立审计=79（相差 17 分）。同一文件内两处 quality_score 不同步，说明门禁数据在提交后被修改但未更新另一处。**修复: 统一 quality_score 为独立审计结果，并更新 gate_timestamp。**

```bash
# 对比 state.json 自评分与独立审计评分
# 如果 quality_score >= 70 但独立审计 < 50 → 标记 STATE_SUSPECT
# 如果 gate_status=PASS 但 L0.5 数据诚实门 FAIL → 标记 GATE_MISMATCH
```

### 修复原则

1. **永远不单独信任 state.json 的 quality_score**——必须独立运行 G1-G7 完整闸门审计
2. 每次对 paper.tex 或 references.bib 做修改后，**必须更新 gate_timestamp** 或重置 gate_status
3. 在质量报告开头显式标注"state.json 声明 vs 实际审计"的差异对比表
4. 若 state.json 与独立审计差异 > 20 分，在报告中标记为 ⚠️ STATE_OVEROPTIMISTIC

## 图真实性检查（2026-06-23 新增）

论文可能包含"占位图"——用 `minipage`+`tabular` 伪装的文本表格，声称是图但无实际渲染内容。

**检测方法**：
```python
# 检查 paper.tex 中真正的渲染图 vs 文本占位
# 真图：\includegraphics / \begin{tikzpicture}
# 假图：\fbox{\begin{minipage} 内嵌 \textbf{图标题} + \begin{tabular}
import re
with open('paper.tex') as f:
    tex = f.read()
real_figs = len(re.findall(r'\\includegraphics|\\begin\{tikzpicture\}', tex))
table_figs = len(re.findall(r'\\begin\{figure\}.*?\\centering\\begin\{minipage\}.*?\\begin\{tabular\}', tex, re.DOTALL))
print(f'Real figures: {real_figs}, Text-based pseudo-figures: {table_figs}')
```

**PIMA案例**（2026-06-23）：paper.tex的"ROC Curve Summary"和"SHAP Global Feature Importance"两个figure环境实际上是 minipage+tabular 文本表格，**无任何实际渲染图**。对于ODE/PINN等计算建模论文，0张真实渲染图（仅tikz流程图）是严重问题。

**修复原则**：
1. 每个 `figure` 环境必须包含 `\includegraphics` 或 `\begin{tikzpicture}`（流程图除外）
2. ROC曲线、SHAP beeswarm、混淆矩阵等标准科学图必须有实际渲染版本
3. 计算建模论文（ODE/PINN）至少需要：轨迹时间序列图、参数恢复散点图、对比条形图

### 消融层级命名一致性检查（2026-06-24 新增）

**问题**：论文定义的消融层级（Minor/Medium/Severe Leakage）与实验 JSON 中的命名可能不一致。在 PIMA 案例中，论文 Methods 说 "Minor Leakage = Global imputation" 但正文又说 "minor leakage (global SMOTE)"——层级定义自相矛盾。同时 JSON 的 `minor_leakage` 定义为 Global SMOTE，而论文 Methods 描述为 Global imputation。

**检测方法**：交叉对比三处来源的消融层级定义：
1. paper.tex Methods 中的层级定义（`\begin{itemize}` 段）
2. paper.tex Results 中的描述语句（如 "mild leakage (global SMOTE)")
3. 实验 JSON 文件中的 `levels` 键名及各层级的 `note` 字段

**规则**：
- 若 Methods 说 "Minor = Global SMOTE" 但 JSON 的 `minor_leakage.note = "Global impute"` → 标记 ⚠️ ABLATION_LEVEL_MISMATCH
- 若同一处 level 在 Methods 和 Results 中描述不同 → 标记 ⚠️ ABLATION_DESCRIPTION_CONTRADICTION
- 修复时以 JSON 的 `note` 字段为真实来源，更新 paper.tex

**PIMA案例**（2026-06-24）：
| 来源 | Minor Leakage 描述 | 问题 |
|:-----|:------------------|:-----|
| Methods (L236) | "Global imputation applied prior to CV splitting" | ❌ |
| Results (L303) | "mild leakage (global SMOTE applied prior to CV splitting)" | ✅ |
| JSON minor_leakage.note | "Global SMOTE (leakage: SMOTE uses train+val stats)" | ✅ |

**修复**：统一 Methods 定义与 JSON 一致。若 JSON 的 minor = global SMOTE，则 Methods 也应写 minor = global SMOTE。

论文修正数据伪造问题后，数值一致性检查必须在**每次文本修订后重新执行**——因为 paper.tex 中的数值可能在后续编辑中被"漂回"旧值。

**检测方法**：在论文 G5-G7 间，每次 paper.tex 被 patch 后，对比所有结果段落/表格值与 definitive experiment result JSON/CSV 的 actual_values 字段。

**PIMA案例严重教训**（2026-06-23）：尽管前次审计（2026-06-20）记录了 Severe Leakage 的虚构值（paper_claims f1=0.7338, recall=0.708），但 paper.tex 仍然包含完全不同的虚构值（recall=0.5030, precision=1.0000），这些值既不在 paper_claims 也不在 actual_values 中。此外，实验代码目录下有多个实验脚本（pima_definitive.py, pima_correct_ablation.py, pima_crispdm_helix.py 等）产生不同结果——paper.tex 引用的是哪个脚本的输出无法从数值本身推断。**修复后必须重新验证，不可信任一次修复。**

**规则**：凡引必验 的同时，**凡数必比对**——论文中每个数值声明的修改都必须重新与实验输出比对。

### 叙事级伪造修复原则（2026-06-24 新增）

**核心问题**：当实验数值被虚构（如 Severe Leakage Recall 从实际 0.6232 被写为 0.5030），这些虚假数字通常**驱动了论文的叙事**（如"catastrophic collapse"）。简单地替换数字（0.5030→0.6232）而不重写叙事，会造成"数字诚实但叙事矛盾"的荒谬局面。

**修复流程**：

```
第一步：提取所有虚构数值的位置
第二步：评估每个位置的数值是否驱动了叙事
  - 如果仅是被动引用（"F1=0.6857"）→ 直接替换数字
  - 如果是主动叙事（"Recall plummets to 0.5030"）→ 必须重写整个句子
第三步：叙事重写三个原则
  1. 不保留旧叙事的语气词（"plummet", "catastrophic", "artificially"）——除非新数值仍支持该语气
  2. 用实际数值构建新叙事（"Recall drops from 0.7464 to 0.6232, a -16.5% decrease"）
  3. 整体叙述方向必须与新数据一致（若数据不支持"膨胀"叙事，改为"选择性扭曲"或"指标失衡"）
```

**PIMA案例**（2026-06-24）：
| 位置 | 旧叙事 | 旧值 | 新值 | 新叙事 |
|:-----|:-------|:----:|:----:|:-------|
| Abstract | "catastrophic metric collapse" | Rec=0.5030 | Rec=0.6232 | "selective metric distortion" |
| Contributions | "Recall plummets" | 0.5030 | 0.6232 | "Recall reduced from 0.7464 to 0.6232" |
| Ablation text | "catastrophic collapse" | F1=0.6661 | F1=0.6451 | "further degrades F1 to 0.6451" |
| Discussion Claim | "Precision reaches 1.0000 while Recall collapses" | 1.0000/0.5030 | 0.7243/0.6232 | "Precision-Recall relationship distorted" |
| Conclusion | "collapses Recall to 0.5030" | 0.5030/1.0000 | 0.6232/0.7243 | "selective metric distortion, Precision elevated, Recall suppressed" |

**交叉引用**：详见 `paper-numerical-integrity-audit` 的 definitive_ablation.json 双结构检测模式。

### definitive_ablation.json 双结构检测（2026-06-24 新增）

**模式**：当实验结果 JSON 文件同时包含 `paper_claims` 和 `actual_values` 两个字段时，这是一个**危险信号**——说明撰文阶段存在系统的数值美化行为。

```json
{
  "paper_claims": {
    "severe_leakage_f1": 0.7338,
    "severe_leakage_recall": 0.708
  },
  "actual_values": {
    "severe_leakage_f1": 0.6451,
    "severe_leakage_recall": 0.6232
  }
}
```

**检测规则**：凡实验代码输出目录下存在包含 `paper_claims` 字段的 JSON 文件，必须：
1. 逐条对比 `paper_claims` 与 `actual_values` 差异
2. 若差异 > 2%，标记为 🔴 PAPER_CLAIMS_FABRICATION
3. 使用 `actual_values` 作为唯一可信数据源修复 paper.tex
4. 应用"叙事级伪造修复原则"（见上）

### 政府申报方案 / 商业计划书检查告警（2026-06-23 新增）

政府/商业申报方案的审计不同于学术论文审计，有**特有的陷阱模式**：

| 陷阱模式 | 信号 | 典型错误 | 修复 |
|:---------|:-----|:---------|:-----|
| **SNR跨域比较** | 将非侵入式SNR与侵入式SNR直接比 | "信噪比100:1远超侵入式BCI的1:10" | 改为与同类技术对比（EEG） |
| **成本无限定** | 说"硬件成本X元"但不区分物料/整机/BOM | "单套成本仅2500元" | 加"物料"限定 + 补充进口对比区间 |
| **规格最高值** | 报所有参数最大值，不做场景化说明 | "三路1920×1080@90fps" | 加"单路最高" + 场景化配置说明 |
| **覆盖范围过度承诺** | "一个平台同时服务6大领域全部可用" | 未区分已验证模块和开发中模块 | 分阶段标注：已验证/验证中/框架规划 |
| **论文/成果数量不核实** | 仅查本地管线不查外部发表 | "BPPV仅5篇→文档14篇夸大" | 同时查PubMed、CNIPA、产品页面 |

**审计流程**：
1. 定位所有数字声明（成本、性能指标、论文数、专利数、覆盖疾病数）
2. 逐项标注数据源：已验证 / 可查证 / 需外部数据库
3. 技术声明检查：区分"与同类技术对比"和"跨类技术对比"——前者可接受，后者需重述
4. 范围声明检查：区分"已实现"和"具备技术框架"——过度承诺降低可信度

- `references/citation-verification-full-text.md` — 参考文献全文级引用恰当性审查方法
- `references/submission-materials.md` — 投稿材料准备清单和模板
- `references/pima-crispdm-data-integrity-audit-2026-06-20.md` — Notebook 多配置冲突导致论文数字无法复现
- `references/comprehensive-quality-report-template.md` — 全面质量检查报告结构模板（结合 L0/L0.5/G1-G7 + P0/P1/P2优先级）
- `references/skill-audit-methodology.md` — 技能目录全面审计方法论
- `references/meddata-authentication-debugging.md` — MedData 认证系统逆向分析
- `references/meddata-authentication-debugging.md` — MedData（博库数据）认证系统逆向分析：medbooks SSO 与 MedData 独立认证、SSO token 格式不兼容（JWT vs uuid:timestamp）、full_look + viewtext 两步 PDF 下载流程、SPA 前端逆向调试方法