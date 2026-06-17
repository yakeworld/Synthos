---
name: bci-wenzhou
description: >-
version: 1.0.0
  温州脑机接口临床应用示范基地 — 政策方案、座谈会材料、用户资产映射、发言策略。
  覆盖：政策方案分析、用户技术资产盘点、政策对齐、讨论会策略、发言草稿、
  瓯越英才申报关联。
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: 温州脑机接口临床应用示范基地 — 政策方案、座谈会材料、用户资产映射、发言策略。覆盖：政策方案分析、用户技术资产盘点、政策对齐、讨论会策略、发言草稿、瓯越英才申报关联。
    signature: "policy_area: str, user_assets: str -> policy_doc: str -> policy_doc: str (policy_analysis: dict, user_assets: list[str], policy_alignment: dict, discussion_strategy: str, speech_draft: str)"
    related_skills: [knowledge-extraction, knowledge-acquisition, argument-expression, paper-pipeline, nsfc-grant-audit]

---



# 温州脑机接口临床应用示范基地

## 背景

温州被浙江省政府明确指定为"一核四基地"中的**脑机接口临床应用示范基地城市**。
2026年6月9日召开小范围讨论会，讨论《关于打造温州市脑机接口临床应用示范基地的方案（初稿）》。

## 核心材料

所有相关文件和资料存储在 `/home/yakeworld/projects/bci-demo-base/` 目录下：

| 文件 | 说明 |
|:-----|:---
  io_contract: input: ['policy_area: str, user_assets: str -> policy_doc: str', 'output: ['policy_doc: str (policy_analysis: dict, user_assets: list[str], policy_alignment: dict, discussion_strategy: str, speech_draft: str)']
--|
| `3d-eye-tracking-bci-report.md` | 核心报告：三维眼动与BCI的逻辑关系（527行完整技术论证） |
| `meeting-prep/speech-outline.md` | 座谈会发言提纲 |
| `digest.md` | 摘要/浓缩版 |
| `policies/bci-policy-summary.md` | 脑机接口政策汇总 |
| `landscape/bci-base-landscape.md` | 温州脑机接口基地全景扫描 |
| `eye-bci/eye-bci-connection.md` | 眼动-BCI技术连接点分析 |
| `references/synthos-capability.md` | Synthos能力说明（作为科研体系证明） |
| `README.md` | 项目说明文档 |

## 用户核心定位

**杨晓凯** — INSTITUTION_NAME_PLACEHOLDER神经科主任、市重点实验室主任、主任医师

### 技术资产
- K230嵌入式三维眼动追踪系统（4D-EyeTraker，1920×1080@90fps，AI2D+KPU双硬件加速）
- T3EM-Net 可解释三维眼动重建算法
- Morpho-Net 半规管自动分割（3D UNet，Dice>0.9）
- 3D对数螺旋模型（HSMM框架，8参数，RMSE 0.07-0.17mm，475条中心线验证）
- PINN物理方程反演（耳石易动性参数）
- 6项已授权发明专利 + 10项实审中

### 临床资产
- BPPV诊疗完整闭环（评估→定位→诊断→治疗）
- 单次复位成功率超90%
- 年门诊量5000+人次
- 三维眼动生物标志物研究（PD/AD/睡眠障碍）
- kappa角计算：视线方向与半规管平面夹角→受刺激半规管定位
- VOR增益量化：前庭眼动反射功能评估
- 扫视动力学分析：幅度-速度关系、峰值速度、潜伏期

### 科研体系
- Synthos：自进化科研操作系统（121技能、53轮进化、38篇论文）
- 市重点实验室（2000㎡场地、GPU集群）
- 33人跨学科团队
- 国家级继教班10余次

## 政策对齐要点

政策方案五大任务与用户匹配：

| 政策任务 | 用户匹配度 | 说明 |
|:---------|:----------:|:-----|
| 高校与平台引领 | ⭐⭐⭐⭐ | 已有T3EM-Net、Morpho-Net、PINN算法体系 |
| 产业孵化 | ⭐⭐⭐ | 3D打印模型已有销售收入，眼动仪有市场规划 |
| 临床资源集聚 | ⭐⭐⭐⭐⭐ | BPPV诊疗闭环已验证，可复制至PD/AD |
| 公共服务平台 | ⭐⭐⭐⭐ | 眩晕病实验室+重点实验室即服务平台雏形 |
| 新型材料研发 | ⭐⭐ | 间接相关，柔性电极/生物材料有交叉 |

## 讨论会策略

**核心目标：** 建立存在感 + 找到嵌入点 + 争取核心成员身份

**关键话术：**
1. "BPPV方向已完成'临床痛点→机理→原型→验证'完整闭环，该路径可复制到方案中提到的PD、AD、睡眠障碍方向"
2. "120Hz眼动仪核心指标超越国际主流品牌，可为脑机接口临床试验提供客观评估指标"
3. "Synthos有组织科研体系可作为脑机接口临床验证的标准化管线"
4. "建议将三维眼动生物标志物检测纳入脑机接口临床试验的标准评估流程"

## 与瓯越英才申报的关联

- 该座谈会材料可直接用于瓯越英才申报"拟开展研究计划"的补充说明
- 方案中的"临床示范基地"定位与用户PPT中的"四维眼动系统"方向完全一致
- 议事协调机构中的"核心成员"身份可作为申报加分项

## 相关技能

- `competition-submission` — 政策对齐工作流程见 `references/policy-alignment-workflow.md`
- `political-proposal` — 参政议政提案写作

## 支持文件

- `references/policy-alignment-workflow.md` — 政策对齐工作流程（由competition-submission共享）
- `references/bci-base-landscape.md` — 温州脑机接口基地全景扫描
- `references/eye-bci-connection.md` — 眼动-BCI技术连接点分析
- `references/bci-policy-summary.md` — 脑机接口政策汇总
- `references/synthos-capability.md` — Synthos科研能力说明
