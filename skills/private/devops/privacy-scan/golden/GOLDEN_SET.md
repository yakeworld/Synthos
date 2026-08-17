# GOLDEN_SET.md — privacy-scan

> 对应原则：P0 证据可溯性（凡数必源）、P1 原子可复现性（同一仓库状态 → 等价扫描结论）
> golden_set_origin: self_defined

## 设计依据

本技能的金标准为自设（`self_defined`），因为 Git 推送前隐私扫描没有公开的标准测试集。金标准设计目标：验证给定相同的仓库文件状态与 `KNOWN_SECRETS` 黑名单，技能能否一致地（1）拦截含敏感凭证的推送、（2）放行干净仓库、（3）对 .gitignore 矛盾给出正确的清理动作。所有数字（命中数、追踪文件数）必须可追溯到 case 输入中列出的文件清单（P0 凡数必源）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 路径 | 正常 + 错误 | 干净仓库放行 / 凭证命中拦截 |
| 敏感类型 | 4 类 | GitHub Token、API Key、手机号、已知泄露凭证 |
| .gitignore 审计 | 2 种 | 注释/规则矛盾、规则一致 |
| 验证命令 | `git ls-tree` 二次验证 | 每次结论必须有可执行验证 |

## 测试用例 (cases/)

### case_001: 干净仓库 — 推送放行（正常路径）
- **输入**: `repo_files` 仅含常规代码与配置（无 Token/Key/手机号/已知泄露凭证），`.gitignore` 注释与规则一致且排除 `skills/private/`
- **期望**: `blocked=false`，`hits=0`，`tracked_private_skill_files=0`，动作仅为 `git push` + `git ls-tree` 二次验证通过

### case_002: GitHub Token 命中 — 推送拦截（错误路径）
- **输入**: `repo_files` 含 1 个 `.env` 文件带 GitHub Token（`ghp_` 前缀）、1 个脚本带手机号，`KNOWN_SECRETS` 含 1 条历史泄露 API Key
- **期望**: `blocked=true`，`hits>=3`（含 token/手机号/已知密钥各 ≥1），动作含"从提交中移除凭证 + 加入 `KNOWN_SECRETS` 黑名单 + 轮换凭证"，禁止 `git push --no-verify` 作为默认恢复路径

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

判定标准（语义等价）：
- `blocked` 布尔值必须精确匹配
- `hits` 计数与输入中可枚举的敏感串一致（P0：命中数 = 输入清单可数凭证数，允许多命中不允许漏报）
- `actions` 必须包含期望动作集合中的全部动作（按 PRIV-xxx 基因编号核对）
- `verification` 必须包含 `git ls-tree` 二次验证步骤

## pass_threshold: 1.0

含义：2 个 case 全部通过（2/2）。

### 阈值理由
- 隐私扫描是安全门，漏报（false negative）的代价远高于误报：放行一个含凭证的推送即构成真实泄露（先例：2026-07-03 已知泄漏，267 commits 被重写）
- 因此不设 < 1.0；两个 case 任一失败都意味着技能不可信

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-19 | 初始自设金标准，2 个 case（正常+错误） | Synthos Agent |
