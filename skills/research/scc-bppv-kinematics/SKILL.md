---
name: scc-bppv-kinematics
description: >-
  SCC (semicircular canal) morphometry analysis and BPPV repositioning kinematics.
  From raw centerline data (.mrk.json) to paired bony-membranous orientation prediction
  to Epley maneuver kinematic simulation. Covers:
  - Loading 3D SCC centerlines from Slicer MRK JSON format
  - Plane orientation analysis (normal, u/v axes, planarity)
  - 3D logarithmic spiral fitting (7-parameter HSMM-2 model)
  - Bony-to-membranous spatial prediction (plane angle, centroid offset, arc ratio)
  - Epley maneuver kinematic simulation (gravity-driven otoconia displacement)
  - Population-level Monte Carlo using published parameter distributions
  - Data quality flags (ICT vs microCT/MRN membranous segmentation reliability)
version: 1.0.0
author: Synthos
signature: "specimen_dir: str, canal: str -> paired_analysis: dict, simulation_results: dict"
allowed-tools: terminal Read Write
tags: [scc, bppv, vestibular, morphometry, epley, semicircular-canal, kinematic-simulation, bony-membranous]
metadata:
  synthos_atom_type: "domain-specific"
  synthos_absorbed_from: "Session 20260529 — H1/H2 fast verification of SCC morphology × BPPV kinematics"
  synthos_absorbed_date: "2026-05-29"
  synthos_data_access_level: "existing_data_only"
  synthos_depends_on: "knowledge-acquisition, hypothesis-generation"
---

# SCC BPPV Kinematics

## 原理层·文言

> 骨以为廓，膜以为室。廓可测于CT，室难见以常仪。
> 三管之姿，各有所向。后管最平，水平最定，前管稍异。
> 数模既立，七参定形。螺旋紧度，是为b值。
> 手法复位，沿管行石。管形变异，石路殊途。
> 知管以知石，量身以定法。

## 触发条件

加载本技能当：
- 需要分析SCC中心线数据（.mrk.json格式）
- 需要评估骨性→膜性SCC方向预测可靠性
- 需要模拟BPPV复位手法（Epley/Semont）中耳石运动
- 需要基于SCC形态参数做群体统计
- 论文涉及SCC空间形态学

## 数据来源

### 三标本六类型

| 标本 | 成像方式 | 文件前缀 | 质量评级 |
|:----|:---------|:---------|:--------:|
| sp1_microct | micro-CT (显微CT) | `ac.mrk.json`等 | ✅ 金标准 |
| sp2_mrn | 7T MRI | `ac.mrk.json`等 | ✅ 可靠 |
| sp3_ict | 工业CT | `AC.mrk.json`等(大写) | ⚠️ 膜性分割不全 |

### 文件命名约定
- 骨性: `{管}.mrk.json`（小写）或 `{管大写}.mrk.json`（ICT）
- 膜性: `{管}_mem.mrk.json` 或 `{管大写}_MEM1/2.mrk.json`
- sp3_ict 有双标注 (MEM1, MEM2)，需评估标注间一致性

### 160例CT群体参数（已发表论文Table 1）

| 管型 | n | \|b\| 均值 | \|b\| SD | \|b\| 范围 |
|:----|:-:|:---------:|:--------:|:----------:|
| AC | 160 | 0.096 | 0.039 | [0.0002, 0.147] |
| PC | 156 | 0.032 | 0.039 | [0.0002, 0.158] |
| LC | 159 | 0.048 | 0.043 | [0.0003, 0.155] |
| All | 475 | 0.059 | 0.049 | [0.0002, 0.158] |

## 分析流程

### Step 1: 加载中心线

`.mrk.json` 格式由3DSlicer标记导出：

```python
def load_pts(path):
    with open(path) as f:
        d = json.load(f)
    return np.array([p['position'] for p in d['markups'][0]['controlPoints']])
```

坐标系统：LPS (Left-Posterior-Superior)，单位mm。

### Step 2: 最近邻路径排序

数据点无序，需建立连续路径：

```python
def nearest_neighbor_path(pts):
    n = len(pts); visited=[False]*n; path=[0]; visited[0]=True; current=0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current]-pts[j]) if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest); visited[nearest]=True; current=nearest
    return path
```

验证：相邻点间距不应超过3mm，否则路径可能不连续。

### Step 3: 平面分析

SVD求平面法线、主轴：

```python
centroid = np.mean(pts, axis=0)
U, S, Vt = np.linalg.svd(pts - centroid, full_matrices=False)
normal = Vt[2, :]  # 平面法线（最小奇异值）
u = Vt[0, :]  # 平面内主轴1
v = Vt[1, :]  # 平面内主轴2
rms_plane = np.sqrt(np.mean(((pts - centroid) @ normal)**2))
```

