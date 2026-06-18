# 伦理影响评估 — Ethics Screening Reference

> 扩展层参考文档，非宪法级约束。
> VER 原子在执行医学/脑机接口/人类受试者/基因编辑/神经增强等领域的验证时，自动附加此检查。

## 触发领域

- 医学诊断/治疗/预后研究
- 脑机接口 (BCI)
- 人类受试者临床研究
- 基因编辑/基因治疗
- 神经增强/认知增强
- 精神类药物/神经调控
- 儿童/弱势群体研究
- 双用途技术（可同时用于好和坏的目的）

## 评估维度

### D1: 双刃剑评估
| 等级 | 描述 | 行动 |
|:-----|:-----|:-----|
| low | 纯基础研究，无明显滥用方向 | 仅记录 |
| medium | 存在潜在误用方向，但可控 | 添加边界声明建议 |
| high | 明显的双用途性质 | 强制风险标注 + 建议伦理声明 |
| critical | 直接涉及人类安全/隐私侵犯 | 标记为"需伦理委员会审查" |

### D2: 受试者保护
- 涉及人群类型（成人/儿童/患者/弱势群体）
- 是否需要 IRB/伦理委员会批准
- 知情同意流程
- 数据隐私保护

### D3: 社会影响评估
- 误用场景列举（至少1个具体情景）
- 影响范围（个人/机构/社会层面）
- 可逆性（如果误用，能否纠正？）

## 输出格式

```yaml
ethics_screening:
  domain: str
  triggered: bool          # 是否触发检查
  risk_level: str         # low/medium/high/critical
  risk_level_justification: str
  dual_use:
    positive: str
    risk: str
    risk_level: str
  subject_protection:
    population: str
    needs_irb: bool
    consent_required: bool
  social_impact:
    misuse_scenarios: list[str]
    impact_scope: str
  recommendation: str      # 可操作建议
  generated_at: timestamp
```
