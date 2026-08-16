---
name: citation-appropriateness-verification
description: 引用适当性验证 — 6 类功能分类、DOI 回源验证、三级回退、专项报告输出
signature: 'citation-appropriateness-verification -> core: 按6类功能审查引用适当性，DOI 回源验证，SS→Crossref→PubMed 三级回退'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 3.2.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    priority: P2
    synthos_version: 3.2.0
    synthos_asserted_compliance: P0,P2,P3
    synthos_mechanical_atoms: ''
---

# Citation Appropriateness Verification — 引用适当性验证

## 契约层 · BOUNDARY

**边界**：引用适当性验证（功能分类 + DOI 真实性），不覆盖引用完整性匹配（见 `citation-completeness-verification`）与 BibTeX 条目质量审计（见 `bib-integrity-audit`）。

## 契约层 · IO_CONTRACT

**输入**：BibTeX 条目 / 引文列表、上下文信息。
**输出**：专项验证报告（独立于通用六域报告，G5 集成点单独标注）。

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

- [ ] 每篇引文已归入 6 类功能之一（背景/基准/对比/方法/局限/支撑），无功能引用已标记为失当
- [ ] 依赖的 BibTeX DOI 已回源验证真实性（SS→Crossref→PubMed 三级回退），未只信条目数据
- [ ] 验证过程中单一 API 源失效时已切换备用源，验证未中断
- [ ] Crossref 查询字符串长度 ≤ 100 字符，未使用已废弃的 `format=bibtex` 参数
- [ ] 验证报告已独立输出（非通用六域报告），G5 集成点已单独标注
- [ ] 每项验证已记录执行结果、失败原因与修复指引（可执行、可记录、可复现）

## 约束规则 · RULES

- 每篇引文必须归入 6 类功能之一（背景/基准/对比/方法/局限/支撑），无功能引用即失当
- bib 中 DOI 必须回源验证真实性，不可只信条目（Chakravarthy2021Deep 案例）
- API 验证走 SS→Crossref→PubMed 三级回退，单源失效不中断验证
- Crossref 查询长度 ≤ 100 字符，且不再支持 `format=bibtex`
- 验证报告独立于通用六域报告输出，G5 集成点单独标注

## Golden 集合 · GOLDEN SET

- **Golden Input**: 含无功能引用的 BibTeX 条目 + 含已知错误 DOI 的条目（如 Chakravarthy2021Deep）
- **Golden Output**: 专项报告标注每篇引文功能归属；错误 DOI 被回源验证并标记（非信任条目数据）；G5 集成点单独标注
- **Golden Error**: 全部 API 源失效时报告三源回退过程并标记无法验证的条目；Crossref 超 100 字符查询被拒绝

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## Pitfalls

| 问题 | 解决 |
|------|------|
| bib DOI 本身有误 | 回源验证（L5），不可只信条目 |
| 单一 API 失效 | SS→Crossref→PubMed 三级回退 |
| Crossref 查询超长 | 截断至 ≤100 字符 |
| Crossref format=bibtex 废弃 | 用 JSON 输出 |
| PDF 命名不匹配 | 扫描时按 DOI 精确匹配 |
| JAMA 403 封锁 | 换源或延时重试 |

## 参考文件

- `references/bib-doi-validation-2026-07-06.md` — DOI 真实性验证完整记录
