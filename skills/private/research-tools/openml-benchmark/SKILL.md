---
name: openml-benchmark
description: '**F1差距分析结论**：OpenML WEKA 结果 (F1=0.75-0.76) 高于 Helix (F1=0.68-0.71)，原因排序：'
signature: 'openml-benchmark -> research-tools: synthetic skill for openml benchmark'
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
    description: '**F1差距分析结论**：OpenML WEKA 结果 (F1=0.75-0.76) 高于 Helix (F1=0.68-0.71)，原因排序：'
    signature: 'openml-benchmark -> research-tools: synthetic skill for openml benchmark'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| OpenML 最佳 | 0.7995 | 0.8026 | 0.8026 | Weka AttributeSelectedClassifier |
| OpenML WEKA RF | 0.7648 | 0.7669 | — | WEKA RF I=200 |
| OpenML WEKA BayesNet | 0.7507 | 0.7526 | — | WEKA BayesNet K2 |
| 我们的 CatBoost (Helix) | 0.7067 | 0.7759 | 0.7756 | sklearn+fold内预处理 |
| 我们的 GBC (Helix) | 0.6868 | 0.7629 | 0.7464 | sklearn+fold内预处理 |
| OpenML 平均 | 0.6745 | 0.6982 | — | 50 个有效样本 |

**F1差距分析结论**：OpenML WEKA 结果 (F1=0.75-0.76) 高于 Helix (F1=0.68-0.71)，原因排序：
1. **WEKA 模型实现不同**（默认超参、剪枝策略、树分裂规则）
2. **不做 SMOTE**（PIDD 268:500 不严重不平衡，SMOTE 引入噪声抵消部分收益）
3. **不做标准化**（树模型/贝叶斯模型不需要）
4. **0→NaN 预处理反而是正向的**（ΔF1=+0.018，已消融验证）
5. 最佳模型用了特征选择 (CfsSubsetEval+BestFirst)，不可移植到 sklearn

**当报告 PIDD 结果时，应同时报告 OpenML 基准对比**，说明：
- 我们的方法在 OpenML 数据库中的排名
- 方法差异（Weka 特定 vs sklearn 通用）
- 方法论可审计性 vs 纯数值优势

## 常见陷阱

1. **参数名错误**：`task_id` → 应为 `task`；`data_id` 在部分 API 端点有效
2. **字符串 vs 浮点**：evaluations 中的 value 是 str，需 `float()` 转换
3. **None 值**：`run.get('predictive_accuracy')` 返回 None，需检查 `output_data.evaluation`
4. **大量 evaluations**：一个 run 可能有 200+ evaluation 项，只提取需要的
5. **无效 runs**：某些 run 的 accuracy=0 或 f1=0，应过滤
6. **API 速率**：逐个查询 run 详情很慢（每个需 30s+），建议批量获取后过滤再逐个查询
7. **采样偏差**：API 返回顺序可能不是按性能排序，需要手动排序
8. **Weka 特有方法不可比**：OpenML 上最佳模型常使用 Weka 特有组合（如 AttributeSelectedClassifier + Bagging_JRip），包含 CfsSubsetEval 特征选择。此类方法在 PIDD 等小数据集上 F1 可达 0.80，但不可移植到 sklearn。论文讨论中应注明框架差异，避免直接用 Top 10% 排名作为核心论点。
9. **API 超时**：`curl -s` 访问 OpenML API 时，1000 条返回量可能超时。建议 limit=500 分批处理，或使用 `--max-time 30` 控制超时。
10. **ZeroReplacer 不是 F1 偏低原因**：对 PIDD，ZeroReplacer 对中位数插补前后的 F1 差异 < 0.007。F1 差距主要来自方法框架差异，而非数据预处理。

## 参考文件

- `references/openml-api-endpoints.md` — OpenML API 端点速查
- `references/pidd-zero-analysis.md` — PIDD 零值分布、临床意义、过采样对比详情
- `references/openml-pidd-detailed-analysis.md` — PIDD 完整诊断：ZeroReplacer 消融、Weka 最佳模型分析、OpenML Top 20 列表（2026-06-20）+ 实时 API Top-30 拉取（WEKA RandomForest F1=0.7648 等）+ Glucose=0 保持原值消融实验（2026-06-23 扩展）

