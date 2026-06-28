---


name: kg-bridge
description: Knowledge Graph — Agent Bridge. 将大型知识图谱接入 Agent 记忆层的方法论，覆盖查询分层、环境隔离、语义搜索增强、脚本化接口。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
triggers:
  - 需要将知识图谱/向量数据库接入 Agent 工作流
  - 图谱节点 > 1000 需要按需检索（非全量注入）
  - Agent 沙盒环境与外部工具环境版本不一致
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: "KG-AG Bridge: Knowledge Graph — Agent Bridge. 将大型知识图谱接入 Agent 记忆层，查询分层 + 环境隔离 + 语义增强 + 脚本化接口"
    signature: 'graph: KG + agent: Agent -> bridge: layered_queries + constraints + scripts'
    related_skills: ["synthos-akne-bridge"]


---


## IO_CONTRACT

- **input**: `data_source: str, bridge_type: str` — 用户请求描述、上下文信息
- **output**: `kg_output: dict — 知识图谱桥接`

> 对应原则：P2（机械原子暴露输入输出规范）



# KG-AG Bridge — 知识图谱 × Agent 桥接方法论

> 通用方法论：如何将大型知识图谱（1000+ 节点）桥接到受限 Agent（沙盒环境、字符限制、工具限制）。
> 不绑定特定图谱实现（AKNE、Neo4j、SQLite 等），适用于任何场景。

## 核心原理

大型知识图谱的查询必须**按需检索**（on-demand），不可全量注入系统提示。三层架构：

```
Layer 1: MEMORY/USER（系统提示，≤2200 chars）—— 高频摘要 + 入口路径
Layer 2: 快速查询（terminal 工具，秒级响应）—— 实体解析 + 局部遍历
Layer 3: 深度查询（脚本，秒~分钟）—— TF-IDF/向量搜索 + 全图遍历
```

## 架构约束

### 1. 环境隔离（常见坑）

Agent 的沙盒环境（execute_code）通常是隔离的 venv（如 Python 3.11），而工具库安装在系统 Python（如 3.12）上。关键原则：

- **execute_code** → 纯逻辑处理，无外部依赖（networkx 等小包可装）
- **terminal** → 重型工具（AKNE 查询、向量搜索），走系统 Python
- **永远不要**在 execute_code 中 import 系统 Python 包

判断方法：`sys.executable` 显示 venv 路径 = execute_code 沙盒。`/usr/bin/python3` = 系统 Python。

### 2. 查询分层策略

| 模式 | 响应时间 | 适用场景 | 工具 |
|------|----------|----------|------|
| quick（simple） | <1s | 日常查询、5-20 节点 | terminal + 快速脚本 |
| graph（BFS） | <2s | 知识域探索、3 跳边界 | terminal + 快速脚本 |
| deep（full） | 10s~min | 全文检索、多词查询 | terminal + 重型脚本 |
| bridge（audit） | <1s | 图谱健康检查、连接报告 | terminal + 统计脚本 |

### 3. 语义搜索增强

QueryEngine 的 `_graph_search` 通常使用词袋匹配，对多词/中英混合查询无效。增强策略：

- **jieba 分词**（中文）+ 多 token 加权：边界 ×2，子串 ×1，阈值 ≥2
- **TF-IDF**（scikit-learn）：对源文件全文建立倒排索引，40916 词汇量
- **fuzzy_node_search**：5 级评分（精确→子串→分词→反向→模糊），回退到所有节点名
- **combined search**：图结果 + 文本结果融合，graph 结果权重更高

## 实施步骤

### Step 1: 诊断图谱状态

```bash
# 统计节点/边/类型
akne-query.sh stats
# 输出: nodes/edges/types/vectors count

# 检查连接健康度
akne-query.sh bridge
# 输出: papers/skills connected, edges by type, orphans
```

### Step 2: 创建快速查询脚本

最小化查询入口（quick 模式）：
- 实体解析：5 级评分策略
- BFS 局部遍历：depth=3 上限
- 输出结构化文本：Agent 可解析

### Step 3: 创建深度查询脚本

重型查询入口（deep 模式）：
- TF-IDF 全文检索（所有源文件索引）
- 多 token 分词匹配
- 图 + 文本融合评分
- 内容预览（前 200 字符）

### Step 4: 桥接 MEMORY.md

在 MEMORY.md 中添加 AKNE 桥接摘要：
- 入口路径：`~/.hermes/scripts/akne-query.sh`
- 模式列表：6 种（simple/graph/concept/full/stats/bridge）
- 关键统计：1475 节点，5868 边，148 论文，25 技能，0 孤儿
- 环境约束：execute_code 走 venv，AKNE 走 terminal（系统 Python）

### Step 5: 端到端验证

模拟 Agent 实际查询场景：
1. 已知实体查询（BPPV → 5 邻居）
2. 概念词查询（眩晕 → fuzzy 找到 `.knowledge/sources/BPPV/眩晕药物经皮渗透.md`）
3. 多词查询（眼动追踪 → jieba 分词 + TF-IDF）
4. 图谱审计（bridge → 0 孤儿，全连接）

## 常见陷阱

### 1. resolve_entity 位置错误

`resolve_entity()` 在 `QueryEngine` 中，不在 `KnowledgeGraph` 中！
- 错误: `kg.resolve_entity(q)` → `AttributeError: 'KnowledgeGraph' object has no attribute 'resolve_entity'`
- 正确: `QueryEngine(graph_index=kg).resolve_entity(q)`

### 2. find_related() 返回格式

`kg.find_related(entity, depth=2)` 返回 `[(neighbor, relation_chain, metadata), ...]`（3 元组）。
- **切勿**用 `for n, r, m, d in related:` 解包（ValueError）
- 用 `data=True` 或 `data=True, keys=True` 时注意 edges 返回格式不同

### 3. 向量搜索依赖过大

sentence-transformers 依赖 torch（500MB+ CUDA 库），不适合放入 Agent venv。
- 替代方案 1：TF-IDF（scikit-learn，系统 Python 通常已有）
- 替代方案 2：纯文本分词 + 子串匹配（jieba + 阈值过滤）
- 替代方案 3：仅在 terminal 工具中调用，不通过 execute_code

### 4. 查询返回过多噪声

`find_related(entity, depth=2)` 可能返回数百条结果（如 `.knowledge/sources/科研` 398 条）。
- 对策：限制输出数量（`related[:20]` 而非 `[:100]`）
- 对策：增加 relevance 过滤（只看特定 relation_type）
- 对策：BFS 分层，先展示 depth=1，按需展开 depth=2

### 5. 文件路径编码问题

AKNE 源文件路径中可能包含特殊字符（空格、中文、连字符）。
- 在 shell 脚本中用 `\"${query}\"` 包裹，避免 glob 展开
- Python 中用 `os.path.relpath()` 标准化路径

## 支持文件

- `scripts/akne-query.sh` — 6 种查询模式入口（terminal 工具执行，系统 Python 3.12）
- `scripts/akne-enhanced-search.py` — 三层搜索策略（实体解析→图遍历→TF-IDF）
- `references/environment-isolation-pattern.md` — execute_code vs terminal 环境差异对照
- `references/query-enhancement-recipes.md` — TF-IDF 配置、jieba 调优、多词匹配策略

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
