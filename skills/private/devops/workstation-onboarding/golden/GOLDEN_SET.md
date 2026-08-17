# GOLDEN_SET.md — workstation-onboarding

> 对应原则：P0 证据可溯性、P1 原子可复现性（同一 SSH 验证结果 → 等价环境搭建结论）
> golden_set_origin: self_defined

## 设计依据

本技能的金标准为自设（`self_defined`）。金标准设计目标：验证技能能否一致地（1）在 SSH 连通时生成完整的环境文件四件套并给出书面验收证明、（2）在 SSH 不通时硬性拒绝搭建（"道不通，则礼不行"，WORK-001 硬前置）。核心判定：`WORK_CHECK_REPORT.md` 是验收的唯一凭据——没有它不得声称环境就绪（WORK-004）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 路径 | 正常 + 错误 | SSH 连通搭建成功 / SSH 超时拒绝 |
| 输出文件 | 4 个 | `~/codex-vllm.sh`、`START_HERE.md`、`培养方案.md`、`WORK_CHECK_REPORT.md` |
| 硬前置 | 1 条 | SSH 连通性验证（WORK-001） |
| Windows 便携约束 | 零依赖 | software_list 只允许绿色软件（WORK-005） |

## 测试用例 (cases/)

### case_001: SSH 连通 — 完整环境搭建（正常路径）
- **输入**: `remote_host="ssh student@10.0.0.5:2222"`（SSH 连通验证通过），`software_list=["codex","obsidian"]`（均零依赖绿色软件）
- **期望**: `proceeded=true`；生成全部 4 个文件；`WORK_CHECK_REPORT.md` 的 checklist 全部 ✅（SSH 连通、codex 启动、软件清单就位）；验收结论以报告文件为凭

### case_002: SSH 超时 — 拒绝搭建（错误路径）
- **输入**: `remote_host="ssh student@10.0.0.99:2222"`（SSH 超时）
- **期望**: `proceeded=false`；**不生成任何**环境文件（4 个文件均 absent）；输出引用 "道不通，则礼不行"；给出恢复建议（检查网络/端口/凭据后重试），不得声称环境就绪

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

判定标准（语义等价）：
- `proceeded` 布尔值必须精确匹配
- `files_generated` 集合必须精确匹配（case_001 四个全在；case_002 一个不能多、一个不能少）
- case_001 的 `work_check_report.checklist` 每项 status 必须为 "pass"，且 `acceptance_basis` 指向该报告文件
- case_002 的 `message` 必须包含硬前置原则引用（"道不通，则礼不行" 或等价表述）

## pass_threshold: 1.0

含义：2 个 case 全部通过（2/2）。

### 阈值理由
- 错误路径（SSH 不通时不搭环境）是宪法级硬前置，失败即违反 WORK-001，构成虚假的环境就绪声称
- 正常路径失败意味着学生拿不到可用环境，直接阻断研究生入门
- 因此不设 < 1.0

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-19 | 初始自设金标准，2 个 case（正常+错误） | Synthos Agent |
