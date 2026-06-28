---


name: system-bridging
description: 跨系统连接模式 — 两个独立系统（知识图谱/论文管线/技能库/监控系统）之间的双向桥接。覆盖连接协议、数据注入、反向查询、同步守护、重叠检测。
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    author: Synthos
    version: 1.0.0
    signature: 'system_a: str, system_b: str -> bridge: dict, sync_script: str, query_script: str'
    related_skills:
    - knowledge-acquisition
    - cognitive-atom-architecture
    - research-skill-audit
    - knowledge-extraction
    - conversation-to-memory
    tags:
    - system-integration
    - knowledge-graph
    - bidirectional-sync
    - cross-reference
    - bridge-protocol



---



## IO_CONTRACT

- **input**: `source_system: str, target_system: str` — 用户请求描述、上下文信息
- **output**: `bridge_spec: dict — 系统桥接`


> 对应原则：P2（机械原子暴露输入输出规范）

# System Bridging (跨系统连接)

## 原理层·文言

> 「经权度信，天人合一。」系统孤立则熵增，互通则熵减。
> 「大道至简，一维一修。」桥接非堆砌，乃建径。
> 两器相合，如阴阳相济，非拼凑，乃交融。

## 方法层·白话

两个独立系统之间的双向连接模式。不是简单的文件复制，而是建立语义层面的连接：
- **注入**：将系统A的实体作为节点/边写入系统B
- **查询**：在系统A中可通过实体名/关键词反向检索系统B的对应项
- **同步**：周期性检测变更并增量更新
- **重叠检测**：自动识别两个系统中同名/同域/同概念的实体

## 触发条件

- 两个独立系统/仓库共存，有重叠知识域（如 Synthos论文管线 + AKNE知识图谱）
- 需要将系统A的产出（论文/技能/数据）注入系统B的索引/图谱
- 需要在一个系统中查询另一个系统的实体
- 需要两个系统之间的增量同步

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|:-----|:-----|:----:|:-----|
| system_a_root | string | ✅ | 系统A的根目录路径 |
| system_b_root | string | ✅ | 系统B的根目录路径 |
| sync_direction | string | ❌ | "a_to_b" | "b_to_a" | "bidirectional"（默认） |
| domain_keywords | dict | ❌ | 领域关键词映射 {"领域名": ["关键词1", "关键词2"]} |
| known_mappings | list | ❌ | 已知的同名/关联映射 [ ("a_name", "b_name"), ... ] |

## 输出契约

```
创建文件:
  - <system_b>/scripts/<a>-to-<b>-bridge.py    # 主桥接脚本
  - <system_b>/scripts/<b>-query-<a>.py        # 反向查询脚本
  - <system_b>/scripts/generate-<a>-index.py   # 索引生成脚本
  - <system_a>/scripts/sync-<a>-to-<b>.sh      # 同步守护脚本
  - <system_b>/.knowledge/wiki/projects/<a>.md # 项目条目
  - <system_b>/.knowledge/sources/<a>/index.md # 自动生成索引
  - <system_b>/.knowledge/wiki/projects/<a>-bridge-protocol.md # 协议文档

执行操作:
  - 将系统A的实体注入系统B的图谱/索引
  - 基于领域关键词创建跨系统边
  - 生成连接报告
```

## 执行步骤

### 0. 摸清系统结构

```bash
# 系统A
ls <system_a_root>/
find <system_a_root> -maxdepth 2 -type d
# 统计：论文数、技能数、文件数、数据量

# 系统B
ls <system_b_root>/
find <system_b_root> -maxdepth 2 -type d
# 统计：图谱节点数、源文件数、Wiki页面数、向量库大小

# 检查重叠
# - 同名实体
# - 同域关键词
# - 已有引用关系
```

### 1. 设计连接协议

在 `system_b/.knowledge/wiki/projects/` 下创建：
- `<a>.md` — 系统A的项目条目（概述、架构、领域覆盖、集成方式）
- `<a>-bridge-protocol.md` — 连接协议文档（架构图、数据流、文件清单、使用方式、质量保障）

### 2. 创建主桥接脚本 (`scripts/<a>-to-<b>-bridge.py`)

核心功能：
- **论文/实体注入**: 系统A目录 → 系统B图谱节点 (type: `<a>_paper` 等)
- **技能索引**: 系统A技能目录 → 系统B概念节点
- **领域重叠检测**: 基于关键词将两个系统的实体建立边
- **交叉引用**: 双向名称匹配 → 图谱边
- **报告生成**: 连接统计、重叠域、节点类型分布

关键设计：
- 增量注入：同名节点不重复创建
- 时间戳：每个节点/边记录 `injected_at`
- 领域分类：根据命名推断论文领域
- 权重计算：名称重叠度 → 边权重

