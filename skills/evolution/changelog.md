|2026-05-27: v2.16.0 — ResearcherSkill 方法论吸收：假说前置协议 + VERIFY 四态决策 + 硬收敛护栏
|  新增: [v2.16] IMPROVE 假说前置 — 每次编辑前必须输出 hypothesis preamble（target, current, hypothesis, expected, falsification）
|  新增: [v2.16] VERIFY 四态决策 — keep:best / keep:insight / discard:regression / discard:useless
|  新增: [v2.16] 硬收敛护栏 — consecutive_no_improvement(3轮→FORCE_PIVOT), same_target_exhausted(3次→LOCK_TARGET), plateau_detected(波动<5%→ESCALATE)
|  吸收: krzysztofdudek/ResearcherSkill (MIT) — 假说驱动实验循环 + 多维决策分类 + 收敛检测
|  文言: 先立说后动刀, 证不成则返 | 败亦有训, 不徒弃之 | 三度不济, 易弦更张
|
|2026-05-27: v2.17.0 — GenericAgent 外部吸收：事后技能结晶 CRYSTALLIZE_SKILL
|  新增: [v2.17] RECORD 步骤 11c. CRYSTALLIZE_SKILL — 从执行轨迹自动结晶技能
|  新增: CRYSTALLIZE_SKILL 触发条件（≥3次同类任务成功 → 自动生成 SKILL.md 草稿）
|  吸收: lsdefine/GenericAgent (⭐12,156, MIT) — 事成即录，录即成技方法论
|  吸收: evolution-proto-col.md — RECORD 步骤扩展为 6 个子步骤
|  文言: 事成即录，录即成技 | 种不可大，大则不生 | 无密则弃，有密则存