**重要**: SVD法线符号任意。比较两个平面时，平面角度 = min(θ, 180°-θ)。

### Step 4: 3D对数螺旋拟合（7参数）

模型: r(θ) = O + R · (a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))^T

参数: cx, cy(平面中心), rot(旋转), a(初始半径), b(螺旋率), A(扭转振幅), ω(扭转频率), φ(扭转相位)

要点：
- 沿路径展开θ（np.unwrap）
- 拟合 log(r) = log(a) + bθ
- 拟合 z = A·sin(ωθ+φ)

#### Step 4.5: MEM分段合并（ICT膜性标注为两段）

工业CT(sp3_ict)的膜性AC和PC各标注为两段（MEM1和MEM2）。
同样地，sp1 microCT的LC也有lc_mem + lc_mem2两段。
**必须合并**后才能分析，否则弧比0.44-0.67（错误），平面角>19°。合并后弧比升至1.0-1.32，平面角降至~2°（正确）。

工业CT膜性标注分为两段（MEM1和MEM2），需合并为完整中心线：

```python
# 验证两段是否连接（端点距离≈0mm表示连续）
pts1 = load_pts('AC_MEM1.mrk.json')  # 49 points
pts2 = load_pts('AC_MEM2.mrk.json')  # 41 points

# 测试4种连接方式，选gap最小
best_gap = min(
    np.linalg.norm(pts1[-1] - pts2[0]),   # MEM1_end→MEM2_start
    np.linalg.norm(pts1[-1] - pts2[-1]),  # MEM1_end→MEM2_end  
    np.linalg.norm(pts1[0] - pts2[0]),    # MEM1_start→MEM2_start
    np.linalg.norm(pts1[0] - pts2[-1]),   # MEM1_start→MEM2_end
)
# 如果gap<1mm，说明是连续的两段 → 合并
merged = np.vstack([best_first, best_second])
```

**验证**：合并后弧比（膜性/骨性）应回升到0.85-1.40范围。原始两段时弧比仅0.44-0.66（错误），合并后为1.0-1.39（正确）。合并后的sp3 ICT平面角从~20°下降到~1.4°（与microCT/MRN一致）。

**sp1 microCT LC合并**同样重要：`lc_mem`(95pts,12.3mm) + `lc_mem2`(29pts,4.2mm)，lc_mem[-1]→lc_mem2[-1] gap=0.22mm（反向拼接：lc_mem + lc_mem2[::-1]）。合并后124pts,16.7mm,弧比1.32（合并前0.97异常偏短）。保存为 `LC_MEM_merged.mrk.json`。

**合并对论文结论的影响**：修正后LC膜性torsion振幅从0.166→0.238（43%增大），配对Wilcoxon从p=0.25（不显著）变为p=0.039（显著），rank-biserial r从0.67→0.78。论文需更新Table 2、正文4处数值和讨论部分。

保存为 `{管大写}_MEM_merged.mrk.json` 供后续复用。

## Step 7: 多模态比较（CT vs uCT）

本会话建立了uCT（62耳，31标本×双侧）与临床CT（160耳，80例）的批量对数螺旋参数对比方法。

### 拟合过程

```python
# 从NPZ读取→ZYX→XYZ→LPS坐标变换→拟合
pts_mm = np.load(npz_path)['smooth_mm']
pts_xyz = pts_mm[:, [2, 1, 0]]
pts_lps = pts_xyz.copy()
pts_lps[:, 0] = -pts_xyz[:, 0]  # X反转: RAS→LPS
pts_lps[:, 1] = -pts_xyz[:, 1]  # Y反转
a, b, A, om, ph, rmse, arc = fit_logspiral(pts_lps)
```

### 统计对比方法

每管各参数用 Mann-Whitney U 检验（非正态分布），Cohen's d 效应量：

```python
from scipy import stats
# For |b|:
t_stat, p_val = stats.mannwhitneyu(ct_abs_b, uct_abs_b, alternative='two-sided')
# Cohen's d:
sp = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
d_cohen = (mean1 - mean2) / sp
```

### 论文整合（2026-05-30）

v5管线(uCT rejection_ratio=0.40)的最终数据已整合入 `scc-mathematical-morphology` 论文：

**Methods §2.3** — 新增 High-Resolution Micro-CT Validation Dataset 段，描述31标本62耳uCT、0.061mm体素、186/186 100%提取成功
**Results §3.3** — 原"Comparison with Micro-CT Reference"扩写为"Cross-Modality Validation"两段式（n=3 micro-CT参考 + n=62 HBL uCT验证）
**Figure 2** — 新增 `figures/uct_vs_ct_b.pdf`：uCT vs CT |b| 箱线图，三管分别Mann-Whitney p值标注
**核心声明** — "Spiral growth rate modality-independent"（参数跨CT/uCT一致）

