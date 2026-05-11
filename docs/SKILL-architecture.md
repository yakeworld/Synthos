# Synthos 架构骨架 v1.0

> 地位：**骨架层**。承接宪法的约束，定义组件的物理边界、通信协议和数据结构。所有原子 SKILL.md 和 pipeline 实现必须遵守本文档。

---

## 1. 四层模型

```
┌─────────────────────────────────────────────────────┐
│ 交互层 (Interaction)                                 │
│ CLI · 人机对话 · session管理 · 审批触发              │
│ 组件: run_pipeline.py, clarify()                     │
├─────────────────────────────────────────────────────┤
│ 组合层 (Composition)                                 │
│ Pipeline编排 · 任务路由 · 审批门 · CallGraph         │
│ 组件: atom_pipeline.py, TaskRouter, Context          │
├─────────────────────────────────────────────────────┤
│ 原子层 (Atom)                  ← 两层契约接口        │
│ 认知原子 (6) · 机械原子 (可插拔)                      │
│ 组件: atom{0-6}_*.py, SKILL.md, base.py             │
├─────────────────────────────────────────────────────┤
│ 基础设施层 (Infrastructure)                           │
│ EvidenceChain · ReproContract · 文件持久化            │
│ 组件: context.py(EV), base.py(ReproContract)         │
└─────────────────────────────────────────────────────┘
```

**调用规则**：
- 上层可以调用下层；下层**绝不**调用上层（依赖单向）。
- 跨层通信仅通过明确定义的接口。

---

## 2. 路由器规格

### 2.1 形态：前置决策 + 短路出口

路由器在 pipeline 启动时**运行一次**，根据用户 query 判定复杂度并输出完整原子链。这是"前置决策"模式。

但保留一个**短路出口**：如果某个原子的输出暴露出链不再适用（最典型：原子1返回0篇论文），pipeline 可以提前终止剩余链，并将短路决策记录到 CallGraph。短路是**组合层行为**，不是原子行为（P2.2）。

```
用户query → Router.run() → atom_chain: [1, 2, 3, 4, 5, 6]
                              ↓
                          Pipeline 逐原子执行
                              ↓
                    原子1返回0篇 → pipeline短路
                    记录到CallGraph: "short_circuit at atom1, reason: empty_result"
```

### 2.2 路由判定规则

| 触发词类 | 复杂度 | 原子链 | skip_reasons |
|---------|--------|--------|-------------|
| 搜索关键词 (find/search/找/文献) | simple | [1] | 5个跳过理由 |
| 分析关键词 (analyze/分析/综述) | medium | [1, 2, 3] | 3个跳过理由 |
| 写作关键词 (write/写/撰写) | complex | [1, 2, 3, 4, 5] | 1个跳过理由 |
| 验证关键词 (verify/验证/评估) | full | [1, 2, 3, 4, 5, 6] | 无 |
| 无明确关键词 | medium (默认) | [1, 2, 3] | 默认链说明 |

### 2.3 路由器是认知原子

路由器归类为认知原子（P2），但其输出不进入 evidence_chain 的数据流——进入 **CallGraph** 的 routing 元数据。

---

## 3. 原子间通信协议

### 3.1 逻辑协议（原子接口）

每个原子的接口是：

```python
run(input_dict: Dict) -> Dict  # 返回 _ok() 或 _err() 信封
```

原子**不知道**通信机制（文件/内存/网络）。它只看到 `input_dict`，只返回信封。

**input_dict / output_dict 的具体 shape 由 `docs/atom-io-schemas.md` 定义**。每个原子的 SKILL.md 必须引用其对应的 schema 条目。

### 3.2 物理协议（pipeline 实现）

当前实现：**文件系统**。理由：
- P0 要求所有证据可审计 → 文件天然可读可 diff
- 无外部基础设施依赖
- 跨 session 持久化

物理承载物：`outputs/context/<run_id>/` 目录。

```
outputs/context/<run_id>/
├── knowledge-acquisition.json          # 原子1输出
├── knowledge-extraction_agent_output.json  # 原子2输出
├── ...
├── _accumulated.json                   # 累积上下文快照
├── callgraph.json                      # P0 执行追踪
├── pipeline_trace.json                 # 整体运行记录
└── approval_gates.json                 # P3 审批门（如有）
```

### 3.3 上下文累积规则

Pipeline 执行原子 N 时，`input_dict` = 所有前序原子的输出 merged。合并规则：
- 同名键：后覆盖前（原子6的输出可以覆盖原子1的同名字段）
- 信封解包：`_ok()` 返回的 `output` 字段被提取后再 merge
- `_chain` 字段记录执行序列，不可被覆盖

---

## 4. CallGraph 数据结构

CallGraph 回答 P0 的问题："这次运行中，谁被调用了、谁被跳过了、为什么"。

