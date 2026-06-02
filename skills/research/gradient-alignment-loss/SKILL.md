---
name: gradient-alignment-loss
description: "Gradient Alignment Loss (GAL) — boundary-aware auxiliary loss for medical image segmentation. Predicts segmentation boundary should align with image gradient peaks. Differentiable, self-supervised, no extra labels needed. Experimental record + protocol for validation."
version: 1.0.0
author: Hermes Agent
license: MIT
priority: P1
execution_rule: >-
  加载此技能前，确保 GPU 可用（nvidia-smi），且数据所在 NFS 已挂载
  （/mnt/nfs/）。遵循"先读实验记录，再续实验"的原则。
allowed-tools: terminal execute_code read_file write_file patch skill_view memory
related_skills:
  - research/scc-mathematical-morphology
  - project-experience-distillation
  - crispdm-helix-experiment
metadata:
  synthos_atom_type: research-protocol
  tags: [segmentation, boundary-loss, self-supervised, gradient-alignment, loss-function]
  data_paths:
    labels_A: /mnt/nfs/UNet_Seg/Gao/step2/nnUNet_raw/Dataset101_SCC_A_manual/
    labels_B: /mnt/nfs/UNet_Seg/Gao/step2/nnUNet_raw/Dataset102_SCC_B_refined/
    images_A: /mnt/nfs/UNet_Seg/Gao/step2/nnUNet_raw/Dataset101_SCC_A_manual/imagesTr/
    images_B: /mnt/nfs/UNet_Seg/Gao/step2/nnUNet_raw/Dataset102_SCC_B_refined/imagesTr/
    preprocessed: /mnt/nfs/UNet_Seg/Gao/step2/nnUNet_preprocessed/Dataset101_SCC_A_manual/nnUNetPlans_3d_fullres/
    uCT_predictions: /mnt/nfs/UNet_Seg/Gao/step1/experiments/resunet_dice_bce_w0.5_0.5_lr0.001_dmg0.3_dual0.3_fold4/predictions_val/
    clinical_single: /mnt/nfs/UNet_Seg/Gao/step1/paper_figures_final/Fig_clinical_repair_test/
    amax_data: 'SSH 100.100.252.99 → /workspace/Dataset_Preprocessed/CT_images/'
  nfs_mount_check: 'mount | grep "/mnt/nfs" (active checked 2026-05-29)'
---

# Gradient Alignment Loss (GAL)

> **边界感知的辅助损失函数**——让分割预测的边界向图像梯度峰对齐。
> 可微、自监督、无需额外标注。

---

## 原理层·文言

| 概念 | 文言 | 义 |
|:-----|:-----|:---|
| 边界对齐 | **像有边界，割随其锋** | 图像梯度峰指示了真实边界位置，预测应与之对齐 |
| 自监督 | **不假外标，内象为鉴** | 梯度信息来自图像本身，不需额外标注 |
| 辅助损失 | **主失为基，辅失为导** | GAL 配合 Dice/CE 使用，不替代主损失 |
| 可微性 | **sobel为桥，链导可达** | 通过 Sobel/Scharr 算子计算梯度，全流程可微 |

---

## 方法层

### 算法定义

给定预测概率图 $P \in [0,1]^{H \times W \times D}$ 和输入图像 $I \in \mathbb{R}^{H \times W \times D}$：

**Step 1:** 计算图像梯度幅值
$$G_I = \sqrt{(I \star S_x)^2 + (I \star S_y)^2 + (I \star S_z)^2}$$

其中 $S$ 为 3D Sobel 算子（3×3×3 核）。

**Step 2:** 计算预测概率图的梯度幅值
$$G_P = \sqrt{(P \star S_x)^2 + (P \star S_y)^2 + (P \star S_z)^2}$$

**Step 3:** 梯度对齐损失（两种变体）

| 变体 | 公式 | 特点 |
|:----|:----|:-----|
| **余弦相似度** | $L_{cos} = 1 - \frac{\sum \nabla P \cdot \nabla I}{\|\nabla P\| \cdot \|\nabla I\|}$ | 方向对齐，对幅值不敏感 |
| **MSE 对齐** | $L_{mse} = \frac{1}{N} \sum \|G_P - G_I\|^2$ | 幅值+方向同时对齐 |

**推荐：余弦相似度变体**——对 CT 骨骼强边缘（幅值大但方向非边界）更鲁棒。

### 预处理

