---
name: akne-knowledge-manager
description: AKNE知识管理系统方法论 — 图谱-记忆-技能三层架构、双向整合、内容质量审计。具体操作细节见 references/。
version: 2.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: "AKNE knowledge management — graph-memory-skill 3-layer architecture, bidirectional integration, content audit methodology."
    signature: 'akne_graph: str, synthos_graph: str -> integration_report: dict + content_audit: dict'
    related_skills: [akne-maintenance, synthos-akne-bridge, skill-integrity-audit]
io_contract:
  input:
    - 'knowledge_type: str, action: str'
  output:
    - 'integration_report: dict (bridge_points, knowledge_flow, issues)'
    - 'content_audit: dict (contradictions, version_clusters, research_gaps, hypotheses)'
---

# AKNE 知识管理

## 思想

> 知识非静态，乃流动之河。图谱为渠，记忆为水，技能为闸。
> 三层架构：图谱存结构，记忆存关联，技能存行为。
> 审计之道：连接即价值，矛盾即线索，空白即方向。

## 原理

1. **三层架构**：
   - **图谱层**（graph.json）：节点+边构成的知识拓扑，承载实体关系和分类体系
   - **记忆层**（sources/ + wiki/）：源文件存储原始知识，Wiki 存储演化日志和索引
   - **技能层**（synthos-akne-bridge）：自动化脚本将图谱、记忆、技能连接起来，实现双向知识流

2. **双向知识流**：Synthos（论文产出管线）↔ AKNE（知识图谱）必须保持双向连接。单向流导致知识孤岛。

3. **质量三维度**：
   - **连通性**：论文覆盖率100%，技能连接率100%，孤立节点≤阈值
   - **一致性**：无矛盾声明，版本簇管理清晰，单位/数值准确
   - **可搜索**：TF-IDF 索引、向量嵌入、图遍历三层搜索策略

4. **发现即修复**：审计发现矛盾、孤立、污染，应直接修复。修复后验证：孤立节点=0，论文连接=100%，技能连接=100%。

## IO Contract

- **Input**: `knowledge_type: str, action: str` — 用户请求描述、上下文信息
- **Output**: 
  - `integration_report: dict` — bridge_points, knowledge_flow, issues
  - `content_audit: dict` — contradictions, version_clusters, research_gaps, hypotheses

## 核心流程

### 总览

```
连通性检查 → 孤立检测 → 技能连接 → Wiki 污染 → 双向边 → 内容审计 → 搜索验证
```

### 阶段说明

| 阶段 | 方法 | 产出 |
|------|------|------|
| 连通性检查 | 桥接报告：synthos_isolated, connected%, 边类型 | 连通性报告 |
| 孤立检测 | 遍历 graph.json，论文/技能节点对比 conn 集合 | 孤立清单 |
| 技能连接 | 按领域映射技能到分类和概念 | 连接补全 |
| Wiki 污染 | grep 检测 `[X, Y]::` 垃圾行 | 污染报告 |
| 双向边 | 检查 paper_concept/concept_paper/source_category/category_paper > 0 | 边完整性 |
| 内容审计 | 矛盾检测、版本簇、研究空白、假设提取 | 内容报告 |
| 搜索验证 | 三层策略验证搜索功能 | 搜索报告 |

## 各阶段方法

### 阶段1：连通性检查

运行桥接报告，检查：
- `synthos_isolated` 应为 0（Synthos 论文必须有边连接）
- `isolated` 应为 ≤10（仅杂项节点）
- `connected` 应 ≥ 99% 总节点

**知识流方向**：Synthos→AKNE（论文→概念/分类）和 AKNE→Synthos（概念→论文/分类）双向边都应 > 0。

**典型路径**：
- `source file → category → synthos paper`（2跳）
- `wiki concept → synthos paper → wiki concept`（3跳闭环）

### 阶段2：内容矛盾检测

读取同主题源文件，提取"创新点"、"关键"、"假设"、"应该"、"不同于"、"错误"等信号词行，对比同一概念在不同文件中的声明。

**矛盾类型**：

| 类型 | 说明 | 严重度 |
|------|------|--------|
| 数值矛盾 | 同一参数在不同文件取值不同 | 中等 |
| 方法矛盾 | 不同文件主张不同技术方案，无版本标注 | 严重 |
| 单位错误 | 数量级错误（如 nm vs μm，差1000倍） | 致命 |
| 方法缺陷自述 | 文件指出某种方法"存在缺陷"但未提供替代方案 | 中等 |

**方法**：同主题文件分组 → 提取关键声明行 → 对比同一概念 → 标注矛盾等级。

### 阶段3：版本簇管理

源文件按 basename stem（去除日期、-1/-2/-3、---草稿后缀）聚类。同 stem 的文件视为版本簇。

**管理规则**：
- 每个簇保留最新/最完整版本（按创建时间和文件大小判断）
- 其余文件标记为 `archived` 或移入 `archive/` 子目录
- 保留文件在 metadata 中新增 `version`、`replaces`、`supersedes` 字段
- 矛盾文件标注 `controversial` 标记

