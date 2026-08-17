---
name: citation-appropriateness-verification
description: GOLDEN_SET.md
---

# 金测集: citation-appropriateness-verification

> 引用适当性验证：6 类功能分类（背景/基准/对比/方法/局限/支撑）、DOI 回源验证（SS→Crossref→PubMed 三级回退）、专项报告输出（G5 集成点单独标注）。
> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

## 测试用例

| ID | 描述 | 关键检查 | 权重 |
|----|------|---------|------|
| 1 | 正常路径：功能分类 + DOI 回源验证均成功 | 每篇引文归入 6 类功能之一；DOI 经回源验证与条目一致；专项报告独立输出且 G5 集成点单独标注 | critical |
| 2 | 错误路径：无功能引用 + 已知错误 DOI（Chakravarthy2021Deep 案例） | 无功能引用标记为"失当引用"并附修复建议；错误 DOI 经三级回退发现条目数据不可信，标注"回源修正"/`DOI_INVALID` | critical |
| 3 | 错误路径：SS/Crossref/PubMed 三源全部失效 | 报告完整记录三源回退过程；待验证条目标记"无法验证"；不编造验证结果（凡数必源）；Crossref 查询超 100 字符被截断/拒绝 | high |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 每项验证可执行、可记录、可复现（P1）
- 无功能引用的存在即失当；bib 中 DOI 不可只信条目（CITA-002）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 已知陷阱（对应 Pitfalls 表）

1. bib DOI 本身有误 → 回源验证（L5），不可只信条目
2. 单一 API 失效 → SS→Crossref→PubMed 三级回退
3. Crossref 查询超长 → 截断至 ≤100 字符，禁用 `format=bibtex`
4. 全源失效 → 标记"无法验证"，不编造结果
