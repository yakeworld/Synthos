# 外部营养采集 · 内化存档

> 每日采集 3 维度外部信息（AI前沿 / 工具发现 / 学术动态），提炼可内化知识。
> 评分 ≥8/10 的资源在此落盘为**内化建议**，供进化引擎与后续会话消费。
> 格式：每日一个文件 `YYYY-MM-DD-external-nutrition.md`。低分资源仅记录名称，不落建议。

---

## 2026-08-17

### 采集概况
- AI前沿: 4条 arXiv 论文（高价值: 3条 → 已内化）[ContinualSkillBench / 2608.04066 / AgentStream；SEVerA 入观察]
- 工具发现: 8条（高价值: 2条 → 已内化）[agent-skills 9分 / prime-agent 8分]
- 学术动态: 3条医学AI综述（高价值: 0条，均为一般综述，无突破性）
- 内化方式: delegate_task 不可用（执行器故障 `DaemonThreadPoolExecutor._initializer`），改为直接落盘建议

### ✅ 高价值资源（≥8/10）— 内化建议

#### 1. addyosmani/agent-skills — 9/10
- **类型**: 工具/项目
- **地址**: https://github.com/addyosmani/agent-skills
- **数据**: 87.7k★ | MIT | JS | 2026-08-14 活跃 | topics: agent-skills/claude-code/codex/cursor
- **用途**: 生产级 AI 编码 Agent 技能集合（工程级 skill 编写标准）
- **内化理由**: 与 Synthos skill-first 架构同构；skill 工程标准（结构/验证/版本化）可反哺 skill-authoring
- **建议操作**: 拉取仓库对照 skill-authoring + skill-quality-check，将工程级 skill 规范（命名、frontmatter、验证清单、版本策略）合入 skill-authoring/references/engineering-standards.md
- **状态**: 建议已落盘，待后续会话执行吸收

#### 2. ContinualSkillBench (arXiv:2608.03874) — 8.5/10
- **类型**: 学术论文（AI Agent 技能进化评估）
- **地址**: https://arxiv.org/abs/2608.03874
- **要点**: 动态评估框架测试 LLM Agent 上下文持续技能学习；5 领域 × 100 互连子任务，难度递增 + 跨任务技能复用；实验：顺序执行通常提升性能但跨模型/领域差异大
- **内化理由**: Synthos 有自进化引擎（四态决策+GEPA）但缺"技能复用评估"基准
- **建议操作**: 为 dsh-self-evolution 增加"技能复用评估"方法论：子任务难度分级 + 跨任务复用检测（golden 集可参照其 5 领域设计）
- **状态**: 建议已落盘，待执行

#### 3. The LLM Proposes, the Executive Disposes (arXiv:2608.04066) — 8.5/10
- **类型**: 学术论文（长程 Agent 结构化自验证）
- **地址**: https://arxiv.org/abs/2608.04066
- **要点**: 确定性 Executive 持有信念；LLM 只能提交类型化提案；主张仅在"行动前预注册预测 vs 代码观测"匹配时被承认——验证是结构性的而非事后；实测 8 次架构运行 4 次被判定无效并定位真实缺陷
- **内化理由**: 与 Synthos"墨证求真"、quality-gate 的 L0.5 数据诚实门高度契合
- **建议操作**: quality-gate 增加"预注册预测"机制：执行前声明预期数值/行为，执行后由代码比对，不符即标 invalid（可先用于 L0.5 数据诚实门试点）
- **状态**: 建议已落盘，待执行

#### 4. PrimeIntellect-ai/prime-agent — 8/10
- **类型**: 工具/项目
- **地址**: https://github.com/PrimeIntellect-ai/prime-agent
- **数据**: 16.5k★ | MIT | TypeScript | 2026-08-16 活跃
- **用途**: 自我改进 RLM agent（编码工作流 + 长程自治任务）
- **内化理由**: 自改进机制与 Synthos 自进化引擎同题；RLM（machine feedback）训练信号设计可借鉴
- **建议操作**: 调研其 RLM 反馈信号设计（如何构造自评/机器反馈），对照 dsh-self-evolution 的 DIAGNOSE→VERIFY 循环
- **状态**: 建议已落盘，待执行

#### 5. AgentStream (arXiv:2608.00155) — 8/10
- **类型**: 学术论文（自进化 Agent 流式评估）
- **地址**: https://arxiv.org/abs/2608.00155
- **要点**: 统一框架评估自进化 LLM Agent 在流式任务（多样复杂任务流）中的表现；现有研究多为独立评估，流式场景理解不足
- **内化理由**: Synthos 自进化引擎目前按批次评估，缺流式（连续任务流）评估视角
- **建议操作**: evolution 评估模式增加"流式任务"维度：连续任务流上的表现追踪而非单点评估
- **状态**: 建议已落盘，待执行

### 👀 观察列表（7-7.9/10，未达内化线）
- NVIDIA-NeMo/Switchyard (1.7k★, Rust, Apache-2.0): LLM 模型/提供商路由，保 OpenAI/Anthropic 兼容 — 与 provider fallback 链相关，待深度评估
- TencentCloud/TencentDB-Agent-Memory (22.2k★, TS): 团队级 Agent 记忆中心（Chat Memory/Skill/LLM-Wiki/Code-Graph）— 与记忆体系相关
- SEVerA (arXiv:2603.25111v2): 自进化 Agent 形式化验证合成 — 与 2608.04066 互补
- cathrynlavery/diagram-design (19.5k★, HTML): Claude Code 编辑级图表设计（29 种）— 与 figure-generation 相关
- cactus-compute/needle: 14MB 端侧基础模型 — 边缘 AI 方向，暂不涉及

### 备注
- 本日采集受环境故障限制：web_extract 不可用（SearXNG 后端）、delegate_task 不可用、并行工具调用报错 `DaemonThreadPoolExecutor._initializer`。改用 curl 脚本 + GitHub API + arXiv API 完成采集。
- 下次运行建议优先验证 delegate_task 是否恢复；若仍不可用，延续"直接落盘"内化模式。
