---
name: adhd-eye-tracking-review
description: "ADHD眼动追踪生物标志物系统综述 + 扩展领域：3D眼动追踪|VOR驱动Kappa角标定|多模态融合筛查"
signature: "input: dict -> output: dict"
related_skills: [academic-paper-completion, arxiv, biorxiv, blogwatcher, bppv-expert]
allowed-tools: [terminal, read_file, write_file, search_files]
compatibility: hermes, opencode
---

# ADHD Eye-Tracking Biomarker Systematic Review — Extended

## 概述
专门用于ADHD（注意缺陷多动障碍）眼动追踪生物标志物的系统综述Skill。基于18篇核心文献语料库（2020-2026），支持文献检索、按年份/方法分类、关键生物标志物提取与跨论文综合。扩展覆盖3D眼动追踪、VOR-Kappa角标定和多模态融合方向。

## 语料库位置
```
/media/yakeworld/sda2/academic_writer/work/research/adhd_notebook_papers/
```
包含18篇论文的元数据+摘要（PubMed格式），覆盖年限2020-2026。

## 核心能力

### 1. 文献检索与筛选 (`/adhd search <query>`)
通过语义搜索在语料库中查找相关论文，支持按字段过滤：
- 按年份：`/adhd search eye-tracking --year 2023`
- 按方法：`/adhd search "machine learning" --method ML`
- 按生物标志物：`/adhd search antisaccade --biomarker`

### 2. 按年份/方法分类 (`/adhd classify`)
将语料库按以下维度自动分类：

**按年份分布：**
| 年份 | 论文数 | 关键主题 |
|------|--------|----------|
| 2020 | 2 | 概念综述, 头戴式ET数据质量 |
| 2021 | 2 | 眼动缺陷meta分析 (26项研究) |
| 2022 | 2 | VR+ET, 计算机技术综述 |
| 2023 | 2 | CNN+ET, 前庭刺激 |
| 2024 | 2 | ML+便携ET, 行为识别 |
| 2025 | 5 | 跨诊断生物标志物, 严肃游戏, 前庭功能, 眼动EEG |
| 2026 | 1 | 便携式ET神经学应用 |

**按方法分类：**
- ML/DL方法 (4): CNN(2023), Random Forest+Extra Trees(2024), 行为识别(2024), 软投票集成(2024)
- 系统综述/Meta分析 (6): 眼动缺陷meta(2021), 计算机技术(2022), 跨诊断(2025), 严肃游戏(2025), 便携ET(2026), 眼动EEG(2025)
- VR/沉浸式 (1): VR+教室干扰物(2022)
- 前庭/感觉 (2): SVS刺激(2023), 前庭功能(2025)
- 方法学 (1): ET滑移数据质量(2020)
- 综述 (1): ADHD概念治疗(2020)

### 3. 关键生物标志物提取 (`/adhd biomarkers`)
从语料库提取的眼动追踪生物标志物清单：

**A. 眼跳类 (Saccade) 生物标志物**
| 生物标志物 | 范式/任务 | 效应方向 | 证据来源 |
|-----------|-----------|---------|---------|
| 反眼跳方向错误率 ↑ | Antisaccade | ADHD更高错误率 | 2021 Maron meta; 2025 Toghi SR |
| 反眼跳潜伏期 ↑ | Antisaccade | ADHD更长 | 2024 Yoo et al. |
| 记忆引导眼跳精度 ↓ | Memory-guided saccade | ADHD更差 | 2021 Maron meta |
| 眼跳幅度增加 ↑ | 多任务 | ADHD更大 | 2024 Yoo et al. |
| 预期性眼跳 ↑ | 内源性注意移位 | ADHD更多 | 2025 Toghi SR |
| 侵入性眼跳 ↑ | 注视任务 | ADHD更多 | 2025 Toghi SR |

**B. 注视类 (Fixation) 生物标志物**
| 生物标志物 | 效应方向 | 证据来源 |
|-----------|---------|---------|
| 注视时间缩短 ↓ | ADHD注视更短 | 2024 Yoo et al. |
| 任务相关区域注视时长 ↓ | ADHD注意力更分散 | 2025 Toghi SR |
| 首次注视潜伏期异常 ↑ | ADHD更慢定向 | 2025 Toghi SR |
| 离任务注视增加 ↑ | VR干扰环境下 | 2022 Stokes et al. |

