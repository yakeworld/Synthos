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
- knowledge_entry_*.md（知识条目）
- research-queue.json（进度跟踪）
- state.json（状态记录）

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

### 进入论文管线
```bash
# 识别需要status.json的论文
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
