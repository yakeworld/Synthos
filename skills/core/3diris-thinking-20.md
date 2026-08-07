### 20. 2026-08-08 扫描 — 可扩展模式

#### 20.1 扫描方法论

- **PubMed API**: ❌ 完全不可用（Python urllib API key "not wellformed"，curl 同样返回此错误）。所有 PubMed 扫描路径已死。
- **PhysioNet HTML**: ⚠️ 主题标签查询返回空 HTML（topic=eye/vestibular/gait 等全部 0 结果），但直接数据集 URL 可访问。必须使用 web_search → PhysioNet 结果页面 路径。
- **web_search**: ⚠️ 质量降级但偶尔可用。搜索大量噪音（德语/荷兰语/土耳其语/俄语站点），必须人工审阅每条结果。作为辅助源。
- **直接 URL 提取**: 主力路径。web_search 返回 Nature Scientific Data / PhysioNet / ETRA 等来源 → 提取 URL → web_search 二次查询获取细节。

#### 20.2 新发现数据集

**P0 — 高价值，2D 分析已发表，3D 分析空白，数据公开可用：**

---

**1. WearGait-PD（Nature Scientific Data, Jan 2026）**
- URL: https://www.nature.com/articles/s41597-026-06806-2
- 数据：100 名帕金森患者 + 85 名年龄匹配对照
- 传感器：原始 IMU（加速度+陀螺仪+磁力计）+ 传感器化鞋垫（每只 16 个压力传感器，3-DOF 加速度+角速度）
- 原作者分析：仅描述数据集本身（Scientific Data 格式），提供描述性统计和信号质量检查
- **3D 空白**：
  - 足底压力 3D 动态分析（压力中心轨迹、足部扭转角）
  - 全身 3D 运动学（IMU 融合姿态估计 → 3D 关节角度）
  - PD 对称性指数（3D 空间中的左右不对称度）
  - 步态阶段 3D 相位空间分析
  - 鞋垫压力与 IMU 的 3D 跨模态融合
- **Synthos 管线评估**：✅ 完全可行。IMU 数据可直接用于 3D 姿态重建；鞋垫压力数据用于足部 3D 动力学分析。数据格式公开（通常 CSV/FISMA），可通过 Synapse (syn52540892) 获取。
- **优先级**：P0 — 高临床价值 + 3D 空白明确 + 数据易获取
- **建议论文标题**：3D Gait Symmetry Index from Wearable IMU and Insole Data in Parkinson's Disease: A Biomechanical Analysis Beyond Descriptive Statistics

---

**2. Eye Movement Benchmark for Smooth-Pursuit Classification（Nature Scientific Data, Mar 2026）**
- URL: https://www.nature.com/articles/s41597-026-06963-4
- DOI: 10.1038/s41597-026-06963-4
- 数据：健康受试者的平滑追踪眼动（smooth pursuit）数据
- 原作者分析：创建了用于分类算法的基准数据集，主要关注机器学习分类性能
- **3D 空白**：
  - 平滑追踪的 3D 眼动轨迹分析（水平 + 垂直 + 角向运动）
  - 3D 追踪增益计算（而非仅 2D 追踪误差）
  - 3D 眼-头协调动力学
  - 不同追踪速度/方向下的 3D 运动学建模
- **Synthos 管线评估**：✅ 可行。平滑追踪是经典的 2D 分析领域，3D 版本几乎无人做过。
- **优先级**：P0 — 经典眼动运动模式的 3D 分析空白
- **建议论文标题**：3D Smooth Pursuit Dynamics: Beyond 2D Gain Computation — A Quantitative Eye Movement Analysis

---

**3. MCFW-Gaze（ETRA 2026 Open Dataset Track）**
- URL: https://dl.acm.org/doi/10.1145/3797246.3806660
- 数据：Tobii Pro Fusion 眼动仪，120 Hz，6 个任务（重复自由观看 100 张图片、阅读、网页浏览等）
- 原作者分析：ETRA 2026 Open Dataset Track 发布，主要描述数据集
- **3D 空白**：
  - 自由观看任务中的 3D 视觉场景探索模式分析
  - 眼-头-身体联合 3D 运动学（如有头动数据）
  - 3D gaze heatmap vs 2D gaze heatmap 的对比分析
- **Synthos 管线评估**：⚠️ 中等。需确认数据是否包含 3D 场景信息。ETRA 数据集通常用于 HCI 分析，3D 视角新颖。
- **优先级**：P1 — HCI 领域，3D 分析新颖但临床意义较低
- **建议论文标题**：3D Gaze Mapping in Free Viewing: A Multiscale Visual Exploration Analysis Beyond 2D Heatmaps

---

