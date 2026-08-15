---
name: competition-submission
description: zip -r submission.zip submission/ -x "*/.*"
signature: 'competition-submission -> content-production: synthetic skill for competition submission'
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
    description: zip -r submission.zip submission/ -x "*/.*"
    signature: 'competition-submission -> content-production: synthetic skill for competition submission'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 竞赛要求 — 赛道、评分维度、格式要求、截止时间、申报表模板
- **input**: 项目素材 — 技术方案、代码、演示数据（用于填充模板）
- **output**: submission.zip — 技术规格书/路线图(Mermaid)/视频脚本/申报表(docx)/答辩PPT(pptx) 打包件
- **output**: 完整性检查结论 — 是否涵盖所有评分维度/格式要求/截止时间

--|
| 技术规格书 | `references/tech-spec-template.md` | Markdown |
| 路线图 | `references/roadmap-template.md` | Mermaid timeline |
| 视频脚本 | `references/video-script-template.md` | 分镜脚本格式 |
| 申报表 | `references/form-filling-guide.md` | python-docx/pdf |
| PPT | `references/presentation-template.md` | python-pptx |

详见各模板文件。

## Step 4-5: 整合与审核

```bash
# 打包
zip -r submission.zip submission/ -x "*/.*"

# 完整性检查
# 检查是否涵盖所有评分维度/格式要求/截止时间
```

## 参考文件

- `references/tech-spec-template.md` — 技术规格书模板
- `references/roadmap-template.md` — 路线图模板
- `references/video-script-template.md` — 视频脚本模板
- `references/form-filling-guide.md` — 中国申报表填写指南
- `references/presentation-template.md` — 答辩PPT模板
- `references/symposium-prep-patterns.md` — 政府座谈会准备模式

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

# Competition Submission---





--|
| 技术规格书 | `references/tech-spec-template.md` | Markdown |
| 路线图 | `references/roadmap-template.md` | Mermaid timeline |
| 视频脚本 | `references/video-script-template.md` | 分镜脚本格式 |
| 申报表 | `references/form-filling-guide.md` | python-docx/pdf |
| PPT | `references/presentation-template.md` | python-pptx |

详见各模板文件。

## Step 4-5: 整合与审核

```bash
# 打包
zip -r submission.zip submission/ -x "*/.*"

# 完整性检查
# 检查是否涵盖所有评分维度/格式要求/截止时间
```

## 参考文件

- `references/tech-spec-template.md` — 技术规格书模板
- `references/roadmap-template.md` — 路线图模板
- `references/video-script-template.md` — 视频脚本模板
- `references/form-filling-guide.md` — 中国申报表填写指南
- `references/presentation-template.md` — 答辩PPT模板
- `references/symposium-prep-patterns.md` — 政府座谈会准备模式

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

# Competition Submission
