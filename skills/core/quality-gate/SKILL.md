---
name: quality-gate
description: "⚡ P0 闸门技能。四层质量架构：①响应级漂移检查 ②项目级L1-L4交付闸门 ③论文管线G1-G7原子闸门 ④SCI内容评审。通用铁律：任务完成→质量评估→不达标→循环执行。无skill_view记录=门不通过。G5引用质量为最关键门。G7通过→自动sci-paper-quality-review。"
version: 2.40.0
priority: P0
signature: "deliverable: dict, context: dict -> quality_report: dict (L0-L4 scores + gate_pass: bool + fix_suggestions: list) -> trigger-loop signal"
related_skills: [project-experience-distillation, evolution, sci-paper-quality-review, paper-pipeline, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification, paperjury, citation-appropriateness-verification, retraction-investigation, paper-knowledge-extraction, paper-knowledge-base]
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


## 触发条件 · TRIGGER_CONDITIONS

- **任务完成触发**：每次任务完成或管线阶段切换时自动运行
- **提交前触发**：git commit / push 前执行质量闸门
- **外部驱动触发**：cron 作业（每4小时或每15分钟文献监控）
- **手动触发**：用户请求质量检查或审计

## 运行模式 · OPERATING_MODES

- **正常模式**：标准质量检查流程，输出四报告
- **快速模式**：仅检查P0级问题，适合快速验证
- **深度模式**：完整检查+人工复核建议，适合提交前
- **审计模式**：全量历史对比，追踪质量趋势

