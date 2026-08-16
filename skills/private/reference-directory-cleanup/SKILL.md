---
name: reference-directory-cleanup
description: 1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
signature: 'reference-directory-cleanup -> private: synthetic skill for reference directory cleanup'
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
    description: 1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
    signature: 'reference-directory-cleanup -> private: synthetic skill for reference directory cleanup'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| 根目录删除旧PDF | 7个 |
| 根目录删除旧元数据 | 3个（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md） |
| 删除bak文件 | 5个 |
| 从pdfs复制匹配PDF到根目录 | 8个 |
| 创建符号链接 | 2个 |
| 规范化后根目录PDF/链接 | 18个 |
| Bib总数 | 29个 |

## 注意事项

1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
2. **名称不匹配需要检查内容** — 如 `Shams2025.pdf` vs `Shams2023BRFSS` 需验证内容
3. **3d-eyeball标准**: 45个PDF在根目录 + references.bib + 空pdfs/子目录
4. **Bib清理顺序**：先清理bib中的无效条目，再删除.tex中的残留引用，最后重新编译。详见 `paper-pipeline/SKILL.md`。

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

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Reference Directory Cleanup---





|
| 根目录删除旧PDF | 7个 |
| 根目录删除旧元数据 | 3个（bibkey-map.json, notebooklm-sources.json, REFERENCE_MANIFEST.md） |
| 删除bak文件 | 5个 |
| 从pdfs复制匹配PDF到根目录 | 8个 |
| 创建符号链接 | 2个 |
| 规范化后根目录PDF/链接 | 18个 |
| Bib总数 | 29个 |

## 注意事项

1. **不要假设子目录PDF都与当前Bib对应** — 旧管线PDF可能完全不相关
2. **名称不匹配需要检查内容** — 如 `Shams2025.pdf` vs `Shams2023BRFSS` 需验证内容
3. **3d-eyeball标准**: 45个PDF在根目录 + references.bib + 空pdfs/子目录
4. **Bib清理顺序**：先清理bib中的无效条目，再删除.tex中的残留引用，最后重新编译。详见 `paper-pipeline/SKILL.md`。

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

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

