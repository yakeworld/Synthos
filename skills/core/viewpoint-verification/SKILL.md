---
name: viewpoint-verification
category: core
signature: "viewpoint-verification -> core: 对假设和论证进行多角度验证（反方观点、证伪条件、鲁棒性），支持 Bayesian 评分、可证伪性检验。"
description: "对假设和论证进行多角度验证（反方观点、证伪条件、鲁棒性），支持 Bayesian 评分、可证伪性检验。"
author: Synthos
license: MIT
version: 2.1.0
entrypoint_type: cognitive
entrypoint_cmd: "从反方观点、证伪条件、鲁棒性三角度验证"
entrypoint_desc: "认知原子"
priority: P1
atom_type: cognitive-atom
allowed-tools: [terminal, read_file, write_file, web_search, session_search]
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Multi-perspective hypothesis and argument verification — falsification, robustness, Bayesian scoring"
    signature: "hypothesis: str, context: dict -> verification_report: dict (score, evidence, counter_evidence, confidence)"
    related_skills: ['hypothesis-generation', 'argument-expression', 'quality-gate']
---

# Viewpoint Verification — 观点验证

> 对假设和论证进行多角度验证：反方观点构造、证伪条件检验、鲁棒性测试、Bayesian 置信度评分。
> 正观反照，虚实相参。立论易，破论难。以反证正，以虚验实。不破不立，不证不立。

## 原理层·文言

> **正观反照，虚实相参。** 正面找证据，反面找反例，虚处查逻辑空隙，实处验数据支撑。
>
> **四验法：**
> - 一验真伪（Popper证伪）：假设是否可证伪？假若假，什么能推翻它？
> - 二验强弱（Bayesian更新）：先验概率→新证据→后验概率
> - 三验鲁棒（敏感性分析）：假设在边界条件下是否仍然成立？
> - 四验全面（多视角枚举）：所有合理的替代解释是否已被排除？
>
> **三条铁律：** 不只看支持性证据（confirmation bias是最大敌人）、不验不可检验的命题（那叫信仰不叫科学）、不产出模糊结论（必须给出明确的 支持/反对/存疑）。

## 方法层·白话

观点验证是认知管道第 6 步（ACQ→EXT→ASC→HYP→ARG→**VER**）。
也是 **质量闸门 G6** 的组成部分：每项论文产出在提交前必须经过 VER 验证。

---

## 触发条件

- HYP 产出新假设 → 验证其可证伪性和初始置信度
- ARG 产出论证 → 验证其逻辑可靠性和证据充分性
- 管线进入质量闸门阶段（G6：观点验证门）
- 用户要求"验证/评估/检验这个假设/论证"

---

## Step 1: Popper 可证伪性检验

对每个假设回答三个问题：

### Q1: 什么证据可以推翻这个假设？

```
假设: "VOR增益随年龄下降，且与跌倒风险正相关"
可推翻条件:
  1. 发现80岁以上老年人VOR增益正常的子群体
  2. 低VOR增益与跌倒风险无相关性（r<0.1, p>0.05）
  3. 去除代偿性扫视影响后，年龄效应消失
  
结果: ✅ 可证伪（有明确的可观测反例条件）
```

### Q2: 这些反例条件在现实中是否可测？

```
条件1: 可测 — 招募80岁以上受试者，VOG测量
条件2: 可测 — 前瞻性队列，随访跌倒频率
条件3: 可测 — 视频头脉冲试验排除扫视

结果: ✅ 所有反例条件可在现有实验中检验
```

### Q3: 如果无法证伪，假设是否应标记为"推测"？

```
不可证伪的假设类型:
  - 同义反复（"模型拟合好是因为它拟合得好"）
  - 不可观测（"潜意识驱动行为"无操作化定义）
  - 保护过强（"除非我的假设错了"）

标记: speculative | tautological | unfalsifiable
```

**输出**：
```json
{
  "hypothesis": "VOR增益随年龄下降且与跌倒风险正相关",
  "falsifiable": true,
  "falsification_conditions": [
    "80岁以上VOR增益正常的子群体存在",
    "低VOR增益与跌倒风险无相关性"
  ],
  "all_testable": true,
  "type": "falsifiable"
}
```

---

## Step 2: Bayesian 置信度更新

对假设的置信度进行定量更新：

### 公式

```
P(H|E) = P(E|H) × P(H) / P(E)

P(H)     = 先验置信度（基于已有文献）
P(E|H)   = 新证据在假设下的可能性
P(E)     = 新证据的总体可能性
P(H|E)   = 后验置信度
```

