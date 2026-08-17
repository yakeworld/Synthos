# GOLDEN_SET.md — figure-generation

> 对应原则：P1（认知原子语义可复现：同一输入 → 等价路由决策通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 父级聚合技能 / 子技能路由入口

## 设计依据

本技能是作图体系的**路由入口**（parent aggregator），核心职责是将用户请求分发到正确的工作模式（A-J）或子技能。金标准验证目标：

1. **路由正确性**：给定用户请求，能否匹配到正确的模式/子技能
2. **错误处理**：无法匹配时的降级行为是否合理（不崩溃、给出可操作建议）
3. **契约完整性**：路由输出是否包含必要的执行契约信息（模式、工具、出口格式）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路由 | 3/10 种模式 | A（数据图）、B（架构图）、I（3D子技能） |
| 错误路径 | 2 种 | 未知子技能请求、空请求 |
| 子技能委托 | 1 种 | 3d-curve-fitting-figures |
| 契约完整性 | 所有 case | 检查路由输出字段完备性 |

## 测试用例 (cases/)

### case_001: 正常路由 — 科学数据图（模式A）
- **输入**: 用户请求"画一个ROC曲线对比3个模型的AUC"，含数据描述
- **期望**: 路由到模式A，工具=matplotlib，出口=PNG(300DPI)+PDF+SVG，QA规则包含双编码检查

### case_002: 正常路由 — 架构/流程图（模式B）
- **输入**: 用户请求"画一个系统架构图，包含数据层、计算层、展示层"
- **期望**: 路由到模式B，工具=matplotlib patches，出口=PNG+PDF+SVG，QA规则包含箭头终点AABB检查

### case_003: 正常路由 — 子技能委托（模式I / 3d-curve-fitting-figures）
- **输入**: 用户请求"将瞳孔追踪中的椭圆逆投影为3D空间圆"
- **期望**: 路由到子技能 3d-curve-fitting-figures，非父级直接处理

### case_004: 错误路径 — 未知子技能/模式
- **输入**: 用户请求"用 Blender 渲染一个 3D 动画"（不属于任何已知模式）
- **期望**: 不崩溃，返回错误/降级响应，包含可用模式列表和恢复建议

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- `routed_mode` 必须精确匹配
- `tool` 字段必须包含期望工具名
- `output_formats` 必须包含所有必需格式
- `qa_checks` 必须包含对应模式的关键检查项
- 错误路径：`error` 非空，`suggestions` 列表非空，`routed_mode` 为 null 或 "unmatched"

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（路由正确性、错误处理不崩溃）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 路由正确性 / 错误处理不崩溃 |
| high | 0.7 | 工具匹配、出口格式完整 |
| medium | 0.4 | QA检查项覆盖、建议列表完备 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"
```