**4. Gaze-VLM（OpenReview, 2025/2026）**
- URL: https://openreview.net/forum?id=RWOpRDABEr
- 数据：眼动数据 + VQA（视觉问答）基准数据集
- 原作者分析：使用眼动数据辅助 VLM（视觉语言模型）的 VQA 性能
- **3D 空白**：
  - 3D 场景中的 gaze-informed VQA（而非 2D 图像）
  - 3D 视觉注意力模式与语言推理的关联
  - 眼动轨迹的 3D 空间编码用于视觉推理
- **Synthos 管线评估**：⚠️ 需要 3D 场景数据。如果数据集包含 3D 信息，则潜力巨大。
- **优先级**：P1 — AI/VLM 交叉领域，3D 视角新颖
- **建议论文标题**：3D Scene Understanding through Gaze-Informed Multimodal Reasoning

---

**P0.5 — 高价值但需进一步验证：**

---

**5. EEGEyeNet（OpenNeuro ds005872）**
- URL: https://openneuro.org/datasets/ds005872/versions/1.0.0
- 数据：同步 EEG + 眼动追踪数据
- **3D 空白**：EEG 驱动的 3D 眼动预测（而非 2D）
- **注意**：仅 1 名受试者，样本量有限。
- **优先级**：P1.5 — 样本量小但方法新颖
- **建议论文标题**：EEG-Driven 3D Gaze Prediction: A Multimodal Brain-Eye Interaction Study

---

**6. DREAMT（PhysioNet 2026）**
- URL: https://physionet.org/content/dreamt/2.2.0/
- 数据：睡眠阶段估计数据集，包含眼动通道（E1, E2）用于快速眼动（REM）识别
- **3D 空白**：REM 眼动的 3D 轨迹分析（而非仅 2D 存在/不存在判断）
- **优先级**：P1.5 — PhysioNet 数据集，REM 眼动的 3D 分析未见
- **建议论文标题**：3D REM Eye Movement Dynamics: Quantifying Rapid Eye Saccades in Sleep

---

**P1 — 中等价值：**

---

**7. Hillel Yaffe Glaucoma Dataset (HYGD)（PhysioNet）**
- URL: https://physionet.org/content/hillel-yaffe-glaucoma-dataset/
- 数据：Gold-standard 标注的眼底图像数据集
- **3D 空白**：眼底图像的 3D 视杯/视盘深度分析（OCT 联合分析）
- **优先级**：P1 — 眼科数据集，3D 分析需要 OCT 数据配合

---

#### 20.3 其他信号源

**ETRA 2026 Open Dataset Track**：
- 已发布多个眼动数据集（MCFW-Gaze 等）
- 2026 年是 ETRA 首次设立专门的 Open Dataset Track
- 未来关注：ETRA 2026  proceedings 完整列表（dl.acm.org/doi/proceedings/10.1145/3797246）
- 建议监控：https://dl.acm.org/doi/proceedings/10.1145/3797246

**Nature Scientific Data 2026**:
- 已确认至少 2 个 2026 年新发布的眼动相关数据集
- 趋势：Scientific Data 越来越多地发布纯数据集论文（非深入分析），为后续研究留出空间

**MDPI 2026**:
- Wearable Sensor-Based Gait Analysis in BPPV（MDPI Biosensors/Bioengineering, 2026）
- 原作者：单一作者，φ-bonacci 指标分析
- **3D 空白**：可穿戴传感器的 3D 步态分析在 BPPV 中完全未探索

#### 20.4 领域扫描统计

| 领域 | 新数据集数 | P0 数 | P0.5 数 | P1 数 |
|------|-----------|-------|---------|-------|
| 帕金森/步态 | 1 (WearGait-PD) | 1 | 0 | 0 |
| 平滑追踪眼动 | 1 (SciData 2026) | 1 | 0 | 0 |
| ETRA 2026 数据集 | 1+ (MCFW-Gaze) | 0 | 1 | 1 |
| VLM/视觉-语言 | 1 (Gaze-VLM) | 0 | 1 | 0 |
| 睡眠/REM 眼动 | 1 (DREAMT) | 0 | 1 | 0 |
| 眼底/青光眼 | 1 (HYGD) | 0 | 0 | 1 |
| 合计 | 5-7 个 | 2 | 3 | 1 |

#### 20.5 工具链状态更新

| 工具/路径 | 状态 | 备注 |
|-----------|------|------|
| PubMed E-utilities | ❌ 完全不可用 | curl + Python urllib 均返回 "API key not wellformed" |
| PhysioNet 主题搜索 | ⚠️ 0 结果 | 直接 URL 路径有效，主题标签路径无效 |
| PhysioNet 直接 URL | ✅ 可用 | 通过 web_search 找到 URL 后可正常抓取 |
| web_search | ⚠️ 质量降级 | 大量噪音，但偶尔找到有用结果，必须人工审阅 |
| Nature Scientific Data | ✅ 有效 | 可通过 web_search + 直接 URL 获取 |
| ETRA proceedings | ✅ 可用 | ACM Digital Library 路径有效 |
| OpenNeuro | ✅ 可用 | OpenNeuro dataset 页面可正常获取 |