### 3. 创建反向查询脚本 (`scripts/<b>-query-<a>.py`)

功能：
- `query <entity_name>` — 查询AKNE实体相关的系统A论文/技能
- `--domain <domain>` — 查询某领域在系统A和B中的分布
- `--list-domains` — 列出所有领域重叠

### 4. 创建同步守护脚本 (`scripts/sync-<a>-to-<b>.sh`)

功能：
- 一次性同步或守护进程模式（循环执行）
- 从系统A侧触发同步
- 记录同步日志

### 5. 创建索引生成脚本 (`scripts/generate-<a>-index.py`)

功能：
- 将系统A的技能/数据目录转化为系统B可读的Markdown索引
- 自动提取每个目录的文件数、SKILL.md描述、按领域分组

### 6. 执行首次同步

```bash
python3 scripts/<a>-to-<b>-bridge.py full
```

验证：
- 节点数变化（注入前 vs 注入后）
- 边数变化（跨系统边数量）
- 领域重叠统计
- 查询功能测试

### 7. 编写连接报告

在协议文档中记录：
- 注入成果（多少论文/技能/边）
- 领域重叠统计
- 使用方式
- 注意事项（gitignore、路径、权限）

## 质量要求

- **增量安全**：不删除已有节点，不破坏现有边
- **命名规范**：注入的节点使用明确类型前缀（`synthos_paper` / `synthos_skill`）
- **领域分类**：根据名称自动推断领域，避免盲连
- **可查询**：反向查询必须能返回有意义的结果
- **可重复**：同步是幂等的，多次运行不产生重复

## Bridge v2 增强（2026-06-07 引入）

Bridge v2 修复了 v1 的三个致命问题：
1. **边格式不统一**: 旧图谱有 `relation` 格式和 `weight` 裸格式混用 → 每次同步自动统一为 `link_type`
2. **源文件孤立**: 1145个源文件全部孤立 → 通过 `source_category` 中间节点连接（24个分类hub）
3. **无版本追踪**: 无同步历史 → `logs/bridge-log.jsonl` 每次记录变更

**关键架构决策**: 源文件不直接建边，而是通过 category 节点（`sources/BPPV`、`sources/眼动研究` 等）作为中间层。边模式：
- `category → source` (1:N, weight=1.0)
- `source ↔ source` within same category (N:8, weight=0.3, 限制每个文件最多7个邻接)
- `paper → category` (论文→分类, weight=0.6, domain映射)
- `paper → wiki_concept` (论文→概念, weight=0.7, 名称重叠)

**增量同步**: 使用 `_exists_node()` 和 `_exists_edge()` 检查，同名节点不重复创建，已有边不重复添加。

**版本追踪**: `logs/bridge-log.jsonl` 每行一个JSON记录：timestamp、new_nodes、new_edges、changes。

## 已知陷阱

1. **同名冲突**：两个系统可能有同名实体但含义不同 → 使用类型前缀区分
2. **边爆炸**：如果关键词匹配太宽泛，会产生过多低权重边 → 设置最小权重阈值（0.3）
3. **路径依赖**：脚本硬编码了绝对路径 → 使用环境变量 `SYNTHOS_ROOT` / `AKNE_ROOT` 配置
4. **git污染**：桥接产生的边和节点可能不该提交 → 确认 graph.json 是否 git tracked
5. **同步循环**：双向同步可能死循环 → 单向注入（A→B），A的变更由A的进程处理
6. **类型不一致**：AKNE图谱有 `entity`/`wiki`/`source` 多种类型 → 桥接边需适配既有 schema
7. **旧数据残留**：AKNE源文件可能有占位行污染（如 `[创新点, 核心技术, 知识点]::` 重复）→ 桥接脚本需跳过/清洗
8. **源文件孤立**: 1145个源文件全部孤立时 → 必须创建 `source_category` 中间节点（24分类hub），再建 `category→source` 边。不要直接 source→source 全连。
9. **向量空洞**: vectors.db 初始可能只有33条记录（1145篇源文件）→ 需要 `fill_vectors()` 填充，但首次填充只写结构（不嵌入GPU模型），实际嵌入需要 sentence-transformers + GPU

## 验证清单

- [ ] 桥接脚本可执行且不报错
- [ ] 图谱节点数正确增加（无重复）
- [ ] 跨系统边数量合理（非全部连全部）
- [ ] 反向查询返回有意义的结果
- [ ] 领域重叠统计准确
- [ ] 同步脚本可运行
- [ ] 协议文档完整

## 命令层

- **Signature**: `system_a: str, system_b: str -> bridge: dict, sync_script: str, query_script: str`
- **Allowed tools**: shell, Read, Write, task_delegation
- **Output**: 7个文件 + 执行报告
- **Pattern**: 结构模板化，内容参数化


## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。
