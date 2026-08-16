---
name: reproducibility-audit
description: '**边界**：技能功能边界。'
signature: 'reproducibility-audit -> private: synthetic skill for reproducibility audit'
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
    signature: 'reproducibility-audit -> private: synthetic skill for reproducibility audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
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