- 正常模式: L0-L4全量检查 + 四报告生成
- 快速模式: P0级问题检测（结构完整性、引用完整性、脚本可运行性）
- 深度模式: 正常模式 + 人工复核建议 + 铁律一致性检查
- 审计模式: 正常模式 + 历史对比 + 趋势分析

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
| 2026-06-24 | 2.15.1 | 新增自主修复不问原则（用户纠正：自己做主不待批准）；新增 OpenML 基准对比作为 G4 数据完整性检查的扩展；新增 EuropePMC 作为 PDF 下载备用通道（Kapoor2023 实战验证） |
| 2026-06-24 | 2.16.0 | 新增 OpenML Claim-Only 检测（G2.5子项）；新增统计量可追溯性检查（p-value/Cohen's d 需在代码中记录）；新增 PDF-bib DOI 不匹配检测（G5子项）；新增 JSON-to-JSON ensemble 三角校验（横向对比所有 JSON 的 ensemble 成员）；新增 references/codex-comprehensive-quality-report-workflow.md |
| 2026-06-24 | 2.17.0 | 新增 自主修复闭环协议（codex-comprehensive-quality-report-workflow.md Step 5）；新增 修复决策矩阵（可自主修复 vs 需人工）；新增 fix-log.md 模板；扩充 comprehensive-quality-report-template.md 增加"报告生成后的必做动作"警告 |
| 2026-06-24 | 2.18.0 | 新增 G6 论文约束系统检查框架：同实体跨位约束、声明-证据对齐约束、比较-基准对齐约束、叙事-数据比例约束。四种约束类型独立于具体论文领域。 |
| 2026-06-24 | 2.19.0 | 新增审稿人评价框架（Q1-Q6六问）：假说问、空白问、解法问、实验问、结论问、价值问。六问不取代G1-G7，而是将G1-G7发现组织到审稿人视角下。新增六问评分标准（60分制）与投稿判定。新增 references/skill-design-abstraction-levels.md 记录抽象层次方法论。 |
| 2026-06-24 | 2.20.0 | 调研 12 个建立已久的审稿框架（PROBAST/TRIPOD/Cochrane/AMSTAR2/EQUATOR 等），提取三项结构性改进待后续版本落地：领域级判定取代总分（Cochrane RoB2）、关键项一票否决（AMSTAR2）、论文类型识别→不同模板（EQUATOR Network）。新增 references/established-review-frameworks.md 和 references/paper-constraint-system.md。 |
| 2026-06-25 | 2.25.0 | 新增 G2.5 隐藏数据集检测（Hidden Dataset Detection）：代码已跑但论文未报的数据集，区分"实验设计缺陷"与"论文呈现不足"；HCS-3WT 实战：WDBC 结果存于 experiment_results.json 但论文仅一句消融提及，正确判定 P1 而非 P2：一篇不过不换下一篇，全部通过才停。Hermes→Codex 迭代协议（Hermes决策，Codex执行，Hermes验证）。新增 cron 整合模式（paper-quality-iteration 每4小时驱动）。更新核心理念表。|。从 ~/.hermes/skills/ 迁移到 Synthos/skills/core/。补 GOLDEN_SET.md + cases/expected/。四报告框架集成到 comprehensive-quality-report-template。认知同步协议：Codex 从 Synthos 文件系统直接加载技能，不再嵌入任务文件。事件驱动 cron 架构：文献监控→PDF收割→评审链。|
| 2026-06-25 | 2.28.0 | 新增 cron 作业 tmux 会话清理协议；新增 state.json 结构变体检测（gates_result.gates 可为 list 或 dict；hard_fails 字段不与个体 gate status 对应）；新增低分 PASS vs HARD_FAIL 决策区分；新增 Codex tmux 多行指令发送模式（每行 send-keys + Enter，需要 Enter 推进）；新增 references/off-axis-iris-fix-2026-06-25.md 修复实录。|
| 2026-06-25 | 2.30.0 | 三项铁律：凡引必验新增"搜索替代文献优先"规则（PDF不可达时先搜等价引用替换而非仅标注）；G5引用审计新增"数据集引用规则"（优先引用描述数据的原始论文而非仓库URL）；新增 references/pdf-alternative-search-protocol.md 替代搜索协议 |
| 2026-06-25 | 2.32.0 | 实战教训固化为铁律：凡引必验新增"DOI可解析性优先于PDF存在性"规则（禁止仅查bib有无DOI字段）。检查员报告模板新增`Resolved?`列，DOI 404→FICTITIOUS_REFERENCE。Hermes→Codex 协作协议新增"咨询模式"（Codex可以给建议/报告，Hermes决断）。用户确认工作流：<br>① Hermes决断策略 → Codex执行 → Codex报告 → Hermes验证<br>② Hermes征求Codex意见 → Codex分析建议 → Hermes决定 |
| 2026-06-25 | 2.33.0 | 新增"外部驱动管线路径"检查协议：cron 作业的质量门扫描必须覆盖所有三条管线路径（`~/outputs/papers/` + `~/桌面/article_todo/` + `/media/yakeworld/sda2/Synthos/outputs/papers/`），不能仅查 `~` 目录。主管线在外部驱动上（157篇），`~` 仅为队列/报告副本。新增 `references/multi-path-pipeline-scan.md` 参考文件。实战教训：2026-06-25 首次发现主管线在 sda2 而非 home 目录，仅扫 home 会得到空结果。新增批量状态扫描的权威数据源确认规则。 |
| 2026-06-25 | 2.35.0 | 新增撤稿论文审计四步法（查→下→QC→论文工厂检测）；新增 retracted-paper-audit-methodology.md 参考文件；新增论文工厂 9 指标检测清单和作者重叠网络分析。实战案例：温州市人民医院 3 篇撤稿论文审计 + 跨领域作者重叠发现。 |：部分论文使用 thebibliography 环境而非 references.bib 文件（如 stroke-prediction）。当 06-references/ 无 .bib 文件时，paper-references-scanning 子技能会静默返回空结果（不报错），导致引用审计跳过。必须在 G5 引用审计的**第一步**（扫描 bib 之前）先检查论文是否使用了 inline bibliography（grep thebibliography paper.tex）。若使用 inline bib，改用 inline 引用提取脚本（引用键从 \\\\cite{} 提取，引用内容从 thebibliography 环境直接读取）。stroke-prediction 有 10 篇 inline 引用，D10a=100%，但引用总量偏少（10篇）需要后续迭代补充。新增 references/inline-bibliography-audit.md；新增 references/retracted-paper-investigation.md 撤稿调查协议 |
| 2026-06-25 | 2.35.0 | 新增"质量报告必须输出完整四报告"陷阱（用户纠正：不是应该有4个完整的这个质量检查报告的吗）；新增 ablation-leakage-implementation.md 中 Leaky SMOTE 索引对齐陷阱（SMOTE后必须重新做CV分割，不可用原始索引） |
| 2026-06-25 | 2.36.0 | 新增 baseline_inconsistency_detection.md（摘要基线不一致检测）：delta值用A作基线但报告中B为基准。新增 numeric_cross_location_consistency.md（关键数值跨位置一致性）：F1膨胀率等核心数字在7+个位置需一致。新增 stale_quality_report_trap.md（旧报告可能完全错误但state.json仍标记PASS） |
| 2026-06-26 | 2.39.0 | 新增 D10a false failure 陷阱（inline bib vs references.bib mismatch）；新增 references/d10a-inline-bib-debugging-2026-06-26.md 实战调试记录；修复 inline bibliography 审计陷阱：当论文同时使用 inline thebibliography 且有 references.bib 时，D10a 必须从 cite ↔ bibitem 计算而非 cite ↔ bib，否则产生假阴性 |
| 2026-06-27 | 2.41.0 | 新增 `state.json scan scope` 陷阱（批量扫描时过滤 papers/submissions/queue/_archive 等非论文目录）；新增 `quality_score_normalized variant` 陷阱（quality_score_normalized 不遵循 /100 缩放规则，不同论文有不同计算公式）；修复批量扫描脚本的论文计数假阳性问题（从 93→93 含过滤逻辑，实际有效论文需排除非论文目录）；新增 inline bibliography D10a 追踪缺失检测（68/93 篇 D10a=?） |
| 2026-06-27 | 2.42.0 | 新增 `paper_count_discrepancy` 陷阱：state.json 统计数（93篇）与 agent-tracker.json completed_papers 数（63篇）不一致，扫描脚本未排除 kaggle-leakage-audit、submissions 等非管线论文目录。修复：扫描必须限定在直接子目录中的 state.json，排除有 state.json 但非管线论文的目录（kaggle-leakage-audit、submissions、papers 索引等）。新增 references/paper-count-discrepancy-trap.md |
| 2026-06-27 | 2.43.0 | 新增 `state.json_audit_flag_freshness` 陷阱（crispdm-wdbc 实战）：state.json audit_history 中的 P2 标记不自动可信，必须独立数值计算验证。cross_dataset_consistency 检测新增重验证规则。crispdm-wdbc 案例：state.json 标记"交叉数据集delta convention不一致"但实际计算确认三数据集使用相同约定（绝对值×100），标记为假阳性并清除。 |
| 2026-06-27 | 2.44.0 | 新增早期DOI 404判定规则（references/pdf-alternative-search-protocol.md）：SAGE/Springer/AJP等出版社的2010年前DOI在DOI解析器+Crossref均返回404/403，但论文真实存在，判定为[WARN]非[FAIL]。bppv-canalith-relocation-ode实战：12个引用中5/12失败(42%)但全部真实。新增DOI前缀→Crossref状态对照表。 |
| 2026-06-29 | 2.45.0 | 新增 paper_json_numerical_consistency 检查（G7子项）：论文数值必须与 experiment_results.json 一致。k=N 参数不一致、样本量/特征数不一致、图脚本硬编码检测。HCS-3WT 实战：代码 k=15 vs 论文 k=6，15 处数值更新，fig3/fig4 改为 JSON 读取，PDF 编译通过，state.json 0.73→0.88。 |
| 2026-06-29 | 2.46.0 | 新增 state.json CLAIMED vs 07-quality/ VERIFIED 审计陷阱（用户纠正：state.json PASS 不等于质量报告完整）。审计队列（AUDIT_QUEUE.md）中论文的状态判定必须独立于 state.json 声明：state.json 的 gate_status=PASS 是\"声称已修复\"，07-quality/ 目录的4份报告是\"已验证修复\"。审计时必须读取 07-quality/ 的实际文件清单，确认 report-1~4 全部存在且内容完整。缺失报告 → 无论 state.json 显示什么，都视为未验证。新增 NEEDS_REPAIR 状态（quality_score<0.85 或关键指标失败时标记）。新增 AUDIT_QUEUE.md 审计协议：读队列→取首篇QS≠0→检查07-quality/ 4份报告→若全部PASS→移除；若P0_WAITING_USER→BLOCKED；否则NEEDS_REPAIR。新增 references/audit-queue-protocol.md 完整协议文档。 |

