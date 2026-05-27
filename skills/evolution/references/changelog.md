# Evolution 变更日志


2026-05-26: v2.15.0 — SkillOpt 吸收：EDIT_BUDGET 编辑预算约束 + rejected_buffer 防护 [吸收自 SkillOpt (Yang et al. 2026)]
  新增: [8.5] EDIT_BUDGET — 每轮编辑预算衰减公式，防止过度修改（base=5, decay=1, min=2）
  新增: rejected_buffer 数据结构（outputs/evolution/rejected_buffer.json）— VERIFY失败自动记录
  新增: IMPROVE 前 rejected_buffer.READ — 自动排除已失败的编辑方案
  新增: VERIFY 联动 FAIL→rejected_buffer.WRITE + PASS→清除匹配
  新增: 连续3轮预算耗尽无改进→Nudge熔断
  新增: rejected_buffer 自动清理（保留近20轮+聚合统计）
  吸收: Yang et al. (2026) SkillOpt: Skill-Level Self-Improvement for Language Model Agents — edit budget decay + rejected program buffer
2026-05-16: v2.9.0 — 输入级护栏 (InputGuardrail) [吸收自 OpenAI Agents SDK]
  新增: InputGuardrail Hook (P0) — 用户输入后/AI执行前运行
  新增: 输入宪法检查 — 检查输入是否要求违反不可修改条款
  新增: 输入范围检查 — 检查是否在当前技能范围内
  新增: 总共7个Hook事件 (SessionStart/InputGuardrail/TaskComplete/SubagentStop/PreResponse/SessionEnd/Setup)
  吸收: OpenAI Agents SDK Guardrails 模式 (OpenAI, openai-agents-python)
2026-05-16: v2.8.0 — 反思式优化 + 多策略选择 [吸收自 GEPA/DSPy生态]
  新增: OPTIMIZE[3] SELECT_STRATEGY — 3种策略: 确定性补丁/反思调整/进化变异
  新增: OPTIMIZE[6] REFLECT — 自我评估优化效果 + 策略权重更新
  新增: 策略选择规则 — 成功率追踪 + 连续失败降权
  吸收: GEPA 反思式 prompt 进化 (arXiv:2507.19457, DSPy生态)
2026-05-16: v2.7.0 — 执行图谱 + 持久化 + 条件分支 + 拦截点 + 追踪 [吸收自 LangGraph]
  新增: 状态机执行模型（节点+条件边+检查点+拦截点）
  新增: 检查点与持久执行（Checkpoint/Resume，每步写入evolution-state.json）
  新增: 条件分支（Conditional Gates，5个门条件，3条执行路径A/B/C）
  新增: 人在回路拦截点（Human-in-the-loop Interrupt，4个拦截点+协议）
  新增: 执行追踪（Execution Trace，trace_{cycle}.json结构化日志）
  新增: **TaskComplete Hook** — 任务完成时自动触发质量门+交付物检查
  新增: 3条核心原则（持久执行/条件分支/状态机）
  修复: SessionEnd 现在触发条件进化循环（之前只做漂移检查）
  修复: SubagentStop 现在触发条件进化（之前只做经验提取）
  吸收: LangGraph durable execution + conditional edges + interrupt/resume + LangSmith tracing
2026-05-18: v2.11.0 — Git-as-Memory + 单指标聚焦 + 假设先行 [吸收自 ARIS]
  新增: Git-as-Memory 循环协议（Phase 0.5/A/B/C，嵌入BENCHMARK→IMPROVE子循环）
  新增: safe_revert 安全回滚函数（处理merge commit + 清理残留）
  新增: IMPROVE 一次聚焦原则（每轮只修最低分维度，含选择规则+修复顺序）
  新增: DIAGNOSE 8.0 假设先行（DIAGNOSE和IMPROVE间插入可验证假说）
  新增: hypothesis_{cycle}.yaml 输出 + stuck协议（连续3轮无提升触发主动推理门）
  吸收: HaiyangDiiing/aris-cli (ARIS, ⭐8, MIT) — 7原则中的 Git-as-Memory、单指标聚焦、假设先行
