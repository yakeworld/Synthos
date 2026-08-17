---
name: healthcare-dataset-discovery
description: GOLDEN_SET.md
---

# 金测集: healthcare-dataset-discovery

> 公共医疗数据集发现技能的标准测试用例集。覆盖正常发现路径、已死链失败路径、
> API 参数陷阱路径。每个用例有明确的"通过"标准。

## 技能定位

`healthcare-dataset-discovery` 为医学 AI 研究发现公开可访问的数据集：
已知可用来源（OpenML）、已知死链来源（UCI/GitHub 镜像/HuggingFace）、
以及各 API 的调用陷阱（OpenML list 端点、Crossref `query=` 参数等）。

输入 `medical_domain: str`（如 "cardiovascular disease"），
输出 `dataset_results: list[Dataset]`，每个 Dataset 含
`name / source / url / description / access_type / relevance`。

## 测试用例

| ID | 文件 | 描述 | 关键检查 | 权重 |
|----|------|------|---------|------|
| case_001 | `cases/case_001.json` | OpenML 心血管数据集发现（正常路径） | 命中 DID=45547，规模 70000，13 特征；列表接口与详情接口结构区分 | critical |
| case_002 | `cases/case_002.json` | UCI stroke 经典数据集已死链（失败路径） | 标记 UNAVAILABLE，每条结论均有 404/认证失败证据；建议转 OpenML | critical |
| case_003 | `cases/case_003.json` | Crossref/PubMed 文献检索参数陷阱 | 用 `query=` + `quote_plus()`，非 `search=`；无空结果或 422 | high |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 每个"不可用"结论必须有具体 404/认证失败证据，禁止凭空的"存在"声明（P0 证据可溯性）
- 输出含来源与访问路径，推荐数据集与查询主题匹配

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 与 SKILL.md 验证清单的映射

- 数据集发现已确认来源（公开机构/数据库） → case_001
- 数据集信息含规模/格式/访问方式 → case_001
- 推荐数据集与查询主题匹配 → case_001
- 输出含来源与访问路径 → case_001 / case_002
- 每个"不可用"结论有具体证据 → case_002
- 查询参数解析正确，无空结果或 422 → case_003