```
图像 I:
  1. 归一化到 [0, 1]（z-score → min-max）
  2. 可选：CLAHE 增强局部对比度（改善骨边缘）

标签（作为真值验证用）:
  1. 直接使用 B（精修标签），不用 A（手工标签）评估
  2. 无标签时只需 CT 图像即可训练（自监督性质）
```

### 训练设置

```
模型: 3D UNet（3层, 16-32-64通道, ~300K参数）
损失: L = α·L_Dice + β·L_CE + γ·L_GAL
推荐: α=0.5, β=0.5, γ=0.1（余弦变体）
优化器: Adam (lr=1e-3)
Batch: 2（64³体积）
Epochs: 50-100
验证: 5-fold CV 或 leave-one-out
```

---

## 实验记录

### 初始调查（2026-05-29）

#### 数据可用性

| 数据源 | 状态 | 说明 |
|:-------|:----:|:-----|
| 160例CT标签A（手工） | ✅ | 64³, 0.488mm, 实际 `.nii.gz` 文件 |
| 160例CT标签B（精修） | ✅ | 64³, 0.488mm, 实际 `.nii.gz` 文件 |
| 160例CT图像 | ❌ 坏链 | 链接指向 `/workspace/`（AMAX 服务器内部路径） |
| uCT 输入+预测（5例） | ✅ | 仅 5 例，样本不足 |
| 临床CT 336744_L（1例） | ✅ | 仅有 1 例完整 CT 图像 |
| AMAX 服务器数据 | ❌ 未迁 | `100.100.252.99` 上的 `/workspace/Dataset_Preprocessed/CT_images/` 有原始 CT |

#### 数据迁移方案

```
# SSH 到 AMAX 后打包 160 个 64³ CT 图像:
ssh 100.100.252.99
cd /workspace/Dataset_Preprocessed/CT_images/
# 每个 CT case 对应 L 和 R 两个 64³ crop
# 命名: CT{ID}_image_{L/R}.nii.gz
# 将 160 个文件 scp 回 NFS:
# /mnt/nfs/UNet_Seg/Gao/Dataset_Preprocessed/CT_images/
```

#### 已完成的探查

1. ✅ 确认 NFS 挂载正常（`/mnt/nfs` active at 100.74.254.55）
2. ✅ 确认标签文件可直接读取（64³, 0.488mm, binary）
3. ✅ 确认图像为坏链（symlink → `/workspace/...`）
4. ✅ 找到 AMAX GPU 服务器（100.100.252.99）
5. ✅ 初步评估了不同实验方案可行性

### 实验协议（待执行）

#### 方案 A（推荐）：迁 AMAX CT 图像后本地训练

**前置步骤：**
```
1. SSH 到 AMAX: ssh 100.100.252.99
2. 找到 /workspace/Dataset_Preprocessed/CT_images/
3. scp -r CT_L/ CT_R/ /mnt/nfs/UNet_Seg/Gao/Dataset_Preprocessed/CT_images/
```

**实验步骤：**

| Step | 操作 | 产出 |
|:----:|:-----|:-----|
| 1 | 加载 160 对 CT 图像 + 标签 A/B | `dataset.py` |
| 2 | 实现 GAL 损失层（PyTorch, Sobel3D） | `gradient_loss.py` |
| 3 | 搭建迷你 3D UNet（3层） | `model.py` |
| 4 | 5-fold CV：Dice+CE baseline | baseline 指标 |
| 5 | 5-fold CV：Dice+CE+GAL (γ=0.1) | GAL 指标 |
| 6 | 统计对比（配对 t-test） | p值表 |
| 7 | 可视化：边界对齐度（BGA） | 箱线图 |

**评价指标：**
- 主指标：Dice 相似系数（vs B 精修标签）
- 副指标：Hausdorff 距离（95th percentile）
- 机制指标：BGA（梯度对齐度，见下文）

**假设：**
> H0: Dice+CE+GAL 的 Dice 不优于 Dice+CE baseline
> H1: Dice+CE+GAL 的 Dice 显著优于 baseline（p<0.05, paired t-test）

**样本量估计：**
- 160 例，5-fold → 每 fold 128 训练 + 32 测试
- 效应量预估：+0.01~0.03 Dice（基于梯度对齐度改善预测边界）
- 能检测的最小效应量：~0.005（n=128, α=0.05, β=0.8）

#### 边界梯度对齐度（Boundary Gradient Alignment, BGA）

