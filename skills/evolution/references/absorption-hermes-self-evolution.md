# L+0 吸收评估 — hermes-agent-self-evolution (NousResearch)

> 评估日期: 2026-05-22 | 版本: v0.1.0 | ⭐ 3,446 | 许可证: MIT
> ICLR 2026 Oral

## 原理层·文言

### 取法之道

> 学于彼而化于此，谓之取法。迹以观其行，理以究其因。
> 不观其果而观其迹，不究其表而究其里。知其败之所由，而后可修也。
> 无金则自炼，无例则自生。以文生案，以约化形。
> 不待外求，自足其用。
> 多利取其重，多径择其优。不偏一隅而观全局，不执一维而失他维。
> 凡改进，必先算其功，而后动其刀。

### 吸收三要义

| 要义 | 文言释 | 白话解 |
|:-----|:-------|:-------|
| 迹以究因 | **观迹知败** | 读执行轨迹理解失败根源，非只看结果 |
| 无金自炼 | **自生其例** | 无测试用例时从技能文本自动合成 |
| 多利取重 | **算功而动** | 多目标 Pareto 前沿选最优改进路径 |

## 来源标记

| 字段 | 值 |
|:-----|:----|
| 名称 | hermes-agent-self-evolution |
| 来源 | NousResearch (官方 Hermes Agent 团队) |
| URL | https://github.com/NousResearch/hermes-agent-self-evolution |
| ⭐ | 3,446 |
| Fork | 375 |
| 许可证 | MIT ✅ |
| 论文 | ICLR 2026 Oral |

## 核心方法论

### 1. GEPA (Genetic-Pareto Prompt Evolution)

GEPA 是整合在 DSPy 中的反射式演化引擎。其核心创新：

- **轨迹读取**：不只看"任务失败"，而是读取完整的执行轨迹，理解**为什么**失败
- **针对性变异**：基于失败原因，生成有针对性的变异（而非随机变异）
- **Pareto 选择**：在多维指标上保持 Pareto 前沿
- **小样本能力**：仅需 3 个样例即可启动优化

### 2. 三层优化目标

| 层级 | 目标 | 方法 |
|:-----|:-----|:-----|
| Tier 1 | SKILL.md 文件 | 包装为 DSPy Signatures，GEPA 进化文本 |
| Tier 2 | Tool descriptions | 作为分类问题优化 |
| Tier 3 | System prompt | 参数化后离线优化 |

### 3. 数据集构建三模式

- **合成模式**：从 skill 内容自动生成训练/验证/测试集
- **金标准模式**：加载预设的 JSON/JSONL 测试用例
- **外部导入**：从 Claude Code、Copilot、Hermes SessionDB 挖掘真实会话

### 4. 约束门控

| 门 | 条件 |
|:---|:------|
| 测试门 | `pytest tests/ -q` 100% 通过 |
| 大小门 | Skill ≤15KB, tool description ≤500 chars |
| 缓存门 | 不可在对话中途变更 |
| 语义门 | 不可偏离原始目的 |
| 人工门 | 所有变更经 PR review |

## 与 Synthos evolution v2.11 对比

| 维度 | Synthos evolution | hermes-agent-self-evolution |
|:-----|:------------------|:---------------------------|
| 架构 | 纯 SKILL.md 驱动 | Python 管线 (DSPy+GEPA) |
| 优化方法 | Agent 推理 + 进化协议 | 自动遗传-Pareto 搜索 |
| 评估数据集 | 无（依赖经验） | 合成/金标准/会话挖掘 |
| 失败分析 | 人工复盘 | 自动执行轨迹分析 |
| 变异策略 | 手动编辑 | 自动针对性变异 |
| 约束门 | 宪法+漂移+质量 | 测试+大小+缓存+语义 |
| 输出 | 直接修改 SKILL.md | Git commit + PR |
| 部署 | 即时 | PR 审批后 |

## 吸收评估

### 可吸收方法论 (High Value)

| 方法 | 吸收到 | 收益 |
|:-----|:-------|:-----|
| **GEPA 反射式分析** — 读取轨迹→理解失败原因→针对性变异 | evolution OPTIMIZE 步骤 | 从"手动复盘"升级为"自动失败分析→针对性修复" |
| **评估数据集构建** — 合成数据生成 + 外部会话挖掘 | BENCHMARK 步骤 | 从"手动构建 golden"升级为"自动生成测试集" |
| **三层约束门** — 大小+缓存+语义 | IMPROVE 步骤 | 增加自动防护，防止 unintended drift |
| **Pareto 优化框架** — 多指标多维进化 | DIAGNOSE 综合评分 | 从"单指标聚焦"升级为"多目标 Pareto 前沿" |

### 不可吸收 (直接搬用成本高)

- Python 代码管线 (DSPy/GEPA 依赖 Python 环境)
- 与 hermes-agent 代码库紧耦合的模块 (batch_runner, trajectory, prompt_builder)
- PR 审批流程 (Synthos 无此架构)

### 综合评分

| 维度 | 评分 | 说明 |
|:-----|:----:|:-----|
| 互补性 | 0.95 | 完美互补 — 解决 Synthos 的最弱维度 (自动化评估+自动修复) |
| 代码/文档质量 | 0.95 | 官方 NousResearch 出品，ICLR 2026，代码清晰 |
| 社区活跃 | 0.90 | 3.4K⭐, 375 forks, 57 open issues (活跃) |
| 集成成本 | 0.70 | 方法论吸收成本低 (纯概念)，代码吸收成本高 (Python依赖) |
| 许可证 | 1.0 | MIT ✅ |
| **综合** | **0.88** | **🔥 强烈建议方法论吸收** |

## 吸收提议

### 提议 1: GEPA 反射式优化 → evolution OPTIMIZE

在 evolution 的 OPTIMIZE 步骤中增加"反射式分析"阶段：

```
COLLECT_FAILURES → [新增] REFLECTIVE_ANALYSIS → ANALYZE_ROOTS → ...
                      │
                      ▼
              读取执行轨迹
              理解失败原因
              生成针对性修复策略
```

### 提议 2: 自动评估数据集 → evolution BENCHMARK

在 BENCHMARK 步骤中增加"自动数据集构建"模式：

```
无 golden 用例 → 自动从 SKILL.md 生成合成测试集
有 golden 用例 → 补充外部会话数据
定期刷新 → 用新经验更新数据集
```

### 提议 3: Pareto 多维优化 → evolution DIAGNOSE

在 DIAGNOSE 中增加 Pareto 前沿分析，替代当前的单指标聚焦：

```
多指标评分
构建 Pareto 前沿
选择 Pareto-optimal 改进
非 Pareto-optimal 改进降级
```

## 决策请求

是否批准 L+1 适配改造（方法论吸收至 evolution 引擎）？

核心工作：
1. **evolution OPTIMIZE** — 增加 REFLECTIVE_ANALYSIS 阶段（读取轨迹→理解失败→针对性修复）
2. **evolution BENCHMARK** — 增加自动评估数据集构建模式
3. **evolution DIAGNOSE** — 增加 Pareto 多维评分
4. **evolution-state.json** — 新增吸收记录
