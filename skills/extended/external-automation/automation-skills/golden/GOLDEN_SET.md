name: automation-skills
description: automation-skills 金测集 — 父级路由 + Batch Quality Score Extraction 的可执行测试
---

# 金测集: automation-skills

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (AUTO-001~006)。
> 本技能是 external-automation 父级聚合入口：既负责把请求路由到子目录（autonomous-ai-agents / github / maintenance / media / metacognition / productivity / quality / red-teaming / shared / smart-home / social-media / yuanbao），
> 又内联承载 "Batch Quality Score Extraction"（批量解析 step_quality_check.md 的 quality_score 并写入 state.json）。
> 每个 case 验证路由决策或批量分数提取的正确性（P1 可复现性、P0 凡数必源）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由到子目录（quality 域批量分数提取） | route=child:quality；执行 Batch Quality Score Extraction 路径；quality_score 归一到 0-100 且可被闸门读取 |
| case_002 | 正常路由到子目录（生产力工具） | route=child:productivity；父级不硬编码执行，转交子目录 |
| case_003 | 未知子技能/子目录（错误路径） | 返回结构化错误：含上下文（请求、已扫描子目录清单）+ 恢复建议；不崩溃、不暴露内部状态 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 必须路由到 quality 域并按格式映射表归一分数（score/max_score、total_score、overall_score、detailed_scores、纯文本→95），
  且已有 quality_score 的论文被跳过（AUTO-006），LaTeX 反斜杠清理后 json.loads 成功（AUTO-001）
- case_002: 必须路由到 productivity 子目录而非父级直接执行；request/context 完整转交
- case_003: 必须拒绝并返回 Golden Error 路径 —— 错误信息含"哪个请求、哪些已知子目录、建议尝试哪个"三段上下文，禁止仅返回通用错误

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 路由结果 / 分数提取结果 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 路由目标子目录名必须精确匹配
- 分数值在 ±0.5 容差内匹配（浮点归一化）
- 错误路径必须同时含 context 与 recovery 两个字段

## 关联

- SKILL.md Genes: AUTO-001~006
- SKILL.md 验证清单: 6 项（os.walk 定位 / LaTeX 清理 / 格式映射 / 跳过已处理 / 批次拆分 / state.json 更新）
- 子目录: autonomous-ai-agents, github, maintenance, media, metacognition, productivity, quality, red-teaming, shared, smart-home, social-media, yuanbao
