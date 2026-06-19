# G7 Deep Quality Review — Autonomous Workflow

> **适用场景**：自主（cron/无用户交互）执行 G7 深度质量评审，对低质量论文进行 7 维全面评估。
> **首次应用**：3wd-framework-trustworthy-clinical-ai (2026-06-19), quality_score=25.
> **前置技能**：quality-gate (P0 闸门), paper-pipeline, paper-references-scanning.

## IO_CONTRACT

- **input**: `papers_dir` — Synthos 论文目录路径
- **output**: `review_report` — 结构化 G7 评审报告（7维评分 + 修复建议 + 估计后修复分数）
- **gate_triggers**: quality_score < 80 且 gate_status = FAIL 或 gate_status 缺失 → 自动进入 G7 深度评审

## 触发条件

- 质量闸门触发 G7 层级
- Cron 例行扫描发现 quality_score < 80 的论文
- 自动推进流水线检测到 stuck-at-complete-steps 但 gate FAIL 的论文

## 工作流

### Step 1: 候选论文扫描

```bash
# 遍历所有状态文件，提取 quality_score
find <papers_dir> -name "state.json" -maxdepth 3 | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  score=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('quality_score','N/A'))" 2>/dev/null)
  echo "$score|$name|$f"
done
```

**选择规则**（优先级排列）：
1. 最低 quality_score 的活跃论文（非 `_drafts_archive/`、非 `_knowledge_only/`、非 `09-manuscript/`）
2. 活跃论文中 gate_status = FAIL 且 steps_pending 有未执行项的优先
3. 分数相同时选 last_updated 最旧的优先（长期未处理）

**排除规则**：
- `_drafts_archive/` 下的论文视为归档不处理
- `_knowledge_only/` 下的论文仅用于知识引用不评审
- 子目录 `09-manuscript/` 内的 state.json 忽略（它是父论文的嵌套）
- quality_score = N/A 或 None 的跳过（尚未初始化）
- vestibular-compensation-ODE: quality_score=4.9 但实际是 5.0 分制（相当于 98/100），需区分

### Step 2: 加载评审上下文

读取文件按顺序执行：

```
1. state.json                          → 全局状态：quality_score, gate_status, gates_result, metrics, 7-dim scores
2. step_quality_check.md               → 原始 G1-G11 门检结果
3. step_quality_review.md              → 已有的 G7 深度评审（如果存在）
4. step_remediation.md                 → 已有的修复计划和进度
5. paper.tex                           → 完整稿件
6. step_method.md / step_results.md    → 分节生成的工作文件（检查一致性）
```

**关键检查点**：step_method.md 和 step_results.md 中的数值和形式化表示是否与 paper.tex 一致。如果不一致，这本身就是 G4/G5 硬失败。

### Step 3: 七维深度评估

七个维度的评分标准和关键诊断问题：

| 维度 | 权重 | 核心问题 | 低分标志 | 高分关键 |
|------|------|----------|----------|----------|
| D1 科学贡献 | 0.20 | 核心想法是否站得住？ | 论断超出证明范围、概念混淆 | 清晰匹配的问题-方法-贡献链条 |
| D2 方法学 | 0.20 | 实验设计是否无懈可击？ | 数据泄露、超参数无理由、架构不一致 | 严谨的符号体系+算法伪代码+控制实验 |
| D3 结果 | 0.15 | 数值是否可信可追溯？ | step文件与paper.tex不一致、缺少源文件 | 实验日志+CSV输出+一致表格 |
| D4 完整性 | 0.10 | 所有必要部分是否都存在？ | 空目录、缺失图表、无附录 | IMRaD完整+代码+数据+图表+补充材料 |
| D5 清晰性 | 0.10 | 论证是否清晰无歧义？ | 双形式化体系、非正式用语、矛盾描述 | 单一一致的形式化、精确的论断语言 |
| D6 新颖性 | 0.15 | 相对于现有文献的新贡献？ | 文献调查不足、论断夸大 | 精确的白空间声明、完整的文献比较 |
| D7 引用质量 | 0.10 | 参考文献是否准确？ | DOI不匹配、遗漏关键文献、不可靠来源 | D8≥30, D10a=100%, DOI≥90%, 无伪造 |