### state.json CLAIMED vs 07-quality/ VERIFIED — 审计队列状态验证陷阱（新增 2026-06-29）

**问题**：state.json 的 `gate_status=PASS` 和 `quality_score=88` 是**声称状态**，不是**验证状态**。当审计队列（AUDIT_QUEUE.md）中一篇论文被标记为"待审计"时，审计员如果直接读取 state.json 就认为"已通过"，会跳过对 07-quality/ 目录中4份标准报告的完整性检查。bppv-pinn-canalolithiasis 案例：state.json 显示 PASS, D8=15/15, D10a=100%, G1-G7全部PASS, quality_score=88，但 07-quality/ 目录仅含1份 quality-report.md，缺失3份标准报告（report-1~4）。这意味着修复已完成但报告文件丢失/未生成，论文实际上**未通过完整审计**。

**正确审计协议**（AUDIT_QUEUE.md 每日三次 cron 作业执行流程）：

1. 读取 `AUDIT_QUEUE.md` 前5行获取队列头部
2. 按优先级取队列中第一篇 `QS≠0` 且状态为"待审计"的论文
3. 检查 `07-quality/` 目录文件清单：
   - **必须存在**：`report-1-universal-six-domains.md`, `report-2-*specialty*.md`, `report-3-references-audit.md`, `report-4-inspector-report.md`
   - 缺失任何一份 → 无论 state.json 显示什么，视为未验证
