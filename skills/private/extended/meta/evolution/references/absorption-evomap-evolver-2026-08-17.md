# 吸收记录 — EvoMap/Evolver (GEP 自进化引擎)

> **吸收日期**: 2026-08-17
> **项目**: [EvoMap/evolver](https://github.com/EvoMap/evolver) (8,978⭐, GPL-3.0)
> **论文**: [From Procedural Skills to Strategy Genes: Towards Experience-Driven Test-Time Evolution](https://arxiv.org/abs/2604.15097) (arXiv:2604.15097)
> **分类**: methodology_only（源码已混淆/转 source-available，仅吸收方法论）
> **五维评分**: 方法论 4.5/5 · 可移植性 4.0/5 · 与 Synthos 互补性 4.5/5 · 实现复杂度 3.5/5 · 证据强度 5.0/5

## 核心发现（论文，4590 次受控实验，45 个科学代码求解场景）

**关键结论**：
- 文档导向的 **Skill 包**（长 markdown 指令）提供**不稳定、稀疏**的控制信号
- 紧凑的 **Gene 表示**（策略基因）提供**最强整体性能**
- Gene 在结构扰动下**更鲁棒**
- Gene 是**迭代经验积累**的更好载体
- 实证：CritPt 上，Gene 进化系统将基础模型从 9.1% → 18.57%，17.7% → 27.14%
- "tokens rise then fall" 签名：推理被压缩进可复用基因

## 三层架构（GEP 协议）

| 层 | 名称 | 职责 |
|:---|:-----|:-----|
| Gene | 策略基因 | 紧凑策略表示，可组合、可变异、可审计 |
| Capsule | 胶囊 | 封装一组 Gene + 上下文 + 激活条件 |
| Event | 事件 | 触发进化循环的信号（成功/失败/新用户/新环境） |

## 关键机制

1. **Gene 变异 (mutation.js)** — 对 Gene 做受控变异，保留成功部分
2. **反射 (reflection.js)** — 从执行轨迹中提取信号，生成新 Gene 候选
3. **候选评估 (candidateEval.js)** — 对新 Gene 做独立验证
4. **技能→Gene 蒸馏 (skill2gep.js)** — 将现有 Skill 文档蒸馏为 Gene 表示
5. **记忆图谱 (memoryGraph.js)** — Gene 间的关系图谱
6. **表观遗传 (epigenetics.js)** — 环境条件控制 Gene 激活/沉默
7. **审计追踪 (assetCallLog.js, validationReport.js)** — 所有进化操作可审计

## 与 Synthos 的对比

| 维度 | Synthos | EvoMap | 互补点 |
|:-----|:--------|:-------|:-------|
| 进化单位 | SKILL.md (markdown 文档) | Gene (紧凑策略) | Synthos 可引入 Gene 作为 SKILL 的内部压缩表示 |
| 验证 | 六维评分 + 独立重算 | candidateEval + 审计追踪 | Synthos 已有，但 Gene 级验证是新增 |
| 经验积累 | 手动提炼 + 批量注入 | 自动从轨迹蒸馏 | EvoMap 的自动蒸馏是 Synthos 的缺口 |
| 多 Agent | 单 Agent + 子代理 | 网络协作 (A2A) | Synthos 暂不需要 |
| 可审计性 | Git-as-memory | 资产调用日志 + 验证报告 | 两者互补 |

## 可吸收方法论（剥离实现）

1. **策略基因压缩**：长技能文档 → 紧凑策略基因，减少 token 开销，提升鲁棒性
2. **执行轨迹 → Gene 自动蒸馏**：从实际执行中自动提取可复用策略，不依赖手动提炼
3. **Gene 级候选验证**：新策略必须在独立验证后才进入基因库
4. **表观遗传激活**：环境条件控制策略激活，而非无条件全部加载
5. **审计追踪**：每次进化操作留下完整审计日志

## 注入点

| 方法论 | Synthos 注入点 | 优先级 |
|:-------|:---------------|:-------|
| 策略基因压缩 | evolution 引擎 (DIAGNOSE → IMPROVE) | P1（需宪法级决策，改变进化单位） |
| 执行轨迹自动蒸馏 | evolution (CRYSTALLIZE 步骤) | P1 |
| Gene 级候选验证 | quality-gate (L0.5 数据诚实门) | P2 |
| 表观遗传激活 | task-router (路由决策) | P2 |
| 审计追踪 | evolution (RECORD 步骤) | P3（已有 Git-as-memory） |

## 风险与限制

- 源码已混淆（正在转 source-available），无法直接复用实现
- 论文实验场景为科学代码求解，与 Synthos 的科研论文管线有差异
- GPL-3.0 许可证限制代码复用（但方法论不受限）
- "Gene 优于 Skill" 的结论需在 Synthos 场景下独立验证（P4 可证伪性）

## 文言提炼

> **基因胜于长文，压缩方得真传。**
> **轨迹生金，不假手笔。**
> **验而后录，录而后传。**

## 状态

- [x] 方法论提取完成
- [ ] Gene 表示引入 Synthos（需宪法级决策 — 改变进化单位是重大架构变更）
- [ ] 执行轨迹自动蒸馏原型
- [ ] 独立验证：在 Synthos 场景下测试 Gene vs Skill 性能
