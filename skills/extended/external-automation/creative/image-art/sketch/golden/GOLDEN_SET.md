---
name: sketch
description: sketch 金测集 — UI 设计方向探索（2-3 个交互式 HTML 变体）的可执行测试
---

# 金测集: sketch

> 来源: SKILL.md 核心方法 + 验证清单 + Genes (SKET-001~006)。
> 技能签名: `sketch(description, style) -> sketch_output`；实际产出为
> `sketches/NNN-stance-name/index.html` + `README.md` 的 2-3 个变体。
> 本技能用于"看到设计方向再决定"，产出可抛弃的一次性 HTML 原型，不是可交付代码。
> 每个 case 验证变体数量/立场差异化、HTML 自包含性与交互、视觉验证、对比交付（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：首页设计探索，用户已给全 intake 三要素 | 生成 2-3 个变体且基于不同设计立场（非仅换色）；每个变体单文件自包含 HTML + README + ≥1 交互状态转换；经 browser 视觉验证；交付含对比表+主观推荐（SKET-001/003/004/005/006） |
| case_002 | 错误路径：请求生产级可交付组件（非探索意图） | 正确识别"当不用此技能"边界 → 拒绝并引导至 claude-design / 正式构建，不产出一次性 sketch（SKET-001 反向） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 变体数 ∈ [2,3]；每个变体目录含 `index.html` + `README.md`；HTML 内联 `<style>`、无构建步骤、真实模拟内容（非 Lorem ipsum）、≥1 可见交互状态转换；交付含多维度对比表且给出明确主观推荐
- case_002: 必须拒绝 sketch 路径 —— 错误/引导信息含"请求回声 + 不适用原因（生产级组件）+ 恢复建议（改用 claude-design 或正式构建）"，禁止仅返回通用错误

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002） |
| high | 0.7 | 重要但不致命 |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 变体清单 / 错误结构
- `verification`: 可执行的校验断言列表（变体数 / HTML 自包含 / 交互存在 / README 字段 / 对比表）

期望输出采用**语义等价判定**：
- 变体数量必须 ∈ [2,3]（1 个或 4+ 均判失败）
- 变体间必须基于不同设计立场轴（密度/强调/美学/布局/接地），非仅配色差异
- 错误路径必须同时含 context 与 recovery 两个字段

## 关联

- SKILL.md Genes: SKET-001~006
- SKILL.md 验证清单: 6 项（2-3 变体不同立场 / 单文件自包含 HTML / ≥1 交互转换 / browser 视觉验证 / README / 对比表+推荐）
- 输出目录: `sketches/NNN-stance-name/`（GSD 场景为 `.planning/sketches/`）
