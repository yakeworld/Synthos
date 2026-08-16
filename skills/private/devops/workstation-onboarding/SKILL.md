---
name: workstation-onboarding
description: 研究生工作站环境配置 + Windows 便携绿色软件分发 — 覆盖远程 Linux 工作站搭建和 Windows 零依赖便携包构建
signature: 'workstation-onboarding -> devops: synthetic skill for workstation onboarding'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 2.0.0
license: MIT
metadata:
  synthos:
    priority: P2
    atom_type: mechanical
    signature: 'workstation-onboarding -> devops: synthetic skill for workstation onboarding'
    related_skills: null
    description: 研究生工作站环境配置 + Windows 便携绿色软件分发 — 覆盖远程 Linux 工作站搭建和 Windows 零依赖便携包构建
    synthos_version: 2.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: devops
author: Synthos
---


|
| codex 一键脚本 | `~/codex-vllm.sh` | 封装环境变量和默认参数 |
| 入门指南 | `~/workspace/START_HERE.md` | 学生首次登录引导 |
| 培养方案 | `~/workspace/*培养方案.md` | 研究方向与里程碑 |
| 工作检查报告 | `~/workspace/WORK_CHECK_REPORT.md` | 环境验收证明（generated） |

## IO_CONTRACT

- **input**: `remote_host: str` — 研究生远程 Linux 工作站地址（SSH 连通性前置）
- **input**: `software_list: list[str]` — 需分发的 Windows 零依赖绿色软件清单
- **output**: `~/codex-vllm.sh` — codex 一键启动脚本（封装环境变量与默认参数）
- **output**: `~/workspace/START_HERE.md` + `*培养方案.md` — 学生首次登录引导与研究方向/里程碑
- **output**: `~/workspace/WORK_CHECK_REPORT.md` — 环境验收证明（generated，登录/SSH 连通性验证通过）

## 原则 (Principles)

1. **「道不通，则礼不行。」** — SSH 连通性验证是硬前置；未通则不建环境。
2. **「一钮启之，不假手学生。」** — codex 环境收敛于 `~/codex-vllm.sh` 一键脚本，封装变量与参数。
3. **「入门有阶，进路有方。」** — START_HERE 与培养方案缺一不可：先入门引导，后研究方向与里程碑。
4. **「验有凭据，不凭口诺。」** — 环境验收必以 `WORK_CHECK_REPORT.md` 为凭，不凭口头声称。

---





|
| codex 一键脚本 | `~/codex-vllm.sh` | 封装环境变量和默认参数 |
| 入门指南 | `~/workspace/START_HERE.md` | 学生首次登录引导 |
| 培养方案 | `~/workspace/*培养方案.md` | 研究方向与里程碑 |
| 工作检查报告 | `~/workspace/WORK_CHECK_REPORT.md` | 环境验收证明（generated） |


## Golden 集合 · GOLDEN SET

- **Golden Input**: `remote_host: "ssh student@10.0.0.5:2222"`（SSH 连通），`software_list: ["codex", "obsidian"]`
- **Golden Output**: 生成 `~/codex-vllm.sh`（环境变量与默认参数封装）、`~/workspace/START_HERE.md` + `*培养方案.md`、`~/workspace/WORK_CHECK_REPORT.md`（环境验收证明）
- **Golden Error**: SSH 连通性验证未通过 → 拒绝搭建环境（"道不通，则礼不行"）；WORK_CHECK_REPORT.md 未生成 → 验收不成立，不得声称环境就绪

## 示例 · EXAMPLES

**输入**：`remote_host: "ssh student@10.0.0.5:2222"`（SSH 连通验证通过），`software_list: ["codex", "obsidian"]`
**输出**：`~/codex-vllm.sh`（含 VLLM_API_KEY、DEFAULT_MODEL 等环境变量）+ `~/workspace/START_HERE.md`（首次登录 5 步引导）+ `~/workspace/培养方案.md`（3 年里程碑）+ `~/workspace/WORK_CHECK_REPORT.md`（SSH 连通 ✅, codex 启动 ✅, 软件清单就位 ✅）

**输入**：`remote_host: "ssh student@10.0.0.99:2222"`（SSH 超时）
**输出**：拒绝搭建，输出 "道不通，则礼不行" — SSH 连通性未通过，不生成任何环境文件

## 约束规则 · RULES

- SSH 连通性验证是硬前置，未通过则不搭建任何环境
- codex 环境收敛于 `~/codex-vllm.sh` 单脚本，不分散配置
- START_HERE 与培养方案缺一不可：先入门引导，后研究方向
- 验收以 `WORK_CHECK_REPORT.md` 为凭，不凭口头声称环境就绪
- Windows 便携包必须零依赖（绿色软件），不要求学生安装运行库

## 验证清单 (Verification)

- [ ] `~/codex-vllm.sh` 一键脚本可用（环境变量与默认参数封装生效）
- [ ] `~/workspace/START_HERE.md` 学生首次登录引导与 `*培养方案.md` 均已就位
- [ ] `~/workspace/WORK_CHECK_REPORT.md` 已生成作为环境验收证明
- [ ] 远程 Linux 工作站登录/SSH 连通性验证通过
