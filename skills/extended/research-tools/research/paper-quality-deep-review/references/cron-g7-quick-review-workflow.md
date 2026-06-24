# Cron G7 Deep Quick Review — 完整执行工作流

> **时间预算**: 15-30 分钟  
> **适用场景**: 定时 cron 任务中的 G7 深度评审（无用户在场）  
> **方法论依据**: `paper-quality-deep-review/SKILL.md` — Quick Review Mode  
> **方向约束依据**: `paper-pipeline/SKILL.md` — 研究方向约束  

---

## Phase 0: Candidate Detection (3 min)

### 0.1 加载核心技能

```
skill_view(name='paper-quality-deep-review')
skill_view(name='paper-pipeline')
```

### 0.2 扫描管线队列

读取 `/media/yakeworld/sda2/Synthos/outputs/papers/paper-queue.json`，对每个条目检查：

| 信号 | 含义 |
|:-----|:------|
| `gates.G7 == "N/A"` 或 `"PASS"` | 未做实质 G7 深度评审 |
| `notes` 中无 `g7_deep_review` / `g7_quality_review` 关键词 | 无深度评审记录 |
| `direction` 属于核心方向 | 见下方过滤器 |

同时扫描管线目录检查 `step_quality_review.md` 是否存在：

```bash
find /media/yakeworld/sda2/Synthos/outputs/papers/<paper_dir> -maxdepth 3 -name 'step_quality_review.md' 2>/dev/null
```

**无文件 + G7=N/A = 候选论文。**

### 0.3 方向过滤器

只评审核心方向论文：

| # | 方向 | 示例 paper_id |
|:--|:-----|:--------------|
| 1 | 瞳孔/虹膜分割 | `3d-eyeball-iris-segmentation`, `dual-ellipse-pupil-localization` |
| 2 | 眼球三维模型建模 | `3d-pupil-localization`, `kappa-*` |
| 3 | 半规管空间姿态 | `membranous-scc-reconstruction` |
| 4 | BPPV 虚拟仿真 | `bppv-*`, `BPPV-canalith-ODE` |
| 5 | VOR 数字孪生 | `tonic-VOR-PINN`, `torsional-VOR-PINN`, `VOR-cancellation-ODE` |
| 6 | 三维眼动算法组件 | `saccade-*`, `smooth-pursuit-PINN` |
| 7 | 公开数据集分析/方法论审计 | `pima-crispdm`, `crispdm-*`, `data-leakage-*` |
| 8 | Synthos 系统 | `synthos-*` |
| 9 | AI 辅助教学 | — |

**跳过**: 角膜/泪膜/晶状体/玻璃体/睑板腺/耳鸣/脑震荡等外围方向。

### 0.4 优先级排序

按 `quality_score` 降序排列候选论文，优先评审最高分论文。高分论文的 G7 门控假阳性风险最高（自动通过掩盖了实质问题）。

---

## Phase 1: 并行深度评审 (15-20 min)

### 1.1 委托并行评审（推荐）

每个 cron 轮次评审 **3 篇**（匹配 `delegate_task` 并行限制），委托命令：

```
delegate_task(
    goal="Perform G7 deep quick review on paper <paper_id>",
    context="""Paper path: /media/yakeworld/sda2/Synthos/outputs/papers/<paper_id>
Key info from state.json/queue.json: <G7 status, qs, D10a, steps>
...""",
    toolsets=["terminal", "file", "search"]
)
```

每个子代理独立完成：
1. 读取 `paper.tex`（Abstract → Contributions → Results → Limitations）
2. 读取 `paper.log`（统计编译错误/警告）
3. 检查 9 个失败模式（A-K）：placeholder figs, zero figs, disconnected components, multi-seed claims, citation gap-mismatch, code URL, synthetic data, hyperparameters, bib count mismatch
4. 统计 figure vs table 数量
5. 验证 D10a（交叉检查 cite 命令 vs bib/bbl 条目）
6. 评分 D1-D7 各维度（0-10 分）
7. 计算 Layer A avg（D1-D7 均值）
8. 生成 `07-quality/step_quality_review.md`
9. 更新 `state.json`（添加 `g7_deep_review` notes + `pipeline_trace` 条目）

### 1.2 检查的失败模式

