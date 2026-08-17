---
name: touchdesigner-mcp
description: touchdesigner-mcp 金测集 — TouchDesigner (twozero MCP, port 40404) 节点构建/参数/录制流程的可执行测试
---

# 金测集: touchdesigner-mcp

> 来源: SKILL.md Golden 集合 + 验证清单（VERIFICATION 6 项）+ Genes (TOUC-001~007)。
> 本技能封装 twozero MCP（Streamable HTTP, localhost:40404）的 36 个原生工具，
> 驱动 TouchDesigner 2025.32 的节点构建、参数设置、连线、验证与视频录制。
> 技能产出 = MCP 调用序列（tool + args）+ 验证结果；本 golden 集验证"输入 brief → MCP 调用序列决策"的正确性。
> 每个 case 验证策略决策（工具选型 / 参数名来源 / 调用拆分）的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：构建 noise→level→null 三段生成链 + 截图验证 | 构建前必须对每个 op type 调用 `td_get_par_info` + `td_get_hints`（TOUC-001）；节点创建用 `td_create_operator` 原生工具（TOUC-004）；参数设置用 `td_set_operator_pars`；非商业版显式 `outputresolution='custom'` + 宽高（TOUC-006）；验证阶段 `td_get_errors(recursive=true)` + `td_get_operator_info(detail=full)` + `td_get_screenshot` |
| case_002 | 正常路径：audio-reactive GLSL 录制（ProRes，非商业版） | 信号链遵循 SKILL.md 已验证配方（AudioFileIn→AudioSpectrum(FFT=512, outlength=256, timeslice=ON)→Math(gain=10)→CHOP to TOP(r, rowscropped)→GLSL TOP）；禁用 Lag/Filter CHOP 做 spectrum 平滑；编码用 `prores`（macOS 非商业版，TOUC-007）；录制前 `td_get_perf` 确认 FPS>0 + `td_get_screenshot` 确认非全黑；`rec.par.file` 先于 `rec.par.record=True` 设置（分两次调用） |
| case_003 | 错误路径：tdAttributeError 触发 + 同名节点销毁/创建混合脚本（双失败面） | `tdAttributeError` 触发后必须立即停止并调用 `td_get_operator_info` 检查失败节点（TOUC-002），禁止盲目重试；cleanup+create 必须拆分为独立 MCP 调用（TOUC-005），禁止在同一 `td_execute_python` 中混合（否则 "Invalid OP object"）；错误信息含上下文（哪个节点/哪个参数）+ 恢复建议 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 调用序列必须含 `td_get_par_info`（对 noiseTOP/levelTOP/nullTOP 各一次）+ `td_get_hints` 在构建前；`td_create_operator` × 3；`td_set_operator_pars` 设置分辨率时 `outputresolution='custom'` + 显式宽高（TOUC-006）；验证阶段含 `td_get_errors` + `td_get_operator_info` + `td_get_screenshot`（VERIFICATION 全部 6 项可追溯）
- case_002: 信号链 6 节点顺序精确匹配 SKILL.md 配方；AudioSpectrum 参数 `FFT=512`、`outputmenu='setmanually'`、`outlength=256`、`timeslice=ON` 缺一不可；`videocodec='prores'`（非 H.264/H.265/AV1，TOUC-007）；无 Lag/Filter CHOP；录制前 pre-check（FPS>0 + 非全黑截图）在 record 之前
- case_003: 必须走 Golden Error 路径 —— `tdAttributeError` 后第一步必须是 `td_get_operator_info`（TOUC-002），恢复序列必须将 cleanup 与 create 拆为独立调用（TOUC-005）；错误信息同时含 `context`（失败节点路径 + 触发参数名）与 `recovery`（≥2 条）；禁止在同一 `td_execute_python` 中混合 destroy+create

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: MCP 调用序列（tool + args 序列）或错误结构（context / recovery / call_sequence）
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 工具选型必须与 MCP Tool Quick Reference 一致（原生工具优先，`td_execute_python` 仅用于复杂多步）
- 参数名必须来自 `td_get_par_info`（禁止凭训练数据猜测，TOUC-001）
- 错误路径必须同时含 `context` 与 `recovery` 两个字段
- 非商业版约束（分辨率/编码）为不可协商项（TOUC-006/007）

## 关联

- SKILL.md Genes: TOUC-001~007
- SKILL.md 验证清单: 6 项（MCP 在线 / 构建前 par_info+hints / 销毁创建拆分 / 构建后 errors+info / 录制前 FPS+非黑 / 非商业版分辨率+编码）
- CRITICAL RULES: #1（不猜参数名）/ #2（tdAttributeError 即停）/ #5（hints 先行）
