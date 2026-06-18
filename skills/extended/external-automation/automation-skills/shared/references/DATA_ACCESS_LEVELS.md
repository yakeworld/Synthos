# 数据访问级别（Data Access Levels）

> [ARS吸收] 自 Academic Research Skills v3.7 — `shared/ground_truth_isolation_pattern.md`
> 对应原则：P6（数据访问分级）

## 三层模型

Synthos 原子按 **数据敏感度** 分为三级，注入后保护验证过程的完整性：

| 级别 | 层 | 含义 | 适用原子 |
|------|-----|------|---------|
| `raw` | Layer 1 | 消费未验证的外部源，假设对抗性/幻觉输入 | knowledge-acquisition |
| `redacted` | Layer 1→2 | 在脱敏/结构化材料上操作，不引入新原始数据 | knowledge-extraction, association-discovery |
| `verified_only` | Layer 2 | 仅在上游完整性验证后运行，执行验证/评价/写证任务 | hypothesis-generation, argument-expression, viewpoint-verification |

## 隔离原则

1. **Layer 1 (raw) 原子**只能读取外部API返回的原始数据
   - 不能读取下游原子的验证结论
   - 输出必须标记 `data_access: raw`

2. **Layer 2 (verified_only) 原子**的评分标准/金标准**绝不与Layer 1共存于同一上下文窗口**
   - 验证原子执行前，必须先确认上游已经过完整性门控
   - 评分标准在独立的 prompt 区域内声明

3. **Layer 3 (ground truth)** 是最终的防火墙
   - 金标准案例、预期输出、评分细则 = Layer 3
   - **永不**与Layer 1或Layer 2的输出生成共存

## 原子级别声明

每个原子的 SKILL.md frontmatter 必须包含：
```
synthos_data_access_level: "raw" | "redacted" | "verified_only"
```

| 原子 | 当前级别 | 理由 |
|------|---------|------|
| knowledge-acquisition | `raw` | 直接消费外部API返回数据 |
| knowledge-extraction | `redacted` | 在结构化论文元数据上操作 |
| association-discovery | `redacted` | 在提取的知识上做关联 |
| hypothesis-generation | `verified_only` | 在已验证文献基础上生成假设 |
| argument-expression | `verified_only` | 在已验证假设基础上写论证 |
| viewpoint-verification | `verified_only` | 假设和论证均须经完整性验证 |
| gap-discovery | `redacted` | 在提取知识中发现空白 |

## 完整性门控

完整性验证（借鉴ARS Stage 2.5/4.5模式）是实际执行点：

1. **上游门控**：每个原子执行前检查其输入是否来自同层级或更高层级的原子
2. **跨层流禁止**：`verified_only` 原子不能直接接收 `raw` 原子的输出。必须经过 `redacted` 原子的转换。
3. **异常处理**：如果数据访问级别不匹配 → 阻止执行 → 记录到 `pipeline_trace.json` → 向用户报告

## 参考

- ARS Academic Research Skills v3.7: `shared/ground_truth_isolation_pattern.md`
- Synthos 宪法 P6: 数据访问分级
