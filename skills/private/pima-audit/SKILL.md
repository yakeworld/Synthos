---
name: pima-audit
description: 在目标数据集的学术论文中验证一致性：
signature: 'pima-audit -> private: synthetic skill for pima audit'
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
    description: 在目标数据集的学术论文中验证一致性：
    signature: 'pima-audit -> private: synthetic skill for pima audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| A     | 0.66    | 0.71      | +7%   |
| B     | 0.48    | 0.70      | +45%  |
| C     | 0.21    | 0.70      | +228% |
```

#### Step 4: 文献验证

在目标数据集的学术论文中验证一致性：
1. 用 Semantic Scholar API 搜索 `dataset X` + `machine learning`
2. 过滤出 report accuracy > 90% 或 F1 > 0.70 的论文
3. 标注这些论文的数据泄露风险
4. 形成：「跨数据集方法论审计 vs 已有论文声明」的对比论证

### 论文升级建议

**原始论调：** "在 PIDD 上证明了方法论正确性的重要性"
**升级后：** "在 3 个数据集上发现**同样的数据泄露问题**——方法论审计的普适性"

推荐增加 2 个数据集：
1. PhysioNet INSCAT（种族泛化 - 印度人群）
2. Diabetes 130-US（规模+真实性 - 美国医院）

形成：PIDD (美国本土) + INSCAT (印度人群) + 130-US (美国大型)
论证链：方法论验证 → 种族泛化 → 规模验证

## Pitfall

1. **Notebook 不是可复现记录** — 如果 notebook 里所有单元格都没有输出（cell outputs），它只是一个设计草稿。实验代码必须是独立的 `.py` 脚本。
2. **helix_benchmark 不完整** — 27 个模型 vs 32 个声称。missing: DummyClassifier, GaussianProcessClassifier, StackingClassifier, TunedThresholdClassifierCV, FixedThresholdClassifier。
3. **Pima 论文 vs HCS-3WT 论文是不同范式** — Pima: 方法论审计（32 基线）；HCS-3WT: 新架构验证（7 模型）。不要混为一谈。
4. **跨数据集审计必须保证实验条件一致** — 同样的 ZeroReplacer、Pipeline 结构、CV 设置、评估指标。否则跨数据集对比无意义。
5. **泄漏后的 F1 趋同 ~0.70 是一个经验观察，不是理论保证** — 需要在更多数据集上验证。
6. **Semantic Scholar API 可能漏检** — 不返回所有论文。建议用 CrossRef 或 PubMed 补充。
7. **OpenML 公开实验可以作为第三方验证** — PIDD (ID:292) 有 200+ 公开实验，其中 accuracy > 90% 的很可能存在泄漏。

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

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Pima Audit---





|
| A     | 0.66    | 0.71      | +7%   |
| B     | 0.48    | 0.70      | +45%  |
| C     | 0.21    | 0.70      | +228% |
```

#### Step 4: 文献验证

在目标数据集的学术论文中验证一致性：
1. 用 Semantic Scholar API 搜索 `dataset X` + `machine learning`
2. 过滤出 report accuracy > 90% 或 F1 > 0.70 的论文
3. 标注这些论文的数据泄露风险
4. 形成：「跨数据集方法论审计 vs 已有论文声明」的对比论证

### 论文升级建议

**原始论调：** "在 PIDD 上证明了方法论正确性的重要性"
**升级后：** "在 3 个数据集上发现**同样的数据泄露问题**——方法论审计的普适性"

推荐增加 2 个数据集：
1. PhysioNet INSCAT（种族泛化 - 印度人群）
2. Diabetes 130-US（规模+真实性 - 美国医院）

形成：PIDD (美国本土) + INSCAT (印度人群) + 130-US (美国大型)
论证链：方法论验证 → 种族泛化 → 规模验证

## Pitfall

1. **Notebook 不是可复现记录** — 如果 notebook 里所有单元格都没有输出（cell outputs），它只是一个设计草稿。实验代码必须是独立的 `.py` 脚本。
2. **helix_benchmark 不完整** — 27 个模型 vs 32 个声称。missing: DummyClassifier, GaussianProcessClassifier, StackingClassifier, TunedThresholdClassifierCV, FixedThresholdClassifier。
3. **Pima 论文 vs HCS-3WT 论文是不同范式** — Pima: 方法论审计（32 基线）；HCS-3WT: 新架构验证（7 模型）。不要混为一谈。
4. **跨数据集审计必须保证实验条件一致** — 同样的 ZeroReplacer、Pipeline 结构、CV 设置、评估指标。否则跨数据集对比无意义。
5. **泄漏后的 F1 趋同 ~0.70 是一个经验观察，不是理论保证** — 需要在更多数据集上验证。
6. **Semantic Scholar API 可能漏检** — 不返回所有论文。建议用 CrossRef 或 PubMed 补充。
7. **OpenML 公开实验可以作为第三方验证** — PIDD (ID:292) 有 200+ 公开实验，其中 accuracy > 90% 的很可能存在泄漏。

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

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Pima Audit