### 操作步骤

```python
# 1. 设定先验 P(H)
#    基于已有文献共识：VOR-年龄负相关在3篇独立研究中被报道
#    → P(H) = 0.7

# 2. 输入每条证据的似然比 LR = P(E|H) / P(E|¬H)
#    LR > 1 支持假设, LR < 1 反对假设, LR = 1 无信息

# 3. 逐条证据更新（Laplace近似）
#    更新公式: posterior = (LR * prior) / (LR * prior + (1-prior))
```

**证据审核标准**：

| 证据质量 | LR范围 | 示例 |
|:---------|:------:|:-----|
| 高质量RCT/荟萃分析 | 8-15 | 多中心随机对照试验 |
| 队列研究 | 4-8 | 前瞻性队列 |
| 病例对照 | 2-4 | 回顾性病例对照 |
| 专家意见/模型模拟 | 1-2 | 无实验数据 |
| 明确指出反例 | 0.1-0.5 | 高质量RCT否定 |

### 置信度判定标准

| 后验置信度 | 判定 | 行动 |
|:----------:|:----:|:-----|
| ≥ 0.90 | 强支持 | 可作为论文核心主张 |
| 0.70-0.89 | 中等支持 | 需注明限定条件 |
| 0.40-0.69 | 不确定 | 标记为"存疑"，需要更多证据 |
| 0.10-0.39 | 中等反对 | 需重新考虑假设 |
| < 0.10 | 强反对 | 推荐放弃该假设 |

---

## Step 3: 鲁棒性检验

对假设进行边界条件测试：

### 3a: 样本敏感性
- 如果排除某个关键论文，结论是否改变？
- 如果加入发表偏倚修正，结论是否改变？

### 3b: 方法敏感性
- 不同的统计方法是否得到相同结论？
- 不同的测量工具是否得到一致结果？

### 3c: 人群敏感性
- 结论是否在不同亚群中一致？
- 是否有某个特定亚群的效应方向相反（Simpson悖论）？

### 3d: 时间敏感性
- 早期研究 vs 近期研究是否有趋势变化？
- 结论是否依赖于特定时间段的数据？

---

## Step 4: 反方观点枚举

强制列出所有合理的替代解释：

```
假设: "VOR增益随年龄下降"
替代解释1: 测量偏差 — 老年人更难配合VOG测试
替代解释2: 混杂因素 — 老年人的耳石功能也下降
替代解释3: 代偿效应 — 扫视掩盖了VOR功能
替代解释4: 发表偏倚 — 阴性结果未发表
替代解释5: 因果倒置 — 是VOR下降导致少动，而非年龄

对每个替代解释标注:
- 是否可排除（基于现有证据）
- 需要什么额外证据才能排除
- 如果不可排除，应列入论文的Limitations
```

---

## Step 5: 伦理筛查

引用 `references/ETHICS_SCREENING.md` 检查：

- [ ] 假设是否有潜在的伦理风险？
- [ ] 实验设计是否涉及受试者权益问题？
- [ ] 数据使用是否符合知情同意协议？
- [ ] 结果是否有被滥用的风险？

---

## Step 6: 输出交付

```bash
mkdir -p outputs/{session}/
python3 -c "import json; json.dump(verification_report, open('outputs/{session}/verification.json','w'), indent=2, ensure_ascii=False)"
cat > outputs/{session}/verification_report.md << 'EOF'
# 验证报告: {假设名称}

## 可证伪性
✅ 可证伪 — 3个可检验反例条件

## Bayesian 置信度
先验: 0.70 → 后验: 0.85（中等支持）

## 鲁棒性
⚠️ 样本敏感性: 排除1篇后置信度降至0.78
✅ 方法敏感性: 两种统计方法结果一致
⚠️ 人群敏感性: 女性效应更强(r=-0.52 vs 男性r=-0.38)

## 反方观点
5个替代解释，其中3个可排除，2个需列入Limitations

## 最终判定
中等支持 — 可作为论文核心主张，但需注明限定条件
EOF
```

---

## 输入契约

| 字段 | 类型 | 必需 | 默认 | 说明 |
|------|------|:----:|------|------|
| `hypothesis` | str | ✅ | — | 待验证的假设 |
| `evidence` | list[Evidence] | ❌ | — | EXT提供的支持/反对证据 |
| `prior` | float | ❌ | 0.5 | 先验置信度 |
| `mode` | string | ❌ | `full` | `full` 或 `quick`（只做证伪检验） |

