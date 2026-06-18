---
name: hermes-scheduler
related_skills: []
description: "Hermes Agent cron job lifecycle management — diagnose failures, migrate providers, load-balance across nodes, create workers, clean up orphan tasks."
version: 1.1.0
author: Synthos
license: MIT
metadata:
  hermes:
    tags: [Scheduler, Cron, DevOps, Infrastructure]
    depends_on: [skill-authoring, debug-env-variables]
---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）


# Hermes Scheduler — Cron Job Lifecycle Management

## 原理层·文言

> 调度者，时序之主也。定时有序，并行有度。
> 器有其用，用当其时。强分则劳，弱合则废。
> 恒者久行，断者复续。动静有常，调度之道尽矣。

## 触发条件

本技能适用于以下场景：
- **调度故障诊断** — Cron任务持续失败、投递错误、空跑无意义输出
- **Provider迁移** — 从API付费provider迁移到本地vLLM节点，或跨节点负载均衡
- **架构优化** — 将"定时触发→运行→退出"改为"常驻后台持续运行"的流水线模式
- **资源利用率** — 发现节点空闲、任务冲突、重复执行需要清理
- **生命周期管理** — 创建、删除、更新cron任务，清理废弃任务
- **合规性审计** — 验证cron任务是否按设计流程执行，检查skill存在性、prompt一致性、执行日志

## 核心流程

### Step 1: 全量诊断

### Step 2: 故障修复

### Step 3: 负载均衡

### Step 4: 定时→持续运行转换

### Step 4.5: Cron任务合规审计（v1.1.0 新增）

当发现cron任务可能未按设计流程执行时，执行以下审计流程（详见 `references/cron-compliance-audit-methodology.md`）：

1. **Skill存在性验证** — 检查每个cron job引用的skill是否存在
2. **Prompt-vs-Implementation对比** — 读取cron output日志中的prompt，对比对应SKILL.md
3. **执行日志分析** — 识别空跑模式、错误模式、完成模式
4. **质量检查覆盖率统计** — 遍历所有论文，分类统计通过质量检查的比例
5. **修复决策树** — skill不存在→改用已存在skill；skill存在但prompt简单→重写prompt；prompt完整但没执行→检查queue；有queue但全是completed→重建queue；无queue→创建新queue

### Step 5: 清理废弃任务

## Pitfalls

1. Cron script errors cause silent failures:
   - **KeyError from stale JSON state**: Cron scripts that use `.json` state files (like `qc_batch_scan.py`) will crash with KeyError when the state file contains entries for deleted directories. **Fix**: Use `.get()` for all key accesses. Clear stale state file (`rm ~/.hermes/qc_last_scan_v2.json`) after fixing.
   - **120s timeout from heavy operations**: `rclone check` or similar heavy operations will timeout. **Fix**: Remove pre-checks, go straight to the sync action with `--stats` for progress.
2. Cron tasks with `no_agent=true` mode deliver stdout directly — they cannot use skills, only shell commands and Python scripts.
3. Cron tasks with `skills:` field require the agent mode — check that referenced skills exist.
4. Cron schedule mismatches: if a cron task depends on file system state (e.g., `outputs/papers/`), changes to directory structure can break assumptions.