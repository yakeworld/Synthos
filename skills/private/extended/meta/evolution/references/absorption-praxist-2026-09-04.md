# Praxist 吸收记录 (2026-09-04)

> 吸收自: sapientinc/PRAXIST (6,849★, Python 3.11+, 2026-08-27 创建, Fair Source 1.0, source-available)
> 论文: arXiv:2608.25955 "Praxist: From Experimental Artifacts to Solution Lineages" (cs.MA)
> 来源: 2026-09-04 外部营养采集 (outputs/nutrition_20260904/nutrition_report.md, 评分 8.5/10)
> 吸收级别: absorbed_methodology (概念级——不 clone 代码、不安装、不集成运行时)

## 项目定位

- URL: https://github.com/sapientinc/PRAXIST
- 文档: https://praxist.sapient.inc/en/docs
- 定位: 面向"可度量、可计算机执行"研究的自主研究系统 (autonomous R&D team)
- 适用前提 (三条件, 缺一即停止并报告缺口):
  1. 目标可度量 — 有至少一个能区分好/坏且方向明确的 metric
  2. 项目已可运行 — baseline 代码、环境、数据已就位
  3. 最佳路径未知
- 核心主张: **研究是持久过程 (persistent process) 而非离散提示序列 (disconnected prompts)**。
  多数系统把每次尝试当近乎自足的单位, 日志/记忆/搜索树只记录"发生了什么",
  不建立三件事: (a) 哪个设计要素产生了改进 (b) 其证据是否通过验证 (c) 它如何与其他方案重组。
  于是长 campaign 不断重复学习同样的教训 (long campaigns keep re-learning the same lessons)。

## 核心机制

1. **Lineage-centered 代际系统 (solution lineage)**: 把可复现 artifacts + evaluator 结果
   转化为 **typed evidence graph**: findings (发现) + lane-structured frontiers (分道前沿) + agendas (议程)。
2. **Parallel research peers**: 并行研究同伴并发探索竞争性假设与实现。
3. **Evaluator → 结构化证据 → planning panel**: 评估器把结果转为证据, 规划面板把证据
   综合为下一代研究议程 (generation → 下一代迭代, 直到收敛或预算耗尽)。
4. **Durable evidence lanes**: 候选解跨代保存在三态成熟度中: incubator (孵化) → frontier (前沿) → Gems (宝石)。
5. **跨代综合 (multi-generation synthesis)**: 后代继承**已验证的机制、未解决的声明、有用的约束**——
   而不只是"更好的参数"。本地 artifact 构建与 cohort 级证据综合分离。
6. **三信任保障**: preregistration (metric/协议/baseline/阈值运行前定义) +
   consistent evaluation (所有候选同一 evaluator, 可疑结果剔除) +
   end-to-end provenance (每个改进声明附证据与 lineage 可审查可复现)。
7. **QD (Quality-Diversity) + DIG (Deep Innovation Gate)**: 保持多样性、逃逸局部最优, 不强制单一探索策略。
8. **负结果即交付物**: 未达标时仍产出 negative-result evidence package + 审计报告 + 停止/转向建议,
   用证据排除已测路径, 防止继续投入无产方向。
9. 中央资源调度: 按观测到的资源压力自适应调整实验准入; resume/replay/monitor 保长程可审查可恢复。

## 关键数据 (论文报告值, 未经独立复现)

- MLE-bench 75 任务标准化套件: Praxist 60 奖牌 (80.0%, 49 金) vs Claude Code baseline (Opus 4.8) 55 奖牌 (73.3%, 34 金)
- 模型花费: $3,054 vs $38,370 (~1/12)
- 四个开放工程案例 (量化交易 / LiDAR-SLAM / 托卡马克磁控 / 火箭着陆) 均改进任务原生 baseline, 发现路径在案

## 与 Synthos gene/evolution 体系的映射

