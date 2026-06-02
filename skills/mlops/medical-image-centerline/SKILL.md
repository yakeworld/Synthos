---
name: medical-image-centerline
description: 从3D二值分割标签提取管状结构的中心线。三算法路线：图论环基法（v5管线→推荐）、中位切+图直径法（后备）、中位切+Greedy Walk法（遗留）。支持CT/MRI/μCT任意体素间距。产出NPZ格式兼容SCC分析管线。
version: 3.2.0
author: Synthos + 杨晓凯
license: MIT
allowed-tools: terminal, read, write, skill_manage
signature: label_nifti_path -> centerline_npz
tags: [centerline, skeleton, medical-image, SCC, inner-ear, uCT, v5-pipeline]
related_skills: [scc-bppv-kinematics, bony-to-memb-scc-mapping]
---

# 医学图像中心线提取 (Medical Image Centerline Extraction)

## 原理层·文言

> 标签者，区域之谓也。中心线者，骨架之精也。
> **三途取线：v5为尊，径次之，走又次之。**
> v5管线：图→环→壶腹剔→B样条→PCA名，五阶一贯，不调参。
> 径法：中位切→图直径，不求步数，但需方向扫描。
> 走法：中位切→贪心行，步随体异，uCT必缩放。
> 凡取uCT，50倍间距之差，非缩步不可行。

---

## 触发条件

下列任一场景自动加载本技能：

- 需要从3D医学图像标签中提取管腔中心线
- 处理 CT/uCT/MRI 内耳迷路数据
- 准备中心线数据用于对数螺旋拟合或形态分析
- 需要批量处理 Human_Bony_Labyrinth 或其他数据集
- 用户提到"step2下面"、"v5管线"或"centerline_v5_pipeline"

---

## 三路线总览

| 维度 | 路线A: v5管线 ⭐推荐 | 路线C: 中位切+图直径法 | 路线B: 中位切+Greedy Walk(遗留) |
|:-----|:---------------------|:-----------------------|:-------------------------------|
| 位置 | `step2/evaluate/centerline_v5_pipeline.py` | 本会话开发的Python脚本 | `centerline_extraction.py` |
| 核心算法 | 骨架→图→**前庭核心识别**→**cycle_basis**→**壶腹半径剔除**→B样条→PCA命名 | 骨架→中位切→图→连通分量→**图直径**(最长路径) | 骨架→中位切→距离矩阵→greedy walk |
| 参数量 | **零参数**(默认值已调好) | 扫描6种载向 | 6种载向+max_count间距缩放 |
| uCT适配 | ✅ **原生支持**(0.06mm无需调参) | ✅ 中等(弧长完整但命名需质心法) | ⚠️ 需手动缩放max_count |
| 弧长完整性 | ✅ 完整(B样条曲率可微) | ✅ 完整 | ❌ 受max_count截断 |
| 命名 | ✅ PCA法向量+解剖学映射 | ⚠️ 质心位置法(易受方向影响) | ✅ 同路线A(同为PCA) |
| 成功率(62耳) | **62/62 三管全部成功** | ~45/62(部分缺第三管) | ~30/62(弧长截断严重) |
| 速度 | ~3-6s/例 | ~3s/例 | ~3s/例 |

### 推荐：路线A — v5管线（5阶段生产级）

**位置**: `/mnt/nfs/UNet_Seg/Gao/step2/evaluate/centerline_v5_pipeline.py` (994行)

