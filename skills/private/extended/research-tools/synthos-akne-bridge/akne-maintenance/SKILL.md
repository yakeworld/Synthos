---
name: akne-maintenance
description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
signature: 'akne-maintenance -> synthos-akne-bridge: synthetic skill for akne maintenance'
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
    description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
    signature: 'akne-maintenance -> synthos-akne-bridge: synthetic skill for akne maintenance'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: AKNE 系统状态（图谱目录、源文件、守护进程）— 待诊断/维护的对象
- **input**: 运维操作请求 — 日常检查、修复、审计类型
- **output**: 16项综合健康审计结果 — 连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式等指标
- **output**: 审计报告（五阶段：健康诊断→内容矛盾→研究空白→假设→修复）

|
| `references/operations-reference.md` | 运维操作速查 — 日常检查、修复、守护进程、常见问题速查表 |
| `references/audit-report-template.md` | 全面审计报告模板 — 五阶段结构（健康诊断→内容矛盾→研究空白→假设→修复） |
| `references/path-redundancy-2026-06-18.md` | 路径冗余诊断 — /home/yakeworld/Synthos 是 /media/.../Synthos 的符号链接，inode相同 |
| `scripts/akne-comprehensive-audit.py` | 16项综合健康审计脚本 — 一次运行覆盖连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式/元数据/Wiki污染/entity命名空间/路径前缀等全部指标 |

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

# Akne Maintenance---





|
| `references/operations-reference.md` | 运维操作速查 — 日常检查、修复、守护进程、常见问题速查表 |
| `references/audit-report-template.md` | 全面审计报告模板 — 五阶段结构（健康诊断→内容矛盾→研究空白→假设→修复） |
| `references/path-redundancy-2026-06-18.md` | 路径冗余诊断 — /home/yakeworld/Synthos 是 /media/.../Synthos 的符号链接，inode相同 |
| `scripts/akne-comprehensive-audit.py` | 16项综合健康审计脚本 — 一次运行覆盖连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式/元数据/Wiki污染/entity命名空间/路径前缀等全部指标 |

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

# Akne Maintenance
