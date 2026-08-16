---
name: journal-selection-medical-ai
description: '*详细内容已移至 references/ 目录。*'
signature: 'journal-selection-medical-ai -> clinical-research: synthetic skill for journal selection medical ai'
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
    description: '*详细内容已移至 references/ 目录。*'
    signature: 'journal-selection-medical-ai -> clinical-research: synthetic skill for journal selection medical ai'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 医学 AI 论文选题与类型 — 临床数据类型、方法学特征（详见 references/ 目录）
- **input**: 目标受众与发表定位 — 期刊档次偏好、APC/审稿周期约束
- **output**: 候选期刊推荐列表 — 医学 AI 领域匹配期刊（选择标准见 references/）
- **output**: 选择依据说明 — 各候选期刊与论文选题的匹配度理由

## 原则 (Principles)

- **选题为纲**：期刊之择以论文选题与方法学特征为纲，选题不明则择期无所据。
- **受众与档次相参**：目标受众、期刊档次、APC 与审稿周期须三者相参，偏一即失其宜。
- **匹配必有据**：推荐列表须附各候选与选题之匹配度理由，无理由之推荐不可信。
- **详情下沉参考**：细节沉至 `references/` 目录，主文件只存纲要；纲详而末简，则用之便捷。

*详细内容已移至 references/ 目录。*


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[JOUR-001]** 论文选题与方法学特征明确 → 以选题和方法学特征为纲进行期刊匹配，避免无据择期
- **[JOUR-002]** 需确定发表定位 → 综合考量目标受众、期刊档次、APC 费用及审稿周期，确保三者平衡
- **[JOUR-003]** 生成候选期刊推荐列表 → 必须附带各候选期刊与论文选题的具体匹配度理由，确保推荐可信
- **[JOUR-004]** 处理详细选择标准与数据 → 将细节下沉至 references/ 目录，主文件仅保留纲要以保持便捷
- **[JOUR-005]** 接收输入参数或文件 → 严格校验参数类型、范围、格式及路径有效性，确保输入完整
- **[JOUR-006]** 执行中间步骤或转换计算 → 验证中间过程的正确性，确保数据转换与计算逻辑无误
- **[JOUR-007]** 生成最终输出结果 → 确保输出格式、内容结构、编码及命名符合预期规范
- **[JOUR-008]** 遇到空输入、极大值或异常场景 → 执行边界验证与错误处理，提供包含上下文和恢复建议的明确错误信息

## 验证清单 · VERIFICATION

- [ ] 输入中论文选题与方法学特征已明确（临床数据类型、方法学特征齐备），选题不明则拒绝择期并提示补充（JOUR-001）
- [ ] 目标受众、期刊档次、APC 费用、审稿周期四要素全部纳入，任一要素缺失已在输出中标注为不确定性（JOUR-002）
- [ ] 推荐列表中每个候选期刊都附带与选题的具体匹配度理由，无理由的推荐已被剔除（JOUR-003）
- [ ] 期刊指标通过 OpenAlex API（2yr_mean_citedness）实测获取并对照 IF 层级表（≥10 Q1 / 7–10 Q1 / 5–7 Q1-Q2 …）归类，未凭记忆填写（JOUR-003 + references/openalex-journal-metrics.md）
- [ ] display_name 逐条核对，排除同名歧义（如 Patterns vs Gene Expression Patterns 误匹配）（JOUR-003 + references 已知陷阱）
- [ ] OpenAlex 无数据的期刊（新刊、中文期刊）已走 fallback：用相似论文检索推断期刊质量，并在输出中标注"推断"（JOUR-006 + references Fallback）
- [ ] 输出仅含纲要级内容，详细选择标准与指标数据已下沉至 references/ 目录，主文件无冗余细节（JOUR-004）

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 选题=医学影像 AI 辅助诊断（WDBC 乳腺癌 10x5 分层 CV，HCS-3WT 级联架构），方法学特征=集成学习 + 级联分流；受众=放射学/肿瘤学临床读者；约束=APC ≤ $3000、审稿周期 ≤ 12 周
- **Golden Output**: 候选期刊推荐列表（≥3 条），每条含 `display_name`、2yr_mean_citedness（OpenAlex API 实测，如 Patterns ≈ 18.4 → Q1）、IF 层级归类、与选题的具体匹配度理由；缺失要素（如 APC）在输出中标注为不确定性
- **Golden Error**: 选题/方法学特征缺失（输入仅含期刊档次偏好）→ 拒绝择期并返回错误信息含上下文（"选题与方法学特征未明确，无法执行期刊匹配"）与恢复建议（"请补充临床数据类型、方法学特征、目标受众"）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Journal Selection Medical Ai---





*详细内容已移至 references/ 目录。*