**5阶段设计**:
```
Stage 1: 骨架化 + 图构建 → 前庭核心定位
  • skeletonize() → 26-邻域networkx图
  • deg≥3节点聚类 → 前庭核心最大连通分量
  • 返回前庭mask + 骨架mask

Stage 2: 图论最小环基 → 三根半规管O型回路
  • nx.cycle_basis(G_无前庭) → 取3最长环
  • min_cycle_len=15过滤(小环=毛刺+噪声)
  • 注意：uCT骨架节点多，环长可达300-600

Stage 3: 壶腹剔除（Cortés-Domínguez 2019半径阈值法）
  • distance_transform_edt → 每体素到管壁距离=局部半径
  • **语义反转报警**：代码 `np.sort(radii)[n_reject] → keep = radii <= threshold`
    实际保留半径最小的 n_reject 个点。ratio=0.4 → 保留~40%最窄段
    ratio越大=保留越多=弧越长=越可能混入共用脚。
  • 保留最长连续低半径段 = C型纯弧
  • 默认 rejection_ratio=0.4(CT) / 0.40(HBL uCT) / 0.30-0.35(裁剪版uCT Dataset)

Stage 4: B-spline亚像素平滑
  • splprep(k=3) + splev → 默认100点等距重采样
  • 可选端点曲率Z-Score裁剪(Zhou 2024)

Stage 5: PCA法向量命名
  • SVD → 第三主成分=平面法向量
  • |n_z|最大 → lateral(水平管)
  • 余两管按z_mean排序：高=superior(A), 低=posterior(P)
  • 异常时fallback→按cycle长度排序赋值
```

**核心优势**:
- 通过**前庭核心识别**定位骨架枢纽，移除后各管自然分离
- 用**cycle_basis**的代数拓扑数学保证独立性（非启发式）
- 用**壶腹半径剔除**而非固定距离截断（解剖学合理）
- **B样条输出天生可微**（曲率/扭率可直接计算）

**用法（nibabel版，SimpleITK不可用时的替代方案）**:
```python
import sys, numpy as np, nibabel as nib
sys.path.insert(0, '/mnt/nfs/UNet_Seg/Gao/step2/evaluate')
from centerline_v5_pipeline import extract_three_scc_v5

img = nib.load('/path/to/label.nii.gz')
arr = (img.get_fdata() > 0).astype(np.uint8)
spacing = np.array(img.header.get_zooms())

result = extract_three_scc_v5(arr, spacing_zyx=tuple(spacing))
# → result.superior_smooth, result.posterior_smooth, result.lateral_smooth
#   坐标是(mm, ZYX顺序)
print(f"AC: {len(result.superior_smooth)} pts, arc={calc_arc(result.superior_smooth):.1f}mm")
print(f"Cycles: {result.n_cycles_found}, lengths: {result.cycle_lengths[:3]}")
```

**已知调整参数** (`extract_three_scc_v5`函数签名):
```python
def extract_three_scc_v5(
    full_mask: np.ndarray,
    spacing_zyx=None,
    # Stage 1
    vestibule_min_cluster_size=3,    # uCT无需改
    vestibule_merge_distance=8,      # 分支点合并阈值
    # Stage 2
    min_cycle_length=15,             # uCT可考虑调至20-30过滤更多噪声
    # Stage 3
    rejection_ratio=0.4,             # ⚡ 语义反转(见下方详述): ratio越高=保留节点越多=弧越长
                                      # CT默认0.4; uCT HBL数据0.40最优; 大/小裁剪版区别见引文
    # Stage 4
    smooth_num_points=100,           # B样条输出点数
    smooth_factor=None,              # None=自动n*0.5
    spline_degree=3,
    # Stage 4.5
    use_curvature_trim=False,        # 端点曲率裁剪(默认关)
):
```

**⚠ 核心教训：这次会话中我尝试了3种自制算法都失败，最后用户提醒才找到v5管线。下次遇到类似任务，应先搜索step2/evaluate/目录下的成熟代码，而非从零实现。**

### 路线B: 中位切 + Greedy Walk法（仅用于无v5管线的环境）

参见v2.0.0文档。本版本保留一简短的参数缩放提示：

**max_count间距缩放（解决uCT弧长截断）**:
```python
mean_sp = np.mean(spacing_zyx)
scale = max(1.0, 0.3 / mean_sp)  # CT参考=0.3mm
max_count = int(40 * scale)       # uCT(0.06mm)→197-200
jump_threshold = max(5.0, 3.0 * scale)
```

### 路线C: 中位切 + 图直径法（路线B的简化改进）

用图直径（最长最短路径）替代贪婪行走，不需要调max_count。命名用质心位置。

---

## 批量处理（v5管线，62耳uCT）

详细调参记录 → `references/rejection-ratio-tuning-20260529.md`（6case验证，AC/PC合并阈值诊断）。

