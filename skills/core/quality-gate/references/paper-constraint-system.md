# 论文约束系统检查参考

## 来源

PIMA 论文审计（2026-06-24）发现质量检查漏了两个问题：
1. 同一实体在不同表中数值矛盾且无解释
2. 声明有数据但缺机制解释

根本原因不是缺少"特定检查项"，而是缺乏**论文作为一个约束系统**的审计视角。

## 原理

一篇论文 = 多个组件（Tables/Text/Figures/Code/Bib）组成的约束系统。

组件孤立检查（数值→JSON匹配、引用→PDF匹配）是 L0.5 层的职责。
组件**关系**检查（跨表一致性、声明-证据对齐等）是 G6 层的职责。

## 通用检查流程

```python
# 对任意论文执行约束系统检查
def check_paper_constraints(tex_path, json_dir, code_dir):
    report = {
        'same_entity_violations': [],
        'claim_evidence_gaps': [],
        'comparison_misalignments': [],
        'narrative_proportion_issues': []
    }
    
    # 1. 同实体跨位约束
    entities = extract_entity_value_pairs(tex_path)
    for (entity, attr), occurences in entities.items():
        if len(occurences) >= 2:
            vals = [o[0] for o in occurences]
            if max(vals) - min(vals) > 0.05:
                report['same_entity_violations'].append({
                    'entity': entity,
                    'attribute': attr,
                    'values': occurences,
                    'max_diff': max(vals) - min(vals)
                })
    
    # 2. 声明-证据对齐约束
    claims = extract_claims(tex_path)
    for claim in claims:
        has_evidence = find_evidence(claim['text'], json_dir, code_dir)
        if not has_evidence:
            report['claim_evidence_gaps'].append(claim)
    
    # 3. 比较-基准对齐约束
    comparisons = extract_comparisons(tex_path)
    for comp in comparisons:
        if not has_protocol_note(comp):
            report['comparison_misalignments'].append(comp)
    
    # 4. 叙事-数据比例约束
    tones = extract_tone_sentences(tex_path)
    for tone in tones:
        ratio = extract_nearby_numbers(tone)
        if disproportional(tone['word'], ratio):
            report['narrative_proportion_issues'].append(tone)
    
    return report
```

## 约束违反的通用修复模板

| 约束类型 | 修复模板 |
|:---------|:---------|
| 同实体跨位 | "Note: F1 values in Table X (0.930) and Table Y (0.698) are from different experimental setups (LR 5x2 CV vs CatBoost 10-fold CV, respectively) and are not directly comparable." |
| 声明-证据对齐 | "As shown in Table Z, the proposed method achieves [value] on [metric], which [supports/confirms] the claim that [claim]." |
| 比较-基准对齐 | "While our Helix F1 of [value] is [lower/higher] than the OpenML max of [value], this comparison is conservative because our protocol enforces strict within-fold preprocessing that most OpenML runs do not apply." |
| 叙事-数据比例 | 替换语气词："catastrophic collapse" → "notable decrease of 6.2%"; "universal inflation" → "selective metric distortion" |

## 与现有质量门的集成

- **L0.5 数据诚实门**: 组件内部检查（单个数值→JSON）
- **G6 逻辑完整门**: 组件之间检查（加此约束系统框架）
- **三要素评价**: 跨组件检查（科学性/创新性/可行性综合评价）