从边界梯度分析（BGA）独立于训练，仅为评估指标：

```python
def bga_score(pred, image):
    """计算预测边界与图像梯度之间的对齐度。
    在预测边界 ±2 体素窗口内，计算梯度方向余弦相似度均值。"""
    G_I = sobel3d(image)          # 图像梯度
    G_P = sobel3d(pred)           # 预测边界梯度
    mask = (G_P > threshold)      # 边界体素
    cos_sim = (G_I * G_P) / (|G_I| * |G_P| + eps)
    return cos_sim[mask].mean()
```

> **已知基线**（已计算，2026-05-29）:
> - A（手工标签）vs CT: BGA = 0.9312
> - B（精修标签）vs CT: BGA = 0.8864
> - C（nnUNet预测）vs CT: BGA = 0.9497

### 代码架构（待实现）

```
gradient-alignment-loss/
├── loss/
│   ├── gradient_loss.py      # GAL 损失函数实现
│   └── sobel3d.py            # 3D Sobel 算子
├── model/
│   └── unet3d.py             # 迷你 3D UNet
├── data/
│   ├── dataset.py            # NIfTI 数据加载器
│   └── transforms.py         # 数据增强
├── train.py                  # 训练循环
├── evaluate.py               # 评估流水线
├── config.yaml               # 超参数配置
└── run_experiment.sh         # 一键执行脚本
```

---

## 使用场景（再续时）

```bash
# 加载当前技能
skill_view gradient-alignment-loss

# 然后按实验协议执行：
# 1. 先检查数据可用性
# 2. 实现损失函数
# 3. 运行实验
```

---

## 已知陷阱

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **CT 骨噪声干扰梯度** — 临床 CT 内耳附近有高密度岩骨，梯度幅值大但非边界 | 使用余弦相似度变体（方向对齐）而非 MSE（幅值对齐）；或对图像做 CLAHE 重归一化 |
| 2 | **标签边界已精确，GAL 无改善空间** — A 与 B 的 Dice=0.857，梯度已高度对齐 | GAL 更适合从粗预测（如 nnUNet 输出）精修边界，不适合精修标签间的微小差异 |
| 3 | **3D Sobel 的边界效应** — 64³ 体积边缘 1-2 体素的 Sober 卷积不完整 | 对中心 60³ ROI 计算损失，边缘 2 体素裁掉 |
| 4 | **损失权重 γ 敏感** — γ 过大抑制自然收缩（Dice 下降），过小无效果 | 用 Fisher 灵敏度分析确定 γ 量级，或做 log-scale 网格搜索 |
| 5 | **CTA 图像有骨+造影剂双边缘** — 梯度峰可能来自血管而非内耳边界 | 预处理时用 HU 阈值（bone > 200 HU）排除岩骨梯度 |
| 6 | **NFS 挂载可能间歇性失效** — CT 图像坏链需从 AMAX 迁回 | 验证数据完整性后再启动长训练 |

---

## 原理扩展

### 为什么梯度对齐能工作

> 医学图像分割的核心困难：**边界模糊**。CT 中部分容积效应、软组织-骨过渡、噪声都导致标签边界与图像边界有偏移。梯度对齐损失告诉模型："如果你把边界放在图像梯度峰处，边界更可能正确。"

这与以下经典方法精神一致：

| 方法 | 关系 |
|:-----|:-----|
| **Active Contour / Snakes** | 能量最小化：图像梯度驱赶轮廓到边界 |
| **Level Set** | 隐式曲面演化：图像边缘停止函数 |
| **Boundary Loss** (Kervadec 2019) | 距离变换在边界附近加权 |
| **Gabor Loss** (频率域) | 频域边界对齐 |

### 与替代方案对比

| 方案 | 优势 | 劣势 |
|:-----|:-----|:-----|
| **GAL（本方案）** | 可微、自监督、简单 | 对噪声梯度敏感 |
| **Boundary Loss** | 理论上限好 | 需距离变换预计算 |
| **Active Contour Loss** | 几何先验强 | 训练不稳定 |
| **Edge-aware CRF** | 后处理效果好 | 非可微，端到端不行 |

### 可发表的视角

> 可能的创新点：**将梯度对齐作为多任务学习的辅助输出来实现**——不只在损失函数中加入梯度项，还让网络额外输出梯度图，用图像梯度作为监督信号。这形成了一个自监督的"边缘检测"辅助任务，与主分割任务共享编码器特征。