参考脚本:

- `scripts/batch_v5_pipeline.py` — nibabel版批量处理，遍历 `Dataset/uCT/labels/{L,R}/` 62耳全自动。
- `scripts/batch_uct_centerlines.py` — 旧版(uCT批量，路线B/C时代遗留)。
- `scripts/extract_hr_centerline.py` — 高分辨单例提取。
- `scripts/batch_mri_fit.py` — MRI批量+紧凑拟合（~2s/管）。
- `scripts/clean_centerline.py` — **干净版v5管线** (476行, 5阶段模块化)。源文件: `scc-mathematical-morphology/code/clean_centerline.py`。依赖: numpy/scipy/skimage/networkx/nibabel。

```bash
python3 scripts/batch_v5_pipeline.py
```

全自动：
1. 遍历 `Dataset/uCT/labels/{L,R}/` 共62耳
2. 每例直接调 `extract_three_scc_v5`（零参数调优）
3. 输出NPZ + meta.json（含cycle长度、弧长、耗时）
4. 断点续跑：`meta.json`已存在则跳过

输出目录：`...centerlines_v5/modeA_no_curv_trim/HBL_uCT_v5/`

**62耳实测结果（2026-05-29）**：
```
AC: 均值8.30±2.68mm [4.4-14.5], PC: 7.59±2.43mm [3.5-14.3], LC: 6.42±1.77mm [1.9-14.1]
成功率: 62/62三管全部成功, 0失败
```

---

## 标签质量优化 — 梯度引导精炼（预实验）

> 详文 → `references/gradient-label-refinement-20260529.md`

**核心发现（正反结论均确认）**:
- ✅ 大幅偏移边界（腐蚀2体素）: Dice从0.29→0.60, 9/9改善
- ❌ 手工标签间精修: 梯度无法替代专家解剖知识, Dice反降0.14
- 适用场景: **粗分割后处理**（NN预测边界微调）
- 不适用: 替代专家精修

## 后续处理 — 对数螺旋拟合

### 批量拟合速度优化（⚡ 性能陷阱）

**不要**用3阶段Nelder-Mead（planar→16×out-of-plane→full 3D，~5000+48000+10000=63,000次迭代/管 → 30-60s/管）。

**正确做法** — 两阶段紧凑法 (~1s/管):
```python
# Stage 1: SVD平面投影 + 线性最小二乘求log(a), b
centroid = pts.mean(axis=0)
U, S, Vt = np.linalg.svd(pts - centroid, full_matrices=False)
normal = Vt[2, :]
x = (pts - centroid) @ u  # in-plane x
y = (pts - centroid) @ v  # in-plane y
r = np.sqrt(x**2 + y**2)
theta = np.arctan2(y, x)
# log(r) = log(a) + b*theta → linear LSQ
coeff = np.linalg.lstsq(np.column_stack([np.ones_like(theta), theta]), np.log(r))[0]
a0, b0 = np.exp(coeff[0]), coeff[1]

# Stage 2: out-of-plane sine (4×3=12初始值, light Nelder-Mead ~200 iter)
z = (pts - centroid) @ normal
# try om in [1,2,3,4], ph in [0, pi/4, pi/2]
best = (1e8, None)
for om_init, ph_init in product([1,2,3,4], [0, np.pi/4, np.pi/2]):
    res = minimize(lambda p: np.mean((z - p[0]*np.sin(p[1]*theta+p[2]))**2),
                   [0.2, om_init, ph_init], method='Nelder-Mead')
    if res.fun < best[0]: best = (res.fun, res.x)

# Stage 3: full 3D refinement (light ~2000 iter)
res = minimize(full3d_cost, [a0,b0,0,0,A0,om0,ph0], method='Nelder-Mead', options={'maxiter':2000})
```

**实测**:
- 慢法: 164例 × 3管 × 40s ≈ 5.5h → ❌ 不可用
- **快法**: 164例 × 3管 × 2s ≈ **10min** → ✅ 完成

参考脚本 → `scripts/batch_mri_fit.py`

中心线NPZ → 对数螺旋拟合 → CT vs uCT统计对比：

