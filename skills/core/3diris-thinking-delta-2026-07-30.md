---
## 二、本次发现的新数据集 (2026-07-30 增量扫描)

> 来源: 全网搜索 (PubMed, Nature, PhysioNet, Kaggle, Crossref, Springer)
> 状态: 10个新数据集, 其中6个为高价值P0/P0.5

### 2.1 VRBiom — Periocular Dataset for Biometric Applications in VR/AR
- **来源**: MDPI Electronics, 2025 (DOI: 10.3390/electronics14091835)
- **URL**: https://www.mdpi.com/2079-9292/14/9/1835
- **描述**: VR环境中捕获的periocular+iris生物识别数据集
- **数据内容**: 近红外/可见光图像, 眼动追踪数据, 用户身份标签
- **可访问性**: 研究用途公开
- **作者**: 见MDPI论文
- **Synthos分析潜力**: P0 — 3D虹膜形态参数化可直接应用，且原作者仅做生物识别分类，未做医学/解剖分析

### 2.2 WearGait-PD — Open-Access Wearables Dataset for Gait in Parkinson's Disease
- **来源**: Nature Scientific Data, 2025 (DOI: 10.1038/s41597-026-06806-2)
- **URL**: https://www.nature.com/articles/s41597-026-06806-2
- **描述**: 原始IMU+传感器化鞋垫数据, 100名PD患者 + 85名年龄匹配对照
- **数据内容**: 原始IMU信号 + 鞋垫压力数据 + 临床评估
- **可访问性**: Open Access (Nature Data Descriptor)
- **作者**: 见Nature论文
- **Synthos分析潜力**: P0.5 — PD步态分析，可复用gait分析管线。原作者仅做基础分类，未做3D姿态参数化。可产出"wearable sensor-derived PD progression index"短文

### 2.3 Multimodal Biomechanical + Eye-Tracking Dataset of Human Movement
- **来源**: Nature Scientific Data, 2025 (DOI: 10.1038/s41597-025-05642-0)
- **URL**: https://www.nature.com/articles/s41597-025-05642-0
- **描述**: 标注的全身运动学+注视追踪+地面反作用力数据
- **数据内容**: 全身运动学 + 注视追踪 + 地面反作用力/力矩
- **可访问性**: Open Access
- **Synthos分析潜力**: P0.5 — 全身运动+眼动的多模态数据集。眼动部分可用于瞳孔/注视分析，运动学部分可用于步态分析。作者未做眼-运动耦合分析

### 2.4 Spontaneous Eye Blink-based ML for Parkinson's Clinical Tracking
- **来源**: npj Parkinson's Disease (Nature), 2025 (DOI: 10.1038/s41531-025-01094-w)
- **URL**: https://www.nature.com/articles/s41531-025-01094-w
- **描述**: 探索自发性眨眼作为PD无创数字生物标志物
- **数据内容**: 眨眼视频记录 + 临床评分 + 机器学习特征
- **可访问性**: 开放获取 (Nature子刊)
- **Synthos分析潜力**: P0 — 眨眼是PD早期检测标志物，与瞳孔/眼动数据形成多模态组合。作者仅做分类，未做时序分析或个体轨迹预测

### 2.5 Automatic Analysis of Eyelid Movement in De-Novo Parkinson's
- **来源**: PMC (PubMed Central), 2025 (PMCID: PMC12144097)
- **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC12144097/
- **描述**: PD患者眨眼率/inter-blink interval异常分析
- **关键发现**: 38% PD患者眨眼率降低, inter-blink interval增加, 与黑质多巴胺能神经元丢失相关(r=0.35, p<0.001)
- **Synthos分析潜力**: P0.5 — 眨眼+瞳孔+眼动三位一体PD数字标志物。作者仅做单变量分析，可做多模态融合

### 2.6 Eye Movement Abnormalities as Objective Biomarkers for PD (VR-based)
- **来源**: BMC Neurology (Springer), 2026 (DOI: 10.1186/s12883-026-04634-w)
- **URL**: https://link.springer.com/article/10.1186/s12883-026-04634-w
- **描述**: VR集成眼动追踪系统评估PD患者眼动功能
- **数据内容**: VR眼动追踪数据 + 临床评估
- **Synthos分析潜力**: P1 — VR环境+眼动+PD的组合。作者仅描述系统能力，未做深入分析

### 2.7 Spontaneous Blink Features for PD Classification
- **来源**: ACM DL, 2025 (DOI: 10.1145/3797246.3803044)
- **URL**: https://dl.acm.org/doi/full/10.1145/3797246.3803044
- **描述**: 基于眨眼视频的PD自动分类框架, 含全新数据集
- **数据内容**: 眨眼视频 + 面部追踪 + PD分类标签
- **Synthos分析潜力**: P0.5 — 眨眼特征+面部分析的PD分类数据集

