# NotebookLM-to-SCI-Paper 生成工作流

从NotebookLM笔记中提取自有算法，建立对比矩阵，生成SCI论文初稿。2026-05-19实践验证：VOR-Kappa + T3EM-Net两篇论文。

## 触发条件

用户说"从NotebookLM中选一个成熟项目写论文"或"生成这个笔记的论文"

## 6步工作流

1. ACQ竞争对手搜索 — 方法学论文只需覆盖主要竞争对手(3-5个)，构建对比矩阵
2. EXT自有算法提取 — 从NotebookLM Pasted Text提取核心创新/架构/公式
3. ASC+GAP定位空白 — 论证方法在至少一个维度上有本质区别
4. ARG生成论文 — IMRaD结构，Introduction含对比表
5. 数据填充 — 仿真或回算数据填充Results
6. 质量门 — G7自动运行(引用>=30条/无未用/编译零错/DOI完整)