4. 如果4份报告全部存在且内容完整：
   - 检查 `quality_score ≥ 0.85`（通过阈值）
   - 检查 `gate_status` 为 PASS/VERIFIED
   - 检查 `quality_gates` 中所有 G1-G7 为 PASS
   - 如果全部通过 → 从队列移除，`gate_status=VERIFIED`
5. 如果存在 `P0_WAITING_USER` → 标记为 `BLOCKED`
6. 如果 `quality_score < 0.85` 或关键指标失败（D8=0, D10a=0%等）→ 标记为 `NEEDS_REPAIR`

**判定规则**：

| 条件 | 队列状态 | 后续操作 |
|------|---------|---------|
| 4份报告全部存在且完整 + qs≥0.85 + G1-G7全PASS | 从队列移除 → VERIFIED | 完成 |
| P0_WAITING_USER 或 BLOCKED 标记 | BLOCKED | 等待人工处理 |
| 07-quality/ 报告缺失/不完整 | IN_PROGRESS 或 NEEDS_REPAIR | 重新生成报告或标记修复 |
| quality_score < 0.85 | NEEDS_REPAIR | 需要完整修复后重新审计 |
| D8=0 或 D10a=0% | NEEDS_REPAIR | 需要补充引用体系 |

**bppv-pinn-canalolithiasis 实战修复**：
- 问题：state.json PASS 但 07-quality/ 缺3份报告
- 修复：从 paper.tex 内容提取引用/指标/模型信息，重新生成4份标准报告
- 结果：D8=15/15, D10a=100%, G1-G7全部PASS, quality_score=88 ≥ 0.85 → VERIFIED
- 更新：07-quality/ 补全4份报告，state.json gate_status PASS→VERIFIED，AUDIT_QUEUE.md 标记移除

**关联陷阱**：
- `stale_quality_report_trap`：旧报告可能过期
- `re-verification_trap`：已修复项必须重新验证
- 此陷阱是上述两个的组合扩展：**声称的修复 + 缺失的验证文件 = 假阳性通过**

**注意**：07-quality/ 目录中的 `status.json` 和 `quality-report.md` 可能来自旧的扫描工具（如 PARTIAL-PAPERS D8/D10a/DOI Batch Scan），不是标准四报告格式。审计时必须检查标准报告文件是否存在，不能仅依赖 status.json 中的分数。
检查点：p-value 和 Cohen's d 必须有可执行代码支持，per-fold 数据需保存到 07-quality/ 目录。

### baseline_inconsistency_detection — 基线不一致陷阱

**问题**：论文声称的变化量（delta）使用的基线值与声明的基线不一致。典型如 `ensemble F1=0.8206` 但 `+14.17%` 膨胀率实际来自 `GBC 0.7886`。读者从摘要 0.8206→0.9004 计算得 +9.72%，与 +14.17% 矛盾。

