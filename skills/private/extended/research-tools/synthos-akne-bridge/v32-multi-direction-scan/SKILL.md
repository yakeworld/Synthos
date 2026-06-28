---
name: v32-multi-direction-scan
description: "Five rotation + five exploration directions. Mode-determined scan: KNOWLEDGE_PIPELINE → SCAN_AND_CREATE → SCAN_AND_REPORT. ABSOLUTE_WHITE detection with cross-source validation."
version: 3.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "research_domain: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: [paper-pipeline, autonomous-execution-threshold]
    ref_skills: [citation-bib-crossref, dataset-discovery]
---

## 思想

研究方向扫描的本质：**在知识空间中探测空白，在时间维度上追踪变化。**

扫描不是重复劳动。每一次扫描必须回答三个问题：
1. 竞争格局是否变化（thawing 或 frozen）
2. 我的假设是否被外部文献验证或威胁
3. 队列中有什么需要推进

扫描的结果要么是一个候选方向，要么是对当前状态的确认。后者同样有价值——知道"什么都没变"就是推进。

## 原则

### P1: 三模式决策（Step 0）

每次扫描开始前，先判断操作模式。模式由两个变量决定：`queue_pending` 和 `edit_budget.remaining`。

| queue | budget | 模式 | 行为 |
|:------|:-------|:-----|:-----|
| >0 | 任意 | KNOWLEDGE_PIPELINE | 推进队列中下一个候选 |
| =0 | >0 | SCAN_AND_CREATE | 扫描→发现空白→注册候选 |
| =0 | =0 | SCAN_AND_REPORT | 扫描→报告→不写文件 |

**预算脱同步检测**：如果 `evolution-state.json` 显示 `consumed=0` 但 `agent-log` 显示 5+ 连续 SCAN_AND_REPORT，则状态文件已过期，以日志为准。

**不要自动修复**：状态文件需要写权限，可能超出预算。记录差异，让用户或下次进化修复。

### P2: 五维旋转扫描

覆盖 9 个核心研究方向，按维度分两组：

**A组 — 分割与几何**
1. 瞳孔/虹膜分割 + PINN/ODE
2. 3D 瞳孔定位与 Kappa 角

**B组 — 前庭动力学**
3. SCC 杯状体计算模型
4. BPPV 数字孪生
5. VOR 数字孪生

每个方向执行 PubMed 精准查询 + OpenAlex 广度交叉验证。

### P3: 五维探索扫描

**探索 A — 算法与数据**
1. 眼动追踪算法组件
2. 新公共数据集
3. 公开数据集方法论审计

**探索 B — 临床转化**
4. 眼震计算模型
5. 瞳孔动力学 + 衰老/AD 生物标志物

### P4: ABSOLUTE_WHITE 验证

如果一个方向 PubMed=0 且 OpenAlex PINN/NeuralODE=0：
- 标记为 ABSOLUTE_WHITE
- 在核心方向内 → 注册为候选
- 在边缘方向 → 记录空白+假设

**交叉验证规则**：OpenAlex 返回大量结果时需手动验证相关性。双字查询易产生同义词碰撞（SCC→small cell carcinoma）。

### P5: 静态检测守卫

SCAN_AND_REPORT 模式下，如果连续 3+ 次扫描结果完全相同：
- 降级为单点探测（最敏感方向，如 PLR-H1）
- 单点探测结果：不变则 [SILENT]，变化则全量重启

**深度探测协议**：当单点探测连续 20+ 次无变化时，深度探测本身成为盲区。每 10 次触发全维度深度扫描（9 个查询并行）。

### P6: 间隙优先级评分

每个候选方向评分（满分 25）：
1. 新颖性（0竞争=最高分）
2. 临床相关性
3. 可行性（数据/设备，1-5）
4. 内核复用（K-001..K-016）

阈值 ≥17 → CANDIDATE 进入队列。

### P7: 三重碰撞防御

PubMed 和 OpenAlex 搜索中最大的系统性误差来源：

**1. 缩写碰撞** — 三字母缩写匹配完全不同的医学领域
- PLR → 血小板/淋巴细胞比率（非瞳孔光反射）
- ODE → 视盘水肿（非常微分方程）
- 每次遇到意外的计数峰值，第一反应是检查标题是否匹配错误领域

**2. 自我污染** — 自己的论文被误认为竞争对手
- 扫描已有 5+ 篇发表的方向时，先运行 PINN/NeuralODE 子过滤器
- 如果子过滤器=0，报告 ABSOLUTE_WHITE。自己的论文不计数

**3. 查询漂移** — 不同周期使用不同查询字符串
- 每次扫描前读取 `agent-log.md` 找到上一个周期的确切查询
- 逐字复制，不靠记忆
- 任何有意宽化的查询标注版本号和基数