### 2.8 PhysioNet Chagas Disease ECG Challenge 2025
- **来源**: PhysioNet / Computing in Cardiology 2025
- **URL**: https://moody-challenge.physionet.org/2025/
- **描述**: 从ECG识别Chagas疾病的挑战赛数据集
- **数据内容**: ECG信号 + Chagas诊断标签
- **可访问性**: PhysioNet标准
- **Synthos分析潜力**: P1 — ECG信号分析, 与现有心电分析管线部分重叠

### 2.9 Atrial Fibrillation Detection Dataset from ICU ECGs
- **来源**: PhysioNet, 2025
- **描述**: 596个标注的10秒ECG记录, 来自加拿大安大略省ICU
- **数据内容**: ECG信号 + AF标记
- **Synthos分析潜力**: P1 — 心电信号分析

### 2.10 mPower Parkinson Dataset (Apple ResearchKit)
- **来源**: Scientific Data (Nature), 2016 持续更新
- **URL**: https://www.nature.com/articles/sdata201611
- **描述**: 9500+ PD患者移动端数据, 含语音/步态/手指tap/加速度计
- **最新研究**: 2026年仍有论文在使用mPower数据集进行多分类语音分析 + 纵向轨迹建模
- **Synthos分析潜力**: P0.5 — mPower是PD数字标志物研究中最广泛使用的公开数据集。包含语音+运动+认知测试, 可做多模态PD进展预测。原作者仅做横断面分析, 可做多模态纵向分析

---

## 三、跨领域空白分析

### 3.1 眼动/眨眼 → Parkinson's 三位一体数字标志物
**空白状态**: 极度稀缺, 多个新数据集出现但都只做单维度分析
**机会**: 
- 合并VRBiom(periocular) + Spontaneous Blink(PD) + WearGait-PD(步态) + mPower(语音+运动) → **多模态PD数字标志物**
- 3D虹膜形态(核心能力) + 眨眼特征 + 步态特征 + 语音特征 → PD分期/进展预测
- **产出潜力**: 可快速产出一篇短文, 核心卖点=多模态数字标志物融合

### 3.2 眼动/眨眼 → BPPV/前庭 数据极度稀缺
**空白状态**: PubMed检索BPPV+dataset仅21篇, 且多为临床论文而非数据集
**机会**:
- 从已有临床论文中逆向构建数据集
- 前庭功能测试(眼震视频+温度测试+旋转椅) → 结构化数据
- **产出潜力**: 创建首个BPPV公开数据集, 然后在其上发表论文 → P0模式

### 3.3 帕金森数字标志物 — 从横断面到纵向
**空白状态**: 多数PD数据集(mPower, WearGait-PD)仅做横断面分类
**机会**:
- 用mPower纵向数据 + 眼动数据 → PD进展轨迹建模
- 核心创新: 从"诊断"到"分期/进展预测"
- **产出潜力**: 中等, 需要纵向数据建模能力

---

## 四、数据集优先级重新排序 (2026-07-30更新)

| 优先级 | 名称 | 来源 | 核心空白 | 评分 |
|--------|------|------|----------|------|
| P0 | VRBiom (periocular iris) | MDPI 2025 | 3D虹膜形态+医学分析 | 24/25 |
| P0 | Spontaneous Blink PD (npj) | Nature 2025 | 眨眼作为PD数字标志物 | 23/25 |
| P0 | Blink Features PD Classification | ACM 2025 | 眨眼视频+PD分类数据集 | 22/25 |
| P0.5 | WearGait-PD | Nature SciData 2025 | PD步态+可穿戴传感器 | 21/25 |
| P0.5 | Multimodal Biomechanical+Eye | Nature SciData 2025 | 全身运动学+眼动 | 21/25 |
| P0.5 | Spontaneous Blink (PMC) | PMC 2025 | 眨眼率+PD黑质关联 | 20/25 |
| P1 | Eye Movement PD (VR-based) | Springer 2026 | VR眼动+PD | 18/25 |
| P1 | Chagas ECG Challenge | PhysioNet 2025 | ECG+Chagas | 16/25 |
| P1 | mPower PD | Nature 2016+ | PD多模态移动端数据 | 16/25 |
| P1 | AF Detection ECG | PhysioNet 2025 | ECG+AF | 15/25 |

---

## 五、网络状态更新 (2026-07-30)

| 数据源 | 状态 | 备注 |
|--------|------|------|
| PubMed API | ✅ 正常 | XML直接解析, eSearch稳定, eFetch JSON返回异常但XML可用 |
| Crossref API | ✅ 正常 | JSON解析, 但返回论文而非数据集本身 |
| Web Search | ⚠️ 部分正常 | 部分查询返回无关结果, 但关键查询命中率高 |
| SearXNG | ❌ 离线 | 持续超时 |
| Kaggle | ❌ 不可用 | 无法直接访问 |
| PhysioNet | ⚠️ HTML可变 | 部分URL返回404, 需验证 |