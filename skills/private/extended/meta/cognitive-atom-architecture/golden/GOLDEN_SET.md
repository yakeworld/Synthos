# Golden 集合 · cognitive-atom-architecture

> 本技能是认知元技能（meta skill）：将 7+1 东西融合哲学框架按
> **extract → trace → classify → fix → verify** 五步流程，追溯为原子技能
> 中可执行之工程约束。本 Golden 集合是该技能的测试单一真理来源。

## 输入输出（真实契约，源自 SKILL.md / IO_CONTRACT）

- **输入**:
  - `philosophical_framework`: 7+1 东西融合哲学框架 markdown（`references/philosophical-foundations.md`）
  - `target_skill`: 待追溯工程约束的原子技能 `SKILL.md` 路径
- **输出**:
  - `engineering_constraints`: 每条哲学约束 → 目标技能 1 条可执行工程约束
    （含目标文件位置与具体措辞），五步（extract→trace→classify→fix→verify）逐项留痕
- **错误路径**:
  - 7+1 框架缺一维（无定义/无度量法/无原子映射）→ 框架失整，追溯中止
  - `references/` 四件套（philosophical-foundations / synthos-dimension-guide /
    验证 pattern / 融合 pattern）缺件 → "原件无损"不成立，拒绝产出

## 测试用例表

| case_id | 类型 | 描述 | 权重 |
|---------|------|------|------|
| case_001 | 正常 | 完整 7+1 框架 + 真实原子技能（knowledge-extraction）→ 每条哲学约束映射为 1 条可执行工程约束，五步留痕，约束含位置与措辞 | 0.5 |
| case_002 | 错误 | 框架缺"度量法"维度（失整）→ 中止追溯，报告失整维度，不产出约束 | 0.3 |
| case_003 | 错误 | references/ 四件套缺 1 件（融合 pattern 缺失）→ 拒绝产出，报告缺失文件名 | 0.2 |

## 通过标准

1. **结构**: `cases/` 与 `expected/` 中每个 `case_XXX.json` 可被 `json.load` 解析；
   case 与 expected 的 `case_id` 一一对应。
2. **case_001（正常）**:
   - 输出包含 `engineering_constraints` 数组，条数 == 输入框架维度数（7+1 框架中
     被追溯的约束数）；
   - 每条约束含 `philosophical_source`（维度名）、`target_skill_location`
     （文件+小节）、`constraint_text`（可直接写入目标技能的可执行措辞）三字段；
   - 五步留痕：输出含 `steps` 数组，依次为 extract/trace/classify/fix/verify；
   - 约束不重复（同技能内同一位置不出现两条矛盾约束）。
3. **case_002（错误-失整）**:
   - `status == "aborted"`，`reason == "framework_incomplete"`；
   - `missing_dimension` 精确指出失整维度（本例: 度量法缺失）；
   - `engineering_constraints` 为空数组 —— 中止即不产出（宁可无产出，不产畸形约束）。
4. **case_003（错误-缺件）**:
   - `status == "rejected"`，`reason == "reference_set_incomplete"`；
   - `missing_files` 列出缺失的四件套文件名（本例: `east-west-syncretism-pattern.md`）；
   - 无任何 `engineering_constraints` 产出。
5. **可复现性 (P1)**: 同一输入二次运行，输出语义等价（约束条数、位置、失整/缺件
   判定一致）。
6. **诚实性 (P0)**: 期望值中的数字（如"7+1"、"4 件"）必须可在 SKILL.md /
   references/ 中溯源，不可凭空构造。

## 用例文件

- `cases/case_001.json` — 正常：完整框架追溯
- `cases/case_002.json` — 错误：框架失整中止
- `cases/case_003.json` — 错误：四件套缺件拒绝
- `expected/case_001.json` … `expected/case_003.json` — 对应期望与验证方法

> 原则: 数必重算，不可袭旧；去形留神，源一不二。