```python
# 拟合入口
from fit_logspiral import fit_logspiral  # 在 scc-mathematical-morphology/code/ 目录

pts_mm = np.load('superior.npz')['smooth_mm']  # (100, 3) ZYX mm
pts_xyz = pts_mm[:, [2, 1, 0]]
pts_lps = pts_xyz.copy()
pts_lps[:, 0] = -pts_xyz[:, 0]
pts_lps[:, 1] = -pts_xyz[:, 1]

a, b, A, om, ph, rmse, arc, n = fit_logspiral(pts_lps)
```

**uCT vs CT关键统计结论（2026-05-29 v5管线）**:
| 参数 | 结论 |
|:-----|:-----|
| |b| (螺旋参数) | **三管均不显著** (AC p=0.26, PC p=0.20, LC p=0.08) ✅ |
| A (离面振幅) | AC显著(CT更大), PC/LC不显著 |
| 弧长 | uCT比CT短15-20% (CT AC=10.5mm vs uCT=8.3mm) |
| RMSE | **三管uCT更优** (p<0.001) — 高分辨确保拟合更好 ✅ |

---

## 三模态对比（2026-05-29 批量结果）

全量163例 MRI 提取 + 对数螺旋拟合完成，比较三模态：

| 参数 | CT (n=480) | uCT HBL (n=186) | MRI semical (n=489) |
|:-----|:----------:|:---------------:|:-------------------:|
| **AC \|b\|** | 0.186±0.273 | 0.194±0.228 | **0.051±0.038** |
| **PC \|b\|** | 0.199±0.318 | 0.188±0.195 | **0.049±0.038** |
| **LC \|b\|** | 0.213±0.290 | 0.260±0.266 | **0.034±0.035** |
| AC arc (mm) | 10.5±3.0 | 8.3±2.7 | 7.9±2.3 |
| PC arc (mm) | 9.7±4.6 | 7.6±2.5 | 7.4±2.2 |
| LC arc (mm) | 7.5±2.3 | 6.4±1.8 | 8.0±2.8 |
| **RMSE (mm)** | **0.05-0.09** | **0.03-0.05** ⭐ | **0.63-0.74** ❌ |

**统计检验 (Mann-Whitney |b|)**:
- CT vs uCT → 三管NS (p=0.08-0.26) ✅ — 模态无关
- CT vs MRI → 三管显著 (p=0.01~<0.001) ❌ — MRI ∣b∣系统性偏低
- MRI RMSE 高出10倍 → 螺旋模型对MRI中心线拟合差

→ MRI的|b|偏低的可能原因：(1) semical标签为半自动分割质量不足；(2) MRI低分辨(0.35mm)；
(3) MRI显示膜迷路，膜螺旋率确实低于骨。需进一步排查。

详情 → `references/mri-three-modal-comparison-20260529.md`

## 数据源与路径

| 数据源 | 位置 | 标签格式 | 适用路线 | 数量 |
|:------|:-----|:--------:|:--------:|:----:|
| CT临床 | `Dataset/CT/labels/` | 二值nii.gz | **A推荐** / B / C | 160耳(80例) |
| uCT裁剪 | `Dataset/uCT/labels/{L,R}/` | 二值nii.gz 269³ | **A推荐** / C后备 | 62耳(31×2) |
| uCT全颞骨 | `Dataset/Original uCT/labels/` | 二值nii.gz 792³ | ❌ 过大不可用 | 54耳 |
| uCT原始ZIP | `Human_Bony_Labyrinth/{F,T}.zip` | 二值nii 0.06mm | A(需解压) | 22标本 |
| MRI GLDcheck | `GLDcheck/MR*/LabelMapVolume_1.nrrd` | NRRD int16, 0.35mm | A(需NRRD→numpy) | 82例 |
| **MRI semical_lab_smooth ⭐** | `step2/evaluate/zhoumi/semical_lab_smooth/` | **二值nii.gz, 0.35mm** | **A直接可用** | **164耳** |

⚠ `Dataset/Original uCT/labels/` 是**全颞骨扫描**(792×792×370)，不可直接骨架化。裁剪版在 `Dataset/uCT/labels/{L,R}/`。