**去重策略**：
1. 精确 basename 匹配：同一文件名在不同目录 → 保留最大文件
2. 激进 stem 匹配：去除日期/版本后缀 → 保留最新/最大版本

### 阶段4：研究空白识别

对比源文件中"创新点"、"已有成果"和"尚未"、"未知"、"问题"等词，识别5类空白：

| 空白类型 | 示例 |
|---------|------|
| 有框架缺验证 | 数学框架完整但缺实验验证 |
| 数学完整缺实验 | 数学完整但缺真实数据验证 |
| 仿真框架有错 | 可运行但参数单位错误 |
| 概念完整缺转化 | 概念完整但缺临床标准化 |
| 初步探索缺系统 | 有文献但缺统一体系 |

### 阶段5：科学假设提取

从源文件中提取可检验假设的3步法：
1. 定位有明确量化目标的声明（"误差 < X"、"准确率 > Y%"）
2. 定位有明确因果关系的假设（"A 与 B 成反比"）
3. 标注验证难度（低/中/高）和优先级（P0/P1）

## 修复模式

### 图谱-磁盘同步

文件删除和图更新是两个独立操作，必须都完成：
1. 删除源文件
2. 运行磁盘扫描，列出所有 .md 文件
3. 对比 graph.json：磁盘有但图无 → 添加节点；图有但磁盘无 → 删除节点+边
4. 恢复被删除节点曾是"保留文件"副本的类别边
5. 最终验证：孤立节点=0，论文连接=100%，技能连接=100%

### Wiki 持续污染

`[X, Y]::` 占位符垃圾反复注入 wiki/index.md 和 wiki/log.md。
- **根因**：LLM 摄入环节输出质量不稳定，缺乏 schema 约束
- **缓解**：每次审计运行清理脚本（正则 `^\[\s*[^]]*\]\s*::.*$`）
- **长期**：改善 LLM 摄入质量，在 akne/ingest/ 环节添加输出过滤

### 论文目录不规范

扫描每个论文目录，检测 `01-manuscript`/`06-references`/`07-quality` 是否存在。不存在则按文件特征归入子目录，重新运行桥接 sync。

### 技能未连接

按领域映射技能到分类和概念：
- `research` → BPPV/科研/投稿 + 科研课题研究/科研思维层级
- `knowledge-acquisition` → 科研/投稿 + 科研论文检索系统
- `hypothesis-generation` → 科研/半规管空间姿态研究 + 科研课题研究/第一性原理

### 双向边修复

`paper_source_domain` 和 `paper_concept` 边是单向的，需要手动添加反向边：
- `category_paper`：分类→论文
- `source_category`：源文件→分类
- `concept_paper`：概念→论文

创建反向边后，`source → category → paper` 路径变为2跳连通。

## 搜索功能

三层策略：
1. **实体解析** — 精确/子串/分词/fuzzy 匹配节点名
2. **图遍历** — 从解析实体出发 2 跳搜索相关节点
3. **TF-IDF 文本搜索** — 对源文件构建索引，支持中英混合

**触发模式**：用户提及"常记忆的库"、"知识库"、"知识图谱"时，指的就是 AKNE，应优先搜索 `.knowledge/sources/` 目录。

**已知问题**：
- 性能偏慢：单次 full-mode 搜索约 22 秒（1118 个源文件）
- Graph 邻居过泛：多数节点连接在 `sources/科研` 或 `sources/编程` 大类下，缺乏精细分类

## 规则

1. **连通性即价值** — Synthos 论文 100% 必须有边连接，零孤立
2. **双向流必须保持** — Synthos→AKNE 和 AKNE→Synthos 双向边缺一不可
3. **文件删除=图更新** — 两个独立操作必须都完成
4. **去重保留最终版** — 同簇文件按创建时间和大小确定最终版，其余归档
5. **矛盾即线索** — 检测到的矛盾不是错误清单，是研究方向指引
6. **单位精度** — 单位错误是致命矛盾，必须修正并添加注释说明
7. **Wiki 持续污染** — 每次审计后运行清理，长期改善 LLM 摄入质量
8. **桥接脚本路径** — 使用 `academic_writer/yakeworld/.knowledge/` 下的桥接脚本

## 参考文件

- `references/synthos-akne-integration-audit.md` — 2026-06-10 修复后完整数据，含边类型分布、双向路径示例、修复历史
- `references/content-audit-aug2026.md` — 2026-06-13 内容级审计，含 3 处矛盾详情、70+ 版本簇、5 个研究空白、7 个假设
- `references/search-performance.md` — 搜索功能测试报告
- `references/akne-vs-obsidian.md` — AKNE 与 Obsidian 架构对比

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-27 | 2.0.0 | 重构：提炼思想/原理/IO Contract/流程/方法/规则。具体命令、案例移至 references/ |
| 2026-06-13 | 1.0.0 | 初始版本：内容级审计（矛盾、版本簇、研究空白、假设） |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。