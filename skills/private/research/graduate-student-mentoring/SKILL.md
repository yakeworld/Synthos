---
name: graduate-student-mentoring
description: '**边界**：技能功能边界。'
signature: 'graduate-student-mentoring -> research: synthetic skill for graduate student mentoring'
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
    signature: 'graduate-student-mentoring -> research: synthetic skill for graduate student mentoring'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


--|
| OpenCode代码跑不通 | 导师用Hermes调Synthos技能库现有代码 |
| 公开数据集不够 | 切换至科室临床数据 |
| 统计分析不会 | 提供分析模板 + ChatGPT协助 |
| 论文写作慢 | 先写中文稿，导师改完再翻英文 |
| 方向发散 | 锚定五大支柱，定期回顾范围约束 |

## 学生自检清单（每周）

- [ ] 本周新增了多少行可运行的代码？
- [ ] 本周产出了几张图/几个Table？
- [ ] 是否理解了代码每一行在做什么？
- [ ] 有没有卡住超过2小时的问题？（有→马上问导师）
- [ ] 是否在AI生成的代码上做了自己的修改？

## 相关参考

- `ref/graduate-training-plan-3d-eye-tracking.md` — 三维眼动分析训练方案全文

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION
## 原则 (Principles)

- **锚定五大支柱**：方向一散即锚定五大支柱，定期回顾范围约束，不散于末节。
- **以代码计周**：每周自检以「新增可运行代码行数 / 图与 Table 产出」为量度，无产出之周不可谓之进。
- **卡二时即问**：卡住逾二小时必问导师，勿待穷时；疑者即明，明则速进。
- **改 AI 以自立**：AI 生码必亲加修改方算己作；不改则知其然不知其所以然，学无所成。


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

# Graduate Student Mentoring---





--|
| OpenCode代码跑不通 | 导师用Hermes调Synthos技能库现有代码 |
| 公开数据集不够 | 切换至科室临床数据 |
| 统计分析不会 | 提供分析模板 + ChatGPT协助 |
| 论文写作慢 | 先写中文稿，导师改完再翻英文 |
| 方向发散 | 锚定五大支柱，定期回顾范围约束 |

## 学生自检清单（每周）

- [ ] 本周新增了多少行可运行的代码？
- [ ] 本周产出了几张图/几个Table？
- [ ] 是否理解了代码每一行在做什么？
- [ ] 有没有卡住超过2小时的问题？（有→马上问导师）
- [ ] 是否在AI生成的代码上做了自己的修改？

## 相关参考

- `ref/graduate-training-plan-3d-eye-tracking.md` — 三维眼动分析训练方案全文

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

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

