---
name: citation-appropriateness-verification
description: '**边界**：技能功能边界。'
signature: 'citation-appropriateness-verification -> core: synthetic skill for citation appropriateness verification'
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
    signature: 'citation-appropriateness-verification -> core: synthetic skill for citation appropriateness verification'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| 2026-07-06 | 3.2.0 | 新增 L5 DOI 真实性验证（bib DOI 可能是错误的，已确认 Chakravarthy2021Deep 案例）；新增 Pitfalls：DOI 错误、PDF 命名不匹配、多目录扫描、Sci-Hub 覆盖盲区、JAMA 403 封锁；新增 `references/bib-doi-validation-2026-07-06.md`。 |
| 2026-07-01 | 3.0.0 | API 故障恢复策略：SS→Crossref→PubMed 三级回退。新增 Crossref 查询长度限制（100字符）和 BibTeX 生成陷阱。Crossref 不再支持 format=bibtex。 |
| 2026-06-24 | 2.0.0 | 从 quality-gate 拆分为独立技能。新增引用功能分类树（6类）、引文性能基准提取、引文网络分析、引用缺失分析。 |
| 2026-06-24 | 2.1.0 | 重构输出格式为独立专项报告，与通用六域报告并行。新增 G5 集成点。 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 原则 (Principles)

> **引必有其用。** 按 6 类功能（背景/基准/对比/方法/局限/支撑）分类审查，无功能引用的存在即失当。
> **凡引必验其真。** bib 中的 DOI 可能本身有误（Chakravarthy2021Deep 案例），须回源验证，不可只信条目。
> **源不可恃，三源回退。** SS→Crossref→PubMed 三级回退，API 失效有备路，验证不因单源中断而停摆。


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[CITA-001]** 引文存在但无明确功能归属 → 按背景/基准/对比/方法/局限/支撑 6 类功能分类审查，无功能引用即判定为失当
- **[CITA-002]** 依赖 BibTeX 条目中的 DOI 信息 → 必须回源验证 DOI 真实性，不可仅信任条目数据以防 DOI 错误
- **[CITA-003]** 单一 API 源（如 Semantic Scholar）验证失败或不可用 → 执行 SS→Crossref→PubMed 三级回退策略，确保验证流程不因单源中断而停摆
- **[CITA-004]** 使用 Crossref API 进行查询 → 确保查询字符串长度 ≤ 100 字符，且避免使用已废弃的 `format=bibtex` 参数
- **[CITA-005]** 生成验证结果报告 → 输出独立的专项报告，与通用六域报告并行，并在 G5 集成点单独标注
- **[CITA-006]** 验证过程执行中 → 确保每项验证可执行、可记录、可复现，失败时明确记录原因和修复指引

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## 约束规则 · RULES

- 每篇引文必须归入 6 类功能之一（背景/基准/对比/方法/局限/支撑），无功能引用即失当
- bib 中 DOI 必须回源验证真实性，不可只信条目（Chakravarthy2021Deep 案例）
- API 验证走 SS→Crossref→PubMed 三级回退，单源失效不中断验证
- Crossref 查询长度 ≤ 100 字符，且不再支持 `format=bibtex`
- 验证报告独立于通用六域报告输出，G5 集成点单独标注

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Citation Appropriateness Verification---





|
| 2026-07-06 | 3.2.0 | 新增 L5 DOI 真实性验证（bib DOI 可能是错误的，已确认 Chakravarthy2021Deep 案例）；新增 Pitfalls：DOI 错误、PDF 命名不匹配、多目录扫描、Sci-Hub 覆盖盲区、JAMA 403 封锁；新增 `references/bib-doi-validation-2026-07-06.md`。 |
| 2026-07-01 | 3.0.0 | API 故障恢复策略：SS→Crossref→PubMed 三级回退。新增 Crossref 查询长度限制（100字符）和 BibTeX 生成陷阱。Crossref 不再支持 format=bibtex。 |
| 2026-06-24 | 2.0.0 | 从 quality-gate 拆分为独立技能。新增引用功能分类树（6类）、引文性能基准提取、引文网络分析、引用缺失分析。 |
| 2026-06-24 | 2.1.0 | 重构输出格式为独立专项报告，与通用六域报告并行。新增 G5 集成点。 |

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

