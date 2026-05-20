# 项目定义：Synthos — 全球数智教育创新大赛

> 阅读此文件 = 了解项目全貌。**无需再次读取原始材料。**
> 当前状态 → 见 QUALITY.md | 变更历史 → 见 CHANGELOG.md

---

## 🏆 竞赛信息

| 项目 | 内容 |
|:-----|:------|
| **大赛** | 全球数智教育创新大赛 AI for Medicine 赛道 |
| **子赛** | "厚道泛雅"医学教育智能体大赛 |
| **赛组** | 医学研究支持智能体 |
| **截止** | 2026-05-15 15:00 |
| **平台** | http://MeedTAC.mh.chaoxing.com |
| **主办** | 北京大学医学部 × 超星 |

---

## 🧬 项目：Synthos

**全称**: Synthos — 自主进化学术科研平台（认知操作系统）
**概念**: 基于八维认知框架，将科研全流程原子化为认知单元，通过 DAG 架构实现有机协同，依托进化引擎自主优化。

### 核心架构

| 层 | 组件 | 说明 |
|:---|:-----|:------|
| **认知原子** | 8 个独立 SKILL.md | ACQ(知识获取) → EXT(知识提取) → ASC(关联发现) → GAP(空白发现) → HYP(假设生成) → ARG(论证表达) → VER(观点验证) + ROU(任务路由器) |
| **进化引擎** | evolution | 质量评估 → 偏差检测 → 技能吸收 → 参数优化，1000s 循环 |
| **教学层** | 73 sources | CRISP-DM, TRIPOD+AI, AIGC 教学法, 25+ 数据集 |
| **方法论** | 八维认知框架 | 第一性原理、系统思维、贝叶斯、类比、奥卡姆剃刀、证伪主义、模型依赖实在论、自由能原理 |
| **技术栈** | Hermes Agent | Agent 原生执行，Zero Python（纯技能驱动） |

### 关键指标

| 指标 | 值 |
|:-----|:---|
| 版本 | v4.3 |
| 进化轮次 | ~30+ |
| 原子质量 | 全部 1.0 |
| 宪法原则 | P0-P6 |
| 进化引擎评分 | 0.95 (EXCELLENT) |
| 数据源 | PubMed, S2, Crossref, OpenAlex, bioRxiv/medRxiv |

### R2 NoteboomLM 优化（12 笔记本）

| 项目 | 状态 |
|:-----|:------|
| 便携式智能眼动仪原型研发 | ✅ 10篇 |
| T3EMNet 瞳孔虹膜动态参数 | ✅ 10篇 |
| 解剖约束四维眼动时空矢量分析 | ✅ 10篇 |
| 基于四维眼动与物理约束的 VOR 解码 | ✅ 10篇 |
| 3D Eyeball Iris Segmentation | ✅ 8篇 |
| 基于 iTrace 的人群 kappa 角分布研究 | ✅ 10篇 |
| 基于头戴式三维眼动追踪 | ✅ 7篇 |
| 基于最小刺激策略的 BPPV 三维仿真与复位 | ✅ 8篇 |
| 实时视频异常检测 | ✅ 8篇 |
| 稀疏模块化 VOR 神经网络 | ✅ 7篇 |
| 3D 眼球扭转追踪 | ✅ 8篇 |
| 多模态医学影像形状先验训练方案 | ✅ 7篇 |

---

## 📁 关键路径

```
/media/yakeworld/sda2/Synthos/
├── CONSTITUTION.md               ← 宪法（P0-P6）
├── evolution-state.json          ← 进化状态
├── evolution-log.md              ← 进化日志
├── README.md / README_CN.md      ← 项目说明（中英分离）
├── .hermes/projects/competition-synthos/  ← 本工作区
├── skills/                       ← 8个认知原子 + 工具技能
│   ├── knowledge-acquisition/
│   ├── knowledge-extraction/
│   ├── association-discovery/
│   ├── gap-discovery/
│   ├── hypothesis-generation/
│   ├── argument-expression/
│   ├── viewpoint-verification/
│   ├── task-router/
│   ├── evolution/
│   └── ... (latex-output, paper-workflow, etc.)
├── outputs/
│   ├── papers/                   ← 54个子目录（R1/R2 文献增强）
│   ├── pdfs/
│   ├── evolution/
│   └── ...
├── docs/                         ← 文档、架构图、评估框架
│   └── synthos-evaluation-framework.md
├── scripts/
│   ├── batch-runner-r2.sh        ← R2 批处理
│   └── enhance-notebook-r2.sh    ← R2 增强
└── .evolution/                   ← 进化历史

/media/yakeworld/sda2/.Trash-1000/files/竞赛材料/
├── 参赛材料总索引.md
├── 附件3-大赛申报书_已填写.docx/pdf
├── 技术路线图.md
├── 智能体建设说明书.md
├── Synthos_Full_Demo.pptx/pdf
├── video-script-super-individual.md
└── Synthos_封面_智能体.png
```

---

## 🎯 持续优化目标

1. **⚡ P0 自进化+规律提取（最高任务）** → 每次复杂任务后运行 project-experience-distillation，提取规律→凝练技能
2. **竞赛材料质量提升** → 逐项迭代至 L4 高质量，每次通过 quality-gate 后触发 P0
3. **Synthos 本体进化** → 原子质量、进化引擎、文档持续改进
4. **知识资产沉淀** → 每次优化产出同时回馈到 Synthos 知识库

## 🧠 执行层级

```
P0 自进化+规律提取 (project-experience-distillation)
    ↑ 每次 quality-gate PASS 后自动触发
    │
P0 质量闸门 (quality-gate)
    ↑ 每次任务完成前必过
    │
P0 记忆管理 (conversation-to-memory)
    ↑ 每次复杂任务结束自动执行
    │
P1-P3 项目交付 (竞赛/NSFC/论文/代码)
    ↑ 一次一件事，达标才停
```

---

*生成: 2026-05-16 | 工作区: .hermes/projects/competition-synthos/*
