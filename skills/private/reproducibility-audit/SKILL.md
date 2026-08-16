---
name: reproducibility-audit
description: '**边界**：技能功能边界。'
signature: 'reproducibility-audit -> private: synthetic skill for reproducibility
  audit'
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
    signature: 'reproducibility-audit -> private: synthetic skill for reproducibility
      audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---


|
| 2026-06-29 | 2.1.0 | 新增：数据集版本陷阱规则、thebibliography与bib同步规则 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 原则 (Principles)

1. **「版有定数，变则复之。」** — 数据集版本陷阱：版本未锁定则复现无凭，须核对数据集版本一致。
2. **「引文两录，须同步之。」** — `thebibliography` 与 `.bib` 双源并存时须同步，不可只改其一。
3. **「Golden 为纲，改必过之。」** — Golden 集合是测试单一真理来源，所有改进必通过 golden 测试。
4. **「验可复现，始谓可信。」** — 每项验证可执行、可记录、可复现，验证失败记录原因与修复。


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[REPR-001]** 数据集版本未锁定 → 必须核对并锁定数据集版本以确保复现依据
- **[REPR-002]** `thebibliography` 与 `.bib` 双源并存 → 必须同步更新两者，禁止仅修改其一
- **[REPR-003]** 执行任何代码或流程改进 → 必须通过 Golden 集合测试以验证单一真理来源
- **[REPR-004]** 执行验证步骤 → 必须确保验证过程可执行、可记录且可复现
- **[REPR-005]** 验证失败发生 → 必须记录具体失败原因及对应的修复措施
- **[REPR-006]** 处理输入/输出/边界场景 → 必须覆盖空输入、极大值及异常场景的错误处理与恢复指引

## 验证清单 · VERIFICATION

- [ ] 数据集版本已锁定：已核对并固定数据集版本，确保复现有据，版本未锁定则复现无凭
- [ ] thebibliography 与 .bib 同步：双源并存时已同步更新两者，禁止仅修改其一
- [ ] Golden 集合通过：任何代码或流程改进均已通过 Golden 集合测试，验证单一真理来源
- [ ] 验证可执行可复现：每项验证步骤可执行、可记录且可复现，过程留痕
- [ ] 验证失败已记录：验证失败时已记录具体失败原因及对应的修复措施
- [ ] 边界场景覆盖：空输入、极大值及异常场景的错误处理与恢复指引已覆盖

## Golden 集合 · GOLDEN SET

- **Golden Input**: 一篇待复现论文的工作目录——数据集版本号已锁定 + `thebibliography` 环境与 `.bib` 文件双源并存 + 完整代码流程（含可执行的 Golden 集合测试）
- **Golden Output**: 复现报告——数据集版本核对一致（REPR-001）、`thebibliography` 与 `.bib` 已同步（REPR-002）、所有改进通过 Golden 集合测试（REPR-003），每项验证步骤留痕可记录、可复现
- **Golden Error**: 数据集版本未锁定 → 判定复现无凭，须先锁定版本再重跑（原则#1 / REPR-001）；或验证失败 → 必须记录具体失败原因及对应修复措施（REPR-004 / REPR-005），禁止静默跳过

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
