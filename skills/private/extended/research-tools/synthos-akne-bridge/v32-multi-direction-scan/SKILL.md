---
name: v32-multi-direction-scan
description: '**边界**：技能功能边界。'
signature: 'v32-multi-direction-scan -> synthos-akne-bridge: synthetic skill for v32 multi direction scan'
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
    signature: 'v32-multi-direction-scan -> synthos-akne-bridge: synthetic skill for v32 multi direction scan'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
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

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# V32 Multi Direction Scan---





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

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# V32 Multi Direction Scan
