---
name: paper-submission-priority
related_skills: [paper-pipeline, sci-paper-quality-review, quality-gate, paper-improvement]
description: "论文投稿优先级评估 — 从管线中筛选最高质量论文，按临床价值、创新性、G1-G7闸门、D10a完整性、代码可用性排序，推荐最优投稿候选。"
version: 1.0.0
allowed-tools: [terminal, file, execute_code]
signature: "paper-submission-priority -> processed_result"
---

# 论文投稿优先级评估

从 Synthos 论文管线中筛选可投稿的高质量论文，按多维度排序推荐最优候选。

## 快速扫描脚本

使用 `scripts/scan_submission_candidates.py` 一键扫描管线，输出所有可投稿候选：
```bash
python3 scripts/scan_submission_candidates.py
```

输出格式：目录名、质量分、D8、D10a、白空间状态、stage。

## IO_CONTRACT

- **input**: 无（自动扫描 `/media/yakeworld/sda2/Synthos/outputs/papers/`）
- **output**: 排序后的论文列表，含质量分、D10a、Gates、临床价值、代码可用性

## 评估流程（5步）

### Step 1: 全量扫描 state.json

遍历所有论文目录，提取以下字段：
- `quality_score`（顶层，非嵌套）
- `status`（排除 HARD_FAIL/FAIL）
- `gates_result`（需 G1-G7 全部 PASS）
- `d8_d10a_scan.d10a`（需 >= 99%）
- `d8_d10a_scan.orphans_count` 和 `zombies_count`（需为 0）
- `white_space.status`（ABSOLUTE_WHITE 优先）

### Step 2: 验证 PDF 和代码

- 检查 `{论文目录}/{论文名}.pdf` 是否存在
- 检查 `{论文目录}/code/` 是否存在（G7 可复现性要求）
- 缺失代码时标记"需要 GitHub 仓库"

### Step 3: 临床价值排序

按以下维度加权评分：
1. **临床影响**（30分）：疾病患病率、手术量、市场规模
   - 白内障/PCO: 24M+ 手术/年 → 高分
   - BPPV: 2.4% 患病率, $3B+ 市场 → 高分
   - 眩晕/前庭: 门诊常见 → 中高分
   - 罕见病/基础研究: → 中分

2. **创新性**（25分）：
   - G6 PubMed=0, OpenAlex=0（白空间验证）→ 满分
   - G2 gap claim 得到 quality check 支持 → 满分
   - "first computational model" 类声明 → 高分

3. **性能指标**（25分）：
   - 有明确 metrics（MAPE, R², AUC, MAE, RMSE）→ 高分
   - MAPE < 10%, R² > 0.90, AUC > 0.85 → 达标
   - 有消融实验 → 加分
   - metrics 未明确指定 → 低分

4. **引用完整性**（20分）：
   - D8 >= 15 → 高分
   - D10a = 100%, 0 orphans, 0 zombies → 满分
   - DOI coverage 完整 → 加分

### Step 4: 输出候选列表

按综合得分降序排列，输出：
- 论文目录名
- 质量分、D8、D10a
- 标题
- 临床价值摘要
- G6 白空间状态
- 性能指标
- 代码可用性状态
- G1-G7 闸门状态

### Step 5: 用户选择后进入投稿准备

选定论文后，检查：
1. PDF 可编译干净（pdflatex 无 error）
2. state.json 中 stage 为 publication_complete 或可推进
3. 代码仓库是否已创建（GitHub）
4. 作者信息、机构署名是否正确
5. 邮箱 yakeworld@wmu.edu.cn 是否正确

## 常见候选论文（2026-06-19 诊断结果）

以下论文通过全部 G1-G7 闸门，D10a=100%，有 PDF：

| 论文 | 质量 | D8 | 临床 | 指标 | 代码 |
|:---|:--:|:-:|:---|:---|:--:|
| 147-lens-capsule-biomechanics-ODE | 96 | 20 | 白内障/PCO | R²=0.93/0.98 | 需补充 |
| 113-nystagmus-compensatory-ODE | 96 | 19 | 眼震 0.5% | 未明确 | 需补充 |
| bppv-canalith-relocation-ode | 95 | 13 | BPPV 2.4% | MAPE=7.8%, R²=0.94 | 需补充 |
| corneal-biomechanics-ODE | 96 | 13 | 角膜生物力学 | N/A | 无PDF |

## Pitfalls

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
5. 检查邮箱：yakeworld@wmu.edu.cn
6. 生成最终 PDF

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



# Paper Submission Priority

