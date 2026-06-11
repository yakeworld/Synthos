# VOR Digital Twin — 技术PPT单页提炼

> 会话: 2026-06-11
> 场景: 用户要求为"标志性成果一：知识引导的VOR数字孪生"制作PPT单页
> 输出: /media/yakeworld/sda2/academic_writer/yakeworld/标志性成果一_VOR数字孪生核心技术.pptx

## 提炼原则

单页PPT只展示**最核心的3-4个技术要点**，避免信息过载。结构：
- 左侧：核心理论突破（3个卡片）
- 中间：技术路线4阶段管线
- 右侧/底部：支撑成果（论文+专利+数据）

## 核心技术提炼

### 1. 闭式解析解
- VOR慢相运动学 → 偏差矢量代数
- Rodrigues旋转公式 + 四元数运动学
- 正交轴分解 → 能量系数 Kx, Ky
- 闭式解: ω = arccos(3 − 2(Kx+Ky)), φ = atan2(√(1−Ky), √(1−Kx))

### 2. BPPV天然探针
- BPPV = 单一半规管刺激的生理学模型
- 耳石异位 → 兴奋/抑制效应 → 眼震
- 证实Flourens/Ewald定律在人体诠释
- 个体化参数反演的天然激励源

### 3. 数字孪生构建
- ODE/PINN 18个模型覆盖VOR全谱系
- 受外周流体力学+中枢控制律约束
- 高保真观测 → 时空解耦 → 反演 → 孪生
- 个体化VOR增益/延迟/速度存储参数

### 4. 技术路线4阶段
- 阶段一: 高保真四维眼动观测 (3D VOG + IMU)
- 阶段二: 时空解耦 (VOR慢相提取)
- 阶段三: BPPV级联反演 (流体ODE → 闭式解)
- 阶段四: 数字孪生构建 (18个ODE/PINN模型)

## 支撑数据

- 论文: Three-dimensional Kappa angle estimation via VOR (D1=0.95, D2=0.90, 30引用)
- 专利: 7项 (内耳空间姿态分析/三维眼动检测/眼震记录/BPPV诊疗)
- 数据: BPPV虚拟仿真 + 18篇ODE/PINN + 148篇BPPV源文件 + 27篇VOR论文

## 设计细节

- 配色: NAVY背景 → 白色内容区 → TEAL/ACCENT_BLUE/GREEN 卡片
- 左侧3张卡片 (1.15in高), 中间4阶段管线, 底部3张成果卡片 + 1个创新badge
- 字号: 标题13-14pt, 卡片标题10pt, 卡片内容9pt
- 箭头: MSO_SHAPE.RIGHT_ARROW, 必须先调用 fill.solid()
