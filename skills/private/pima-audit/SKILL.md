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

- [ ] 跨数据集对比实验条件一致：ZeroReplacer、Pipeline 结构、CV 设置、评估指标均相同，否则标注"对比无效"
- [ ] 实验代码为独立 `.py` 脚本且 cell 有输出，无输出记录的 Notebook 视为设计草稿、拒绝作为可复现记录
- [ ] 基线数量与声称一致（如 helix_benchmark 27/32），缺失模型逐一点名（DummyClassifier/GaussianProcessClassifier/StackingClassifier/TunedThresholdClassifierCV/FixedThresholdClassifier）
- [ ] 文献验证用 Semantic Scholar + CrossRef/PubMed 多源互补搜索，过滤 Acc>90% 或 F1>0.70 论文并标注数据泄露风险
- [ ] 高准确率论文交叉参考 OpenML 公开实验（PIDD ID:292）作为第三方验证
- [ ] 泄漏后 F1 趋同 ~0.70 标注为经验观察而非理论保证，并说明需更多数据集持续验证
- [ ] 严格区分 Pima（方法论审计 32 基线）与 HCS-3WT（新架构验证 7 模型）范式，未混同结论

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

- **Golden Input**: 一个 PIDD 泄漏审计目录——独立 `.py` 脚本（非无输出 Notebook）、实验条件已固定（ZeroReplacer/Pipeline/CV 一致）、文献库含 accuracy>90% 论文、OpenML PIDD ID:292 可访问（覆盖正常审计路径）
- **Golden Output**: 审计结论——基线 27/32 缺失模型逐一点名（DummyClassifier 等 5 个）、文献多源搜索（Semantic Scholar + CrossRef/PubMed）过滤高准确率论文并标注泄漏风险、泄漏后 F1 趋同 ~0.70 标注为经验观察（PIMA-007）、Pima 32 基线与 HCS-3WT 7 模型范式严格分列（精确匹配 VERIFICATION 七条）
- **Golden Error**: 实验条件不一致（ZeroReplacer/Pipeline/CV 不同）→ 标注"对比无效"；Notebook 无 cell 输出 → 按 PIMA-002 拒绝作为可复现记录；Pima 与 HCS-3WT 结论混同 → 按 PIMA-006 隔离重审（覆盖失败路径）

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

- **Golden Input**: 一个 PIDD 泄漏审计目录——独立 `.py` 脚本（非无输出 Notebook）、实验条件已固定（ZeroReplacer/Pipeline/CV 一致）、文献库含 accuracy>90% 论文、OpenML PIDD ID:292 可访问（覆盖正常审计路径）
- **Golden Output**: 审计结论——基线 27/32 缺失模型逐一点名（DummyClassifier 等 5 个）、文献多源搜索（Semantic Scholar + CrossRef/PubMed）过滤高准确率论文并标注泄漏风险、泄漏后 F1 趋同 ~0.70 标注为经验观察（PIMA-007）、Pima 32 基线与 HCS-3WT 7 模型范式严格分列（精确匹配 VERIFICATION 七条）
- **Golden Error**: 实验条件不一致（ZeroReplacer/Pipeline/CV 不同）→ 标注"对比无效"；Notebook 无 cell 输出 → 按 PIMA-002 拒绝作为可复现记录；Pima 与 HCS-3WT 结论混同 → 按 PIMA-006 隔离重审（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[PIMA-001]** 跨数据集审计时 → 必须保持 ZeroReplacer、Pipeline 结构、CV 设置及评估指标完全一致，否则对比无效
- **[PIMA-002]** 验证实验可复现性时 → 拒绝无输出记录的 Notebook，必须使用独立的 .py 脚本作为唯一可信记录
- **[PIMA-003]** 进行文献一致性验证时 → 结合 Semantic Scholar 与 CrossRef/PubMed 多源搜索，以弥补单一 API 的漏检风险
- **[PIMA-004]** 评估高准确率论文（Acc>90% 或 F1>0.70）时 → 优先标注数据泄露风险，并参考 OpenML 公开实验进行第三方交叉验证
- **[PIMA-005]** 构建普适性论证链时 → 采用“方法论验证 + 种族/人群泛化 + 规模/真实性验证”的多数据集组合策略
- **[PIMA-006]** 区分不同研究范式时 → 严格隔离“方法论审计”（如 Pima 32 基线）与“新架构验证”（如 HCS-3WT 7 模型），禁止混同结论
- **[PIMA-007]** 解释泄漏后指标趋同现象（如 F1~0.70）时 → 明确其为经验观察而非理论保证，需通过增加数据集数量来持续验证

## 示例 · EXAMPLES

**示例 1**（跨数据集条件一致性）
- **输入**：拟在 INSCAT 与 130-US 上复跑 PIDD 的泄漏审计对比
- **操作/输出**：按 **PIMA-001** 固定 ZeroReplacer、Pipeline 结构、CV 设置与评估指标；实验代码写为独立 `.py` 脚本（**PIMA-002**，Pitfall 1），非无输出 Notebook
- **验证**：验证清单「对比无效」项未触发；三数据集泄漏后 F1 均趋同 ~0.70，按 **PIMA-007** 标注为经验观察而非理论保证

**示例 2**（文献一致性验证）
- **输入**：目标数据集的已有论文声称 accuracy > 90%
- **操作/输出**：按 Step 4 与 **PIMA-003** 用 Semantic Scholar + CrossRef/PubMed 多源搜索，过滤 Acc>90% 或 F1>0.70 的论文并标注泄漏风险；按 **PIMA-004** 交叉参考 OpenML 公开实验（PIDD ID:292，200+ 实验）
- **验证**：高准确率论文与审计实测（F1≈0.71）偏差显著，形成「跨数据集方法论审计 vs 已有论文声明」对比论证

**示例 3**（基线完整性核查）
- **输入**：helix_benchmark 记录 27 个模型，论文声称 32 基线
- **操作/输出**：按 Pitfall 2 逐一点名缺失模型（DummyClassifier、GaussianProcessClassifier、StackingClassifier、TunedThresholdClassifierCV、FixedThresholdClassifier），补齐后重跑
- **验证**：基线数量 27→32 与声称一致；Pima（方法论审计 32 基线）与 HCS-3WT（新架构 7 模型）按 **PIMA-006** 严格分列，未混同结论