```
CallGraph = {
    routing_decision: str,        # "simple" | "medium" | "complex" | "full"
    routing_rationale: str,       # 人类可读的路径选择理由
    skipped_atoms: [str],         # 被跳过的原子名
    execution_trace: [
        {
            atom: str,            # 原子名
            type: str,            # "MECHANICAL" | "COGNITIVE"
            version: str,         # SemVer
            invoked: bool,        # 是否实际执行
            skipped: bool,        # 是否被跳过
            skip_reason: str,     # 跳过原因（如跳过）
            timestamp: str,       # ISO 时间戳
            duration_s: float,    # 执行时长
        },
        ...
    ],
    short_circuit: {              # 可选：短路信息
        at_atom: str,
        reason: str,
        triggered_by: str,        # "empty_result" | "error" | "approval_denied"
    }
}
```

---

## 5. EvidenceChain 传递规则

每个原子的输出信封携带自己的 `evidence_chain`，引用其输入来源。

**证据链节点类型**：

| source_type | source_ref | 示例 |
|------------|-----------|------|
| `doi` | DOI字符串 | `10.3389/fpsyt.2023.1260031` |
| `url` | URL + fetch_time | `https://api.semanticscholar.org/...` |
| `atom_output` | 上游原子名 | `knowledge-acquisition` |
| `empty_result` | 检索证据文件路径 | `empty_result_evidence.json` |
| `callgraph` | CallGraph节点哈希 | `cg:node:3` |

**传递规则**：
1. 原子1（机械）：evidence_chain 节点 = 每个数据源的 API 调用证据
2. 原子2-6（认知）：evidence_chain 节点 = 引用上游原子输出 + 自身的推理记录
3. 原子N 的证据链是 N-1 的超集（追加，不删除）

---

## 6. 受控变更流程的物理承载

| 产物 | 位置 | 格式 |
|------|------|------|
| 变更提案 | `docs/proposals/<YYYYMMDD>-<slug>.md` | Markdown，含模板字段 |
| 审批记录 | 提案文件末尾追加 | `## Approval` 节 |
| 变更日志 | `docs/change-log.md` | 反向时间序列表 |
| 宪法修订历史 | `docs/SKILL-principles.md` 末尾 | `## 修订历史` 节 |

**提案模板必含字段**：
- 提案日期、提案人（AI/人类）
- 变更类型（新增认知原子 / 修改金标准 / 原子版本升级 / 其他）
- 非重叠性证明（如是新增原子）
- 影响的组件清单
- 回滚方案

---

## 7. 原则 × 架构决策 追溯矩阵

| 架构决策 | 对应宪法条款 | 如果违反会怎样 |
|---------|------------|--------------|
| 路由器前置决策 + 短路出口 | P2.2（编排不下沉） | 短路逻辑进原子 → P2 违反 |
| 文件系统通信 | P0（证据可审计） | 换内存通信 → 证据不可 diff |
| input_dict/output_dict 接口 | P2.1（两层契约） | 原子知道文件路径 → 耦合 |
| CallGraph 独立于数据流 | P0.2（路径是证据） | 路由决策不记录 → 无法审计 |
| 受控变更提案模板 | P2.4 + P3.4 | 无模板 → 提案不完整 → 审批失效 |
| 原子不承载 P3 | P3.1 | 原子弹窗 → 审批疲劳 |
| 金标准绑定原子版本 | P1.4（金标准硬约束） | 改金标准不升版本 → 复现性崩溃 |

---

## 8. 组件目录

```
Synthos/
├── docs/
│   ├── SKILL-principles.md          # 宪法层
│   ├── SKILL-architecture.md        # 骨架层
│   ├── SKILL-spec-profile.md        # SKILL.md 规范适配层
│   └── atom-io-schemas.md           # 原子 I/O Schema 全集
├── core/
│   ├── atoms/
│   │   ├── base.py                  # AtomBase + ReproContract + EvidenceChain
│   │   ├── atom0_task_router.py     # 路由器（认知原子）
│   │   ├── atom1_knowledge_acquisition.py  # 知识获取（机械原子）
│   │   ├── atom2_knowledge_extraction.py   # 知识提取（认知原子）
│   │   ├── atom3_association_discovery.py  # 关联发现（认知原子）
│   │   ├── atom4_hypothesis_generation.py  # 观点生成（认知原子）
│   │   ├── atom5_argument_expression.py    # 论证表达（认知原子）
│   │   └── atom6_viewpoint_verification.py # 观点验证（认知原子）
│   ├── atom_pipeline.py             # 组合层：Pipeline 编排器
│   ├── agent_atom.py                # 组合层：认知原子 → Agent prompt 桥接
│   ├── context.py                   # 基础设施：Context + CallGraph + ApprovalGate
│   ├── llm_client.py                # 基础设施：可选外部 LLM 调用
│   └── __init__.py
├── run_pipeline.py                  # 交互层：CLI 入口
├── skills/                          # 原子层：SKILL.md 定义
│   ├── task-router/SKILL.md
│   ├── knowledge-acquisition/SKILL.md
│   ├── knowledge-extraction/SKILL.md
│   ├── association-discovery/SKILL.md
│   ├── hypothesis-generation/SKILL.md
│   ├── argument-expression/SKILL.md
│   └── viewpoint-verification/SKILL.md
├── outputs/context/                 # 运行时产物
└── scripts/                         # 辅助工具（待吸收）
```