**检测方法**（G7 数值验证阶段执行）：
1. 提取论文中所有 delta/膨胀/变化百分比声明
2. 对每个声明，确认 baseline 值和 delta_end 值
3. 从代码/JSON 中独立计算 `(delta_end - baseline) / baseline * 100`
4. 比对声明值与计算值
5. **同时检查同一 delta 在全文所有位置的 baseline 是否一致**

**修复**：选择正确基线，统一全文所有位置，修正数值。

**参考**：`references/baseline-inconsistency-detection.md`

### cross_dataset_consistency — 交叉数据集delta convention一致性

**问题**：论文跨数据集比较时，delta/百分比变化使用不一致的计量约定（绝对值 vs 相对值）。典型如 crispdm-wdbc：PIDD F1 +6.71% 是绝对值（6.71 percentage points），Heart F1 +14.17% 是相对值（14.18%），WDBC F1 -0.10% 两者巧合接近（-0.10pp vs -0.103%），掩盖了不一致。

**检测方法**（G7 数值验证阶段执行）：
1. 提取所有 delta/百分比声明
2. 对每个声明，计算绝对值 AND 相对值
3. 检查是否所有声明使用相同公式
4. 特别注意高基线值（如 F1>0.95）：绝对值和相对值数值接近，容易隐藏不一致
5. **重验证规则**：state.json 中记录的 P2 标记不自动可信。每次重验证时，必须独立计算所有三个数据集的绝对/相对 delta，确认约定是否真的不一致。crispdm-wdbc 案例：state.json 标记"不一致"但实际计算确认三数据集使用相同约定（绝对值×100），标记为假阳性。

**修复**：统一为相对值（推荐科学论文惯例），全文明确标注。

| references/cross-dataset-consistency-check.md (含 crispdm-wdbc 假阳性案例) |

**关联**：常与 `baseline_inconsistency_detection` 同时出现。旧报告（stale_quality_report_trap）通常不检测此问题。**特别注意**：旧 audit 的 P2 标记可能是假阳性，必须通过数值计算重新验证。

### state.json_audit_flag_freshness — 旧审计标记不可信陷阱

**问题**：state.json 中 audit_history 记录的修复标记（如 "P2 pending"）是**历史审计声称**，不是**当前验证结果**。重验证时如果直接引用旧标记，会产生假阳性结论。

**典型场景**：
- state.json 记录 "P2: cross-dataset convention inconsistent"
- 重验证时直接引用该记录，跳过实际计算
- 实际上三数据集约定一致，标记为假阳性

**正确流程**：
1. state.json 中的 audit_history 记录只作为**检查清单来源**（告诉你要检查什么）
2. 对每个旧标记执行独立数值计算验证
3. 确认标记仍然有效 → 保留；无效 → 清除并记录
4. 在 fix-log 中添加 "假阳性清除" 条目

**关联**：与 `re-verification_trap` 互补。re-verification_trap 关注已修复项是否残留，此陷阱关注旧标记是否仍然正确。

### numeric_cross_location_consistency — 数值跨位置一致性

**问题**：同一数值在论文不同位置（Abstract/Intro/Results/Discussion/Conclusion/Figure caption/Figure content）出现时值不一致。

**检测方法**：对每个核心数值，grep 全文所有位置，逐位置对比。

**参考**：`references/numeric-cross-location-consistency.md`

### stale_quality_report_trap — 旧报告过期陷阱

**问题**：07-quality/ 目录中的旧质量报告可能完全过时，但 state.json 仍标记 PASS。审计时如果误读旧报告，会得到错误结论。

**检测方法**：
1. 对比 quality-report.md 日期 vs state.json last_updated
2. 对比报告中 D8/D10a 值 vs state.json reference_health
3. 不一致 → 报告已过期，必须重新审计

**参考**：`references/stale-quality-report-trap.md`

### re-verification_trap — 重验证必须执行（新增 2026-06-26）

**问题**：对之前已审计+修复的论文执行新一轮审计时，如果跳过验证直接用旧报告结论，会产生假阳性通过。state.json 中的修复记录是"声称已修复"，不是"已验证修复"。

