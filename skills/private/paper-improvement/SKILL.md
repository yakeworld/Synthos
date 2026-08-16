---
name: paper-improvement
description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
signature: 'paper-improvement -> private: synthetic skill for paper improvement'
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
    description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
    signature: 'paper-improvement -> private: synthetic skill for paper improvement'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| `references/benchmark-alignment-checklist.md` | 实验模型清单一致性校验清单 |
| `references/hcs3wt-fake-doi-replacement-2026-06-25.md` | HCS-3WT实战：假DOI替换记录 |
| `references/hcs3wt-p0-remediation-full-cycle-2026-06-29.md` | HCS-3WT实战：质量检查→P0修复完整闭环（数值伪造修复模式选择、引用批量修复、数据集统一） |
| `references/pima-catboost-claim-verification-2026-06-25.md` | PIMA实战：CatBoost声称验证 |
| `references/latex-citation-replacement-fallback.md` | LaTeX引用替换回退方案（sed）|
| `references/latex-compilation-workflow.md` | LaTeX编译工作流详细说明 |
| `references/standard-audit-report-templates.md` | 四份标准审计报告模板和生成规范 |
| `BOUNDARY.md` | 技能边界声明 |
| `EVIDENCE_SCHEMA.md` | 技术证据架构 |
| `IO_CONTRACT.md` | 输入输出规范 |

## 六、版本历史

- **v1.0.0** (2026-03): 初始版本
- **v1.1.0** (2026-06): 新增虚假引用替换、SHAP验证、OpenML基准对比
- **v1.2.0** (2026-06): 重构为思想/原则/方法/规则结构

## 验证清单 · VERIFICATION

- [ ] 输入参数/文件/路径完整性校验通过（论文目录、.tex、PDF 均存在），无效输入被阻断未进入改进流程（PAPE-001）
- [ ] 虚假引用/假 DOI 全部完成替换并生成替换日志，日志中每条替换可回溯到原 DOI 与新 DOI（PAPE-002）
- [ ] 实验模型清单与基准（helix_benchmark vs notebook all_estimators）完成一致性对齐，偏差项（如 LightGBM/CatBoost 外部库、CV 成对分类器）逐项列出并处置（PAPE-003）
- [ ] P0 级缺陷（数值伪造等）走完整修复闭环：模式选择 → 引用批量修复 → 数据集统一，闭环各步骤有产物记录（PAPE-004）
- [ ] LaTeX 引用替换若失败，已启用 sed 回退方案并验证回退后引用解析成功（PAPE-005）
- [ ] 改进完成后 pdflatex 编译干净（0 error、0 undefined reference），数值声称可回源验证（PAPE-006）
- [ ] 按标准模板（四份审计报告）生成审计报告，验证项可执行、可记录、可复现（PAPE-006）

## Golden 集合 · GOLDEN SET

- **Golden Input**: 一个完整论文目录——含 .tex、PDF、references/，且检出 3 条假 DOI、实验模型清单与 helix_benchmark 存在偏差项（覆盖正常改进路径）
- **Golden Output**: 改进后 pdflatex 编译 0 error / 0 undefined reference，假 DOI 替换日志逐条可回溯（原 DOI→新 DOI），偏差项（LightGBM/CatBoost 等）逐项列出并处置，四份标准审计报告齐备（精确匹配 VERIFICATION 七条）
- **Golden Error**: 输入不完整（缺 .tex 或 PDF）→ 按 PAPE-001 立即阻断不进入改进流程；LaTeX 替换失败 → 按 PAPE-005 启用 sed 回退并验证回退后引用解析成功（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Paper Improvement---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[PAPE-001]** 输入参数/文件/路径不完整或无效 → 立即执行输入验证并阻断后续流程
- **[PAPE-002]** 发现虚假引用或DOI → 执行批量替换与修复，并记录替换日志
- **[PAPE-003]** 实验模型清单与基准不一致 → 依据一致性校验清单进行对齐检查
- **[PAPE-004]** 遇到P0级质量缺陷（如数值伪造） → 启动完整修复闭环，包括模式选择、引用修复及数据集统一
- **[PAPE-005]** LaTeX引用替换失败 → 启用sed脚本作为回退方案
- **[PAPE-006]** 改进过程结束 → 确保所有验证步骤可执行、可记录且可复现，并生成标准审计报告

## 示例 · EXAMPLES

1. **输入**: 给定论文目录（含 .tex、PDF、references/）。**操作**: 按 PAPE-001 先做输入完整性校验（目录/.tex/PDF 均存在）→ 通过才进入改进流程；缺件则立即阻断。**验证**: VERIFICATION 第一条打勾，阻断或放行决定记录在审计报告（PAPE-006）。
2. **输入**: 检出 3 条假 DOI（对照 hcs3wt-fake-doi-replacement 记录）。**操作**: 按 PAPE-002 批量替换为真实 DOI 并生成替换日志，日志逐条记录原 DOI→新 DOI；LaTeX 替换失败处按 PAPE-005 用 sed 回退。**验证**: 日志每条可回溯（PAPE-002），回退后引用解析成功（VERIFICATION 第五条）。
3. **输入**: P0 级数值伪造缺陷。**操作**: 按 PAPE-004 走完整闭环：模式选择 → 引用批量修复 → 数据集统一（参照 hcs3wt-p0-remediation-full-cycle 记录），每步留产物。**验证**: 闭环各步骤产物齐备，最后 pdflatex 编译 0 error、0 undefined reference，数值声称回源验证（VERIFICATION 第六/七条）。