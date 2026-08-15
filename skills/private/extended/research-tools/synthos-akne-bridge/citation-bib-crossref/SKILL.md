---
name: citation-bib-crossref
description: pima-crispdm           33   100%    0     0    ✅
signature: 'citation-bib-crossref -> synthos-akne-bridge: synthetic skill for citation bib crossref'
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
    description: pima-crispdm           33   100%    0     0    ✅
    signature: 'citation-bib-crossref -> synthos-akne-bridge: synthetic skill for citation bib crossref'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 论文库目录（.tex 文件 + .bib 文件）— 待审计的 LaTeX 论文集合
- **input**: 触发条件 — 定期审计/批量编译前/批量改引后/质量门审查前
- **output**: 引用完整性审计结果 — 每篇论文 D8（bib条目数）/D10a（\cite↔\bib 匹配率）
- **output**: 问题分级清单 — 孤儿引用（无bib条目）、僵尸条目（未引用）、条目不足30的论文

pima-crispdm           33   100%    0     0    ✅
```

### Problem detail

```
严重问题 (D8=0):
- 3d-eye-bppv-diagnosis: D10a=0.0% (孤儿: Aw2013, Balatsouras2012, ...62 total)
  无 .bib 文件 / .bib 为空

中等问题 (D10a<100%):
- 3d-iris-normalization: D10a=93.8% (孤儿: <label>, lamport94)
  bib 文件存在但 2 个引用未匹配

低问题 (D8<30):
- bppv-epley-semont: D8=26, D10a=100%
  bib 完整但条目不足 30

混合问题 (孤儿+僵尸 均 >5):
- bppv-pc-repositioning: D10a=75% (孤儿: Baloh2003, Chang2004, Kim2012)
  僵尸: Anagnostou2018, Beyea2012, ...35 total)
```

### Summary

```
总计: 65篇, 健康: 16篇, 问题: 49篇
```

## When to Use

- Periodic integrity audit of a growing paper library
- Before batch compilation of multiple papers
- After bulk citation changes across papers
- When investigating "why did compilation fail on paper X?"
- Prior to quality-gate reviews (D8/D10a is L0.5 data honesty gate)

## Related Skills

- `bib-integrity-audit` — DOI completeness and suspicious entries within .bib files (complementary: this skill checks \cite↔\bib matching, that checks \bib entry quality)
- `paper-pipeline` → `citation-completeness-verification` — same-concept check for in-text \bibitem{} (within a single .tex file, not cross-file)
- `quality-gate` — D8/D10a metrics feed into L0.5 gate evaluation

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

# Citation Bib Crossref---





pima-crispdm           33   100%    0     0    ✅
```

### Problem detail

```
严重问题 (D8=0):
- 3d-eye-bppv-diagnosis: D10a=0.0% (孤儿: Aw2013, Balatsouras2012, ...62 total)
  无 .bib 文件 / .bib 为空

中等问题 (D10a<100%):
- 3d-iris-normalization: D10a=93.8% (孤儿: <label>, lamport94)
  bib 文件存在但 2 个引用未匹配

低问题 (D8<30):
- bppv-epley-semont: D8=26, D10a=100%
  bib 完整但条目不足 30

混合问题 (孤儿+僵尸 均 >5):
- bppv-pc-repositioning: D10a=75% (孤儿: Baloh2003, Chang2004, Kim2012)
  僵尸: Anagnostou2018, Beyea2012, ...35 total)
```

### Summary

```
总计: 65篇, 健康: 16篇, 问题: 49篇
```

## When to Use

- Periodic integrity audit of a growing paper library
- Before batch compilation of multiple papers
- After bulk citation changes across papers
- When investigating "why did compilation fail on paper X?"
- Prior to quality-gate reviews (D8/D10a is L0.5 data honesty gate)

## Related Skills

- `bib-integrity-audit` — DOI completeness and suspicious entries within .bib files (complementary: this skill checks \cite↔\bib matching, that checks \bib entry quality)
- `paper-pipeline` → `citation-completeness-verification` — same-concept check for in-text \bibitem{} (within a single .tex file, not cross-file)
- `quality-gate` — D8/D10a metrics feed into L0.5 gate evaluation

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

# Citation Bib Crossref
