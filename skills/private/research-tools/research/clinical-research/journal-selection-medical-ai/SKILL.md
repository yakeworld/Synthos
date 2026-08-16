---
name: journal-selection-medical-ai
description: '*详细内容已移至 references/ 目录。*'
signature: 'journal-selection-medical-ai -> clinical-research: synthetic skill for journal selection medical ai'
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
    description: '*详细内容已移至 references/ 目录。*'
    signature: 'journal-selection-medical-ai -> clinical-research: synthetic skill for journal selection medical ai'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 医学 AI 论文选题与类型 — 临床数据类型、方法学特征（详见 references/ 目录）
- **input**: 目标受众与发表定位 — 期刊档次偏好、APC/审稿周期约束
- **output**: 候选期刊推荐列表 — 医学 AI 领域匹配期刊（选择标准见 references/）
- **output**: 选择依据说明 — 各候选期刊与论文选题的匹配度理由

## 原则 (Principles)

- **选题为纲**：期刊之择以论文选题与方法学特征为纲，选题不明则择期无所据。
- **受众与档次相参**：目标受众、期刊档次、APC 与审稿周期须三者相参，偏一即失其宜。
- **匹配必有据**：推荐列表须附各候选与选题之匹配度理由，无理由之推荐不可信。
- **详情下沉参考**：细节沉至 `references/` 目录，主文件只存纲要；纲详而末简，则用之便捷。

*详细内容已移至 references/ 目录。*


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[JOUR-001]** 论文选题与方法学特征明确 → 以选题和方法学特征为纲进行期刊匹配，避免无据择期
- **[JOUR-002]** 需确定发表定位 → 综合考量目标受众、期刊档次、APC 费用及审稿周期，确保三者平衡
- **[JOUR-003]** 生成候选期刊推荐列表 → 必须附带各候选期刊与论文选题的具体匹配度理由，确保推荐可信
- **[JOUR-004]** 处理详细选择标准与数据 → 将细节下沉至 references/ 目录，主文件仅保留纲要以保持便捷
- **[JOUR-005]** 接收输入参数或文件 → 严格校验参数类型、范围、格式及路径有效性，确保输入完整
- **[JOUR-006]** 执行中间步骤或转换计算 → 验证中间过程的正确性，确保数据转换与计算逻辑无误
- **[JOUR-007]** 生成最终输出结果 → 确保输出格式、内容结构、编码及命名符合预期规范
- **[JOUR-008]** 遇到空输入、极大值或异常场景 → 执行边界验证与错误处理，提供包含上下文和恢复建议的明确错误信息

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Journal Selection Medical Ai---





*详细内容已移至 references/ 目录。*

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