**C. 瞳孔/其他**
| 生物标志物 | 注释 |
|-----------|------|
| 凝视预测偏差 | CNN模型(2023)端到端预测 |
| 行为视频特征 | 非可穿戴RGB行为识别(2024) |

### 4. 跨论文综合 (`/adhd synthesize <topic>`)
对指定主题执行跨论文综合，输出格式：

```
## Topic: [topic]
### 一致性发现
- 跨N篇论文一致的结论
### 争议点
- 论文间不一致或矛盾的结果
### 研究空白
- 语料库中未覆盖的方向
### 效应量汇总
- 可用效应量/统计量的整理
```

### 5. 证据质量评估 (`/adhd quality`)
对每篇论文提供：
- 研究设计类型（RCT/队列/系统综述/病例对照）
- 样本量
- 统计方法
- 偏倚风险（基于CASP/MMAT等工具标注）

## 扩展领域：3D眼动追踪与VOR-Kappa角方法

### 6. 三维眼动追踪技术 (`/adhd 3d-et`)
将ADHD眼动筛查从2D拓展至3D/4D维度：

**传统2D vs 3D对比：**
| 维度 | 传统2D-VNG | 3D眼动追踪 |
|:-----|:-----------|:-----------|
| 可测参数 | 水平+垂直眼动 | 水平+垂直+旋转（扭转）+ 旋转轴 |
| 生物标志物丰富度 | 低 | 高（含torsion信息） |
| Kappa角影响 | 忽略（投影误差小） | 必须标定（否则视线估计偏差>5°） |
| VOR评估 | 定性 | 定量：三维旋转轴+增益 |

**3D眼动核心技术：**
- 瞳孔双椭圆拟合（Dual-Ellipse Fitting）：提高边界检测精度（参考：A Dual-Ellipse Fitting Method for High-Accuracy Pupil Boundary）
- 三维虹膜重建与展开：基于空间圆形重构法恢复虹膜平面法向量（=光轴方向）
- 虹膜特征点匹配追踪：提取眼球绕光轴的扭转分量
- 四元数→轴角分解：将3D旋转分解为旋转轴 $\hat{\mathbf n}$ 和旋转角 $\theta$

**3D眼动数据流向：**
```
视频帧 → 瞳孔/虹膜分割 → 三维虹膜平面重构 → 光轴方向 → 四元数表示 → 轴角分解(旋转轴+旋转角)
```

### 7. VOR驱动的Kappa角标定

**生理原理：** 固视（Fixation）是统一生理过程，头动时的VOR是其执行机制——VOR驱动补偿性眼动维持固视。因此动态固视（VOR下的固视）与静态固视提供的信息格式相同：视轴锁定在已知目标上。

**Kappa角定义：** 光轴（瞳孔轴）与视轴（黄斑-角膜中心连线）之间的空间角。

**核心问题：** 传统标定需已知视轴方向（注视标定点），限制其在儿童/不配合人群中的应用。

**创新方法（VOR闭式解法）：**
- **无需视轴信息**：仅通过3D眼动追踪数据，从VOR刺激下的光轴旋转轨迹解算Kappa角
- **无需头动传感器**：VOR增益≈1 → 3D眼动追踪测得的眼球旋转轴等价于头动旋转轴
- **无需注视标定点**：X、Y两组正交VOR提供两个独立约束，闭式解算

**数学框架（罗德里格斯变换法）：**
1. 定义光轴 $\mathbf O_W$ 与视轴 $\mathbf V_W$ 的偏差矢量 $\mathbf D_W = \mathbf O_W - \mathbf V_W$
2. VOR旋转 $\theta$ 后，偏差矢量为 $\mathbf D_H$（Rodrigues公式）
3. 观测角 $\gamma$ 满足 $1-\cos\gamma = K(1-\cos\theta)$，$K$ 为能量占比系数
4. 两组正交方向（Pitch+Yaw）线性回归得 $K_x$、$K_y$
5. 闭式解：
   $$\omega = \arccos(3 - 2(K_x + K_y))$$
   $$\phi = \operatorname{atan2}\left(\sqrt{1-K_y},\ \sqrt{1-K_x}\right)$$