| 模式 | 严重度 | 检测命令 |
|:-----|:-------|:---------|
| A: Placeholder Figures | 🔴 Critical | `grep -c 'To be generated\|\\\\textsl{' paper.tex` |
| A2: Zero Figures | 🔴 High | `grep -c '\\\\begin{figure}' paper.tex == 0` |
| B: Disconnected Components | 🔴 High | 追踪组件从声明 → 实现 → 系统动力学 |
| C: Multi-Seed Without Error Bars | 🟡 Moderate | `grep -c 'seed\|random' paper.tex` + 验证每个结果表有不确定度 |
| D: Citation Gap-Mismatch | 🟡 Moderate-High | 交叉检查 Introduction 引用 vs `\\bibitem` |
| E: Placeholder/Missing Code URL | 🟡 Moderate | 检查 Data/Code 声明中的具体 URL |
| F: Synthetic-Data-Only | 🔵 Variable | 搜索 `synthetic\|simulated`，需要明确范围声明 |
| H: Cross-Database No Citation | 🔴 High | 扫描 `03-code/*.py` 的数据集加载模式 |
| I: Self-Contradictory Limitation | 🔴 High | 检查 Limitations vs 实验代码 |
| J: Missing Hyperparameters | 🟡 Minor-Moderate | 搜索 `optimizer\|learning rate\|epoch\|batch size` |
| K: Bib Entry Count Mismatch | 🟡 Low-Moderate | `grep -c '@[a-z]*{' references.bib` vs cite 调用数 |

### 1.3 D1-D7 评分标准

| 维度 | 权重 | 含义 |
|:-----|:------|:------|
| D1: Contribution | 15% | 新颖性是否由空白扫描支撑？假设是否可证伪？ |
| D2: Methodology | 15% | ODE/PINN 公式是否合理？基线是否适当？ |
| D3: Data/Reproducibility | 15% | 图表是真实还是占位符？代码是否具体？ |
| D4: Literature | 15% | D10a=100%？Gap-mismatch？缺失关键工作？ |
| D5: Method Quality | 15% | SOTA 对比？训练细节？误差线？ |
| D6: Results Integrity | 15% | 目标是否达到？统计显著性？单/多 seed？ |
| D7: Code/Completeness | 10% | GitHub URL 真实？DOI 真实？图表存在？ |

Layer A avg = mean(D1..D7)。分级：
- **T1 PASS**: ≥ 8.0
- **T2 PASS**: ≥ 5.0
- **T3 FAIL**: < 5.0

---

## Phase 2: 结果验证 (3 min)

子代理返回后，**验证其输出**：

1. **文件验证**: 确认 `07-quality/step_quality_review.md` 已创建
   ```bash
   wc -l /media/yakeworld/sda2/Synthos/outputs/papers/<paper>/07-quality/step_quality_review.md
   ```

2. **state.json 验证**: 确认 `notes` 包含 `g7_deep_review_<date>` 且 `pipeline_trace` 追加了新条目
   ```bash
   python3 -c "import json; d=json.load(open('state.json')); n=d.get('notes',{}); t=d.get('pipeline_trace',[]); print([k for k in n if 'g7' in k.lower()], len(t))"
   ```

3. **补漏修复**: 如果子代理未正确更新 state.json，手动补加 notes + pipeline_trace

---

## Phase 3: 日志与报告 (2 min)

### 3.1 追加 Agent Log

使用 `patch`（禁止 `write_file`）在 `agent-log.md` 末尾追加摘要：

```markdown
## G7 Deep Review | YYYY-MM-DD (cron)
**Model**: <model> via <provider>
**Action**: G7 deep quick review on N core-direction papers

### Reviewed Papers
| Paper | qs | Layer A | Score | Key Findings |
|:------|:---|:--------|:------|:-------------|
| <paper> | N | N.N/10 | T1/T2 PASS | <2-line summary> |

### Summary
- N papers reviewed, X T1 + Y T2 PASS, Z FAIL
- Critical failures found: <count>
- D10a status: <summary>
- state.json updated: <all/most/partial>
```

### 3.2 Agent Log 附加协议

`agent-log.md` 被多个 cron 任务写入（autonomous-core-researcher, paper-repair, paper-layer-b-review, literature-monitor 等）。

**永远使用 `patch` 追加，禁止 `write_file`。** 如果误覆盖，从 session_search 重建。

---

## 常见陷阱

### ⚠️ Subagent 路径错误
子代理可能将文件写入 `/home/yakeworld/` 或错误路径。验证并纠正：
```bash
cp /home/yakeworld/07-quality/step_quality_review.md /media/yakeworld/sda2/Synthos/outputs/papers/<paper>/07-quality/step_quality_review.md
```

### ⚠️ Subagent state.json 更新不完整
子代理可能只更新了 `notes` 但未加 `pipeline_trace`，或反之。手动补全。

### ⚠️ state.json 中存在 `gates` 与 `gates_result` 两种结构
早期 pipeline 使用 `gates` dict，后期迁移到 `gates_result.gates[]` array。检查 state.json 的实际结构后再更新。

### ⚠️ 管线论文 vs article_todo 工作区论文
`paper-queue.json` 中的论文（`/media/yakeworld/sda2/Synthos/outputs/papers/`）使用标准 pipeline 结构。  
`~/桌面/article_todo/` 中的论文是工作区草稿，结构不统一（`paper.md` 而非 `paper.tex`），不适合 G7 评审。