**计分方法**：每个维度 0.0–1.0，最终 quality_score = 加权平均 × 100。

**高亮检查模式**（源自实战经验）：

**Theorem/Claim 对比检查**：将 paper.tex 中 abstract 的论断与 Theorem 的证明结论逐句对比。常见模式：abstract 说"证明 X"，Theorem 实际证明的是"Y≤X"。如果断言和证明之间有空隙，这就是 D1/D5 双扣分。

**三文件一致性检查**：将 paper.tex 表、step_results.md 表、step_method.md 公式并列对比。任何数值差异 > 2% 或方法描述差异（不同算法/不同模型/不同成本函数）都是 G4 硬失败。

**数据结构完整性检查**：检查 03-code/, 04-data/, 05-figures/ 目录是否为空。空目录 = G7 硬失败（不可复现）。

### Step 4: 与已有评审和修复计划交叉引用

读取已有的 `step_quality_review.md` 和 `step_remediation.md`：
- 如果评审已在数天前完成但 remediation 未执行 → 评估进度，给出**追加建议**而非重写
- 如果 remediation 已有 Round 分配 → 确认当前轮到哪一轮，为下一轮提供具体指令
- 如果尚无 remediation → 创建完整的 8 轮修复计划（见模板）

**不要重复已做的工作**。如果某个 DOI 已经在 remediation Round 1 中修复，不要在报告中再次要求修复同一条。

### Step 5: 生成结构化报告

报告结构：

```
---
# ⚕️ G7 Deep Quality Review — <paper_title>

## 1. Paper Overview
(方向、分数、状态)

## 2. Seven-Dimension Deep Analysis
### D1 — Scientific Contribution (current: X → target: Y)
### D2 — Methodological Rigor
### D3 — Results
### D4 — Completeness
### D5 — Clarity & Language
### D6 — Novelty
### D7 — Citation Quality

## 3. Execution Status of Existing Remediation Plan
(如果已有 plan，逐 round 标注状态)

## 4. Critical Path & Priority Action Items
### 🔴 P0 — Must fix
### 🟡 P1 — High priority
### 🟢 P2 — Medium priority

## 5. Post-Fix Quality Score Estimate
(表格：当前 → 各修复阶段后 → 最终估计)

## 6. Key Recommendations for Next Executor
```

### Step 6: 后修复分数估计方法

| 阶段 | 分数范围 | 条件 |
|------|---------|------|
| 当前 | 原始 | 从 state.json 读取 |
| 代码修复后 (G7) | +15~20 | 创建 experiment.py + 数据脚本 + 图表 |
| 度量同步后 (G4) | +10~15 | 运行真实实验、统一 paper.tex 与代码输出 |
| 方法论修复后 (G5) | +10~15 | 修复泄露实验、统一形式化、修正论断裂言 |
| 文献补充后 (G2/G3) | +5~10 | 添加缺失引用、调整新颖性措辞 |
| 全文审查后 (完整) | +5 | 图表生成、补充材料、编译清理 |

**上限**：对于 G4/G5/G7 三个硬失败全部存在的论文，最大后修复分数约 70-75/100（不会一次达到 90+）。

## 常见陷阱

1. **分数制混淆**：某些纸上 state.json 的 quality_score 是 5 分制（如 vestibular-compensation-ODE: 4.9 ≈ 98/100）。检查 metrics 字段是否有 MAPE/R² 等数值来分辨。如果 quality_check.md 说 "Overall: 4.90/5.0"，则 quality_score 是 5 分制，需 ×20 转换为百分制。

2. **step_quality_check.md 中的虚高自评**：某些纸上自己的 Quality Check 自评满分但真实的 quality_score 很低。**不要相信自评**，以 state.json 的 gates_result 为准。

3. **修复计划执行顺序依赖**：G7 代码修复（Round 2）必须在 G4 度量同步（Round 3）之前，因为度量同步需要真实实验输出。不要安排并行执行。

4. **陈旧评审不可复用**：如果 quality_review.md 的日期超过 7 天且期间有新的 state.json 更新，需要重新评估而非引用旧结果。

5. **批量扫描时注意排除项**：`_drafts_archive/`, `_knowledge_only/`, 和嵌套的 `09-manuscript/` 中的 state.json 不应作为 G7 评审的候选对象。
