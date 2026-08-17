---
name: dogfood
description: dogfood 金测集 — Web 应用浏览器自测（dogfood）可执行测试
---

# 金测集: dogfood

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (DOGF-001~007)。
> 本技能为机械原子（atom_type: mechanical），对目标 Web 应用做真实浏览器自测，
> 输入/输出契约：
> `target_app_url: str, test_scenarios: list[str] -> browser_findings: list, screenshot_evidence: MEDIA:<path>`。
> 每个 case 验证"以己器测己"（真实用例覆盖）、"静默即警"（console 检查）、
> "所见必证"（带标注截图证据）三原则，期望输出采用语义等价判定（findings 结构 + MEDIA 证据 + console 检查校验）。

## 核心能力

| # | 能力 | 关键约束 |
|---|------|---------|
| 1 | 真实用例覆盖 | 有效+无效输入、多步导航、长页滚动、边界空态，禁止仅测单一正常路径（DOGF-001/006） |
| 2 | 静默错误捕获 | 每次导航与关键交互后必查 `browser_console()`，JS 静默错误即高价值发现（DOGF-002） |
| 3 | 证据截图 | 缺陷必附 `browser_vision annotate=true` 截图，报告以 `MEDIA:<path>` 内联（DOGF-003） |
| 4 | 长页尽览 | 滚动至页面底部，检测折叠线以下的渲染/布局问题（DOGF-004） |
| 5 | 端到端流程 | 多步业务流程全程走通，验证中间状态转换（DOGF-005） |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：多步表单流程自测（有效+无效输入 + console + 截图证据） | 覆盖有效/无效/边界输入（DOGF-001/006）；关键交互后查 `browser_console()`（DOGF-002）；缺陷附 `MEDIA:<path>` 证据（DOGF-003）；端到端走通（DOGF-005） |
| case_002 | 正常路径：长页滚动尽览 + 布局观察 | 滚动至页面底部（DOGF-004）；记录折叠线以下渲染/布局问题；console 无静默错误 |
| case_003 | 错误路径：目标应用 URL 无效/不可访问 | 必须拒绝执行 —— 错误含上下文（哪个 URL、哪一步失败）+ 恢复建议（检查 URL/服务状态），不伪造 findings |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `test_scenarios` 覆盖有效 + 无效/边界输入（DOGF-006）；`browser_findings` 中每个缺陷含复现步骤；关键交互后存在 `browser_console()` 调用记录（DOGF-002）；发现的缺陷以 `MEDIA:<path>` 内联 `browser_vision annotate=true` 截图（DOGF-003）
- case_002: 存在滚动至页面底部的操作记录（DOGF-004）；findings 含布局/渲染观察；导航与关键交互后查 console
- case_003: 必须拒绝并返回 Golden Error 路径 —— 错误信息含"请求回声（目标 URL）+ 失败上下文（DNS/连接/超时）+ ≥2 条恢复建议（核对 URL / 检查服务是否启动 / 换可访问入口）"，禁止在 URL 不可达时伪造 browser_findings 或截图证据

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: browser_findings 列表 + screenshot_evidence（MEDIA 引用）
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- `browser_findings` 为列表，每个条目含 `type`（console_error / form_bug / layout / render）与复现步骤
- 证据截图必须以 `MEDIA:<path>` 格式内联，且来自 `browser_vision annotate=true`
- 错误路径必须同时含 `context` 与 `recovery` 两个字段
- 全程仅测试、不修改目标应用代码（验证清单项 5）

## 关联

- SKILL.md Genes: DOGF-001~007
- SKILL.md 验证清单: 5 项（URL 有效 / 覆盖核心用户路径 / 缺陷含复现步骤 / 输出含结果+缺陷清单 / 未修改目标代码）
- SKILL.md IO_CONTRACT: `target_app_url: str, test_scenarios: list[str] -> browser_findings: list, screenshot_evidence: MEDIA:<path>`
