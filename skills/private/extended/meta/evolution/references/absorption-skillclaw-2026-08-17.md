# 吸收记录 — AMAP-ML/SkillClaw (集体技能进化)

> **吸收日期**: 2026-08-17
> **项目**: [AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw) (2,447⭐, MIT)
> **论文**: [arXiv:2604.08377](https://arxiv.org/abs/2604.08377)
> **分类**: methodology_only（方法论吸收，无代码注入）
> **五维评分**: 方法论 4.5/5 · 可移植性 4.5/5 · 与 Synthos 互补性 5.0/5 · 实现复杂度 4.0/5 · 证据强度 4.0/5

## 核心架构：双循环

```
┌─ Hermes 任务时循环 (task-time loop) ─────────────────────┐
│  Agent 执行任务 → 引用/修改技能 → 生成会话数据              │
└──────────────────────┬───────────────────────────────────┘
                       ↓ 会话数据上传
┌─ SkillClaw 任务后进化循环 (post-task evolution loop) ─────┐
│  1. Summarize: LLM 压缩原始会话 → 结构化摘要               │
│  2. Aggregate: 按技能分组会话                              │
│  3. Analyze: 识别成功/失败模式，归因 (技能/代理/环境)       │
│  4. Decide: 对每个技能决定动作 (optimize/create/deprecate) │
│  5. Execute: 写入新/更新技能包                             │
│  6. Verify: 独立验证门 (skill_verifier.py)                 │
│  7. Publish: 通过验证 → 上传共享存储 → 分发到所有 Agent     │
└───────────────────────────────────────────────────────────┘
```

## 关键机制

### 1. 会话聚合 (aggregation.py)
- 按技能引用分组：会话引用了技能 X → 归入 X 组
- 无技能引用的会话 → NO_SKILL 组（考虑是否创建新技能）
- 一个会话可归入多个技能组

### 2. 技能验证门 (skill_verifier.py)
**保守验证**：无法确信通过 → 阻止发布，记录拒绝原因

验证四维检查：
| 检查项 | 含义 |
|:-------|:-----|
| grounded_in_evidence | 是否有会话证据支撑 |
| preserves_existing_value | 是否保留现有有价值内容 |
| specificity_and_reusability | 是否具体且可复用（非泛泛建议） |
| safe_to_publish | 是否安全发布到共享存储 |

输出：`{"decision": "accept/reject", "score": 0-1, "checks": {...}}`

### 3. 归因分析 (EVOLVE_AGENTS.md)
失败归因三分法：
- **技能问题**：指导错误/缺失
- **代理问题**：误用、上下文溢出
- **环境问题**：API 不稳定、网络问题

### 4. 多 Agent 统一
- 多个 Agent 的技能合并、去重、交叉授粉
- Frontend Agent 的 React 模式让 Backend Agent 的 API 设计更好
- 跨设备统一：Home/School/Work 实例共享技能

### 5. 集体进化
- 用户 A 调试数据库 → 技能进化 → 用户 B/C/D 立即受益
- N 用户，1 技能，持续进化

## 与 Synthos 的对比

| 维度 | Synthos | SkillClaw | 互补点 |
|:-----|:--------|:----------|:-------|
| 进化触发 | 定时 (cron) + 手动 | 会话数据驱动 | SkillClaw 的会话驱动是 Synthos 缺口 |
| 验证 | 六维评分 + 独立重算 | 四维验证门 (保守) | 两者互补，Synthos 可引入保守验证门 |
| 归因 | 无显式归因 | 三分法 (技能/代理/环境) | Synthos 应引入归因分析 |
| 多 Agent | 单 Agent + 子代理 | 多 Agent 统一技能库 | 方向不同 |
| 发布 | Git commit | 共享存储 + 验证门 | Synthos 的 Git 是更简单的发布机制 |
| 去重 | P032 确定性去重 | 自动合并去重交叉授粉 | 类似，SkillClaw 更自动 |

## 可吸收方法论

1. **保守验证门**：发布前四维检查，无法确信 → 阻止。Synthos 的 quality-gate 可引入此保守原则
2. **失败归因三分法**：技能/代理/环境。Synthos 进化日志应标记失败根因
3. **会话驱动进化**：从实际会话数据中提取进化信号，而非仅定时诊断
4. **技能历史版本**：每个技能保留 history/v*.md 快照 + 证据文件
5. **交叉授粉**：跨 Agent/跨技能的技能合并与交叉改进

## 注入点

| 方法论 | Synthos 注入点 | 优先级 |
|:-------|:---------------|:-------|
| 保守验证门 | quality-gate (L0.5) | P1 |
| 失败归因三分法 | evolution (DIAGNOSE + RECORD) | P1 |
| 会话驱动进化信号 | evolution (触发条件) | P2 |
| 技能历史版本 | evolution (CRYSTALLIZE) | P2 |
| 交叉授粉 | skill-absorption (吸收流程) | P3 |

## 文言提炼

> **会话生知，知生技能。**
> **验而不信，则止不传。**
> **一技之失，三因分判：技之过、使之误、境之变。**

## 状态

- [x] 方法论提取完成
- [ ] 保守验证门原型（quality-gate 增强）
- [ ] 失败归因三分法集成到 evolution 日志
- [ ] 技能历史版本机制