## 脚本

- `scripts/openml_benchmark_fetcher.py` — 批量获取 OpenML 基准数据

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 报告结果时已同时提供 OpenML 数据库基准对比表，注明本方法在 OpenML 中的排名位置
- [ ] 方法框架差异（Weka vs sklearn）已明确说明，未将 Weka 特有方法（如 AttributeSelectedClassifier + Bagging_JRip）的 Top 排名直接作为核心论点
- [ ] OpenML API 返回的 string 型 evaluation value 已 `float()` 转换，accuracy/f1 为 0 的无效 runs 已过滤
- [ ] 批量获取策略已执行：先拉取 run 列表 → 过滤 → 再逐个查询详情，未因逐个查询导致速率限制（每 run 30s+）
- [ ] F1 差距归因已按优先级排序（模型实现差异 > 预处理差异），未将差距错误归因于数据预处理
- [ ] 树模型/贝叶斯模型已跳过特征标准化步骤，未对不严重不平衡数据（如 268:500）应用 SMOTE
- [ ] API 请求已设置 `--max-time 30` 超时控制及 `limit=500` 分批参数，未出现请求超时

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

# Openml Benchmark---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[OPEN-001]** 报告分类任务结果时 → 必须同时提供 OpenML 数据库基准对比，明确说明方法框架差异（如 Weka vs sklearn）及排名位置
- **[OPEN-002]** 处理 OpenML API 返回的评估指标时 → 需将字符串类型的 value 转换为浮点数，并过滤掉 accuracy 或 f1 为 0 的无效 runs
- **[OPEN-003]** 面对大量 OpenML run 详情查询需求时 → 采用批量获取列表后过滤再逐个查询详情的策略，以避免因逐个查询导致的速率限制和超时
- **[OPEN-004]** 分析 F1 分数差距且涉及不同框架（如 Weka vs sklearn）时 → 优先归因于模型实现差异（超参、剪枝、分裂规则）而非数据预处理，避免错误归因
- **[OPEN-005]** 处理不平衡数据且不平衡程度不严重（如 268:500）时 → 避免使用 SMOTE 等过采样技术，以防引入噪声抵消潜在收益
- **[OPEN-006]** 使用树模型或贝叶斯模型进行预测时 → 跳过特征标准化步骤，因为此类模型对特征尺度不敏感且标准化可能无益
- **[OPEN-007]** 调用 OpenML API 获取大量数据（如 >500 条）时 → 设置 limit 分批处理（如 limit=500）并配置超时控制（--max-time 30）以防止请求超时

## 示例 · EXAMPLES

1. **输入**：PIDD 数据集上 CatBoost F1=0.7759 待报告 → **操作**：按 OPEN-001/OPEN-004 拉取 OpenML 基准（WEKA RF F1=0.7648、最佳 WEKA 0.8026），归因排序：模型实现差异 > 不做 SMOTE/标准化 > 特征选择不可移植 → **验证**：通过 VERIFICATION 清单第 1/5 项——基准对比表已附、差距归因未指向预处理（OPEN-004 优先级）。
2. **输入**：OpenML 任务 500+ 个 run 的 F1 均值计算 → **操作**：按 OPEN-002/OPEN-003/OPEN-007 以 `limit=500` 分批 + `--max-time 30` 拉取 run 列表，`float()` 转换 value，过滤 accuracy/f1=0 的无效 runs 后再逐个查询详情 → **验证**：50 个有效样本均值 0.6745 与 0.6982 复算一致（数必重算），无速率限制报错。
3. **输入**：PIDD 268:500 轻度不平衡 + GBC 树模型 → **操作**：按 OPEN-005/OPEN-006 跳过 SMOTE 与特征标准化，仅保留 0→NaN 预处理并做消融（ΔF1=+0.018）→ **验证**：对照陷阱第 10 条确认 ZeroReplacer 影响 < 0.007，消融数字可复现（P1 原子可复现性）。