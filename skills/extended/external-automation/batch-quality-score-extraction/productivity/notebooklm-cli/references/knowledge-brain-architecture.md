# NotebookLM as Knowledge Brain: 双层认知架构设计

> 架构模式定义日期: 2026-05-23
> 哲学基础: Synthos 可移植协议 (文言+SKILL.md) + 认知原子架构

## 核心理念

**NotebookLM = 免费 Gemini 级知识大脑 + Hermes Agent = 执行皮层**

通过 CLI 桥接，将 NotebookLM 的 Gemini 级推理能力以零成本挂载到本地 Agent 上。
任何本地模型不够强的场景，都可以通过此架构获得云端级推理。

## 架构层次

```
┌──────────────────────────────────────────────────────────┐
│                    Synthos Evolution Engine                │
├────────────────────────────┬─────────────────────────────┤
│                            │                              │
│  TIER 1: Knowledge Brain   │  TIER 2: Execution Cortex    │
│  (NotebookLM / Gemini)     │  (Hermes Agent / Local)      │
│                            │                              │
│  Role: 新皮层 (Neocortex)  │  Role: 前额叶 (PFC)          │
│                            │                              │
│  深层推理: ask              │  工具编排: terminal/code      │
│  文献RAG:  source add      │  LaTeX编译: pdflatex          │
│  Gap/假设: Q1-Q6序列       │  Git管理: git                 │
│  7维评审: ask --json       │  文件操作: write_file         │
│  内容生成: generate         │  命令执行: terminal           │
│                            │                              │
│  成本: FREE (Google账号)   │  成本: FREE (本地模型)        │
│  延迟: ~60-90s (深研)      │  延迟: ~1-3s (即时)           │
└──────────┬────────────────┴──────────────┬──────────────┘
           │                                │
           └──────────────┬─────────────────┘
                          ▼
             ┌────────────────────────────┐
             │       ROUTER (路由层)       │
             │                             │
             │  深层推理? → TIER 1          │
             │  执行操作? → TIER 2          │
             │  混合? T1推理, T2执行        │
             └────────────────────────────┘
```

## 路由协议

```
IF 任务需要:
  深层推理 (文献分析, 假设形成, 质量评审)
  → notebooklm use <id> && notebooklm ask "..."

  知识检索 (RAG, 源文件查询)
  → notebooklm source get <id> || notebooklm source fulltext <id>

  文献发现 (联网搜索, 跨库检索)
  → notebooklm source add-research "query" --mode deep --no-wait
  → notebooklm research wait --import-all

  内容生成 (报告/音频/视频/幻灯片)
  → notebooklm generate <type> "description"

ELSE (执行操作):
  → 直接在 Hermes Agent 中执行 terminal/code/file/git

IF 混合任务:
  → TIER 1 先推理出方案 (ask)
  → TIER 2 执行方案 (terminal/code)
```

## P0 证据可溯链

NotebookLM 的黑盒 RAG 曾被认为是 P0 违背（有损压缩）。解决方案:

```
ask --json "问题"
    → JSON输出含 source 引用ID
      → source fulltext <id> 提取原文
        → 原文供 VER 原子做白盒验证
          → 证据链完整: 问题→回答→原文→验证
```

## 成本模型

| 配置 | 单篇论文 | 长期运行 (50篇) | 硬件要求 |
|:-----|:--------:|:--------------:|:---------|
| 单体API模型 (GPT-4o) | $2-5 | $100-250 | 低 (云端) |
| 本地大模型 (70B) | $0 | $0 | 高 (4x GPU) |
| 本地小模型 + NotebookLM | **$0** | **$0** | **低 (笔记本即可)** |

## 与 Synthos 进化的集成

在 evolution 引擎的 DIAGNOSE 阶段，若检测到高认知不确定性（benchmark variance > 0.2 或置信度突降），自动触发：

```
DIAGNOSE
  └─ 认知不确定性高?
      └─ 生成检索关键词
          └─ notebooklm source add-research "topic" --mode deep --no-wait
              └─ 自动吸收新文献到知识库
                  └─ 重新评估 (ask → 更新置信度)
                      └─ 知识库自进化
```

## 已知限制

1. **异步延迟** - deep research 需 60-90s，不适合即时反馈任务
2. **无并行 ask** - 同一项目禁止并行 ask（串话风险）
3. **源文件大小** - 超大 PDF 可能上传失败（改用 LaTeX 源）
4. **评分偏高** - NotebookLM Q&A 评分比人工高 0.05-0.15

## Synthos 自身上传：让 Gemini 理解认知框架

> 2026-05-23 实践总结

将 Synthos 自身的架构文档上传到 NotebookLM，让 Gemini 在 Q&A 时理解 7+1 框架约束：

**上传哪些文件**（优先级排序）:
1. `synthos-for-notebooklm.md` — 精简速查（~3K字），含框架总览、8维工程约束、原子清单、宪法、论文写作10条约束
2. `philosophical-foundations.md` — 7+1 框架完整定义，逐维精讲（~15K字）
3. `synthos-dimension-guide.md` — 维度指南与评估方法（~8K字）

**上传方式**:
```bash
# 首选: source add（如果 CLI 版本兼容）
notebooklm source add synthos-for-notebooklm.md

# 备用: note create（当 source add 因 API 版本不兼容失败时）
notebooklm note create "$(cat synthos-for-notebooklm.md)"
```

**上传后在 Q&A 中的效果**:
- Gemini 能主动按 7+1 框架约束回答（如生成假设时检查 entropy_reduced 字段）
- 不需要每次重新解释 Synthos 是什么
- 但 Note 的索引深度不如 Source——关键框架文件应优先以 Source 形式上传

**陷阱**:
- 文件不能太大（>20K字会被截断，用精简版本）
- Note 和 Source 在 NotebookLM 中的检索优先级不同：Source 被深度索引，Note 仅做浅层 RAG
- CLI `source add` 可能因版本不兼容失败（错误: Failed to get SOURCE_ID），改用 `note create` 或直接在网页端上传

## 参考文献

- notebooklm-cli SKILL.md v3.1.0 — CLI 操作协议
- cognitive-atom-architecture Principle 3 — 可移植协议原理
- evolution DIAGNOSE 阶段 — 自主知识更新触发
