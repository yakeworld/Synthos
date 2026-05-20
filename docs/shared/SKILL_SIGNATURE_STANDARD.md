# Synthos 技能签名规范 (Skill Signature Standard)

> 版本: 1.0.0 | 吸收自: DSPy (stanfordnlp/dspy, 20K+⭐)
> DSPy 模式: 声明式签名 `'inputs -> outputs: type'` 类型安全 + 模块化

---

## 核心理念

**签名 = 合约。不是文档，是承诺。**

每个技能必须声明其输入/输出的类型和格式。签名不是描述性的（"这个技能做什么"），而是**声明性的**（"这个技能承诺接收什么、产出什么"）。

## 签名格式

### 基础格式

```
input_field1, input_field2 -> output_field1: type, output_field2: type
```

### 类型系统

| 类型 | 含义 | 示例 |
|:-----|:-----|:-----|
| `str` | 字符串 | `query: str` |
| `int` | 整数 | `count: int` |
| `float` | 浮点数 | `threshold: float` |
| `bool` | 布尔 | `verified: bool` |
| `list[T]` | 类型T的列表 | `hypotheses: list[Hypothesis]` |
| `dict[K,V]` | 键值对 | `metadata: dict[str,any]` |
| `T` | 自定义类型 | `Hypothesis` / `Argument` / `Verification` |

### 在 SKILL.md 中的位置

frontmatter 新增 `signature` 字段：

```yaml
signature: "hypotheses: list[Hypothesis], evidence: optional[list[EvidenceNode]] -> verification_results: list[Verification], aggregate_confidence: AggregateConfidence, verdict: str"
```

## L1 格式门要求

从 v2.5 起，L1格式门新增签名检查：

- [ ] `signature` 字段存在于 frontmatter
- [ ] 签名格式符合 `inputs -> outputs: type` 规范
- [ ] 每个字段类型有效（str/int/float/bool/list/dict 或自定义）
- [ ] IO_CONTRACT.md 与 signature 字段一致（如存在）

## 与 IO_CONTRACT.md 的关系

```
signature (frontmatter)    — 简版：声明输入输出类型
     ↓
IO_CONTRACT.md (references) — 详版：字段说明、默认值、边界条件、错误状态
```

签名是**摘要合约**，IO_CONTRACT 是**完整规范**。两者必须一致。

## 当前技能签名

| 技能 | 签名 |
|:-----|:------|
| knowledge-acquisition | `topic: str, depth: int -> knowledge: list[KnowledgeNode], gaps: list[Gap]` |
| knowledge-extraction | `source: str, fields: list[str] -> extracted: dict[str,any]` |
| hypothesis-generation | `gaps: list[Gap], context: dict -> hypotheses: list[Hypothesis]` |
| viewpoint-verification | `hypotheses: list[Hypothesis], arguments: list[Argument] -> verification_results: list[Verification], verdict: str` |
| evolution | `cycle: int, prev_scores: dict -> report: EvolutionReport, next_actions: list[str]` |
| quality-gate | `deliverable: str, quality_matrix: dict -> gate_result: GateResult` |

## 与 DSPy 的差异

| 维度 | DSPy | Synthos |
|:-----|:-----|:---------|
| 运行时 | Python 编译器验证签名 | Agent 读取签名作为约束 |
| 类型安全 | 编译时检查 | Agent 运行时检查 |
| 组合性 | 签名自动推导组合 | 手动 through related_skills |
| 优化 | 优化器修改提示但不改签名 | 签名固定，优化内容 |

Synthos 签名更接近**设计契约**（Design by Contract）——不是给编译器看的，是给 Agent 和 skill 作者看的。
