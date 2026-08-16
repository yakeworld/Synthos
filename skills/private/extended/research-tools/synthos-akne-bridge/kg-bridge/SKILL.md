---
name: kg-bridge
description: QueryEngine 的 `_graph_search` 通常使用词袋匹配，对多词/中英混合查询无效。增强策略：
signature: 'kg-bridge -> synthos-akne-bridge: synthetic skill for kg bridge'
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
    description: QueryEngine 的 `_graph_search` 通常使用词袋匹配，对多词/中英混合查询无效。增强策略：
    signature: 'kg-bridge -> synthos-akne-bridge: synthetic skill for kg bridge'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 知识图谱查询请求 — 多词/中英混合查询，模式选择（quick/graph/deep/bridge）
- **input**: 图谱状态 — 节点/边/类型/向量库（供健康度诊断）
- **output**: 图谱查询结果 — 节点匹配（精确→子串→分词→反向→模糊 5级评分）+ 文本检索融合
- **output**: 图谱连接健康报告 — 节点/边/类型/向量计数、论文/技能连接数、孤立节点清单

## 原则 (Principles)

> **分层而查，轻重有别。** quick/graph/deep/bridge 四档，按查询成本选路——日常走快速脚本，深查才启重型检索。
> **图文相参，互补为强。** 词袋匹配不敌多词与中英混合，须 jieba 分词 + TF-IDF 全文检索与图结果融合，图权重居先。
> **级评分降，模糊为末。** 实体解析走 精确→子串→分词→反向→模糊 五级降级，逐级而退，不误投他物。
> **限噪分层，先一后二。** 查询结果须限量（≤20）、BFS 分层展开，先 depth=1 后按需 depth=2，噪声不淹意图。

|
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


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[KGB-001]** 查询成本敏感或日常高频查询 → 优先使用 quick 模式（<1s），仅当需要深度探索时才启用 deep 模式
- **[KGB-002]** 面对多词或中英混合查询导致词袋匹配失效 → 采用 jieba 分词 + TF-IDF 全文检索，并与图结果融合（图权重更高）
- **[KGB-003]** 实体解析存在歧义或匹配不确定 → 执行 精确→子串→分词→反向→模糊 五级降级评分策略，逐级回退以避免误投
- **[KGB-004]** 查询结果噪声过大或数据量爆炸 → 限制输出数量（≤20）并采用 BFS 分层展开，先展示 depth=1 再按需展开 depth=2
- **[KGB-005]** 需要调用重型依赖（如 sentence-transformers/torch）进行向量搜索 → 避免在 Agent venv 中加载，改用系统 Python 的 TF-IDF 或纯文本分词替代
- **[KGB-006]** 调用图谱 API 时出现属性错误（AttributeError） → 确认 `resolve_entity` 位于 `QueryEngine` 而非 `KnowledgeGraph`，且 `find_related` 返回值为 3 元组

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


# Kg Bridge---
> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Kg Bridge
