# Synthos — 使用指南

## 如何在 Hermes 中使用

### 方法1：直接加载

```
在对话中加载：skill_view(name='Synthos')
```

加载后，告知你想要做什么（"帮我写一个文献综述"），Hermes 会自动按照流程执行。

### 方法2：分步使用 Skill

每个子 skill 可单独加载：

```
skill_view(name='文献检索与摘要')     # 单独做文献检索
skill_view(name='章节写作')           # 单独生成某个章节
skill_view(name='参考文献管理')       # 单独处理参考文献
```

### 方法3：通过工作流编排

```
workflows/lit-review-paper-draft.md  定义了完整流程
```

按照工作流中的步骤，逐步执行。

## 环境要求

- Hermes Agent 已安装
- 环境变量中已配置 Semantic Scholar API Key
- 有网络连接（用于文献检索）

## 典型会话流程

### 会话1：启动项目

```
User: 我想做一个关于ADHD眼动追踪的文献综述
Agent: [加载 Synthos skill]
       请描述你的研究问题（PICO格式）
User: P: ADHD儿童, I: 头戴式眼动追踪, 
      C: 传统方法, O: 筛查准确率
Agent: 好的，开始Step 1：多源文献检索...
```

### 会话2：继续项目

Hermes 的 session 记忆会自动保留上下文。新 session 中直接说：

```
User: 继续文献综述项目
Agent: [自动识别上下文]
       当前状态：已完成文献检索，有42篇相关文献
       请确认是否继续生成文献笔记？
```

### 会话3：审稿迭代

```
User: 审阅了引言和综述部分，修改意见：
      1. 引言太长，需要压缩
      2. 综述需要增加最近3年的论文
Agent: 收到，重新生成引言（压缩版）+ 补充检索近3年文献...
```

## 与已有工具协同

| 任务 | 使用工具 |
|------|----------|
| 文献检索 | `semantic-scholar`、`pubmed`、`openalex`、`arxiv` |
| 文献阅读管理 | `notebooklm` — 上传PDF做深度阅读 |
| 文献监控 | `literature-monitor` — 定期追踪新论文 |
| 系统综述 | `systematic-review` — PRISMA流程 |
| 期刊推荐 | `journal-selection-medical-ai` |
| 基金申请 | `nsfc-grant-audit` |
| 论文OCR | `ocr-and-documents` — 扫描版论文转文本 |

## 常见问题

**Q: 能完全自动化吗？**
A: 不能。Synthos 是"人在回路"的设计。自动化承担文献检索、摘要、初稿生成等重复性工作，人工负责选题、审稿、决策等创意性工作。

**Q: 支持英文论文吗？**
A: 支持。章节写作时指定语言即可。

**Q: 能处理图片/图表吗？**
A: 当前版本主要处理文本。图表可以描述数据结构，AI 提供图表制作建议，但实际图表制作需借助其他工具（如 matplotlib、GraphPad）。

**Q: 如何保存项目？**
A: 每次运行的中间结果保存在 `output/YYYYMMDD-项目名称/` 目录下。每个 session 之间通过 Hermes 的 session 记忆保持上下文。

**Q: 可以多个项目并行吗？**
A: 可以。不同项目的上下文通过不同的 output 目录区分。但同一个 time 只能专注一个项目的对话上下文。

## 版本历史

- **V0.1** (2026-05-08): 初始版本 — 文献综述 + 论文起草流水线
