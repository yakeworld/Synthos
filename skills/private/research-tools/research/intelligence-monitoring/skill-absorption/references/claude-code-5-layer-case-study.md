# Claude Code 五层提取案例研究

> 2026-05-16 | 来源: anthropics/claude-code (123K⭐)
> 演示 skill-absorption 的「五层提取规范」在实际项目分析中的完整流程。

---

## 按五层顺序的提取记录

### 第1层：思想 (Philosophy)

**发现**:
- 分布式宪法（~20个指令块散布在系统提示中，而非单一文件）
- 哲学免疫系统（不会被良好论证改变其核心性格）
- 默认帮助主义（default helpfulness stance）
- 认知美德：真理>讨好，批判性评估
- 版权不可协商（优先级高于安全）

**决策**: 参考级。与Synthos的P0-P6宪法方向一致但深度不同。哲学免疫系统概念记作未来CONSTITUTION.md更新候选。

### 第2层：规范 (Standard)

**发现**:
- Hook事件类型规范（8种事件：PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Setup）
- 技能触发条件+验证清单为必选项（行业标准）
- 渐进式三级加载（元数据→SKILL.md→资源）
- confidence评分0-100，≥80才输出

**决策**: 
- Hook事件规范 → 吸收到 evolution 引擎（v2.3→v2.4）
- 触发条件+验证清单 → 吸收到 project-experience-distillation L1格式门
- 渐进式加载 → Synthos已有，跳过
- confidence评分 → quality-gate已有L1-L4分级，跳过

### 第3层：规律 (Pattern)

**发现**:
- 子Agent用不同模型独立执行（isolation pattern）
- 主线程→子Agent→结果回传的编排模式
- Settings的分层覆盖（managed > project > user）

**决策**: 
- 子Agent隔离模式 → 参考级。Synthos的delegate_task已有类似能力
- 编排模式 → 参考级
- Settings分层 → 参考级

### 第4层：能力 (Capability)

**发现**:
- 40+内置工具（bash, Read, Write, Edit, Grep, LSP等）
- 13个官方插件 + plugin-dev SDK
- 87个隐藏feature flags（KAIROS/COORDINATOR_MODE/VOICE_MODE等）
- 4级权限系统

**决策**: 全部跳过。定位差异（工程工具 vs 认知OS），无功能缺口需要填补。

### 第5层：任务规律 (Task Pattern)

**发现**:
- feature-dev 7阶段工作流
- 代码审查并行5Agent模式
- Ralph-loop自迭代模式
- 子任务自动化/编排模式

**决策**: 参考级记录。

---

## 吸收统计

| 层级 | 分析项数 | 实际吸收 | 吸收率 |
|:----:|:--------:|:--------:|:------:|
| 1 思想 | 6 | 0（全部参考级） | 0% |
| 2 规范 | 4 | 2（Hook事件+行业标准） | 50% |
| 3 规律 | 3 | 0（全部参考级） | 0% |
| 4 能力 | 4 | 0（全部跳过） | 0% |
| 5 任务规律 | 4 | 0（全部参考级） | 0% |

> **关键发现**: 业界领头羊的最大价值不在第4-5层（能力/任务），而在第1-3层（思想/规范/规律）。
> Claude Code最有价值的是它的**规范**（Hook事件系统），而非它的**能力**（40+工具）。
> 这验证了「吸收规范比吸收能力更有价值」的原则。

## 与本技能其他机制的关联

- **Gap-driven评估**: 本次吸收的缺口来自「项目持续优化」的对话中内部反思发现的「缺少事件驱动能力」
- **五层提取**: 完整实践了第1-5层有序提取
- **Deep Structural**: Hook系统属于Phase 1（核心机制注入，不改变I/O合约）
- **双循环**: 内部反思（发现缺口）→ 外部吸收（填补缺口）→ 内部反思（升级质量门标准）
