---
name: v32-multi-direction-scan
description: '**边界**：技能功能边界。'
signature: 'v32-multi-direction-scan -> synthos-akne-bridge: synthetic skill for v32
  multi direction scan'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '**边界**：技能功能边界。'
    signature: 'v32-multi-direction-scan -> synthos-akne-bridge: synthetic skill for
      v32 multi direction scan'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

--|
| 3.0.0 | 2026-06-27 | 重构为"思想-原则-方法-规则"结构。从60KB压缩至~10KB。具体实现细节移至ref/目录。 |
| 2.0.21 | 2026-06-24 | 添加Cycle 245 vhit漂移案例 |
| 2.0.20 | 2026-06-24 | PubMed ODE/视盘水肿碰撞 |
| 2.0.0 | 2026-06-23 | 对齐paper-pipeline 9核心约束；添加Step 0模式决策；添加后耗尽协议 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 扫描任务启动前已执行 Step 0 模式决策，并对齐 paper-pipeline 9 核心约束（SK-001、v2.0.0 约束）
- [ ] 请求描述与上下文信息（输入参数/文件/路径）缺失或无效时，已触发输入验证并阻断后续流程（SK-002）
- [ ] 空输入、极大值或异常场景已执行边界验证，系统保持稳定（SK-003）
- [ ] 扫描各方向的中间步骤、转换与计算无偏差，已执行过程验证（SK-004；参照 Cycle 245 vhit 漂移案例检查漂移）
- [ ] 最终结果格式与内容符合 IO_CONTRACT 输出契约（SK-005）
- [ ] 任务失败时已输出含上下文与恢复指引的错误信息（SK-006）
- [ ] 技能改进/迭代已通过 Golden 集合（Input/Output/Error）测试，验证失败已记录原因与修复措施以保证可复现（SK-007/008）

## Golden 集合 · GOLDEN SET

- **Golden Input**: 扫描任务描述 + 上下文（目标方向集合、paper-pipeline 9 核心约束清单），覆盖 Step 0 模式决策的正常路径
- **Golden Output**: 各方向扫描结果表，格式符合 IO_CONTRACT 输出契约（SK-005），且过程验证确认无 Cycle 245 式 vhit 漂移（SK-004）
- **Golden Error**: 请求描述/上下文缺失或无效时，触发输入验证并阻断后续流程，错误信息含上下文与恢复指引（SK-002/006）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# V32 Multi Direction Scan---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[SK-009]** 执行任何扫描任务前 → 必须执行 Step 0 模式决策以对齐 paper-pipeline 9 核心约束
- **[SK-010]** 遇到输入参数、文件或路径缺失/无效时 → 立即触发输入验证并阻断后续流程
- **[SK-011]** 处理空输入、极大值或异常场景时 → 必须执行边界验证以确保系统稳定性
- **[SK-012]** 中间步骤、转换或计算出现偏差时 → 执行过程验证以确认逻辑正确性
- **[SK-013]** 生成最终结果时 → 执行输出验证以确认格式与内容符合预期
- **[SK-014]** 任务执行失败时 → 提供明确的错误信息并启动恢复指引
- **[SK-015]** 进行技能改进或迭代时 → 必须通过 Golden 集合（Input/Output/Error）测试作为单一真理来源
- **[SK-008]** 验证失败发生时 → 记录具体原因和修复措施以确保可复现性