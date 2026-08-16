# 吸收记录 — rohitg00/pro-workflow (自修正记忆)

> **吸收日期**: 2026-08-17
> **项目**: [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) (2,775⭐, MIT)
> **分类**: methodology_only
> **五维评分**: 方法论 4.0/5 · 可移植性 4.5/5 · 与 Synthos 互补性 4.0/5 · 实现复杂度 4.0/5 · 证据强度 3.5/5

## 核心架构

```
┌─ SQLite 统一存储 ─────────────────────────────────────────┐
│                                                            │
│  1. Self-Correction Memory                                 │
│     用户纠正 → 规则 → FTS5 可搜索 → SessionStart 自动加载  │
│                                                            │
│  2. Knowledge Plane                                        │
│     持久研究 Wiki → 磁盘 + FTS5 影子索引                    │
│     可被任何会话查询，可选自动研究循环增长                    │
│                                                            │
│  3. Quality Gates                                          │
│     LLM 驱动的 Hook + 确定性 git/secret 守卫               │
│     压缩感知状态 + 成本追踪                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## 关键机制

### 1. 自修正记忆
- 每次用户纠正 → 生成规则 → 存入 SQLite
- FTS5 全文搜索，SessionStart 自动加载所有学习
- UserPromptSubmit 时自动注入相关 Wiki 命中
- 50 次会话后纠正率趋近零

### 2. 知识平面 (Knowledge Plane)
- 持久研究 Wiki：磁盘文件 + FTS5 影子索引
- 任何会话可查询
- 可选自动研究循环：后台自动增长 Wiki 内容
- 200 条被引用声明的 Wiki 比手动整理的列表更密集

### 3. 质量门
- LLM 驱动的 Hook（24 个事件，37 个脚本）
- 确定性 git/secret 守卫（不依赖 LLM）
- 压缩感知状态（上下文压缩后不丢失关键信息）
- 成本追踪

### 4. 17 个实战技能 + 8 个 Agent + 23 个命令
- 跨 32+ 代理兼容（Claude Code, Cursor, Codex, Gemini CLI 等）
- 通过 `skills add` 统一安装

## 与 Synthos 的对比

| 维度 | Synthos | pro-workflow | 互补点 |
|:-----|:--------|:-------------|:-------|
| 记忆 | evolution-state.json + 手动提炼 | SQLite + FTS5 自动加载 | pro-workflow 的自动加载是 Synthos 缺口 |
| 纠正 → 规则 | 无自动机制 | 纠正 → 规则 → 自动加载 | 直接可引入 |
| 知识持久化 | Git-as-memory | SQLite + 磁盘 Wiki | 类似，实现不同 |
| 质量门 | 六维 + 四层架构 | LLM Hook + 确定性守卫 | 互补 |
| 多 Agent | 子代理 | 32+ 代理兼容 | 方向不同 |

## 可吸收方法论

1. **纠正 → 规则自动转化**：用户纠正自动生成规则，SessionStart 自动加载
2. **FTS5 知识索引**：全文搜索 + 影子索引，任何会话可查询
3. **压缩感知状态**：上下文压缩后关键信息不丢失
4. **确定性 + LLM 双门**：确定性守卫（git/secret）不依赖 LLM，LLM 门做语义检查

## 注入点

| 方法论 | Synthos 注入点 | 优先级 |
|:-------|:---------------|:-------|
| 纠正 → 规则 | conversation-to-memory | P1 |
| 压缩感知状态 | task-router (路由决策) | P2 |
| 双门验证 | quality-gate | P2 |

## 文言提炼

> **纠一次，不再错。**
> **知有所栖，索而即得。**

## 状态

- [x] 方法论提取完成
- [ ] 纠正 → 规则自动转化原型
- [ ] 压缩感知状态机制
