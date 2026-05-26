---
name: task-router
description: Synthos system entry point. Routes user queries to the correct cognitive atom chain and orchestrates execution. Agent-native — no Python code, all atoms executed by Agent loading SKILL.md files.
license: MIT
metadata:
  synthos_atom_type: "router"
  synthos_version: "1.0.0"
  synthos_skill_md_hash: "4a8d1f6e2c9b3a7e5d0f8c2a4b6e0d1f3a5c7b9e2d4f6a8c0b1e3d5f7a9c2b"
  synthos_model_tested_on: "2026-05-10T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P2,P3"
  synthos_depends_on: "knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification"
  synthos_author: "Synthos Agent (v4.1 zero-python refactor)"
allowed-tools: terminal web delegate_task Read Write skill_view
---

# Synthos 任务路由器 (Task Router) — 技能驱动入口

## 概述
本 SKILL.md 是 Synthos 系统的**唯一入口**。所有用户请求都通过本文件定义的流程路由到正确的认知原子链。Agent 读取本文件后，自主推理、编排和执行，不需要任何 Python 代码。

## 工作目录
所有输出写入 Synthos 项目的 `outputs/runs/` 目录：
```
/media/yakeworld/sda2/Synthos/outputs/runs/<run_id>/
```
每次运行创建一个以时间戳命名的子目录，例如 `outputs/runs/20260510_201500/`。

Atom 输出文件命名规则：`<atom-name>_output.json`

## 执行流程

### 第 0 步：创建运行目录
```
run_id = 当前时间戳 (YYYYMMDD_HHMMSS)
mkdir -p /media/yakeworld/sda2/Synthos/outputs/runs/<run_id>
```

### 第 1 步：分析查询 → 确定原子链

分析用户查询，按关键词匹配确定复杂度：

| 关键词类别 | 标记 | 示例关键词 |
|-----------|------|-----------|
| 检索 | `needs_acquisition` | 找论文、搜索、文献、find papers、search |
| 分析 | `needs_extraction` | 分析、综述、现状、趋势、analyze、review |
| 关联 | `needs_association` | 比较、对比、关系、矛盾、compare、contradiction |
| 假设 | `needs_hypothesis` | 提出、假设、新方向、hypothesis、propose |
| 写作 | `needs_expression` | 写论文、起草、撰写、write、draft |
| 验证 | `needs_verification` | 评估、检验、可行性、verify、validate |

**复杂度确定**（基于标记数量）：
- `simple` (1个标记)：极简链，1个原子
- `medium` (2个标记)：短链，2个原子
- `complex` (3-4个标记)：中长链，3-4个原子
- `full` (5+个标记)：完整链，5-6个原子

**原子链顺序**（标准的 DAG 依赖顺序）：
```
knowledge-acquisition → knowledge-extraction → association-discovery → hypothesis-generation → argument-expression → viewpoint-verification
```

只包含标记为需要的原子。每个跳过的原子给出清晰理由。

**输出**：写入 `<run_dir>/pipeline_trace.json` 的 `routing` 字段。

### 第 2-7 步：按序执行每个原子

对原子链中的每个原子，按顺序执行：

```
for each atom_name in atom_chain:
    1. 用 skill_view(name=atom_name) 加载对应的 SKILL.md
    2. 读取上游原子输出（如果有的话）
       - 从 <run_dir>/<上游atom名>_output.json 读取
    3. 按 SKILL.md 中的指令执行
       - 使用 terminal、web、delegate_task 等工具
    4. 保存输出到 <run_dir>/<atom_name>_output.json
    5. P0: 在执行记录中附 evidence_chain（引用上游数据源）
```

**对应关系**（atom 名称 → skill 名称）：
| Atom 名 | Skill 名 | 功能 |
|---------|----------|------|
| `knowledge-acquisition` | `knowledge-acquisition` | 多源文献检索 |
| `knowledge-extraction` | `knowledge-extraction` | 结构化知识提取 |
| `association-discovery` | `association-discovery` | 关联发现与分析 |
| `hypothesis-generation` | `hypothesis-generation` | 假设生成 |
| `argument-expression` | `argument-expression` | 论证写作 |
| `viewpoint-verification` | `viewpoint-verification` | 观点验证 |

### 空结果短路（P2.2）

执行完 `knowledge-acquisition` 后，检查 `raw_papers` 数组：
- 如果为空（0篇论文）：
  1. 记录短路原因到 `pipeline_trace.json` 的 `short_circuit` 字段
  2. 跳过剩余所有原子
  3. 输出："搜索返回空结果，终止后续分析"
- 如果不为空：正常继续

### 第 8 步：汇总输出

读取所有已执行原子的输出文件，组装最终结果：
```
assembled_output.json
├── run_id
├── query
├── routing (原子链、复杂度、跳过理由)
├── short_circuit (如有)
├── outputs: {
      "knowledge-acquisition": { ... },
      "knowledge-extraction": { ... },  (如有)
      ...
    }
```

## 输出格式（pipeline_trace.json）

写入 `<run_dir>/pipeline_trace.json`：
```json
{
  "run_id": "20260510_201500",
  "query": "用户原始查询",
  "status": "completed | short_circuited | error",
  "routing": {
    "complexity": "medium",
    "atom_chain": ["knowledge-acquisition", "knowledge-extraction"],
    "skip_reasons": ["..."]
  },
  "short_circuit": {
    "at_atom": "knowledge-acquisition",
    "reason": "Search returned zero papers across all sources",
    "executed_count": 1,
    "skipped_count": 4
  },
  "atoms_executed": ["knowledge-acquisition", "knowledge-extraction"],
  "output_dir": "outputs/runs/20260510_201500",
  "started_at": "2026-05-10T20:15:00Z",
  "completed_at": "2026-05-10T20:16:30Z"
}
```

## 已知陷阱

### 1. 不要用旧 Python 代码
`core/` 目录下的 Python 代码已经全部删除。不要尝试 import 或运行它们。所有功能通过 SKILL.md + Agent 工具实现。

### 2. 输出目录不存在则创建
`mkdir -p` 确保目录树存在。不要在运行目录不存在时报错。

### 3. 上游输出未找到
如果某原子需要读取上游输出但文件不存在：
- 第一个原子（knowledge-acquisition）不需要上游输出，这是正常的
- 后续原子如果找不到上游输出 → 记录错误到 `pipeline_trace.json` 并终止

### 4. Agent 是执行引擎
- 本 SKILL.md 由 Agent 读取并执行。Agent 的 terminal、web、delegate_task、read_file、write_file 工具即是执行手段。
- 不需要也**不应当**创建任何 Python 脚本来执行原子。

### 5. 执行完向用户报告
每个原子执行完后，向用户简要报告结果（找到 N 篇论文 / 提取了 N 条知识 / 等）。

## 变更日志
2026-05-10: v1.0.0 — 从 Python pipeline 重构为纯技能驱动入口。
  移除: core/atom_pipeline.py (188行), core/context.py (341行), core/agent_atom.py (180行),
        core/trust.py (156行), run_pipeline.py (207行), 所有 core/atoms/atom*.py (3,027行)
  移除: scripts/ 中依赖 Python 核心的脚本
  新增: Agent 直接编排所有原子，读取 SKILL.md 执行
  影响: Synthos 实现零 Python 代码，全部技能驱动
