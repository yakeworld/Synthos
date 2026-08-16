---
name: training-pipeline-audit
description: '**IMRaD结构规划**:'
signature: 'training-pipeline-audit -> research: synthetic skill for training pipeline audit'
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
    description: '**IMRaD结构规划**:'
    signature: 'training-pipeline-audit -> research: synthetic skill for training pipeline audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| 方法学论文 | 管线完整+有实证结果 | 训练结果+管线描述 | Q1-Q2 |
| 实证分析论文 | 有对比实验/消融实验 | 对比数据+统计检验 | Q2-Q3 |
| 综述论文 | 有文献基础+领域知识 | 文献综述+领域分析 | Q1 |
| 算法-only | 数学推导新颖 | 推导+1-2个demo | Q2-Q3 |

**IMRaD结构规划**:
1. **Introduction**: 背景 → 现状 → 缺口 → 贡献
2. **Methods**: 管线步骤 → 算法 → 实验设计 → 数据
3. **Results**: 主结果(Val Dice/CErr) → 消融实验 → 对比实验
4. **Discussion**: 优势 → 局限 → 与文献对比 → 未来方向
5. **Conclusion**: 核心贡献总结

**文献基础**: 补充15-30篇相关文献(方法学/临床/算法)

**产出**: paper_plan.json (IMRaD结构+文献列表+时间表)

## 实战案例：K230训练管线

### 项目概要
- 数据: 901帧K230图像(800×480) + 976帧OpenEDS
- 管线: 7步CV管线(瞳孔定位→区域生长→椭圆精修→眼球中心标定→3D能量蛇→SAM眼裂→Seg Mask)
- 模型: MobileNetV2+T3EM, 4阶段渐进训练(30+20+20+20 epoch)
- 结果: Val Dice=0.8955, CErr=1.63px

### 发现的研究空白
1. 单目3D眼球追踪精度理论极限未验证
2. SAM vs 传统CV性能边界未定义
3. 不同人种解剖学参数泛化性未评估
4. 时序信息增益未量化
5. 混合训练泛化性增益未量化

### 生成的科学假设
- H1: 分割误差主导总误差(claim: ≥60%)
- H2: SAM在虹膜边缘优于能量蛇，在瞳孔定位不如区域生长
- H3: 时序建模比单帧提升Val Dice ≥0.03
- H4: 混合训练比单一数据集提升Val Dice ≥0.05
- H5: 固定几何参数导致系统性偏差

### 论文撰写计划
- 论文A(方法学): Q1, IEEE TBME/IOVS, 2周
- 论文B(实证分析): Q2, Scientific Reports, 4周

## 参考文件

- ref/legacy-paper-rescue-workflow.md — 管线/训练分析经验
- ref/legacy-paper-rescue-workflow.md — 管线/训练分析经验
- ref/hypothesis-generation-ref/io-contract.md — 假设生成IO合同
- ref/hypothesis-generation-ref/boundary.md — 假设生成边界
- references/k230-pipeline-audit-2026-06-13.md — K230训练管线审计报告(实战案例)
- references/k230-code-patterns.md — K230训练管线核心代码模式(数据加载/训练/参数)
- references/skill-library-audit-2026-06-13.md — 技能库审计与更新报告

## 实战案例

- **K230训练管线** (2026-06-13): 从901帧K230数据+训练日志提取5个研究空白、5个科学假设、2篇SCI论文计划。详见references/k230-pipeline-audit-2026-06-13.md。

## 验证

- [ ] 所有项目文件已扫描和统计
- [ ] 管线步骤已拆解为方法论
- [ ] 已识别至少3个研究空白
- [ ] 已生成至少3个可检验假设
- [ ] 已输出论文撰写计划(IMRaD结构+文献列表)
- [ ] 假设格式符合hypothesis-generation的IO_CONTRACT

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

# Training Pipeline Audit---





|
| 方法学论文 | 管线完整+有实证结果 | 训练结果+管线描述 | Q1-Q2 |
| 实证分析论文 | 有对比实验/消融实验 | 对比数据+统计检验 | Q2-Q3 |
| 综述论文 | 有文献基础+领域知识 | 文献综述+领域分析 | Q1 |
| 算法-only | 数学推导新颖 | 推导+1-2个demo | Q2-Q3 |

**IMRaD结构规划**:
1. **Introduction**: 背景 → 现状 → 缺口 → 贡献
2. **Methods**: 管线步骤 → 算法 → 实验设计 → 数据
3. **Results**: 主结果(Val Dice/CErr) → 消融实验 → 对比实验
4. **Discussion**: 优势 → 局限 → 与文献对比 → 未来方向
5. **Conclusion**: 核心贡献总结