**重验证流程**（每次对已有修复记录的论文审计时必须执行）：
1. 读取 fix-log.md 和 07-quality/report-*.md
2. 对每个已修复项执行 grep 全文残留检测
3. 重新运行 D8/D10a 扫描
4. 重新核对所有数值与 JSON 的一致性（含 k=N 参数、样本量、CV 策略）
5. 重新运行所有图生成脚本，确认从 JSON 读取数据
6. 如果旧修复仍然有效 → 标记 VERIFIED；如果有残留 → 执行修复
7. 更新 fix-log.md 添加重验证记录

**参考**：`references/re-verification-audit-pattern.md`

### paper_json_numerical_consistency — 论文-JSON 数值一致性检查（新增 2026-06-29）

**问题**：论文文本中的数值声明（Abstract/Intro/Table/Results/Discussion/Conclusion）必须与 experiment_results.json 完全一致。HCS-3WT 审计发现：代码参数 k=15 与论文声称 k=6 不一致，导致所有单分类器精度差异 2-5%，自动化率差异 8pp。

**检测方法**（G7 数值验证阶段执行）：
1. grep 论文所有数值行（Table + Abstract + 正文 + 结论）
2. 从 experiment_results.json 独立计算所有数值
3. 逐一对比：单分类器 ACC/REC/PREC/F1/AUC → 误差>2% 为 P0
4. HCS-3WT 关键指标 → 误差>3% 为 P0
5. 检查参数一致性：k 值、CV 策略、数据集描述、预处理步骤
6. 检查图生成脚本是否从 JSON 读取数据（非硬编码）
7. 更新论文以匹配 JSON（JSON 为真理源）
8. 重新编译 LaTeX（检查 Table 最后一行是否缺 `\\`）
9. 更新 state.json

**参考**：`paper-experiment-audit/references/paper-json-numerical-consistency-check.md`

### block_vs_in_progress_decision — 队列状态精确判定

**问题**：[IN_PROGRESS] 被滥用为"有未解决问题"的通用标记，但实际上 [IN_PROGRESS] 应该仅用于"审计正在执行中"。P0问题应使用 [BLOCKED: 原因]。

**决策规则**：
| 条件 | 队列状态 |
|------|---------|
| 所有 P0 修复完成且验证通过 | 可移至 VERIFIED 或处理 P1 |
| P0 数值修复完成但 P0 代码/统计检验未完成 | [BLOCKED: P0] |
| P0 有残留修复问题（如 p<0.01 残留） | [BLOCKED: P0_RESIDUE] |
| 仅 P1/P2 问题 | [IN_PROGRESS] 或处理完后标记完成 |
| 审计正在执行中 | [IN_PROGRESS] (仅用于正在进行的审计) |

### state.json scan scope — 管线扫描范围陷阱（新增 2026-06-27）

**问题**：批量扫描 state.json 时，以下 entry **不是论文**，会导致假阳性计数和错误审计：

1. **`papers/` 目录**：顶层 state.json 中有 `"papers"` entry，这是一个扫描索引，不是论文。
2. **`submissions/` 目录**：其中的 state.json 文件是投递优先级索引，不是管线论文。
3. **`queue/` 目录**：队列目录可能有 state.json，不代表论文。
4. **`_archive/`、`_archive_scripts/`、`_knowledge_only/`、`_template/`、`_templates/` 目录**：这些是归档/模板，不应纳入质量门统计。

**检测模式**（批量扫描脚本必须执行）：
```python
# 正确：只统计管线论文目录中的 state.json，排除所有非论文目录
import os, json, glob
base = '/media/yakeworld/sda2/Synthos/outputs/papers'
papers = []
for state_path in glob.glob(os.path.join(base, '*/state.json')):
    parent_dir = os.path.basename(os.path.dirname(state_path))
    # 1. 过滤归档/模板/知识目录
    if parent_dir.startswith('_'):
        continue
    # 2. 过滤非论文目录（完整列表见 references/paper-count-discrepancy-trap.md）
    non_paper_dirs = {
        'papers', 'submissions', 'queue', 'research', 'knowledge-index',
        'kaggle-leakage-audit'
    }
    if parent_dir in non_paper_dirs:
        continue
    # 3. 验证 state.json 内容 — 必须有 quality_score 或 gates_result
    try:
        with open(state_path) as f:
            data = json.load(f)
        if 'quality_score' not in data and 'gates_result' not in data:
            continue
    except:
        continue
    papers.append(state_path)
# 4. 验证：对比 agent-tracker.json 的 completed_papers 长度
# 差异超过 5 篇说明还有遗漏
```

