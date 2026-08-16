---
name: paper-improvement
description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
signature: 'paper-improvement -> private: synthetic skill for paper improvement'
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
    signature: 'paper-improvement -> private: synthetic skill for paper improvement'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| `references/benchmark-alignment-checklist.md` | 实验模型清单一致性校验清单 |
| `references/hcs3wt-fake-doi-replacement-2026-06-25.md` | HCS-3WT实战：假DOI替换记录 |
| `references/hcs3wt-p0-remediation-full-cycle-2026-06-29.md` | HCS-3WT实战：质量检查→P0修复完整闭环（数值伪造修复模式选择、引用批量修复、数据集统一） |
| `references/pima-catboost-claim-verification-2026-06-25.md` | PIMA实战：CatBoost声称验证 |
| `references/latex-citation-replacement-fallback.md` | LaTeX引用替换回退方案（sed）|
| `references/latex-compilation-workflow.md` | LaTeX编译工作流详细说明 |
| `references/standard-audit-report-templates.md` | 四份标准审计报告模板和生成规范 |
| `BOUNDARY.md` | 技能边界声明 |
| `EVIDENCE_SCHEMA.md` | 技术证据架构 |
| `IO_CONTRACT.md` | 输入输出规范 |

## 六、版本历史

- **v1.0.0** (2026-03): 初始版本
- **v1.1.0** (2026-06): 新增虚假引用替换、SHAP验证、OpenML基准对比
- **v1.2.0** (2026-06): 重构为思想/原则/方法/规则结构

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

# Paper Improvement---





|
| `references/benchmark-alignment-checklist.md` | 实验模型清单一致性校验清单 |
| `references/hcs3wt-fake-doi-replacement-2026-06-25.md` | HCS-3WT实战：假DOI替换记录 |
| `references/hcs3wt-p0-remediation-full-cycle-2026-06-29.md` | HCS-3WT实战：质量检查→P0修复完整闭环（数值伪造修复模式选择、引用批量修复、数据集统一） |
| `references/pima-catboost-claim-verification-2026-06-25.md` | PIMA实战：CatBoost声称验证 |
| `references/latex-citation-replacement-fallback.md` | LaTeX引用替换回退方案（sed）|
| `references/latex-compilation-workflow.md` | LaTeX编译工作流详细说明 |
| `references/standard-audit-report-templates.md` | 四份标准审计报告模板和生成规范 |
| `BOUNDARY.md` | 技能边界声明 |
| `EVIDENCE_SCHEMA.md` | 技术证据架构 |
| `IO_CONTRACT.md` | 输入输出规范 |

## 六、版本历史

- **v1.0.0** (2026-03): 初始版本
- **v1.1.0** (2026-06): 新增虚假引用替换、SHAP验证、OpenML基准对比
- **v1.2.0** (2026-06): 重构为思想/原则/方法/规则结构

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

