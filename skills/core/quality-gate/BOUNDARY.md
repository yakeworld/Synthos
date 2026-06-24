# Quality Gate — Boundary Definition

## What Quality Gate Covers

- **L0 动灵层**: 交付物/技能方向与系统生长路径一致性检查
- **L0.5 数据诚实门**: 论文中可验证数据声明的源文件支撑验证
- **L1 响应级**: 当前会话输出质量（PreResponse Hook）
- **L2 项目级**: 交付物 D1-D6 完成质量
- **L3 管线级**: 论文 G1-G7 原子闸门（每阶段切换触发）
- **L4 内容级**: SCI 7维评审（G7通过后自动）
- **G5 引用质量**: 形式检查（D10a/孤儿/僵尸/DOI）+ 实质检查（引用恰当性）
- **提交材料**: G7通过后的 Cover Letter、Highlights、Graphical Abstract、Author Info、Submission Checklist

## What Quality Gate Does NOT Cover

| Area | Reason | Owner |
|------|--------|-------|
| 论文内容创作 | 科学论证、实验设计、写作逻辑 | Human + argument-expression |
| 文献检索与下载 | 知识获取、PDF下载、三级验证 | knowledge-acquisition |
| 引用文献PDF内容阅读 | 逐篇阅读全文做实质检查（无法自动化） | citation-appropriateness-verification |
| 代码实现 | 实验代码编写、运行、调试 | software-development |
| 进化决策 | 四态决策、GEPA反射、Pareto优化 | evolution |
| 任务路由 | 复杂度判断、4种执行模式选择 | task-router |
| 语义审查 | claim是否站得住、论证链完整性 | paperjury |

## Overlap with Other Skills

| Skill | Boundary |
|-------|----------|
| paperjury | quality-gate负责可量化检查，paperjury负责语义审查。G7通过后quality-gate L4 → paperjury review |
| evolution | evolution修复技能结构，quality-gate检查技能质量。进化后需重新过质量门 |
| citation-appropriateness-verification | quality-gate L4调用它做引用实质检查。形式检查在paper-references-scanning |
| sci-paper-quality-review | quality-gate L4的具体评审执行器。quality-gate负责触发和状态流转 |
| paper-pipeline | quality-gate是管线的质量门，paper-pipeline是管线的执行流程。G1-G7切换时触发 |
| reference-verification | quality-gate调用它做DOI存在性和格式验证（形式检查） |

## Failure Modes

1. **质量门被跳过**: 无skill_view记录 = 门不通过。必须显式调用skill_view
2. **G5引用质量未验证**: 论文质量上限=引用质量。G5不通过则全篇不合格
3. **数据源缺失**: L0.5要求可验证数据有源文件支撑，无源文件数据必须删除
4. **方向错误**: L0检查方向一致性，方向不对不进入技术检查