2026-05-16: v2.10.0 — SEPL回滚机制 + ARA结构化溯源 + 主动推理门 [吸收自 DeepResearchAgent + AI-research-SKILLs + Synthos哲学审计]
  新增: [5.5] ROLLBACK — 回滚决策（propose→assess→commit 提交门，自动回滚，版本快照，止损规则）
  新增: RECORD 11.2 — 结构化事件类型（决策/实验/死胡同/转折/主张/启发式/观察）+ provenance 标记
  新增: DIAGNOSE 8.8 — 主动推理门（4触发条件：置信度跨度/信息熵高/知识空白/用户困惑；生成最小化不确定性实验建议）
  吸收: SkyworkAI/DeepResearchAgent SEPL协议 (3,388⭐, MIT) — rollback + auditable lineage
  吸收: Orchestra-Research/AI-research-SKILLs ARA Research Manager (8,492⭐, MIT) — 7种事件类型 + 溯源标记
  哲学: Synthos哲学审计（八维框架实现度差距分析）— 自由能原理实现度55%→主动推理门
2026-05-16: v2.6.0 — 技能签名系统 + 自动优化器 [吸收自 DSPy]
  新增: signature 字段（frontmatter，声明式输入输出类型）
  新增: OPTIMIZE 步骤（step 6，基于 BENCHMARK 失败自动调优 skill 描述）
  新增: DIAGNOSE 8.5 OPTIMIZE 效果评估（对比修复前后的失败数变化）
  新增: 综合评分加入 OPTIMIZE 效果权重（10%）
  新增: 技能签名规范（docs/shared/SKILL_SIGNATURE_STANDARD.md）
  更新: project-experience-distillation L1格式门—新增signature检查项
  更新: quality-gate, conversation-to-memory 添加 signature 字段
  吸收: DSPy 声明式签名系统 + auto-optimizer 模式 (stanfordnlp/dspy)
  参考: docs/shared/SKILL_SIGNATURE_STANDARD.md — 签名规范
2026-05-16: v2.5.0 — 宪法集成 + 漂移检测 + 渐进披露 + 响应质量门 [Claude Code v2]
  新增: CONSTITUTION.md 集成（第0步 LOAD_CONSTITUTION + 宪法对齐检查）
  新增: 会话漂移检测（DRIFT_CHECK，三问自检 + 四级漂移等级 + 日志格式）
  新增: 能力渐进披露（三级可见性协议 L1 核心/L2 扩展/L3 专业）
  新增: 响应级质量门（PreResponse Hook，认识论门+宪法门+漂移门）
  新增: 综合评分加入宪法对齐分（权重20%）
  新增: Synthos 宪法 v5.0（哲学免疫系统+认识论原则+宪法层级）
  新增: 3条新陷阱（宪法加载失败/漂移过严/渐进披露冲突）
  新增: synthos_constitution_ref、synthos_asserted_compliance 扩展
  吸收: Claude Code system_reminder（漂移检测）+ 哲学免疫系统 + 认识论框架
  参考: /media/yakeworld/sda2/Synthos/CONSTITUTION.md — 完整宪法文档
2026-05-16: v2.4.0 — 吸收自 Claude Code Hook 事件系统。
  新增: 事件驱动触发器（Hook System）— 5种事件类型（SessionStart/SubagentStop/PostToolUse/SessionEnd/Setup）
  新增: 双模式架构（Timer+Event），Timer管系统健康，Event管项目质量
  新增: 事件→进化步骤映射 + quality-gate/project-experience-distillation协作图
  新增: synthos_absorbed_from: "Claude Code Hook System" 元数据字段
  参考: references/claude-code-absorption-2026-05-16.md — 完整吸收报告
2026-05-11: v2.3.0 — 主动吸收引擎重构 + 评估框架集成 + Progressive Disclosure。
  新增: absorption-tracked.json 项目追踪数据库（20项目, 1已吸收）
  新增: 关键词自我扩展 + 自检关键词生成
  新增: 三级上下文加载（Progressive Disclosure，吸收自 KILO-KIT）
  新增: DIAGNOSE 5.5 评估框架对照（对接 synthos-evaluation-framework.md）
  新增: RECORD 8.6 吸收追踪库更新
  修复: SKILL.md 意外覆盖保护——每次patch前备份
2026-05-11: v2.2.0 — 新增Golden金标准验证 + evolution-latest.json快速摘要。
2026-05-11: v2.1.0 — 新增Lesson学习机制。
2026-05-11: v2.0.0 — 升级自进化引擎：BENCHMARK+EXTERNAL+技能树+综合评分。
2026-05-11: v1.0.0 — 初始版本，6步循环。

- `references/project-health-assessment.md` — manual project health evaluation methodology (absorbed from `project-health-assessment`). Provides a comprehensive 6-dimension scoring framework as a supplement to the automated PROBE/BENCHMARK/DIAGNOSE cycle.