### P8: 时间维度检测

**外部验证加速度**：比较连续周期的计数。PLR-H1 从 5→11 表示文献积累加速，比快照本身更有验证价值。

**终端 plateau**：10+ 连续相同计数（如 5）= 终端 plateau。2025 年队列饱和。记录为战略信号：假设被验证，但先发窗口收窄。

## 方法

### 标准扫描流程

```
1. Step 0: 读取队列+预算 → 确定模式
2. Step 1: 执行 5 维旋转扫描
3. Step 2: 执行 5 维探索扫描
4. Step 3: ABSOLUTE_WHITE 交叉验证
5. Step 4: 间隙优先级评分
6. Step 5: 队列生命周期检查
7. Step 6: 后耗尽协议（mode=SCAN_AND_REPORT）
8. Step 7: 检查清单验证
9. Step 8: 进化状态同步
```

### 后耗尽协议（Step 6）

当队列空+预算=0时：

1. **Track A 就绪检查**：读取各论文 `submission-manifest.json`，交叉验证 quality_score。Layer B <0.75 但标记 ready_for_review → 标记异常
2. **文章工作室检查**：`ls ~/桌面/article_todo/` 检查成熟论文数量和状态
3. **报告当前状态**：队列、提交、扫描发现、下次推荐
4. **禁止创建文件**：只追加日志，不创建新条目

### 检查清单（Step 7）

- [ ] 模式正确确定
- [ ] PubMed + OpenAlex 查询执行
- [ ] ABSOLUTE_WHITE 交叉验证
- [ ] 日志更新（追加，不覆盖）
- [ ] 进化状态一致性验证
- [ ] SCAN_AND_REPORT 下无文件创建

## 规则

1. **不重复扫描已完成方向** — 21 个原始 v32 候选已全部完成，改用 9 个核心约束方向
2. **PINN/NeuralODE 子过滤器优先** — 在任何方向上，先运行窄子过滤器，确认=0再报告空白
3. **查询必须版本化** — 每次扫描引用上一个周期的确切查询字符串
4. **追加而非覆盖** — 日志更新只追加，永远不覆盖
5. **预算=0时不创建** — 只报告，不创建新文件/条目/模板
6. **连续 10+ 相同推荐** — 精简为单行引用，不重复完整列表

## 案例参考

### 查询字符串示例（来自 references/iclr-competition-queries.md）

PINN-only 子过滤器标准查询（避免 ODE 缩写碰撞）：
```
("endolymph" OR "Meniere") AND ("PINN" OR "physics-informed" OR "NeuralODE") AND 2020:2026[dp]
```

PLR-H1 窄 AD 探测（避免 PLR 缩写碰撞）：
```
("pupillometry" OR "pupil light reflex") AND ("Alzheimer" OR "MCI") AND 2025:2026[dp]
```

### 深度探测查询（来自 references/external-validation-trends.md）

全 9 维深度探测覆盖：分割+DL、3D定位、SCC模型、BPPV模拟、VOR模型、PINN交叉、眼震、AD标志物、数据集。

### 参考文件

- `references/iclr-competition-queries.md` — 5个ICLR领域的标准PubMed查询
- `references/batch-scan-pattern.md` — 单次Python调用批量执行10+查询
- `references/pubmed-json-keys.md` — NCBI JSON键映射表（小写）
- `references/pubmed-api-resilience.md` — PubMed API不稳定时的容错模式
- `references/openalex-api-failure-diagnosis.md` — OpenAlex返回-1的诊断
- `references/external-validation-trends.md` — 跨周期外部验证计数记录

## 陷阱

### 缩写碰撞（最高优先级）

PLR、ODE、SCC 等三字母缩写是系统性误差的最大来源。任何意外的计数峰值，第一反应是检查标题是否匹配错误领域。

### 自我污染

自己的论文被误认为竞争对手是已知模式。扫描有5+篇发表的方向时，先运行窄子过滤器确认。

### 查询漂移

不同周期使用不同查询 = 假阳性。必须逐字复制上一周期查询。

### 静态守卫盲区

单点探测连续20次无变化后，守卫本身成为盲区。每10次必须触发全维度深度扫描。

## 变更日志

| 版本 | 日期 | 变更 |
|:-----|:-----|:-----|
| 3.0.0 | 2026-06-27 | 重构为"思想-原则-方法-规则"结构。从60KB压缩至~10KB。具体实现细节移至references/目录。 |
| 2.0.21 | 2026-06-24 | 添加Cycle 245 vhit漂移案例 |
| 2.0.20 | 2026-06-24 | PubMed ODE/视盘水肿碰撞 |
| 2.0.0 | 2026-06-23 | 对齐paper-pipeline 9核心约束；添加Step 0模式决策；添加后耗尽协议 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。