# NotebookLM 论文质量评审工作流

> 用途: 使用NotebookLM对论文进行质量评审 + 可执行的补救改进
> 版本: v2 (2026-05-22) — 增加5门逐级评审 + 【必答】补救指令

---

## 评审模式选择

| 模式 | 适用场景 | 耗时 | 输出 |
|:-----|:---------|:----:|:-----|
| **5门逐级** (Q1→Q5) | 初稿完整评估，每门含补救 | 30-60min/篇 | 评分+搜索词+LaTeX代码 |
| **单门快速** (仅Q5) | 已定稿论文快速反馈 | 2-3min/篇 | 7维评分+宏观建议 |

## 5门逐级评审

**执行规则**：Q1→Q2→Q3→Q4→Q5，一次一门，不跳步。每门PASS后才进入下一门。

每门必须包含**【必答】补救指令**：
```
**【必答】对于评分<0.85的维度，请逐一给出具体的补救方案：**
- 缺失了什么?列出标题/DOI
- 应该用什么检索词在哪个数据库搜索?
- 时间范围和过滤条件建议?
```

完整5门模板见 `paper-pipeline/skills/paper-pipeline/references/notebooklm-quality-gates.md`。

## 单门快速评审 (Q5)

```bash
# 1. 上传论文源码
cp paper.tex /tmp/paper-current.md
notebooklm use <project_id>
notebooklm source add /tmp/paper-current.md

# 2. 执行7维评审
notebooklm ask "请对论文进行全面7维SCI质量评审，每维评分(0-1)和改进建议：
1. 科学贡献 2. 方法学严谨性 3. 结果可信度 4. 完整性 5. 清晰性 6. 新颖性 7. 引用质量
**【必答】对于评分<0.85的维度，请给出具体的改进建议和LaTeX修改代码。"
```

## NotebookLM 评审 vs 人工评审

| 方面 | NotebookLM评审 | 人工评审 |
|:-----|:---------------|:---------|
| 速度 | 60-90秒/门 | 15-30分钟 |
| 深度 | 基于全量源文件（含引用PDF） | 仅基于论文文本 |
| 评分 | 通常偏高(+0.05~0.15) | 更严格 |
| 建议 | 宏观方向性+可执行补救 | 微观逐句修改 |
| 最佳用途 | 初稿快速反馈+方向指引+文献检索 | 定稿前最终把关 |

## 补救执行流程

```bash
# 当Q1覆盖度<0.85时，按NotebookLM建议的检索词执行：
notebooklm source add-research "suggested query" --mode deep --no-wait
notebooklm research wait --import-all
notebooklm ask "重新评估该维度，是否有改善?更新后的评分?"
```

## 输出保存

```bash
# 1. 评分摘要 → outputs/papers/papers-to-notebooks.md → 质量评审记录节
# 2. 详细建议 → <paper-dir>/notebooklm-review.md
```
