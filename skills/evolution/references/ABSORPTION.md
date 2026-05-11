# Synthos 外部技能吸收指南

## 概述

Synthos 的技能树不应封闭。外部有优秀的开源项目、Hermes 社区技能、学术论文方法等，
可以吸收来增强系统能力。本指南定义如何搜索、评估、提议吸收外部技能。

**核心原则**：
- 原子（6认知原子+路由器）保持稳定，除非用户明确批准修改
- 吸收对象是**技能树**的扩展（新技能、新工具集成、新数据源）
- 每次吸收需生成**吸收提议**供用户审批
- 不自动执行，只提议+呈现证据

## 搜索频率

**主动扫描**：每轮进化循环都执行 EXTERNAL 步骤。每轮选 2-3 组关键词进行搜索（8类别轮转），确保所有方向定期覆盖。

**定期随访**：对已追踪项目，至少每7轮重新检查一次状态（star变化、新release、新documentation）。

## 搜索来源

### 1. GitHub 搜索

用 `web_search` 工具搜索以下关键词组合：

| 搜索方向 | 关键词 |
|---------|--------|
| AI科研助手 | "AI research assistant" "academic paper agent" site:github.com |
| 文献检索工具 | "semantic scholar agent" "paper search tool" site:github.com |
| 知识图谱 | "knowledge graph extraction academic" site:github.com |
| 可进化系统 | "self-evolving agent" "autonomous research" site:github.com |
| Hermes生态 | "hermes agent skill" "hermes mcp" site:github.com |

每次搜索取前 5 个结果，过滤条件：
- ⭐ Star ≥ 50（至少有一定社区认可）
- 📅 最近 1 年内有更新（不是死项目）
- 📄 有 README 和文档

### 2. Hermes 技能库

用 `skills_list` 查看所有可用技能，找出可能与 Synthos 互补的技能：

| 互补方向 | 查找目标 |
|---------|---------|
| 数据源扩展 | openalex, pubmed, biorxiv, arxiv 相关技能 |
| 分析增强 | systematic-review, notebooklm-literature-optimization |
| 输出增强 | competition-submission, nsfc-grant-audit |
| 平台扩展 | native-mcp, huggingface-hub |

### 3. 学术论文

用 `web_search` 搜索最新相关论文：
- "AI agent for scientific research" (2025-2026)
- "autonomous literature review system"
- "knowledge-driven research assistant"

## 关键词自我扩展

发现新项目后，从项目的 topics/description 中自动提取新关键词，追加到关键词库：

1. 提取 project.topics 中的所有标签
2. 提取 project.description 中的核心名词短语
3. 过滤：已在关键词库中、过于通用、非英文
4. 已在 >=2 个不同项目中出现 => high value，立即加入
5. 加入 `self_discovered` 类别，标记原始项目

## 自检关键词生成

从 PROBE/DIAGNOSE 结果中发现新的搜索方向：

| 发现 | 生成的关键词方向 |
|------|----------------|
| 某个原子结构分 < 0.7 | [原子功能] improvement, [原子功能] alternative |
| 某 API 连续失败 | [API名] replacement, [API名] alternative |
| 技能树覆盖率 < 0.5 | skill framework, cognitive architecture |
| golden 测试缺失 | 从 golden_set 提取相关领域关键词 |
| 历史 lesson 提示特定缺陷 | lesson issue 相关的搜索词 |

## 项目追踪数据库

所有发现的项目存储在 `outputs/evolution/absorption-tracked.json`，每个项目包含：

```json
{
  "id": "gh:owner/repo",
  "source": "github | hermes_skill | paper",
  "name": "项目名称",
  "url": "https://...",
  "stars": 12000,
  "description": "项目描述",
  "first_seen": "2026-05-08",
  "last_checked": "2026-05-11",
  "status": "tracking | evaluating | absorbed | deferred | archived",
  "absorption_score": 4.2,
  "absorbed_skills": [],
  "tags": ["research", "agent"],
  "notes": "评估笔记"
}
```

状态定义：
- **tracking**: 正在观察，未做决定
- **evaluating**: 有潜力，正做深入评估
- **absorbed**: 已完成吸收
- **deferred**: 延迟决策（30轮后自动清理）
- **archived**: 确定不吸收

| 维度 | 权重 | 评估方法 |
|------|------|---------|
| 与 Synthos 互补性 | 0.25 | 是否填补了 Synthos 的功能空白？ |
| 代码/文档质量 | 0.20 | README 完整？有例子？ |
| 社区活跃度 | 0.15 | Stars, PRs, Issues 响应 |
| 集成成本 | 0.25 | 是否容易整合到纯SKILL架构？ |
| 许可证兼容 | 0.15 | MIT/Apache/BSD 优先 |

**综合分 = Σ(维度分 × 权重)**

| 综合分 | 决策 |
|--------|------|
| ≥4.0 | 🔥 强烈建议吸收，立即生成提议 |
| 3.0-3.9 | 👍 建议吸收，记录在下次汇总中 |
| <3.0 | ⏭️ 跳过，记录原因 |

## 吸收提议格式

找到值得吸收的项目后，在报告 `outputs/evolution/report_{cycle}.json` 中添加：

```json
{
  "absorption_proposals": [
    {
      "id": "ABS-001",
      "source_type": "github | hermes_skill | paper",
      "name": "项目/技能名称",
      "url": "https://...",
      "complementarity_score": 4.2,
      "synthos_gap": "填补的具体功能空白",
      "proposed_action": "创建新技能 in skills/ 或 增强已有原子",
      "integration_effort": "low | medium | high",
      "rationale": "为什么这个值得吸收..."
    }
  ]
}
```

## 用户审批流程

吸收提议写入报告后，Agent 在记录步骤中向用户呈现：

```
📥 外部技能吸收提议

项目: xxx (⭐ 123)
填补: Synthos 缺少 [功能]
综合评分: 4.2/5
集成成本: medium

是否批准吸收？[Y/n]
```

用户批准后才执行。不批准则记录到 `archive/absorption-deferred/`，
30 轮后若仍未决策则自动清理提议。

## 禁止吸收的情况

- ❌ 闭源/专有许可证
- ❌ 核心原子逻辑替代（不能替换 knowledge-acquisition 等）
- ❌ 需要 Python 运行时依赖
- ❌ 依赖外部付费 API（非已有）
- ❌ 安全风险（执行远程代码、访问文件系统等）

## 吸收后的验证

吸收新技能后，需要：
1. 集成到技能树（更新 evolution-state.json 的 skill_count）
2. 下一轮 BENCHMARK 测试新技能
3. 记录吸收结果到 evolution-log.md
