---
name: citation-verification
description: citation-verification 金测集 — 引用三验（L1存在/L2得当/L3全面）的可执行测试
---

# 金测集: citation-verification

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (CITA-001~007)。
> 本技能是引用三位一体验证管线（atom_type: quality, P0），输入 `paper_dir`，输出 phase1/phase2/phase3/overall 四阶段验证报告 + 修复后的 bib。
> 每个 case 验证一个关键决策分支的正确性（P1 可复现性）：假DOI判定、DOI篡改修复、@misc数据集替换、D10a孤儿回归、Phase 2语义比对、Phase 3遗漏分类、输入阻断。

## 管线阶段（被测目标）

| 阶段 | 名称 | 关键检查 | 关联 Genes |
|------|------|---------|-----------|
| Phase 1 | 是否存在 | DOI验真、假DOI检测、替代、PDF Triage | CITA-001/002/003/007 |
| Phase 2 | 是否得当 | 读PDF全文、语义比对、错误检测 | CITA-004/005 |
| Phase 3 | 是否全面 | 独立检索、遗漏检测、补充建议 | CITA-006 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | Phase 1 假DOI判定：DOI 404 + Crossref 404 + SS 无匹配 | 判定 `FABRICATED`，进入替代文献决策树（删/换），不尝试修复DOI（CITA-001） |
| case_002 | Phase 1 DOI篡改：DOI 404 但 SS 搜到不同DOI | 判定 `DOI_TAMPERED`，修复DOI+元数据以匹配真实文献（CITA-002） |
| case_003 | Phase 1 修改bib后 D10a 回归 | 删除假DOI条目后 tex 中 `\cite{deleted_key}` 变孤儿，必须执行 `comm -23` 回归检查并报告孤儿键（CITA-007） |
| case_004 | Phase 2 语义比对：PDF 存在但作者与 bib 不符 | 提取语境+读PDF，标题/作者/年份/内容比对发现作者不匹配 → 判定 `INAPPROPRIATE`（CITA-004/005） |
| case_005 | Phase 3 全面性：CRISP-DM 论文遗漏 2021 综述 | 独立检索对比引用列表，识别遗漏并分类为 `critical`/`suggested`（CITA-006） |
| case_006 | 输入阻断（错误路径）：paper_dir 缺失 06-references | 输入校验失败 → 结构化错误，阻断并说明缺什么，不产生半成品报告 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 三验铁律必须同时满足（doi 404 + Crossref 404 + SS 无匹配）才能判 FABRICATED；单条404不得直接判虚构
- case_002: 必须区分"篡改"(SS找到不同DOI→修复)与"虚构"(SS无匹配→替代)，不得混用处置
- case_003: 修改bib后必须触发D10a回归，孤儿键列表非空时报告且overall不得判PASS
- case_004: Phase 2 必须基于PDF全文阅读而非仅API标题匹配；作者不匹配判 INAPPROPRIATE
- case_005: 遗漏须按阈值分类（被引>1000+主题>80%→critical；>100+>60%→suggested），不得一律suggested
- case_006: 必须阻断并返回结构化错误（缺 01-manuscript 还是 06-references），禁止静默继续

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003 / case_006） |
| high | 0.7 | 重要但不致命（case_002 / case_004 / case_005） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 该阶段的判定/动作（verdict、action、orphan_keys 等）
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- verdict 取值必须来自受控集（FABRICATED / DOI_TAMPERED / INAPPROPRIATE / MISSING / ORPHANED / OK）
- 假DOI三验必须三条全真才成立（CITA-001）
- 错误路径必须含 `error.context`（缺什么）+ `error.recovery`（≥1条恢复建议）

## 关联

- SKILL.md Genes: CITA-001~007
- SKILL.md 验证清单: 5 项（L1存在/L2得当/L3全面/报告四阶段/输入完整）
- quality-gate G5 三层检查对应 Phase 1/2/3
