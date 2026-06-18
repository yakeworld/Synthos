# AKNE vs Obsidian — 架构决策参考

> 2026-06-18 用户询问"为什么不采用Obsidian现成方案"，以下是对比分析。

## 核心结论

**Obsidian = 优秀的可视化+协作工具（面向人）**
**AKNE = 可编程的知识图谱基础设施（面向机器/Agent）**

两者定位不同，互补而非替代。

## Obsidian 擅长

| 能力 | 说明 |
|------|------|
| 可视化图谱 | DAG 视图，点击即看关系网 |
| 双向链接 | Markdown 中 `[[链接]]` 即双链，零配置 |
| 笔记编辑 | 丰富的编辑器体验，Markdown 原生 |
| 社区插件 | Dataview, Kanban, Templater, Calendar 等 |
| 多设备同步 | 付费 Cloud 服务 |
| 开放API | JS API，社区可开发插件 |

## AKNE 不可替代的能力

| 能力 | Obsidian 能做到吗 |
|------|-------------------|
| 图算法 (shortest_path, betweenness, community_detection) | ❌ 需自写插件 |
| 向量嵌入/语义搜索 | ❌ 无内置 embedding |
| 图查询语言 (类 Cypher/SPARQL) | ❌ 无声明式查询 |
| 结构化分析 (连通性统计、孤立节点检测) | ❌ 需自写脚本 |
| 自动化维护 (cron驱动孤立边清理、节点统一) | ❌ 本质是桌面应用 |
| 图神经网络接入 | ❌ |
| 知识推理/本体引擎 | ❌ |
| 可编程接口 (Python `import akne.graph`) | ❌ 非 Python 原生 |
| Agent调用 (Hermes cron 直接查询图谱) | ❌ |
| 分布式/服务端 | ❌ |

## 互补方案

### 方案一：双向同步（推荐）

```
AKNE (graph.json, sources/, wiki/, vectors.db)
  ↓ 导出
Obsidian Vault (Markdown + 双向链接)
  ↑ 导入 (定期)
```

- AKNE 做后端：向量检索、图算法、自动化维护
- Obsidian 做前端：可视化图谱浏览、笔记编辑
- 定期同步脚本从 graph.json 生成 Obsidian 格式

### 方案二：可选视图

- 保留 AKNE 完整结构不变
- 增加 `akne-to-obsidian` 导出工具，按需导出
- 用户用 Obsidian 浏览图谱，不直接编辑

### 方案三：不引入 Obsidian

- 主要用户是 Agent（cron任务、论文管线、技能检索）
- `akne-query.sh` + `akne-enhanced-search.py` 已够用
- 成本最低，维护最简单

## 决策标准

1. **谁在浏览知识库？** 人 → 加 Obsidian；Agent → 不需要
2. **是否需要多人协作编辑笔记？** 是 → Obsidian 生态有价值；单用户+脚本 → AKNE 足够
3. **是否需要在知识库上做复杂图查询/推理？** 是 → AKNE 不可替代，Obsidian 做辅助

## AKNE 当前状态

- 1550 节点, 6237 边, 100% 连通
- 1480 条向量嵌入 (384维)
- 5 层搜索: 实体解析 + 图遍历 + TF-IDF + 向量 + 组合排序
- Python 原生 API, 可被 Hermes Agent 直接调用
- Cron 驱动自动化维护

Obsidian 无法提供其中任何一项（除可视化浏览外）。