**与ADHD筛查的关联：** Kappa角标定精度直接影响3D视线估计精度 → 影响眼动生物标志物可靠性 → 影响ADHD分类模型可信度。固定Kappa角假设在3D眼动中引入系统性偏差，本方法可消除该偏差。

### 8. 跨模态融合方向

| 模态 | 现有证据 | Synthos方向 |
|:-----|:---------|:------------|
| 3D眼动追踪+VOR | VOR增益异常与NDD相关（Van Hecke 2025） | VOR-Kappa联合评估 |
| 前庭VEMP+眼动ET | 前庭功能与NDD高度相关 | 前庭-眼动多模态筛查 |
| 便携ET+ML分类 | Yoo(2024) 76.3%准确率 | 加入Kappa标定→精度提升 |

## 完整语料库清单

| # | 年份 | 标题 (缩写) | 类型 | 核心贡献 |
|---|------|-------------|------|---------|
| 1 | 2020 | ADHD概念与治疗综述 (Drechsler) | 综述 | 无有效神经标志物 |
| 2 | 2020 | 头戴ET滑移数据质量 (Niehorster) | 方法学 | 4种设备滑移对比 |
| 3 | 2021 | 眼动缺陷meta分析 (Maron) | Meta分析 | 26项研究, 反眼跳/记忆眼跳缺陷 |
| 4 | 2022 | VR+ET注意力干扰 (Stokes) | VR研究 | 教室干扰物, 离任务注视 |
| 5 | 2022 | 计算机技术综述 (Montaleão) | SR | 61% ML, 5.6% ET |
| 6 | 2023 | CNN+ET筛查 (Chen) | ML | 112 ADHD vs 325 TD |
| 7 | 2023 | 前庭刺激SVS (Jostrup) | 实证 | SVS无改善效果 |
| 8 | 2024 | ML+便携ET筛查 (Yoo) | ML | 33特征, 76.3%准确率 |
| 9 | 2024 | 行为识别ADHD (Li) | ML | RGB视频, M-ADHD数据集 |
| 10 | 2025 | 眼动EEG工具 (Knyazhansky) | 叙述综述 | VR+ML诊断 |
| 11 | 2025 | 跨诊断ET生物标志物 (Toghi) | SR | 75项研究, 跨诊断标志物 |
| 12 | 2025 | 严肃游戏+ET (Shaikh) | SR | PRISMA, 37项研究 |
| 13 | 2025 | 前庭功能NDD (Van Hecke) | 实证 | oVEMP/cVEMP升高 |
| 14 | 2026 | 便携ET神经学 (Haddad) | SR | Tobii/Neurolign设备 |

## 工作流示例: 完整系统综述

```
# 阶段1: 分类语料库
/adhd classify --output markdown > classification.md

# 阶段2: 提取所有生物标志物
/adhd biomarkers --format table > biomarkers.md

# 阶段3: 按范式综合
/adhd synthesize "antisaccade" --cross-study > antisaccade_synthesis.md
/adhd synthesize "fixation" --cross-study > fixation_synthesis.md
/adhd synthesize "smooth pursuit" --cross-study > pursuit_synthesis.md

# 阶段4: 研究空白分析
/adhd synthesize "research gaps" > gaps.md

# 阶段5: 证据质量
/adhd quality --matrix > evidence_matrix.md

# 阶段6: Kappa角影响分析 (扩展)
/adhd ask "Kappa angle calibration impact on ADHD screening accuracy"
/adhd ask "VOR-based biomarkers for attention assessment"

# 阶段7: 输出完整综述草稿
cat classification.md biomarkers.md *synthesis*.md gaps.md \
    evidence_matrix.md > draft_review.md
```

## 注意事项
- 语料库仅含18篇论文，非全面系统性检索
- 生物标志物效应方向基于现有摘要信息
- 需要配合PubMed/Scopus完整检索以获得系统综述的全面性
- 建议使用 `SEMANTIC_SCHOLAR_API_KEY` 进行增量文献扩展
- 对于效应量合并，需获取全文进行完整meta分析
- **3D眼动/Kappa角方向**为该领域新兴方向，语料库中暂无直接覆盖；需通过扩展检索获取