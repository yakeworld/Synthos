---
name: paper-submission-priority
description: 1. `pdflatex paper.tex` 确认编译干净（0 error, 0 undefined ref）
signature: 'paper-submission-priority -> private: synthetic skill for paper submission
  priority'
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
    description: 1. `pdflatex paper.tex` 确认编译干净（0 error, 0 undefined ref）
    signature: 'paper-submission-priority -> private: synthetic skill for paper submission
      priority'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---


|:--:|
| 147-lens-capsule-biomechanics-ODE | 96 | 20 | 白内障/PCO | R²=0.93/0.98 | 需补充 |
| 113-nystagmus-compensatory-ODE | 96 | 19 | 眼震 0.5% | 未明确 | 需补充 |
| bppv-canalith-relocation-ode | 95 | 13 | BPPV 2.4% | MAPE=7.8%, R²=0.94 | 需补充 |
| corneal-biomechanics-ODE | 96 | 13 | 角膜生物力学 | N/A | 无PDF |

## IO_CONTRACT

- **input**: `papers_dir: path` — `outputs/papers/*` 论文目录集合（各自含 `state.json` 质量分数与 `stage` 字段）
- **input**: `state.json: file` — 顶层 `quality_score` / `D10a` / `Gates_result`（注意：分数在顶层非嵌套字段）
- **output**: `submission_priority_list: table` — 按质量分排序的投稿候选论文清单（含缺项标注：需补充/无PDF）
- **output**: `submission-ready bundle` — 选定论文的最终 PDF + 干净的 `pdflatex` 编译（0 error, 0 undefined ref）+ GitHub 代码仓库 + 署名/邮箱核验

## Pitfalls
- 
- 

## Verification
- 
- 

- **state.json quality_score 在顶层，不在嵌套字段中** — 之前误查嵌套字段导致所有论文 score=-1
- **D10a 可能是数字 100.0 或字符串 "100%"** — 解析时需处理两种格式
- **D10a=0.0 的论文（如 concussion-oculomotor-PINN、ocular-torsion-ODE）引用健康异常** — 需单独检查
- **D8_d10a_scan.orphans_count 和 zombies_count 可能为 0 但 D10a 仍为 0** — 需同时检查
- **Gates_result 格式不一致** — 可能是字符串 "PASS" 或包含 "gates" 列表的字典
- **code/ 目录不存在 ≠ 没有代码** — 代码可能在论文目录其他位置
- **所有 Synthos 论文都需要 GitHub 代码仓库** — G7 可复现性要求，投稿前必须创建

## 投稿准备清单

选定论文后执行：
1. `pdflatex paper.tex` 确认编译干净（0 error, 0 undefined ref）
2. 检查 `state.json` 的 `stage` 字段
3. 创建 GitHub 仓库并推送代码
4. 检查作者署名：Department of Neurology, Wenzhou People's Hospital
5. 检查邮箱：[USER_EMAIL]
6. 生成最终 PDF

## 验证清单 · VERIFICATION

- [ ] state.json 顶层读取：从顶层字段读取 quality_score，未误查嵌套字段导致分数错误
- [ ] D10a 格式兼容：D10a 已兼容数字（100.0）与字符串（"100%"）两种格式，未解析失败
- [ ] 引用异常单独核查：D10a=0 或 Gates_result 格式不一致（字符串/字典）的论文已单独检查 orphans_count 与 zombies_count
- [ ] 代码位置全局搜索：未仅依赖 code/ 目录存在与否，已全局搜索论文目录定位实际代码位置
- [ ] pdflatex 编译干净：已运行 pdflatex 确认 0 error、0 undefined ref 并生成最终 PDF
- [ ] GitHub 仓库已推送：已创建 GitHub 仓库并推送代码，满足 G7 可复现性要求
- [ ] 署名邮箱已核验：署名确认为 "Department of Neurology, Wenzhou People's Hospital" 且邮箱匹配指定用户邮箱

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

- **Golden Input**: `papers_dir=outputs/papers/*`，各论文含顶层 `quality_score`/`D10a`/`Gates_result` 的 `state.json`（PAPE-001/002）
- **Golden Output**: 按质量分降序的 `submission_priority_list`（如 147-lens-capsule=96 → bppv=95），缺项标注「需补充/无PDF」，且 D10a 数字与 "100%" 字符串均解析成功
- **Golden Error**: D10a=0 的论文（如 concussion-oculomotor-PINN）→ 单独核查 orphans/zombies_count 与 Gates_result 格式（字符串/字典），异常标记「需补充」而非混入正常候选（PAPE-003）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

## 示例 · EXAMPLES

- **示例 1**：输入 `papers_dir=outputs/papers/*`（含各论文 `state.json`）→ 按 IO_CONTRACT 从 **顶层**读取 `quality_score`/`D10a`/`Gates_result` 生成投稿候选清单（如 147-lens-capsule-biomechanics-ODE=96 → bppv-canalith-relocation-ode=95）→ 验证：无论文因误查嵌套字段得到 score=-1，且 D10a 数字（100.0）与字符串（"100%"）两种格式均解析成功（PAPE-001/002）。
- **示例 2**：输入 D10a=0 的论文（如 concussion-oculomotor-PINN）→ 按 PAPE-003 单独核查 `D8_d10a_scan.orphans_count` 与 `zombies_count`，同时检查 Gates_result 是字符串 "PASS" 还是字典 → 验证：引用健康异常被单独标记为「需补充」，而非混入正常候选。
- **示例 3**：输入选定论文（如 147-lens-capsule-biomechanics-ODE）→ 按「投稿准备清单」执行 `pdflatex paper.tex`（PAPE-005）、全局搜索代码位置（PAPE-004）、创建 GitHub 仓库并推送（PAPE-006）、核验署名 Wenzhou People's Hospital 与邮箱（PAPE-007）→ 验证：pdflatex 0 error、0 undefined ref 并生成最终 PDF，投稿包满足 G7 可复现性要求。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。


## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[PAPE-001]** 解析 `state.json` 质量分数时 → 必须从顶层字段读取 `quality_score`，避免误查嵌套字段导致分数错误
- **[PAPE-002]** 处理 `D10a` 指标数据时 → 需兼容数字（如 100.0）和字符串（如 "100%"）两种格式，防止解析失败
- **[PAPE-003]** 评估论文引用健康度时 → 若 `D10a` 为 0 或 `Gates_result` 格式不一致（字符串/字典），需单独检查 `orphans_count` 和 `zombies_count` 以确认异常
- **[PAPE-004]** 检查代码可复现性时 → 不能仅依赖 `code/` 目录是否存在，需全局搜索论文目录以定位实际代码位置
- **[PAPE-005]** 执行投稿前最终检查时 → 必须运行 `pdflatex` 确保编译干净（0 error, 0 undefined ref）并生成最终 PDF
- **[PAPE-006]** 准备投稿包时 → 必须创建 GitHub 仓库并推送代码，以满足 G7 可复现性要求
- **[PAPE-007]** 核验作者信息时 → 必须确认署名为 "Department of Neurology, Wenzhou People's Hospital" 且邮箱匹配指定用户邮箱
