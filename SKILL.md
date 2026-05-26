# Synthos — 认知操作系统

## 愿景

**Synthos** 是一个可计算的、协作的、持续进化的公共认知操作系统，用于科学研究。

> "A computable, collaborative, and evolving public cognitive operating system for science."

## 架构：6认知原子

基于**Synthos八维认知框架**，平台将科研全流程原子化为6个独立认知单元，构成有向无环图（DAG）。

```
[1] 知识获取 → [2] 知识提取 → [3] 关联发现 → [4] 观点生成 → [5] 论证表达
                                                              ↓
                                                      [6] 观点验证 ↺
```

## 认知原子

| # | 中文名 | 英文名 | 功能 | Synthos维度 |
|---|--------|--------|------|-------------|
| 1 | 知识获取 | knowledge-acquisition | 多源论文检索+摘要+全文下载 | 第一性原理、系统思维 |
| 2 | 知识提取 | knowledge-extraction | 从论文提取结构化知识 | 第一性原理、奥卡姆剃刀 |
| 3 | 关联发现 | association-discovery | 识别矛盾/补充/演进/空白 | 系统思维、模型依赖实在论 |
| 4 | 观点生成 | hypothesis-generation | 生成可验证研究假设 | 第一性原理、类比、贝叶斯思维 |
| 5 | 论证表达 | argument-expression | 构建论文章节/论据链 | 系统思维、第一性原理、奥卡姆剃刀 |
| 6 | 观点验证 | viewpoint-verification | 反方观点/证伪检验/鲁棒性测试 | 证伪主义、贝叶斯思维、自由能原理 |

### 原子架构

```
layer 0: task-router (编排层 - 奥卡姆剃刀)
  │
  ├──→ layer 1: knowledge-acquisition
  │        │
  │        └──→ layer 2: knowledge-extraction
  │                 │
  │                 └──→ layer 3: association-discovery
  │                          │
  │                          └──→ layer 4: hypothesis-generation
  │                                   │
  │                                   ├──→ layer 5: argument-expression
  │                                   └──→ layer 5: viewpoint-verification
```

### 输入输出流

```
Query → [1] raw_papers, pdfs
         ↓
[pdfs] → [2] extracted_knowledge
         ↓
[knowledge] → [3] associations, knowledge_graph, research_gaps
              ↓
[associations, gaps] → [4] hypotheses, rationale, novelty_score
                        ↓
              ┌──────→ [5] sections, arguments, references
              │
              └──────→ [6] verification_results, weaknesses, confidence
```

## 任务编排（奥卡姆剃刀）

```
用户请求 → [路由器] → 判断复杂度 → 最短原子链 → 执行 → 输出
```

### 复杂度判断规则

1. **检索型**（"找论文"、"搜索"）→ 极简链 [原子1]
2. **分析型**（"分析"、"综述"）→ 中长链 [原子1→2→3]
3. **写作型**（"写论文"、"起草"）→ 完整链 [原子1→2→3→4→5]
4. **验证型**（"评估"、"检验"）→ 短链 [原子4→6]

### 最短任务链

| 复杂度 | 示例 | 路径 | 原子数 |
|--------|------|------|--------|
| 极简 | 找3篇ADHD论文 | 知识获取 | 1 |
| 短链 | 找论文+提取方法 | 知识获取 → 知识提取 | 2 |
| 短链 | 提出假设+验证 | 观点生成 → 观点验证 | 2 |
| 中长 | 分析XX领域现状 | 知识获取 → 知识提取 → 关联发现 | 3 |
| 中长 | 生成假设+写论证 | 观点生成 → 论证表达 | 2 |
| 完整 | 写综述/基金申请 | 完整链 | 5-6 |

## Synthos八维认知框架

| 维度 | 覆盖原子 | 实现度 |
|------|----------|--------|
| 第一性原理 | 1, 2, 4, 5 | 95% |
| 系统思维 | 1, 3, 5 | 95% |
| 贝叶斯思维 | 4, 6 | 90% |
| 类比 | 4 | 70% |
| 奥卡姆剃刀 | 2, 5 | 80% |
| 证伪主义 | 6 | 60% |
| 模型依赖实在论 | 3 | 40% |
| 自由能原理 | 6 | 30% |

**综合实现度: 68%**

详细哲学见 [docs/synthos-philosophy.md](docs/synthos-philosophy.md)

## 技能吸收与进化

### 跨领域技能复用

通过语义匹配发现外部技能的可复用模式：
- **pdf → knowledge-extraction**: 增强PDF解析能力
- **docx → argument-expression**: 增强文档格式化
- **skill-creator → task-router**: 增强技能自我优化

### 持续进化

- 每月扫描外部技能源
- 自动检测语义相似的技能
- 手动审核吸收建议
- 定期更新吸收报告

## 质量保障

### 测试验证

所有技能必须通过：
- 结构测试（YAML、命名、描述）
- 功能测试（端到端、错误处理）
- 质量评估（语义、重复检测）

### 生命周期

```
DRAFT → TESTING → VALIDATED → ACTIVE → DEPRECATED
```

### 当前状态

- **总技能数**: 7
- **通过测试**: 7/7 (100%)
- **平均质量**: 0.97
- **淘汰建议**: 0

## 文件结构

```
Synthos/
├── SKILL.md                          # 认知操作系统总编排
├── skills/
│   ├── knowledge-acquisition/        # Atom 1
│   ├── knowledge-extraction/         # Atom 2
│   ├── association-discovery/        # Atom 3
│   ├── hypothesis-generation/        # Atom 4
│   ├── argument-expression/          # Atom 5
│   ├── viewpoint-verification/       # Atom 6
│   └── task-router/                  # 编排层
├── scripts/
│   ├── skill_network.py              # 网络分析
│   ├── skill_tester.py               # 质量测试
│   ├── skill_absorber.py             # 技能吸收
│   └── evolution_scheduler.py        # 进化调度
├── test-results/                     # 测试报告
├── docs/                             # 文档
└── evolution-state.json              # 进化状态
```

## License

MIT