**文献基础**: 补充15-30篇相关文献(方法学/临床/算法)

**产出**: paper_plan.json (IMRaD结构+文献列表+时间表)

## 实战案例：K230训练管线

### 项目概要
- 数据: 901帧K230图像(800×480) + 976帧OpenEDS
- 管线: 7步CV管线(瞳孔定位→区域生长→椭圆精修→眼球中心标定→3D能量蛇→SAM眼裂→Seg Mask)
- 模型: MobileNetV2+T3EM, 4阶段渐进训练(30+20+20+20 epoch)
- 结果: Val Dice=0.8955, CErr=1.63px

### 发现的研究空白
1. 单目3D眼球追踪精度理论极限未验证
2. SAM vs 传统CV性能边界未定义
3. 不同人种解剖学参数泛化性未评估
4. 时序信息增益未量化
5. 混合训练泛化性增益未量化

### 生成的科学假设
- H1: 分割误差主导总误差(claim: ≥60%)
- H2: SAM在虹膜边缘优于能量蛇，在瞳孔定位不如区域生长
- H3: 时序建模比单帧提升Val Dice ≥0.03
- H4: 混合训练比单一数据集提升Val Dice ≥0.05
- H5: 固定几何参数导致系统性偏差

### 论文撰写计划
- 论文A(方法学): Q1, IEEE TBME/IOVS, 2周
- 论文B(实证分析): Q2, Scientific Reports, 4周

## 参考文件

- ref/legacy-paper-rescue-workflow.md — 管线/训练分析经验
- ref/legacy-paper-rescue-workflow.md — 管线/训练分析经验
- ref/hypothesis-generation-ref/io-contract.md — 假设生成IO合同
- ref/hypothesis-generation-ref/boundary.md — 假设生成边界
- references/k230-pipeline-audit-2026-06-13.md — K230训练管线审计报告(实战案例)
- references/k230-code-patterns.md — K230训练管线核心代码模式(数据加载/训练/参数)
- references/skill-library-audit-2026-06-13.md — 技能库审计与更新报告

## 实战案例

- **K230训练管线** (2026-06-13): 从901帧K230数据+训练日志提取5个研究空白、5个科学假设、2篇SCI论文计划。详见references/k230-pipeline-audit-2026-06-13.md。

## 验证

- [ ] 所有项目文件已扫描和统计
- [ ] 管线步骤已拆解为方法论
- [ ] 已识别至少3个研究空白
- [ ] 已生成至少3个可检验假设
- [ ] 已输出论文撰写计划(IMRaD结构+文献列表)
- [ ] 假设格式符合hypothesis-generation的IO_CONTRACT

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。


> (P032 去重: 保留合并前第二份的 6 行独有内容)
## 验证清单 (Verification)
- [ ] 项目文件已全量扫描统计，管线步骤已拆解为方法论
- [ ] 识别 ≥3 个研究空白（精确定位到文献矛盾/方法缺口）
- [ ] 生成 ≥3 个可检验假设（含检验条件与反证路径），格式符合 hypothesis-generation 的 IO_CONTRACT
- [ ] 已输出 paper_plan.json（IMRaD 结构 + 15-30 篇文献列表 + 时间表）
- [ ] 所有数值（Val Dice/CErr 等）可追溯到训练日志/代码输出，未编造

## 示例 · EXAMPLES
- **示例一（K230 训练管线）**：输入：901帧 K230 图像 + 976帧 OpenEDS 数据 + 训练日志（MobileNetV2+T3EM，4阶段 30+20+20+20 epoch）→ 输出：5 个研究空白（如单目 3D 精度极限未验证）、5 个可检验假设（H1: 分割误差主导总误差 ≥60%）、2 篇 SCI 论文计划（方法学 Q1 论文 A + 实证分析 Q2 论文 B），含 IMRaD 结构与 15-30 篇文献列表。来源：`references/k230-pipeline-audit-2026-06-13.md`，Val Dice=0.8955 / CErr=1.63px 可追溯至训练日志。
- **示例二（算法-only 管线）**：输入：纯数学推导 + 1 个 demo 脚本 + 训练日志 → 输出：1 个方法学论文计划（Q2-Q3），IMRaD 结构含推导+demo 结果，假设 ≥3 个（含反证路径），文献 15-20 篇。判定标准：管线完整 + 有实证结果。