最终编译25页，无错误。

### 关键结果（2026-05-29分析）

**⚠ 弧长修正**：首次分析发现uCT弧长仅~4-5mm（CT的一半），根因是 `centerline_extraction.py` 的 `max_count=40` 对uCT(0.06mm)不够——40步只能走~3mm。HR版本（max_count≈200）后弧长恢复正常：AC 10-12mm, PC 8-17mm, LC 6-11mm。修正脚本见 `medical-image-centerline` 技能的 `scripts/extract_hr_centerline.py`。

| 参数 | 发现 | 解读 |
|:-----|:-----|:------|
| **b** | AC p=0.28, PC p=0.16, LC p=0.08 | ❌ 无显著差异 → 螺旋参数模态无关 |
| **A** | 全部 p<0.001, d>0.8 | uCT离面振幅显著小于CT → uCT平面几何更保真 |
| **弧长** | 全部 p<0.001, d>1.4 | uCT弧长(4-5mm) ≈ CT一半(7-10mm) → uCT FOV可能截断管端 |
| **RMSE** | AC/PC p<0.001(uCT优), LC p=0.55 | uCT拟合精度一般更优（高分辨优势） |

参考脚本：`scripts/uct_vs_ct_analysis.py`

对齐膜性方向到骨性：

```python
# 如果膜性起点≈骨性终点，翻转膜性方向
if np.linalg.norm(m_first - b_last) < np.linalg.norm(m_first - b_first):
    memb_pts = memb_pts[::-1]
```

预测模型：
- Model 1 (Identity): 膜性平面 = 骨性平面（误差=平面角）
- Model 2 (Per-canal offset): 按管型校正系统偏差

**结论**（基于sp1 microCT + sp2 7T MRI 合并sp3 ICT）：
- LC: 2.43° ± 0.28° — 最稳定
- PC: 1.89° ± 0.28° — Epley靶向管，骨膜几乎同面
- AC: 2.81° ± 0.35° — 同可靠
- **临床CT足以可靠估算膜性方向，预测误差~2.5°**

### Step 5.5: 对数螺旋参数映射（骨→膜参数可推）

本会话发现，对数螺旋参数可在参数层面建立骨→膜映射：

**可通用预测的参数（p<0.05，跨管型成立）：**
```
memb_a   = 0.948 × bony_a   + 0.592   (r=0.93, p=0.0003)
memb_b   = 0.749 × bony_b   − 0.050   (r=0.76, p=0.019)
memb_arc = 0.929 × bony_arc + 3.075   (r=0.83, p=0.006)
```

**需按管型校正的参数：**
- A (扭转振幅): PC/LC几乎一致(MAE<0.04mm)，AC方向反转
- ω (扭转频率): 每个管型有特征值(~2.3-2.7)
- φ (扭转相位): 同管型内MAE仅1.9-3.5°，跨管型差异大

### Step 5.6: 中心线直接映射（位移场D(s)法）

参数映射（Step 5.5）给出的是全局标量关系。如需逐点预测膜性中心线三维坐标，用**位移场法**：

**模型**: `X_memb(s) = X_bony(s) + D_canal(s)`

其中s∈[0,1]为归一化弧长，D_canal(s)是管型特异性平均三维位移场，训练自配对数据。

**实现**：

```python
def param_by_arclength(pts, n_samples=200):
    path = nearest_neighbor_path(pts)
    ordered = pts[path]
    diff = np.diff(ordered, axis=0)
    mask = np.concatenate([[True], np.any(np.abs(diff) > 1e-6, axis=1)])
    ordered = ordered[mask]
    ds = np.sqrt(np.sum(np.diff(ordered, axis=0)**2, axis=1))
    s = np.concatenate([[0], np.cumsum(ds)])
    s_norm = s / s[-1]
    target = np.linspace(0, 1, n_samples)
    result = np.zeros((n_samples, 3))
    for d in range(3):
        result[:, d] = np.interp(target, s_norm, ordered[:, d])
    return result, s[-1]

# Train: collect D(s) from all paired specimens
for each paired dataset:
    b_curve = param_by_arclength(bony_pts)[0]
    m_curve = param_by_arclength(memb_pts)[0]
    D = m_curve - b_curve

# Predict: apply mean displacement field
D_canal_mean = np.mean(all_D_for_this_canal, axis=0)
memb_predicted = bony_curve + D_canal_mean
```

**留一标本交叉验证精度**（三个管型均一致性良好）：