### MRI数据优先级

**首选**: `step2/evaluate/zhoumi/semical_lab_smooth/`（164例二值nii.gz，直接喂v5管线，15/15试跑成功）
   - 每标签~14,000-15,000体素（纯半规管），弧长4-13mm，与CT可比
   - 文件命名: `MR_XXXXXX_lab.nii.gz`
   - **不要用** `eye_lab/` — 全颞骨标签(139,702体素)，中心线会混入前庭（AC~16mm）
   - **不要用** `semical_lab/`（未平滑版）— 弧长偏短(~5mm)

**后备**: `GLDcheck/MR*/LabelMapVolume_1.nrrd`（82例NRRD格式，需内联解析器转numpy）

### NRRD解析（GLDcheck MRI用）

```python
import gzip, numpy as np
def read_nrrd(path):
    with open(path, 'rb') as f:
        raw = f.read()
    header_end = raw.index(b'\n\n') + 2
    header_text = raw[:header_end].decode('ascii')
    data = raw[header_end:]
    meta = {}
    for line in header_text.split('\n'):
        if ':' in line and not line.startswith('#'):
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip()
    sizes = [int(x) for x in meta['sizes'].split()]
    dtype_map = {'short': np.int16, 'float': np.float32, 'uchar': np.uint8}
    dtype = dtype_map.get(meta['type'], np.float64)
    if meta.get('encoding') == 'gzip':
        data = gzip.decompress(data)
    arr = np.frombuffer(data, dtype=dtype).reshape(sizes, order='F')
    # Parse spacing from space directions: "(-0.35,0,0) (0,-0.35,0) (0,0,0.35)"
    dir_str = meta.get('space directions', '')
    parts = [p.strip().strip('(').strip(')') for p in dir_str.split(')') if p.strip()]
    spacing = (abs(float(parts[0].split(',')[0])),
               abs(float(parts[1].split(',')[1])),
               abs(float(parts[2].split(',')[2])))
    return arr, spacing

---

## 已知陷阱

### 通用

1. **标签连通性** — 耳蜗与前庭若分离，骨架图断裂。`binary_closing` 预处理。
2. **坐标约定** — NPZ坐标ZYX(NIfTI)。Log-spiral拟合需转为LPS：先XYZ→RAS再RAS→LPS。
3. **SimpleITK不可用** — 本环境未安装SimpleITK，用nibabel替代。调 `extract_three_scc_v5` 时直接传numpy数组+spacing，不用sitk.ReadImage。
4. **Arial字体缺失** — matplotlib无Arial时用DejaVu Sans。设置 `font.sans-serif: ['DejaVu Sans']` 或 `font.family: 'DejaVu Sans'`。

### 路线A (v5管线) 特有

5. **不要从零实现** — v5管线已经过完整测试验证，别重复造轮子。
6. **rejection_ratio是"保留比"而非"剔除比"** — 代码实际保留半径最小的 n_reject 个节点。ratio越大弧越长，但≥0.45时AC/PC会共用同一段（common crus未剥离），导致PCA命名法将两条管输出相同坐标。诊断：AC/PC的centroid距离<1mm。修复：降回0.40。
7. **HBL uCT rejection_ratio=0.40最优** — Human_Bony_Labyrinth标本(0.06mm体素)经6case验证。0.35弧偏短(~6mm), 0.40弧合理(~7mm), 0.45开始AC/PC混淆。
8. **调参协议** — 先用F01测全范围(0.25-0.55)，再在多个case上验证窄范围(0.35-0.45)。同时跑CT对照组。F02是解剖特例(always merge)，不做调参目标。

### 路线B (Greedy Walk) 特有

7. **未缩放max_count时弧长截断诊断** — AC仅有30-50点/2-4mm → 间距缩放。
9. **MRI标签选择** — `step2/evaluate/zhoumi/` 有三个子集：
    - `eye_lab/` (152例): 全颞骨标签(139K体素)，AC可达16mm（混入前庭）。❌ 不要用。
    - `semical_lab/` (164例): 纯半规管，但未平滑，弧长偏短~5mm。⚠ 后备。
    - `semical_lab_smooth/` (164例): ✅ **首选**。纯半规管平滑版，14K体素/例，弧长4-13mm，v5管线直接可用。
10. **NRRD解析** — `GLDcheck/` 的MRI标签是NRRD格式（gzip编码short int16），nibabel不支持。用内联 `read_nrrd()` 函数（见上节）。
11. **MRI提取成功率** — `semical_lab_smooth/` v5管线15/15全部成功，部分case AC/PC合并(~20%)，与uCT/HBL同比例。LC偶有偏短(~2.5mm)，可能是MRI分辨率限制。

---

## 输出目录结构

```
centerlines_v5/modeA_no_curv_trim/
├── A_manual/           ← 80例CT (原管线)
├── B_refined/
├── C_pred_MA/
├── D_pred_MB/
├── HBL_uCT_v5/         ← v5管线62耳uCT（★★★ 最新）
│   ├── ALPHA_L/
│   │   ├── superior.npz
│   │   ├── posterior.npz
│   │   ├── lateral.npz
│   │   └── meta.json
│   ├── F01_L/
│   ├── ... (62耳)
│   └── summary.csv
├── HBL_uCT/            ← 旧版(路线B/C, 弧长偏短)
└── HBL_uCT_v2/         ← 旧版(HR, 不完整)
```

---

## 变更日志

2026-05-29: v3.3.0 — 三模态对比 + 拟合速度优化
  新增: 三模态 (CT/uCT/MRI) 对比表 + Mann-Whitney检验结果
  新增: references/mri-three-modal-comparison-20260529.md（完整统计输出）
  新增: scripts/batch_mri_fit.py（~2s/管紧凑拟合，10min跑完全量）
  新增: "批量拟合速度优化"节 — 线性LSQ替代3阶段Nelder-Mead的性能陷阱警示
  注意: 全量163例MRI提取完成，|b|显著偏低(p<0.001)，RMSE高10倍

2026-05-29: v3.2.0 — MRI中心线提取 + NRRD解析器 + semical_lab_smooth数据集
  新增: MRI数据源 `semical_lab_smooth/` (164例，nii.gz直接可用) 为首选
  新增: GLDcheck NRRD内联解析器（read_nrrd函数）
  新增: 数据源表MIR行 + 优先级说明（eye_lab→semical_lab→semical_lab_smooth）
  新增: 陷阱9(MRI标签选择), 10(NRRD解析), 11(MRI提取成功率)
  新增: 多模态对比段 — MRI 15/15成功率，弧长4-13mm

2026-05-29: v3.1.0 — rejection_ratio语义修正 + HBL uCT调参指南
  新增: references/rejection-ratio-tuning-20260529.md（6case系统调参协议）
  修复: Stage 3描述—揭露代码语义反转(实际是keep_ratio)
  修复: 函数签名rejection_ratio注释—纠正"uCT建议0.3-0.35"为"0.40最优"
  新增: 陷阱6(AC/PC合并阈值诊断)+陷阱7(HBL uCT 0.40最优)+陷阱8(调参协议)
  新增: 批量处理段引用调参文档
  注意: 版本跃升3.0→3.1而非3.0.1，因参数语义修正影响所有调用者

2026-05-29: v3.0.0 — 纳入v5生产级管线
  新增: 路线A (v5管线) 作为首选推荐
  新增: v5管线5阶段详细说明（前庭核心识别→cycle_basis→壶腹半径剔除→B样条→PCA命名）
  新增: nibabel版批量脚本 scripts/batch_v5_pipeline.py
  新增: 62耳实测统计（AC=8.3mm, PC=7.6mm, LC=6.4mm, 62/62全成功）
  新增: uCT vs CT对比统计结论表（|b|三管不显著）
  新增: 陷阱5 ("不要从零实现"), 陷阱4 (SimpleITK不可用), 陷阱6 (rejection_ratio调优)
  新增: 核心教训（先搜索step2/evaluate/而非造轮子）
  修复: 路线C的命名问题（质心位置法替代PCA法线）
  降级: 路线B从推荐降为遗留（仅用于无v5管线的环境）
