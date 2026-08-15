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

---





|
| codex 一键脚本 | `~/codex-vllm.sh` | 封装环境变量和默认参数 |
| 入门指南 | `~/workspace/START_HERE.md` | 学生首次登录引导 |
| 培养方案 | `~/workspace/*培养方案.md` | 研究方向与里程碑 |
| 工作检查报告 | `~/workspace/WORK_CHECK_REPORT.md` | 环境验收证明（generated） |

## 验证清单 (Verification)

- [ ] `~/codex-vllm.sh` 一键脚本可用（环境变量与默认参数封装生效）
- [ ] `~/workspace/START_HERE.md` 学生首次登录引导与 `*培养方案.md` 均已就位
- [ ] `~/workspace/WORK_CHECK_REPORT.md` 已生成作为环境验收证明
- [ ] 远程 Linux 工作站登录/SSH 连通性验证通过
