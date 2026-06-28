---
name: training-pipeline-audit
description: "训练管线全面审计 — 从代码+数据+文档出发，提取研究空白、科学假设、论文撰写计划。"
version: 1.0.0
author: "Synthos + 用户杨晓凯"
metadata:
  synthos:
    priority: P1
    atom_type: research
    description: "从训练管线/实验代码/数据文件出发，系统性地提取研究空白、生成可检验假设、产出SCI论文撰写计划。"
    signature: "pipeline_dir: str -> audit_report: dict (project_summary, research_gaps, hypotheses, paper_plan)"
    related_skills: [hypothesis-generation, data-driven-hypothesis, paper-pipeline, sci-paper-standard-structure, research-skill-audit]
---

# Training Pipeline Audit

## 原理层·文言

> 代码为器，数据为粮，管线为径。审器观径，察粮析理，空白自现，假说乃生。
> 先见其全，后察其微。知其然，更知其所以然。

## 触发条件

当用户指向一个训练管线/实验代码目录并要求"分析""提取空白""写论文"时执行此技能。

## 核心流程（四阶段）

```
数据审计 → 管线分析 → 空白/假设 → 论文计划
  (1h)       (2h)       (2h)       (1h)
```

### Phase 1: 项目数据审计

1. **目录结构扫描**: `find` + `du` 了解整体规模
2. **核心文件读取**: README.md, PIPELINE.md, iris_config.json 等配置
3. **数据文件统计**: 图像数量、标签数量、训练/验证集划分
4. **训练结果提取**: train.log、best_model.pth、评估指标(Val Dice/CErr等)
5. **可视化文件**: 选择关键图示(viz_*.png)
6. **代码结构**: 管线脚本数量、模型架构、训练策略

**产出**: 项目概要报告(数据规模、方法、结果)

### Phase 2: 管线深度分析

1. **管线步骤拆解**: 每个Step的方法论、输入/输出、参数
2. **关键参数分析**: 固定参数 vs 可调参数、参数来源(解剖学先验/数据驱动)
3. **模型架构分析**: 网络结构、损失函数、优化策略、训练阶段设计
4. **数据策略分析**: 数据来源、混合训练策略、数据增强
5. **版本演进**: 管线版本历史(v1→v2→v6)，关键修复记录

**产出**: 管线方法论报告

### Phase 3: 研究空白 + 科学假设

基于Phase 1-2的发现，系统性识别：

**研究空白(Gap)判定标准**:
- Gap必须是项目中发现的，而非凭空想象
- Gap必须在文献中确实不存在解决方案
- Gap必须可验证(有具体的淘汰条件)

**科学假设(Hypothesis)生成格式**:
```json
{
  "name": "H1",
  "claim": "明确的可验证声明",
  "type": "primary",
  "falsification": "什么结果能证伪该假设",
  "testable_prediction": "具体可测量的预测",
  "baseline_to_beat": "需要超越的基线方法",
  "suggested_design": {
    "type": "消融实验",
    "population": "K230帧+OpenEDS",
    "sample_size": "100帧",
    "key_measurements": ["Val Dice", "CErr"]
  },
  "scores": {
    "testability": 0.9,
    "novelty": 0.7,
    "importance": 0.8,
    "feasibility": 0.85,
    "overall": 0.81
  }
}
```

**假设要求**:
- 至少3-5个假设(H1主攻，H2/H3辅助验证)
- 每个假设必须有falsification条件
- 每个假设必须可量化验证
- 假设之间可以互补或竞争

**产出**: gap_analysis.json + hypotheses.json

### Phase 4: 论文撰写计划

基于空白和假设，推荐论文路径：

**论文类型选择**:
| 论文类型 | 适用场景 | 数据需求 | 目标期刊 |
|----------|----------|----------|----------|
| 方法学论文 | 管线完整+有实证结果 | 训练结果+管线描述 | Q1-Q2 |
| 实证分析论文 | 有对比实验/消融实验 | 对比数据+统计检验 | Q2-Q3 |
| 综述论文 | 有文献基础+领域知识 | 文献综述+领域分析 | Q1 |
| 算法-only | 数学推导新颖 | 推导+1-2个demo | Q2-Q3 |

**IMRaD结构规划**:
1. **Introduction**: 背景 → 现状 → 缺口 → 贡献
2. **Methods**: 管线步骤 → 算法 → 实验设计 → 数据
3. **Results**: 主结果(Val Dice/CErr) → 消融实验 → 对比实验
4. **Discussion**: 优势 → 局限 → 与文献对比 → 未来方向
5. **Conclusion**: 核心贡献总结

**文献基础**: 补充15-30篇相关文献(方法学/临床/算法)

**产出**: paper_plan.json (IMRaD结构+文献列表+时间表)

## 实战案例：K230训练管线

### 项目概要
- 数据: 901帧K230图像(800×480) + 976帧OpenEDS
- 管线: 7步CV管线(瞳孔定位→区域生长→椭圆精修→眼球中心标定→3D能量蛇→SAM眼裂→Seg Mask)
- 模型: MobileNetV2+T3EM, 4阶段渐进训练(30+20+20+20 epoch)
- 结果: Val Dice=0.8955, CErr=1.63px

### 发现的研究空白
1. 单目3D眼球追踪精度理论极限未验证
2. SAM vs 传统CV性能边界未定义
3. 不同人种解剖学参数泛化性未评估
4. 时序信息增益未量化
5. 混合训练泛化性增益未量化

### 生成的科学假设
- H1: 分割误差主导总误差(claim: ≥60%)
- H2: SAM在虹膜边缘优于能量蛇，在瞳孔定位不如区域生长
- H3: 时序建模比单帧提升Val Dice ≥0.03
- H4: 混合训练比单一数据集提升Val Dice ≥0.05
- H5: 固定几何参数导致系统性偏差

### 论文撰写计划
- 论文A(方法学): Q1, IEEE TBME/IOVS, 2周
- 论文B(实证分析): Q2, Scientific Reports, 4周

## 参考文件

- references/legacy-paper-rescue-workflow.md — 管线/训练分析经验
- references/legacy-paper-rescue-workflow.md — 管线/训练分析经验
- references/hypothesis-generation-references/io-contract.md — 假设生成IO合同
- references/hypothesis-generation-references/boundary.md — 假设生成边界
- references/k230-pipeline-audit-2026-06-13.md — K230训练管线审计报告(实战案例)
- references/k230-code-patterns.md — K230训练管线核心代码模式(数据加载/训练/参数)
- references/skill-library-audit-2026-06-13.md — 技能库审计与更新报告

## 实战案例

- **K230训练管线** (2026-06-13): 从901帧K230数据+训练日志提取5个研究空白、5个科学假设、2篇SCI论文计划。详见references/k230-pipeline-audit-2026-06-13.md。

## 验证

- [ ] 所有项目文件已扫描和统计
- [ ] 管线步骤已拆解为方法论
- [ ] 已识别至少3个研究空白
- [ ] 已生成至少3个可检验假设
- [ ] 已输出论文撰写计划(IMRaD结构+文献列表)
- [ ] 假设格式符合hypothesis-generation的IO_CONTRACT


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。
