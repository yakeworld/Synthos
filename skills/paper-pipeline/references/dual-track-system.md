# 论文管线双轨制 (Dual-Track System)

> 2026-06-18 确立：论文质量为唯一KPI，研究空白进知识库不进论文管线。

## 核心原则

轨道A（论文管线）和轨道B（知识库）是两条平行轨道，不再混用。

| 维度 | 轨道A：论文管线 | 轨道B：知识库 |
|------|-----------------|---------------|
| 目标 | 产出完整SCI论文 | 积累研究空白/假设/洞察 |
| 入口 | 有paper.tex + status.json | 无paper.tex但有研究内容 |
| 流程 | G1-G7质量门禁 | 知识条目生成 |
| 入口触发 | 人工遴选/质量门禁通过 | cron产出/自动积累 |
| 出口 | ready_for_submission | 进入论文管线（如需） |
| KPI | 论文质量分数 | 研究积累数量 |

## 轨道A：论文管线

### 进入条件
- 有完整的paper.tex（≥2000字符）
- 有06-references/或references.bib
- 有01-manuscript/目录
- 状态为"pending_review"

### 流程
```
状态：pre-gate
  → G1: 文献检索（≥60候选, ≥30 PDF, DOI 100%）
  → G2: 知识提取（结构化提取）
  → G3: 关联空白发现（关联+空白矩阵）
  → G4: 假设生成（可证伪假设）
  → G5: 论文论证 + 引用全文验证
  → G6: 观点验证
  → G7: LaTeX编译验证
  → 状态：ready_for_submission
```

### 输出
- 07-quality/status.json（质量门禁记录）
- 09-submission/（提交包）
- 编译产物：paper.pdf

### 维护
- 每篇论文必须有status.json
- 无status.json = 未完成
- cron的paper-repair只处理有明确低分status.json的论文

## 轨道B：知识库

### 进入条件
- 无paper.tex
- 但有研究内容（有step_*.md文件、有参考文献、有代码、有目录）

### 内容类型
- 研究空白分析
- 科学假设
- 文献洞察
- 方法论探索

### 流程
```
cron产出（autonomous-core-researcher）
  → 知识库条目（knowledge_entry_*.md）
  → 更新research-queue.json
  → 人工评估是否进入轨道A
```

### 输出
- knowledge_entry_*.md（知识条目）→ 见下方产出物规范
- research-queue.json（进度跟踪）
- state.json（状态记录，含knowledge_score字段）

### 知识条目产出物规范

#### 文件结构

`knowledge_entry_{candidate_id}.md` — Markdown文件，包含以下必须节：

| 节 | 内容 | 示例 |
|:---|:-----|:-----|
| 元数据 | Type, Source, Status, Generated | Research Finding (Computational Modeling) |
| Research Gap | ABSOLUTE_WHITE 验证结果 | 6-query PubMed battery, 0 competitors |
| Approach | 方法概要 | 2-ODE coupled system + PINN |
| Key Findings | 核心数值结果表 | MAPE=7.8%, R²=0.93, n≈0.69 |
| Clinical Implications | 临床转化意义 | BVL grading, fall risk stratification |
| Methods Assessment | 方法学评价 | Competing approaches addressed, PINN advantages |
| Knowledge Score | 六维评分 + 加权平均 | gap_sig:0.85, method:0.80, overall:0.80 |
| Tags | 关键词标签 | `vestibular` `PINN` `absolute-white` |

#### Knowledge Score 六维评分矩阵

| 维度 | 权重 | 描述 | 示例高分 |
|:-----|:----:|:-----|:---------|
| Gap Significance | 0.25 | 研究空白的重要性和独特性 | ABSOLUTE_WHITE 验证通过，有临床需求 |
| Methodological Soundness | 0.20 | 方法的合理性和完整性 | ODE+PINN+, SO(3)约束, 控制实验 |
| Result Completeness | 0.20 | 结果覆盖面和证据强度 | 参数恢复+轨迹+分类+分岔+消融全方位 |
| Clinical Translation | 0.15 | 临床转化思路的清晰度 | BVL分级+跌倒风险+康复分层具体方案 |
| Reproducibility | 0.10 | 数据和代码的可复现性 | 合成数据+代码声明+清晰参数 |
| Narrative Quality | 0.10 | 知识条目的可读性和完整性 | 完整结构+引用链+领域标签 |

**加权平均 ≥ 0.80 → T2 PASS**。

#### quality_score 在每个步骤的基准分

| 步骤 | 基准分 | 说明 |
|:-----|:------:|:-----|
| literature_scan | 60 | 初始空白扫描完成 |
| gap_analysis | 65 | G6 first-mover 验证通过 |
| hypothesis_generation | 72 | 可证伪假说生成 |
| knowledge_entry | 80 | 完整知识条目产出 |

#### state.json 更新协议

knowledge_entry 完成后更新：

- quality_score: base + 2（从 gap_analysis 分值提升）
- gate_status: PASS
- 新增 knowledge_score: 0.0-1.0（六维加权平均）
- steps_completed: 追加 "knowledge_entry"