**关联陷阱**：`papers/` entry 在 top-level state.json 中的字段是 `d8`, `d10a`, `doi_pct`, `has_tex` — 这些字段名与论文不同（论文用 `quality_score`, `gate_status`, `current_step` 等）。可通过字段名差异自动过滤。

**参考**：无独立参考文件（此陷阱已在 top-level state.json 结构设计中体现）

### quality_score_normalized variant — 归一化分数不遵循 /100 规则（新增 2026-06-27）

**问题**：`quality_score_normalized` 字段的缩放比例**不是简单的 `quality_score / 100`**。

| 论文 | quality_score | quality_score_normalized | 实际比例 |
|------|--------------|-------------------------|---------|
| 02-corneal-tension-ODE | 75 | 0.1 | 75 → 0.1（非 0.75） |
| 137-ciliary-body-ODE | 45 | 0.45 | 45 → 0.45（= /100） |

**根因**：`quality_score_normalized` 的计算方式可能是多层级综合（G1-G7 + layer_a_b + D8/D10a + 统计维度）的加权归一化，而非简单的线性缩放。不同论文/不同阶段可能有不同公式。

**正确做法**：
1. 直接使用 `quality_score`（0-100 范围）作为主要判定指标
2. 如果 `quality_score` 不存在（None），再尝试 `gates_result.quality_score`
3. **不要**通过 `quality_score_normalized` 反推 `quality_score`
4. 如果 `quality_score` 为 None 且无 `gates_result.quality_score`，标记为"未评分"

**关联**：与 `state.json 结构变体检测`（2.28.0）和 `state.json 内部不一致检测`（2.13.0）相关。批量扫描时必须处理三种结构变体。

**问题**：用户要求"质量检查报告"时，输出不完整的一体化报告而非标准四报告结构（通用六域+类型专项+引用审查+检查员）。2026-06-25用户明确纠正："不是应该有4个完整的这个质量检查报告的吗？"

**修复**：任何时候生成质量报告，必须：
1. 加载 `comprehensive-quality-report-template.md` 确认四报告结构
2. 按顺序输出全部四份独立报告：报告一（通用六域）、报告二（类型专项）、报告三（引用审查）、报告四（检查员+凡数必源+虚构检测）
3. 每份报告独立评分/判定
4. 最终以最严格判定为准
5. MD转PDF时需处理emoji/Unicode不兼容问题（替换为[OK]/[NO]/[WARN]/[CRIT]等文本标记，用xelatex + Noto Sans CJK SC编译）

**对应原则**：模板存在的意义就是被完整使用。部分输出的报告比没有更差——它给用户虚假的质量感知。

**2026-06-26 新增 — 文献监控交付物质量门（L2）**：cron 作业的文献监控产出需要质量闸门验证，包括论文发现可信度、下载可用性、与管线重叠检测。详见 `references/retracted-paper-audit-methodology.md`。

**2026-06-26 新增 — 撤稿论文与管线论文状态分离（L3）**：撤稿论文审计产物（如温州撤稿论文）只有 quality_report.md 没有 state.json，这是预期行为。cron 批量扫描需区分"审计目标（无 state.json）"和"管线论文（必须有 state.json）"。详见 `references/quality-gate-cron-bulk-scan.md` 的"质量报告有但 state.json 缺失"章节。

**覆盖范围**：适用于所有论文类型的质量检查（临床ML用PROBAST，基础医学用实验专项，综述用AMSTAR2，通用用模板默认项）。

---

### inline bibliography 审计陷阱

**问题**：paper-references-scanning 子技能依赖 `references.bib` 文件来扫描引用。当论文使用 inline bibliography（`\\begin{thebibliography}` 环境在 paper.tex 内）时：
1. `references.bib` 不存在 → paper-references-scanning 静默跳过
2. 引用审计从未执行 → G5 门从未检查 → 论文被标记为"通过"（因为无失败，也没有检查）
3. 这是**假阳性通过**——论文可能引用了虚构文献，但我们从未检查