## 输出契约

```json
{
  "meta": {
    "source_atom": "HYP-003 | ARG-002",
    "verified_at": "ISO时间戳",
    "mode": "full|quick"
  },
  "falsification": {
    "falsifiable": true,
    "conditions": ["条件1", "条件2"],
    "all_testable": true,
    "type": "falsifiable|speculative|tautological|unfalsifiable"
  },
  "bayesian": {
    "prior": 0.70,
    "posterior": 0.85,
    "evidence_items": [
      {"summary": "...", "lr": 8.0, "quality": "high", "impact": "positive"}
    ],
    "verdict": "strong_support|moderate_support|uncertain|moderate_oppose|strong_oppose"
  },
  "robustness": {
    "sample_sensitive": false,
    "method_sensitive": false,
    "population_sensitive": true,
    "time_sensitive": false,
    "details": "女性效应更强(r=-0.52 vs 男性r=-0.38)"
  },
  "alternatives": [
    {
      "explanation": "替代解释",
      "excludable": true,
      "exclusion_evidence": "需什么证据",
      "in_limitations": false
    }
  ],
  "ethics": {
    "cleared": true,
    "issues": []
  },
  "summary": {
    "verdict": "moderate_support",
    "confidence": 0.85,
    "recommendation": "可作为核心主张，注明人群限定",
    "included_in_limitations": ["替代解释4", "替代解释5"]
  },
  "evidence_chain": [
    {"source_type": "atom_output", "source_ref": "hypothesis-generation", "note": "假设来源"},
    {"source_type": "doi", "source_ref": "10.xxx", "note": "支持证据"},
    {"source_type": "doi", "source_ref": "10.yyy", "note": "反例证据"}
  ]
}
```

---

## 陷阱（Pitfalls）

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **只找支持性证据** — 确认偏误（confirmation bias）是验证中最常见的错误 | 必须主动搜索反例，没有反例就构造替代解释 |
| 2 | **验不可验** — 对不可证伪的命题（如"宇宙中有其他智慧生命"）进行验证 | 先过Popper证伪门：不可证伪的命题标记为 speculative，不进入Bayesian |
| 3 | **置信度主观** — LR值凭感觉给而非基于证据质量 | LR必须基于证据质量分级（RCT=8-15, 队列=4-8, ...） |
| 4 | **忽视发表偏倚** — 只看到已发表的阳性结果 | 用Rosenthal's fail-safe N估计需多少阴性研究才能推翻结论 |
| 5 | **忽视替代解释** — 找到一个支持性证据就停止 | 最低枚举3个合理的替代解释 |
| 6 | **鲁棒性空谈** — 说"结论稳健"但没做敏感性分析 | 敏感性分析必须有具体数字（排除某研究后置信度变化多少） |
| 7 | **结论模糊** — 输出"既有支持也有反对"不作出判定 | 必须给出明确的 verdict：strong_support / moderate_support / uncertain / moderate_oppose / strong_oppose |

---

## 验证清单

- [ ] Popper证伪检验：假设可证伪，且有可观测的反例条件
- [ ] 所有反例条件在现实中可检验
- [ ] Bayesian更新：先验→后验，有证据质量分级
- [ ] 鲁棒性检验：样本/方法/人群/时间四维敏感性
- [ ] 反方观点：≥3个合理的替代解释
- [ ] 伦理筛查已通过
- [ ] 结论明确（5级判定），非模糊
- [ ] 需列入Limitations的内容已标注
- [ ] 已保存：verification.json + verification_report.md

## 边界声明

- 本原子只做**验证**，不做假设生成（那是HYP）
- 不做论证构建（那是ARG）
- 不做关联发现（那是ASC）
- 伦理筛查不代替正式的IRB伦理审查
- Bayesian置信度是学术讨论工具，不是正式的统计推断方法

## 相关文件

- `references/bayesian-hypothesis/` — Bayesian假设检验完整方法
- `references/citation-f1-methodology.md` — 引用F1评分方法
- `references/reproducibility/` — 可复现性检验框架
- `references/review-simulation/` — 模拟同行评审
- `references/ETHICS_SCREENING.md` — 伦理筛查清单
- `references/BOUNDARY.md` — 边界声明
- `references/EVIDENCE_SCHEMA.md` — 证据链结构
- `references/IO_CONTRACT.md` — 输入输出契约