| Praxist 机制 | Synthos 对应物 | 差距/增量 |
|:---|:---|:---|
| typed evidence graph (findings/frontiers/agendas) | pipeline_trace + gene_trace + lessons.jsonl | Synthos trace 是"执行记录"; Praxist 要求成为可支撑跨代继承的"类型化证据图" |
| 跨代综合 (继承已验证机制) | evolution 循环的 state 继承 + inherited_knowledge | Synthos 继承"分数+教训"; Praxist 继承"哪个设计要素产生改进 + 证据验证状态" |
| 证据成熟度三态 (incubator→frontier→Gems) | golden 验证 / quality-gate / Gene 候选→正式录入 | Synthos 有验证闸门但无"证据成熟度分层"语义 |
| 改进归因到设计要素 | EVOL-002 (技能修订绑定证据 {diagnosis, edit, outcome, rejected_alternatives}) | Synthos 证据在"技能修订"粒度; Praxist 推到"设计要素 (gene)"粒度——与 v5.1 "Gene 为最小进化单位"方向一致 |
| preregistration + consistent evaluator | BENCHMARKS + pre-registered-experiment-protocol 技能 | 已对齐 |
| 负结果证据包 | rejected_buffer (被驳回建议) | rejected_buffer 只记"不采纳"; 可升级为"负证据包 (为何失败 + 排除了什么)" |
| 项目/harness 所有权分离 (Praxist owns 编排/证据协议; task owns 目标/评估器/baseline) | 宪法层 (policy) 与技能层 (skill) 分离 | 同构: 进化循环不得修改"什么算有效证据"的定义, 只管理"如何搜索" |

## 吸收点 (值得内化的思想)

1. **Evidence 跨代存活验证 (evidence survival validation)** — 核心吸收点:
   声明须通过验证才进入下一代议程驱动决策; 未验证声明也可继承但标记 unresolved, 不驱动决策。
   映射 Synthos: lessons → Gene 结晶路径 (CRYSTALLIZE) 已有"验证后录入"闸门, 强化其语义:
   每条 lesson/Gene 须记录 (a) 哪个设计要素产生改进 (b) 证据是否通过独立验证 (c) 与其他方案重组的约束。
   文言: **验而后传, 未验者悬而不用。**
2. **改进归因到设计要素**: 教训重学的根因是日志只记"发生了什么"。
   映射 Synthos: gene_activation trace (behavior 维 activation_pct) + GEPA 失败定位已指向此方向,
   强化: 每次 OPTIMIZE 变更须归因到具体 gene/文件要素, VERIFY 结果回写到该要素。
3. **证据成熟度分层**: incubator→frontier→Gems 是 Synthos Gene 生命周期
   (Gene 候选 → 验证 Gene → 结晶进 SKILL.md) 的天然对应语义。
4. **负结果是交付物**: 无进展的进化周期不应"静默零输出", 应产出"排除了什么方向 + 建议停止/转向"。
5. **不静默造轮子**: 前提缺失时停止并精确报告缺口——不静默下载数据集、不虚构 simulator、不编造 baseline。
   (与 Synthos "不可用则如实报告, 禁止编造输出" 纪律一致, 互为印证。)

## 边界与纪律

- **概念级吸收**: 不 clone、不 pip install、不集成 praxist 运行时。
- **许可注意**: Fair Source License 1.0 (source-available, 非 OSI 开源)——年收入 ≥$1M 的组织商用需谈判
  Commercial License; 教学与学术研究豁免。Synthos 为研究用途, 合规。
- **数据未独立复现**: MLE-bench 数值为论文自报, 仅作方法论参考, 不作 Synthos 基准声称。
- **可选跟踪**: 如需持续监控, 用 oss-project-tracking 的 GitHub API 模式
  (state 文件 /tmp/praxist_track_state.json), 不主动建 cron。

## 验证

- [x] README 全文核读 (2026-09-04, raw.githubusercontent.com)
- [x] 论文摘要核读 (arxiv.org/abs/2608.25955)
- [x] GitHub 仓库元数据核对 (6,849★, 2026-08-27 创建, last push 2026-09-03, 活跃)
- [x] 映射关系与 evolution 技能 Gene 层 (v5.1) 交叉核对
