---
title: DSH 域外部吸收扫描 (Cycle 265)
date: 2026-08-17
cycle: 265
scope: agent-execution-sandbox / tool-permission / headless-orchestration / multi-agent-safety / workflow-engine
method: GitHub API search (unauthenticated), 6 并行 scout, 独立核验 (P0)
status: evaluated — 1 absorbed (methodology_only), 8 tracked
---

# DSH 域外部吸收扫描 — Cycle 265

> 触发: 用户指令 "进行外部吸收扫描"。域: 执行沙箱/工具权限/无头编排/多智能体安全/工作流引擎。
> 纪律: 宁无所得，不取伪术。无法验证的声明不入库 (P0 证据可溯性)。

## 独立核验记录 (P0)

scout 报告 12 候选，父级独立核验 (GitHub API, 非复用 scout 输出):

| 仓库 | scout 报告 | 父级核验 | 判定 |
|:-----|:----------|:---------|:-----|
| omnigent-ai/omnigent | 8965⭐ Apache-2.0 2026-06-11 | ✅ 一致 | 可信 |
| sandbaseai/sandbase-harness | 613⭐ Apache-2.0 2026-07-11 | ✅ 一致 | 可信 |
| Rath-Team/OpenRath | 901⭐ BSD-3 2026-05-04 | ✅ 一致 | 可信 |
| Bevel-Software/Hexis | 69⭐ Apache-2.0 2026-07-30 | ✅ 一致 | 可信 |
| christiangrey922/multi-agent-workflow-lab | 87⭐ MIT 2026-08-12 | ⚠️ rate-limit 未核验 | 待核验 |
| prashar32/riskkernel | 20⭐ Apache-2.0 | ⚠️ rate-limit 未核验 | 待核验 |
| Inomy-shop/allen | 46⭐ MIT | 未核验 | tracked |
| EXXETA/exxperts | 333⭐ Apache-2.0 | 未核验 | tracked |
| VisionForge-OU/foreman | 456⭐ NOASSERTION | 未核验 | tracked (license 风险) |
| TencentCloud/CubeSandbox | 11170⭐ NOASSERTION | ⚠️ 未核验 (scout 亦未验证) | 不入库 |
| 100yenadmin/LCO | 38⭐ | 未核验 | tracked |
| BuckG71/whizzard | 1⭐ MIT | 未核验 | 忽略 (信号过低) |

**核验陷阱**: 本轮与 cycle 220 的 VLLM EROFS 不同 — 是 GitHub 匿名 rate limit (core 60/h)。
4/12 独立核验通过, 2/12 待核验, 6/12 仅 scout 单源。按 P0: 单源不吸收, 仅 tracked。

## 五维评分 (已核验候选)

评分维度: 方法论 25% / 可移植性 20% / 互补性 25% / 复杂度 15% / 证据 15% (各 1-5 分, ≥4.0 进入吸收)

### sandbaseai/sandbase-harness — 4.30 (ABSORB, methodology_only)

| 维度 | 分 | 依据 |
|:-----|:--:|:-----|
| 方法论 | 4.5 | credential vault + permission policy + approval gate 的完整执行层实现; audit + replay |
| 可移植性 | 4.0 | Apache-2.0; 核心是 policy/approval 数据结构与流程, 非框架绑定 |
| 互补性 | 4.5 | DSH-008 只有"分级+留痕"原则, 缺凭据/审批的具体机制; 与 commit-first-then-measure 机制互补 |
| 复杂度 | 4.0 | 613⭐ 小型, 可深读 |
| 证据 | 4.0 | 仓库存在已独立核验; 源码细节未深读 (下轮) |

**吸收内容 (P7 方法论剥离, 不搬代码)**:
1. **DSH-009 凭据隔离**: agent 不持凭据 — 工具凭据经 vault 代理注入, 会话内可审计。与 DSH-008 组合: DSH-008 管"越级须确认", DSH-009 管"凭据不进上下文"
2. **审批留痕最小集**: 每次越级 = {who, what, scope, reason, timestamp, result} — 结构化审计事件, 可重放
3. **audit+replay 作为验证原语**: 进化循环的 VERIFY 步可重放 dispatch 轨迹做独立审计 (与 EVOL-007 一致)

### omnigent-ai/omnigent — 4.10 (tracked → deep-read next)

meta-harness 模式: 单一编排层横跨异构 agent (Claude Code/Codex/Cursor/Pi), 策略+沙箱强制, **跨 agent 互审** (一个 agent 审查另一个的产出 = 独立验证原语的外部验证)。8965⭐ 活跃, Apache-2.0。
判定: 与 Synthos "harness 无关 + 独立验证" 方向强互补, 但代码库大, 本轮仅 tracked; 下轮深读 docs/ 的 policy/sandbox 节。

### Rath-Team/OpenRath — 3.60 (tracked)

PyTorch-like 多 agent 运行时 (显式可组合对象 Session/Sandbox/Memory/Tool/Agent/Workflow + 纯 Python 控制流)。arXiv:2606.19409。范式与 Synthos (技能/Gene 容器) 差异大, 组合对象思路可参考, 不吸收。

### Bevel-Software/Hexis — 3.80 (tracked)

git-backed control plane: 每个 skill/tool/permission/identity 是 git 文件 → 审计轨迹即存储层, 文件级 RBAC, agent 无凭据。与 Synthos "Git 即记忆" 高度共鸣; 69⭐ 小, 下轮深读 per-file access 解析。

## 待核验 (下轮, rate limit 恢复后)

- christiangrey922/multi-agent-workflow-lab: 若核验成立, "确定性规则独立于模型裁判评估行为" 与 EVOL-007 同构, 预期高分
- prashar32/riskkernel: 确定性 governor (成本/循环/时间预算 + 人工审批门), 若成立可补 DSH 执行层预算护栏

## 明确不吸收

- CubeSandbox: 未验证 + license NOASSERTION → 不入库 (宁缺毋滥)
- foreman: license NOASSERTION → tracked only
- whizzard: 1⭐ 信号不足

## 与现有体系的关系 (去重检查)

- DSH-008 (cycle 263, Codex 分级审批): 互补不重叠 — DSH-008 是原则层 (默认封闭/越级留痕), DSH-009 是机制层 (vault/approval/audit)
- EVOL-007 (独立重算): omnigent 跨 agent 互审是其外部变体, 已跟踪
- 与 ledger 现有 20 项目零碰撞 (scout 已查 projects + tracked_but_not_absorbed)
