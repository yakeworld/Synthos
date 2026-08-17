# Golden 集合 · akne-knowledge-manager

> 本技能是 Synthos-AKNE Bridge 的知识管理子技能：对 AKNE 知识库执行
> **内容级审计**（矛盾、版本簇、研究空白、假设）与 **KnowledgeGraph/QueryEngine
> 查询**（实体解析、关系遍历）。原则优先级：**准确 > 证据 > 可复现**。
>
> 真实 IO（源自 SKILL.md 各小节）:
> - **输入**: 知识库源文件集（如 `BPPV拟真参数设置.md`）或 QueryEngine 查询请求
>   （实体名 / 关系遍历）
> - **输出**: 审计结论（每条矛盾标注 文件路径 + 声明原文 + 正确值来源）或
>   查询结果（实体解析 / 关系列表）
> - **错误路径**: 空实体名 / 未知实体 → 明确错误信息 + 恢复指引，禁止静默空结果

## 测试用例表

| case_id | 类型 | 描述 | 权重 |
|---------|------|------|------|
| case_001 | 正常 | 内容级审计：提取 BPPV 知识库各文件物理参数声明并交叉比对，发现"耳石半径 0.5~15nm"与碳酸钙晶体实际 5-30 μm 相差 1000 倍的致命级矛盾 | 0.4 |
| case_002 | 正常 | QueryEngine 正常查询：`qe.resolve_entity("BPPV")` 与 `qe.get_relations("bppv")` 精确/模糊匹配命中 | 0.3 |
| case_003 | 错误 | 边界查询：空实体名与未知实体（`resolve_entity("")` / `resolve_entity("杨晓凯")`）→ 明确错误 + 恢复指引，非静默空结果 | 0.3 |

## 通过标准

1. **结构**: `cases/` 与 `expected/` 中每个 `case_XXX.json` 可被 `json.load` 解析；
   case 与 expected 的 `case_id` 一一对应。
2. **case_001（审计-正常）**:
   - 每条矛盾含四字段: `file_path`（源文件路径）、`declared_value`（声明原文）、
     `correct_value_source`（正确值来源）、`severity`（级别）；
   - 耳石半径矛盾被检出且 `severity == "fatal"`，量级差标注为 1000 倍
     （0.5~15 nm vs 5-30 μm）；
   - 结论可复算：从声明原文到量级差的手算路径可复现（AKNE-003 可复现性）。
3. **case_002（查询-正常）**:
   - `resolve_entity("BPPV")` 返回 `"bppv"`（精确/模糊匹配命中，
     见 references/api-reference.md 实测）；
   - `get_relations("bppv")` 返回的关系列表非空，每条关系含
     `type` 与 `target` 字段。
4. **case_003（查询-错误边界）**:
   - 空实体名: 返回 `error`（非空、非异常栈裸抛），含 `recovery_hint`
     （建议的查询入口或参数修正）；
   - 未知实体（"杨晓凯"）: 实测 `resolve_entity` 返回 None → 技能层必须将其
     转为明确错误信息 + 恢复指引（AKNE-007），不得静默返回空；
   - 错误输出含上下文（查询实体名、失败阶段）与恢复指引（AKNE-006）。
5. **诚实性 (P0/AKNE-001)**: 所有数值（1000 倍、5-30 μm）可溯源到
   references/ 或源文件，无编造数据。
6. **可复现 (AKNE-003)**: 同一输入二次运行，审计结论条数、矛盾判定、
   查询结果语义一致。

## 用例文件

- `cases/case_001.json` — 正常：内容级审计（单位矛盾检出）
- `cases/case_002.json` — 正常：QueryEngine 实体解析与关系查询
- `cases/case_003.json` — 错误：空/未知实体边界查询
- `expected/case_001.json` … `expected/case_003.json` — 对应期望与验证方法

> 原则优先级: 准确 > 证据 > 可复现。违反任何原则的输出视为失败。