| 管型 | 平均RMSE | 最大单次误差 |
|:----|:-------:|:----------:|
| PC | **0.67mm** | 1.33mm |
| AC | **0.80mm** | 1.30mm |
| LC | **0.94mm**（合并后）| 1.59mm |

PC（Epley靶向管）预测精度最优。AC略高但仍在亚毫米级。

**注意**：去零距重复点（`np.any(np.abs(diff)>1e-6,axis=1)`）是必做步骤——scipy插值不允许重复s坐标。

### Step 6: Epley手法运动学仿真

简化的重力驱动模型（恒定重力方向，无流体动力学）：

1. 定义标准Epley手法为4个头部位置(P0→P4)的旋转矩阵序列
2. 对每个位置，将重力矢量 g = [0,0,-1] 变换到头坐标系
3. 计算重力沿SCC中心线切线方向的分量
4. 沿路径积分，得耳石有效位移
5. Monte Carlo采样群体b值分布

**关键结果**（160 CT分布仿真）：
- PC行程：P5=0.04mm, P95=1.31mm, 跨个体5.3×管径
- AC变异最大：CV=37%, 11.1×管径
- 标准化手法对部分患者（低b值）几乎不产生有效位移

## 数据质量检查

| 检查项 | 正常范围 | 异常指示 |
|:-------|:---------|:---------|
| 膜性弧长/骨性弧长 | **0.85-1.40** | <0.70 → 膜性分割不全 |
| 平面角度 | <5° (可靠标本) | >10° → 数据质量警告 |
| MEM1 vs MEM2差异 | <3° | >5° → 标注不一致 |
| 最近邻路径最大间隙 | <3mm | >3mm → 路径断裂 |
| 螺旋拟合RMSE | <0.2mm | >0.3mm → 拟合可能失败 |

**sp3 ICT已知问题**：工业CT对膜迷路分辨力不足，AC和PC的膜性标注弧比仅0.44-0.66，平面角>19°。应排除或标记为低置信度数据。

## 已知陷阱

1. **SVD法线符号歧义**：法线方向任意，比较平面始终用 min(θ, 180-θ)
2. **膜性数据方向反转**：标注时起点可能对应骨性终点，必须校核
3. **sp3 ICT大写文件名**：工业CT数据文件名为大写(AC.mrk.json)，非小写(ac.mrk.json)
4. **160例CT原始参数文件未独立保存**：群体参数在论文Table 1中，无单独CSV
5. **简化运动学模型局限**：未模拟杯顶力学、流体黏滞、耳石大小和形态
6. **Monte Carlo采样使用正态假设**：实际b值分布为右偏态，可用对数正态更精确

## 与上游技能的关系

本技能处理**已提取的中心线**（.mrk.json或NPZ格式）。中心线提取（从二值标签→中心线点云）由 `medical-image-centerline` 技能负责，该技能包含5阶段管线（骨架化→图构建→环提取→壶腹剔除→B样条平滑→PCA命名），支持CT/MRI/μCT标签数据。

```
medical-image-centerline (标签→中心线)
  ↓ NPZ格式中心线
scc-bppv-kinematics (本技能: 分析→拟合→仿真)
  ↓ 参数映射
bony-to-memb-scc-mapping (骨→膜预测)
  ↓ 位移场
个体化BPPV复位规划


- `references/bony-to-memb-prediction.md` — H2完整分析方法和结果表
- `references/epley-kinematic-simulation.md` — H1蒙特卡洛仿真方法
- `references/160ct-population-params.md` — 160例CT群体参数表
- `references/session-20260529-parameter-mapping.md` — 原始会话参数
- `references/parameter-mapping-detailed.md` — 完整方程映射表和中心线位移场结果（含合并前/后对比、LOOCV表格）
- `references/uct-vs-ct-comparison.md` — uCT vs CT多模态统计比较方法和结果
- `scripts/epley-simulate.py` — 可复用的Epley仿真脚本
- `scripts/uct_vs_ct_analysis.py` — uCT vs CT批量拟合+统计+图

## 吸收记录

本技能于2026-05-29吸收：
1. `scc-bony-to-memb-mapping`（v1.0）— 空壳技能，内容已合并
2. `bony-to-memb-scc-mapping`（v1.0）— 参数映射+中心线位移场方法，已合入Step 5.5-5.6
## 验证清单

- [ ] 加载.mrk.json后验证点数量≥20
- [ ] 最近邻路径最大间隙<3mm
- [ ] 膜性数据方向已校核（起点→终点与骨性一致）
- [ ] 平面角用 min(θ, 180-θ) 计算
- [ ] sp3 ICT数据标记质量等级
- [ ] MEM1/MEM2差异已计算（如存在双标注）
- [ ] 群体仿真使用论文Table 1参数
- [ ] 结果报告含临床意义解读（×管腔直径倍数）
