# Golden 集合 · graduate-student-onboarding

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 对应 SKILL.md「Golden 集合 · GOLDEN SET」小节（GRAD-001…GRAD-006）。

## 语义

本技能为新研究生生成 onboarding 方案：按 Scope tiers 将研究方向分为
**Core**（全流程：5 pillars + Synthos + 教学 + 算法组件 + 公开数据集）与
**Peripheral**（仅空白+假设：角膜/晶状体/玻璃体/泪膜/耳鸣/脑震荡生物力学），
并据此下发 5 个 Cron 任务配置（autonomous-core-researcher / paper-repair /
paper-quality-review / paper-layer-b-review / literature-monitor），将收敛决策
作为持久化事实写入 Memory。Golden 集合覆盖：

- **正常路径**：清单含 1 个 Core 方向 + 1 个 Peripheral 方向 → 正确分级 +
  5 个 cron 配置 + Memory 收敛决策。
- **错误路径**：存在无法归类方向 → 拒绝生成方案，报出未分类方向名称并要求补全清单。

## 测试用例表

| Case | 类型 | 输入要点 | 期望要点 | 验证基因 |
|------|------|----------|----------|----------|
| `case_001_normal` | 正常 | "5 pillars 公开数据集分析" + "泪膜生物力学" | `success`；前者 Core/全流程、后者 Peripheral/仅空白+假设；5 个 cron 配置边界清晰；收敛决策写入 Memory | GRAD-001…005 |
| `case_002_error` | 错误 | 含一个无法按 Scope tiers 归类的方向 | `error`；`onboarding_plan_generated=false`；报错含未分类方向名称 + 恢复指引；Memory 不写入非法状态 | GRAD-002/006 |

## 通过标准

1. 每个 case 的 `expected_status` 与实际执行状态一致（success/error）。
2. 正常 case：`scope_classification` 与 Scope tiers 定义一致（公开数据集分析→Core，
   泪膜→Peripheral）；`cron_configs` 中 5 个任务全部满足各自边界
   （prompt 显式允许/禁止、repair 仅 in-scope、review 跳过 out-of-scope、
   monitor 核心完整报告/外围仅附录）；`memory_convergence_decision.written_as_durable_fact=true`。
3. 错误 case：`onboarding_plan_generated=false` 且 `memory_convergence_decision_written=false`；
   `error.message_must_include` 两条均出现（未分类方向名称、恢复指引）。
4. 原则优先级：准确 > 证据 > 可复现（GRAD-006）—— 输出无编造数据，
   结论可追溯到 Scope tiers 定义；同输入二次执行结果一致（可复现）。
5. 验证失败时必须记录原因与修复措施。

## 文件布局

```
golden/
├── GOLDEN_SET.md          # 本文件（语义 + 用例表 + 通过标准）
├── cases/
│   ├── case_001_normal.json
│   └── case_002_error.json
└── expected/
    ├── case_001_normal.json
    └── case_002_error.json
```
