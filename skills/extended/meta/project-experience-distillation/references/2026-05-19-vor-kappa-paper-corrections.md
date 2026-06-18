# VOR-Kappa 论文生成经验（2026-05-19）

## 模式：数学推导 + 仿真验证 + Quality Gate 完整闭环

从一次完整的 SCI 论文生成流程中提取的模式。适用于方法学论文（有新算法/数学推导 + 仿真验证）。

### 流程

1. **从 NotebookLM 提取算法** — 用户 notebook 中的 Pasted Text 源包含算法代码 + 推导
2. **直接写 LaTeX 骨架** — IMRaD 结构
3. **嵌入比较矩阵** — Semantic Scholar/OpenAlex 搜竞争对手，建立对比表
4. **编写仿真脚本** — 用 forward model 生成 synthetic data，验证 reverse algorithm
5. **生成图表** — RMSE 图、Bland-Altman 图
6. **填充 Results** — 数据驱动，不空留占位符
7. **Quality Gate G7** — 30 bib, cite-bib 1:1, 零 error 后才报告完成

### 陷阱

| 陷阱 | 表现 | 修复 |
|:-----|:------|:-----|
| 完成论文后忘记跑 quality gate | 用户纠正"又要重复这个质量检查的流程啊" | 写 sci-paper-standard-structure skill 强制 Step B |
| Results 留空占位符 | 生成论文后声称完成了，但 Table 为空 | 必须先写仿真脚本填充数据 |
| 引用篇数不足 | v1 只有15篇引用 | 从 OpenAlex/PubMed 批量补到30+ |
| LaTeX 转义破坏 | patch tool 把 \item 变成 \\item | 用 skill_manage patch 不能含转义引号 |

### 五层提取

| 层 | 内容 |
|:---|:------|
| 思想 | SCI 论文不是骨架就完成，是数据填充+质量门验证后才算完成 |
| 规范 | 论文生成后自动 G7 闸门 |
| 规律 | 方法学论文 = 推导 + 仿真验证 + 对比表 + 30+引用 |
| 能力 | 仿真脚本生成、结果图绘制、BibTeX 管理 |
| 任务 | 见上面流程 |