**检测方法**（在 G5 引用审计开始后立即执行）：
```bash
# 检查 inline bibliography
if grep -q 'thebibliography' paper.tex; then
    echo "INLINE_BIB: 使用 inline bibliography"
    # 改用 inline 引用提取脚本
else
    # 常规 .bib 扫描
    paper-references-scanning ...
fi
```

**修复**：若使用 inline bib，引用审计改为：
1. 从 paper.tex 直接提取所有 `\\cite{key}`
2. 从 thebibliography 环境提取所有条目
3. 对每个 DOI 执行 `curl -I https://doi.org/<DOI>` 验证
4. 计算 D10a = cited/bibitem 总数

**stroke-prediction 教训**：10 篇 inline 引用，全部无 PDF 全文，部分 DOI 返回 404（但非虚构），D10a=100%。若未检测 inline bib，此论文的引用审计会被完全跳过。

### D10a false failure — inline bib vs references.bib mismatch (新增 2026-06-26)

**问题**：当论文同时使用 inline thebibliography **且有** references.bib 文件时（HCS-3WT 案例），D10a 检查工具错误地用 references.bib 中的键集合与 paper.tex 中的 `\\cite{}` 键集合做匹配。结果：
- paper.tex 的 inline thebibliography 有 29 个 `\\bibitem{}` 
- references.bib 有 32 个条目（其中 6 个是 inline thebibliography 没有但在 bib 中独有的）
- 6 个 inline bibitem 键不在 references.bib 中（它们是 inline 独有的）
- 工具报告 D10a = 23/29 = 79.3% ❌ **这是假阴性**

**根因**：D10a 检查工具假设论文使用 `\\bibliography{references.bib}` 方式，但 HCS-3WT 使用 inline `thebibliography`。引用审计工具比较了**两个不同的引用来源**（inline vs bib文件），而非正确的匹配对（cite ↔ bibitem）。

**正确方法**：
1. **第一步：识别论文引用的 BibTeX 方式**
   ```bash
   grep -c '\\\\bibliography{' paper.tex    # >0 则使用外部 bib
   grep -c 'thebibliography' paper.tex   # >0 则使用 inline
   ```
2. **第二步：选择正确的匹配源**
   - 外部 bib → `\\cite{key}` 匹配 `references.bib` 中的 key
   - Inline bib → `\\cite{key}` 匹配 `paper.tex` 内 `thebibliography` 环境中的 `\\bibitem{key}`
3. **第三步：当两者并存时**
   - 论文实际编译使用 inline thebibliography（pdflatex 会忽略 `\\bibliography{}` 如果有 inline）
   - D10a 应该从 **cite ↔ inline bibitem** 计算
   - references.bib 作为**同步备份**（应该包含所有 inline bibitem 的对应条目）
   - 如果 references.bib 中有 6 个条目是 inline 没有的，这是**冗余**（非 D10a 问题）
   - 如果 inline bib 中有 6 个条目不在 references.bib 中，这是**不同步**，需要在 bib 中补充

**HCS-3WT 实际案例**：
- inline thebibliography: 29 个键
- references.bib: 最初 32 个条目（3 个冗余 + 6 个 inline 独有缺失）
- D10a（正确计算）: 29/29 = 100% ✅
- 修复后 references.bib: 29 个条目（删除冗余，补充缺失）

**修复步骤**：
1. 提取 inline thebibliography 的所有 `\\bibitem{key}` 键
2. 提取 paper.tex 的所有 `\\cite{key}` 键
3. 计算 cite → bibitem 的匹配率（这是真正的 D10a）
4. 对比 references.bib：确保它与 inline thebibliography 完全同步
5. 如果 references.bib 有未使用条目 → 删除
6. 如果 inline thebibliography 有不在 bib 中的条目 → 添加到 bib
7. 重新编译验证：`pdflatex` 必须通过（0 errors, 0 warnings, 0 undefined citations）

**验证命令**：
```bash
# 检查编译产物
grep -i 'undefined' paper.log | grep -i 'cite\\|label'
# 应该无输出
```
## 验证清单 · VERIFICATION

1. **输入验证**: {输入条件是否完整}
2. **输出验证**: {输出格式是否符合预期}
3. **边界验证**: {边界条件是否处理}
4. **错误处理**: {异常场景是否覆盖}

> 每项验证必须可执行、可记录、可复现。

