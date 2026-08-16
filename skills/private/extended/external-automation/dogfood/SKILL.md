---
name: dogfood
description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
signature: 'dogfood -> external-automation: synthetic skill for dogfood'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
    signature: 'dogfood -> external-automation: synthetic skill for dogfood'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| `browser_navigate` | Go to a URL |
| `browser_snapshot` | Get DOM text snapshot (accessibility tree) |
| `browser_click` | Click an element by ref (`@eN`) or text |
| `browser_type` | Type into an input field |
| `browser_scroll` | Scroll up/down on the page |
| `browser_back` | Go back in browser history |
| `browser_press` | Press a keyboard key |
| `browser_vision` | Screenshot + AI analysis; use `annotate=true` for element labels |
| `browser_console` | Get JS console output and errors |

## IO_CONTRACT

- **input**: `target_app_url: str` — 待自测（dogfood）的 Web 应用入口
- **input**: `test_scenarios: list[str]` — 覆盖有效/无效输入、多步导航、长页滚动、边界输入（空态/长文本/特殊字符）的用例集
- **output**: `browser_findings: list` — 缺陷与观察记录（JS console 静默错误、表单验证 bug、布局问题、渲染异常）
- **output**: `screenshot_evidence: MEDIA:<path>` — 证据截图（`browser_vision annotate=true`，报告中以 MEDIA 引用内联）

## 原则 (Principles)

- **以己器测己**：自测（dogfood）必用真实用例（有效+无效输入、多步导航、长页、边界空态），不试真实流程者，验不得真缺陷。
- **静默即警**：每次导航与关键交互后必查 `browser_console()`，JS 静默错误乃最贵之发现，勿待界面崩坏方见。
- **所见必证**：缺陷必附 `browser_vision annotate=true` 之截图，以 `MEDIA:<path>` 内联入报告；无图之断言，不取信于人。
- **尽览无余**：长页必滚动尽览、多步必全程走通、边缘（空态/长文/特殊字符/快速点击）必试；略其一，则验有隙。


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[DOGF-001]** 执行自测任务 → 必须使用覆盖有效/无效输入、多步导航及边界空态的真实用例集，禁止仅测试单一正常路径
- **[DOGF-002]** 完成页面导航或关键交互后 → 立即调用 `browser_console()` 检查 JS 静默错误，将其视为高价值缺陷发现
- **[DOGF-003]** 发现缺陷或需要记录观察结果时 → 必须使用 `browser_vision annotate=true` 生成带标注的截图，并以 `MEDIA:<path>` 格式内联至报告作为证据
- **[DOGF-004]** 面对长页面内容 → 必须执行滚动操作直至页面底部，以检测折叠线以下可能存在的渲染或布局问题
- **[DOGF-005]** 测试多步业务流程 → 必须端到端完整走通所有导航步骤，确保流程连贯性并验证中间状态转换
- **[DOGF-006]** 处理表单输入场景 → 必须同时测试有效数据和无效数据（如特殊字符、超长文本），以暴露表单验证逻辑缺陷
- **[DOGF-007]** 遇到快照引用不清或需分析元素位置时 → 使用 `browser_vision` 配合 `annotate=true` 获取元素标签辅助定位，而非盲目点击

## Tips

- **Always check `browser_console()` after navigating and after significant interactions.** Silent JS errors are among the most valuable findings.
- **Use `annotate=true` with `browser_vision`** when you need to reason about interactive element positions or when the snapshot refs are unclear.
- **Test with both valid and invalid inputs** — form validation bugs are common.
- **Scroll through long pages** — content below the fold may have rendering issues.
- **Test navigation flows** — click through multi-step processes end-to-end.
- **Check responsive behavior** by noting any layout issues visible in screenshots.
- **Don't forget edge cases**: empty states, very long text, special characters, rapid clicking.
- When reporting screenshots to the user, include `MEDIA:<screenshot_path>` so they can see the evidence inline.

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Dogfood---





|
| `browser_navigate` | Go to a URL |
| `browser_snapshot` | Get DOM text snapshot (accessibility tree) |
| `browser_click` | Click an element by ref (`@eN`) or text |
| `browser_type` | Type into an input field |
| `browser_scroll` | Scroll up/down on the page |
| `browser_back` | Go back in browser history |
| `browser_press` | Press a keyboard key |
| `browser_vision` | Screenshot + AI analysis; use `annotate=true` for element labels |
| `browser_console` | Get JS console output and errors |

## Tips

- **Always check `browser_console()` after navigating and after significant interactions.** Silent JS errors are among the most valuable findings.
- **Use `annotate=true` with `browser_vision`** when you need to reason about interactive element positions or when the snapshot refs are unclear.
- **Test with both valid and invalid inputs** — form validation bugs are common.
- **Scroll through long pages** — content below the fold may have rendering issues.
- **Test navigation flows** — click through multi-step processes end-to-end.
- **Check responsive behavior** by noting any layout issues visible in screenshots.
- **Don't forget edge cases**: empty states, very long text, special characters, rapid clicking.
- When reporting screenshots to the user, include `MEDIA:<screenshot_path>` so they can see the evidence inline.

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