#### 20.6 关键洞察

1. **WearGait-PD 是本周期最高价值 P0 发现**：100 PD 患者 + 85 对照 + 原始 IMU + 鞋垫数据，原作者仅做描述性统计。3D 步态分析、足部 3D 动力学、全身对称性指数全是空白。Synthos 的 3D 运动学管线可立即启动。

2. **平滑追踪的 3D 分析是经典的未开发领域**：Smooth pursuit 是眼动研究中研究最深入的 2D 运动类型，但 3D 版本几乎无人尝试。Nature Scientific Data 刚发布了基准数据集，意味着 3D 分析的时机已成熟。

3. **ETRA 2026 Open Dataset Track 是重要信号**：首次设立专门的 Open Dataset Track 表明眼动领域正在经历数据开放浪潮。这为 Synthos 的 3D-aware 分析提供了大量新数据源。

4. **PubMed API 和 PhysioNet 主题搜索均不可用**：当前 cron 环境下的数据发现路径已严重受限。必须转向：(a) web_search → Nature Scientific Data / ETRA / OpenReview 直接抓取；(b) 监控 arXiv 新论文中的数据集发布；(c) 定期查看 conference websites（ETRA、MICCAI Open Data Session 等）。

5. **可穿戴传感器数据是未来趋势**：WearGait-PD（IMU + 鞋垫）、BPPV gait analysis（可穿戴传感器）等趋势表明，低成本可穿戴设备正在替代昂贵的实验室设备。3D-aware 分析在低成本设备数据上的应用是一个新兴方向。

#### 20.7 推荐实施路径

**立即（2-4 周）**：
- 启动 WearGait-PD 管线：获取 IMU + 鞋垫数据 → 3D 姿态重建 → 步态对称性分析 → 3D 空间分析 → 撰写论文
- 平滑追踪 3D 分析：获取数据集 → 3D 眼动轨迹建模 → 追踪增益的 3D 扩展 → 撰写论文

**中期（4-6 周）**：
- MCFW-Gaze 数据集的 3D 探索模式分析
- Gaze-VLM 的 3D 场景理解方向
- DREAMT 的 REM 眼动 3D 分析

**长期（6-12 周）**：
- 构建一个统一的 3D 可穿戴数据分析平台
- 将 3D 方法应用于 BPPV 步态分析
- 探索 VR 环境中的 3D 眼-头-身体联合动力学

#### 20.8 数据集优先级更新（本周期新增）

| 数据集 | 优先级 | 领域 | 3D 空白 | 数据获取 |
|--------|--------|------|---------|---------|
| WearGait-PD | P0 | 帕金森步态 | 全面 3D 分析 | Synapse (公开) |
| Smooth Pursuit Benchmark | P0 | 平滑追踪眼动 | 3D 轨迹分析 | Nature Sci Data |
| MCFW-Gaze | P1 | 自由观看眼动 | 3D 场景映射 | ETRA 2026 |
| Gaze-VLM | P1.5 | VLM/视觉 | 3D 场景理解 | OpenReview |
| DREAMT | P1.5 | 睡眠/REM | 3D REM 分析 | PhysioNet |
| HYGD | P1 | 眼底/青光眼 | 3D 视杯分析 | PhysioNet |

#### 20.9 关键洞察（补充）

1. **可穿戴传感器数据是未来趋势**：WearGait-PD（IMU + 鞋垫）、BPPV gait analysis（可穿戴传感器）等趋势表明，低成本可穿戴设备正在替代昂贵的实验室设备。3D-aware 分析在低成本设备数据上的应用是一个新兴方向。

2. **Nature Scientific Data 是最佳数据集发现源**：2026 年已有多个高质量数据集发布在该期刊，均为纯数据集论文（描述性统计为主），为后续分析留出大量空间。

3. **ETRA 2026 Open Dataset Track 是重要信号**：首次设立专门的 Open Dataset Track 表明眼动领域正在经历数据开放浪潮。这为 Synthos 的 3D-aware 分析提供了大量新数据源。

4. **PubMed API 和 PhysioNet 主题搜索均不可用**：当前 cron 环境下的数据发现路径已严重受限。必须转向 web_search → Nature Scientific Data / ETRA / OpenReview 直接抓取。

5. **BPPV 可穿戴传感器数据未被充分利用**：MDPI 2026 的单作者论文仅使用 φ-bonacci 指标，3D 步态分析完全空白。这与 WearGait-PD 的 PD 步态数据形成互补。