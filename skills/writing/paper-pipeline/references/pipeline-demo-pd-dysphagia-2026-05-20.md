# Pipeline 实战验证：PD误吸风险预测（2026-05-20）

## 摘要
从零到论文全流程验证 Synthos 论文管线，选用 PD误吸风险预测项目（63源文件，Proposal型项目），完整执行 P-1→P4 共9步，产出10页方法论框架论文。

## 关键发现

### 1. Proposal 型项目的处理策略
三步确权法判定为 Proposal → 论文定位调整为 Methodological Framework / Protocol Paper，Results 写理论设计参数而非实验结果。所有数值标注为"theoretical design values"。

### 2. 倒叙法写作顺序验证
写作顺序 P2.3(Results)→P2.2(Methods)→P2.4(Discussion+Conclusion)→P2.1(Introduction) 证明了倒叙法的有效性：Results 确定 Punchline 后，Methods 只需描述已验证路径，写起来更高效。

### 3. 理论驱动的可迁移性
CARS/图尔敏/金字塔/沙漏在同一管线中同时使用，互不冲突。CARS 管 Introduction，图尔敏管 Discussion，各自独立但总分一致。

## 产出统计
- 论文：10页, 309KB, 0错误, 0未定义引用
- 操作步数：15步（P-1:4步+P2:5步+P3:3步+P4:1步+中间2步）
- 耗时：约25分钟（含编译等待）
- 回传：PDF 已导入 NotebookLM 项目

## 与其他项目的管线对比
| 维度 | PIMA糖尿病 (实验型) | PD误吸 (Proposal型) |
|:-----|:-------------------|:--------------------|
| 数据 | 34模型实际运行结果 | 理论设计参数 |
| Results | 真实数值表格 | 理论设计参数表 |
| 文章定位 | 方法论基准论文 | 方法论框架/Protocol |
| 产出质量 | 16页, avg 0.79 | 10页, 全通过 |
| 引用 | 47篇 | 8篇（快速验证用） |
