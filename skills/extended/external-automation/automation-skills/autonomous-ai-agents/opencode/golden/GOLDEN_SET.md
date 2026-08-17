# GOLDEN_SET.md — opencode

> 对应原则：P0（证据可溯性）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能的金标准基于 SKILL.md 中定义的诊断流程（5 步）、故障排查表和核心原则。
验证目标：**给定标准诊断输入，技能能否按正确顺序执行诊断步骤、正确解读
非常驻服务语义、准确区分 OpenCode 与 Codex 的 API 差异**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 进程检查 | 正常 | 无进程 = 正常（非常驻服务），不报故障 |
| 安装验证 | 正常 + 错误 | `opencode --version` 返回版本 / command not found |
| 配置完整性 | 正常 | `~/.config/opencode/opencode.json` 存在且格式正确 |
| 后端连通性 | 正常 + 错误 | 3 节点 `nc -zv` 全通 / 某节点不可达 |
| 子命令边界 | 错误 | 未知子命令 → 路径切换错误 |
| API 区分 | 隐含 | chat/completions（非 responses） |

## 测试用例 (cases/)

### case_001: 完整 5 步诊断（正常路径）
- **输入**: 诊断请求，含 3 个后端节点地址
- **期望**: 按 Step 1→5 顺序执行，无进程视为正常，安装验证通过，配置完整，
  3 节点全通，最近使用记录存在
- **关键检查**:
  - Step 1: `ps aux | grep opencode` 无匹配 → 判定"正常（非常驻服务）"，非故障
  - Step 2: `opencode --version` 返回版本号（如 "1.17.8"）
  - Step 3: `~/.config/opencode/opencode.json` 存在，JSON 可解析，含 `provider` 和 `model` 字段
  - Step 4: 3 个 `nc -zv` 全部成功（100.125.10.93:8000, 100.82.27.51:8000, 100.100.252.99:8000）
  - Step 5: `prompt-history.jsonl` 存在且非空

### case_002: 诊断发现后端节点不可达（错误路径）
- **输入**: 诊断请求，其中 100.82.27.51:8000（AMAX 备用）不可达
- **期望**: Step 1-3 通过，Step 4 报告 AMAX 节点不可达，
  故障排查指向 Tailscale 状态 / vLLM 容器，不判定为 OpenCode 本身故障
- **关键检查**:
  - 诊断结论区分"OpenCode 安装正常"和"AMAX 后端不可达"
  - 修复建议包含 Tailscale 检查或 vLLM 容器检查
  - 不将后端不可达误报为 OpenCode 进程故障

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。
采用**语义等价判定**：
- 诊断步骤顺序固定（1→5），不可乱序
- 正常路径：各步骤结果与预期一致，结论为"系统正常"
- 错误路径：故障定位精确到具体节点，修复建议可操作

## pass_threshold: 0.80

含义：2 个测试用例中，至少 1 个通过（但 2/2 为满分 1.0）。

### 阈值理由
- **不设 1.0**：网络连通性存在瞬态波动（Tailscale 重连），允许 1 个非关键节点偏差
- **不设 < 0.8**：诊断顺序正确性和非常驻服务语义是核心能力，错误解读会导致误修