#### research-queue.json 递进

```
当前步骤完成 → 更新 steps_completed → 更新评分字段
→ 设置 current_step 为下一步或 null
→ 设置 next_candidate 为下一个 PENDING 候选
→ 失败则设 status=stuck + notes=原因 → 自动跳转
```

### 四步知识条目工作流（Autonomous Core Researcher）

```
Run N:   literature_scan     — 扫描研究空白，检查white space
Run N+1: gap_analysis        — 深入分析，明确G6 first-mover claim
Run N+2: hypothesis_generation — 生成可证伪假说
Run N+3: knowledge_entry     — 产出 knowledge_entry_*.md + 更新评分
                             → 完成后标记 candidate 为 completed
```

每步需要 `skill_view()` 加载对应的认知原子技能（knowledge-acquisition / knowledge-extraction 等）。每步产出文件放入候选目录（与 step_*.md 同层）。

### 维护
- 不生成.tex
- 不跑编译
- 不占论文目录配额
- 定期评估是否进入轨道A

## 状态转换

```
轨道A: pre-gate → in_progress → complete → ready_for_submission
轨道B: pending → in_progress → complete → [可选] → 轨道A

空壳: 0文件 → 删除
归档: 低价值 → _drafts_archive/
```

## 目录结构

```
outputs/papers/
├── _drafts_archive/          # 空壳归档（48篇）
├── _knowledge_only/          # 知识库轨道（34篇）
└── [论文目录]/               # 论文管线（66篇）
    ├── 01-manuscript/        # 手稿
    ├── 02-abstract/          # 摘要
    ├── 03-introduction/      # 引言
    ├── 04-methods/           # 方法
    ├── 05-results/           # 结果
    ├── 06-discussion/        # 讨论
    ├── 06-references/        # 参考文献
    ├── 07-quality/           # 质量门禁
    │   └── status.json       # 质量门禁记录
    └── 09-background/        # 背景
```

## 操作协议

### 清理空壳
```bash
# 识别空壳（<5文件）
find papers/ -maxdepth 1 -type d | while read d; do
  count=$(find "$d" -type f | wc -l)
  if [ $count -lt 5 ]; then
    mv "$d" "_drafts_archive/"
  fi
done
```

### 移入知识库
```bash
# 识别无.tex但有内容的论文
find papers/ -maxdepth 1 -type d | while read d; do
  if [ ! -f "$d/01-manuscript/paper.tex" ] && [ $(find "$d" -type f | wc -l) -gt 5 ]; then
    mv "$d" "_knowledge_only/"
  fi
done
```

### 进入论文管线（晋升协议）

```bash
# 识别 _knowledge_only/ 中有 paper.tex 但未入 Track A 的候选人
KNOWLEDGE="outputs/papers/_knowledge_only"
PAPERS="outputs/papers"
for d in "$KNOWLEDGE"/*/; do
    name=$(basename "$d")
    if [ ! -f "$d/paper.tex" ] && [ ! -f "$d/01-manuscript/paper.tex" ]; then
        continue  # 无 paper.tex → 保持 Track B
    fi
    
    # 检查 paper-queue.json 是否有冲突
    if grep -q "\"$name\"" "$PAPERS/paper-queue.json" 2>/dev/null; then
        echo "⚠️ 冲突: $name 已在 paper-queue.json 中"
        continue
    fi
    
    # 轻量晋升：mv + index.md + paper-queue.json 入队
    mv "$d" "$PAPERS/$name"
    
    # 创建 index.md（如不存在）
    if [ ! -f "$PAPERS/$name/index.md" ]; then
        echo "---" > "$PAPERS/$name/index.md"
        echo "source: promoted_from_track_b" >> "$PAPERS/$name/index.md"
        echo "promoted_at: $(date -Iseconds)" >> "$PAPERS/$name/index.md"
        echo "---" >> "$PAPERS/$name/index.md"
    fi
    
    # 确保 paper.tex 在正确位置
    if [ -f "$PAPERS/$name/paper.tex" ] && [ ! -f "$PAPERS/$name/01-manuscript/paper.tex" ]; then
        mkdir -p "$PAPERS/$name/01-manuscript"
        ln -sf "../paper.tex" "$PAPERS/$name/01-manuscript/paper.tex"
    fi
    
    # 入 paper-queue.json（基础条目）
    echo "$name 晋升到 Track A"
done

# 识别 need_status.json 的论文
find papers/ -maxdepth 1 -type d | while read d; do
  if [ -f "$d/01-manuscript/paper.tex" ] && [ ! -f "$d/07-quality/status.json" ]; then
    echo "$d" >> "need_status.json"
  fi
done
```

## 注意事项

1. 论文数量不再是KPI，质量才是
2. 每篇论文必须有status.json，否则不算"完成"
3. cron产出直接走轨道B（知识库），论文需要人工遴选
4. 空壳直接删除，不占管线空间
5. 归档目录不纳入活跃论文统计
