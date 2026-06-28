# K230训练管线代码模式

> 2026-06-13 实战: 从/mnt/nfs/training_pipeline提取的核心代码模式

---

## 一、管线脚本模式

### Step1: 瞳孔定位
```python
# 两阶段暗像素加权质心
# 16x缩小 → 切左60px → 百分位[5-20%]找暗区
# 输出: centers.json → (cx,cy)₀
```

### Step2: 区域生长 + ec约束圆填充
```python
# GROW_TH_PCT=5, 流动质心(200px间隔), 距离分布修剪(DROP_RATIO=0.25)
# DO_EC_FILL=True, 圆心=瞳孔中心, 半径≤R_IRIS×0.85, 迭代5轮
# 输出: masks/*.npy, grow_results.json
```

### Step3: 椭圆精修 (能量蛇5参数)
```python
# W_EDGE=1.0, W_DICE=10.0 (生长mask边界模糊，Dice为主)
# Nelder-Mead, 5参数 (cx,cy,a,b,angle)
# 输出: optimized_ellipses.json
```

### Step4: 眼球中心标定
```python
# 最圆30帧瞳孔中心中位数
# 最终值: ec=(434,142) 由7光斑法交叉验证确认
# 输出: eyecenter.json
```

### Step5: 3D能量蛇 (3参数)
```python
# W_EDGE=3.0, W_DICE=10.0 (3D几何约束需更强边缘)
# 变量: (cx,cy,rp) — 3DoF, a/b/angle由3D投影自动确定
# 必须在Step2 ec填充后运行(使用填充后mask做Dice锚定)
# 输出: optimized_3d_params.json
```

### Step6: SAM眼裂 + Seg Mask
```python
# 瞳孔: 3D投影 → fillPoly (替代cv2.ellipse)
# 眼裂: SAM双点(cx,cy)+(cx+rp+15,cy) → 降采样样条15pt平滑
# 输出: seg_masks_v6/*.npz, sam_eye_v6/*.npy
```

---

## 二、训练代码模式

### 数据加载
```python
class K230_Dataset(Dataset):
    def __init__(self, json_path, seq_len=16):
        # 加载labels, 按帧号排序
        # seq_len=16帧序列
        
    def __getitem__(self, idx):
        # 16帧序列 → 图像+seg_mask+static_p+iris_p+pupil_p
        # 图像: 800x480 → 256x320 (resize+pad)
        # seg_mask: 480x800 → 256x320 (nearest resize+pad)
        # static_p: ec_x, ec_y, R, r_iris (固定几何参数)
        # iris_p: 16帧的虹膜参数
        # pupil_p: 16帧的瞳孔参数
```

### 模型架构
```python
# MobileNetV2 + T3EM (35M参数)
# T3EM_EncDec_Net: 
#   - 静态输入: ec, R, r_iris
#   - 动态输入: 16帧图像序列
#   - 输出: 静态参数 + 动态参数 + 分割mask

# 损失函数:
#   l_stat: SmoothL1Loss(静态参数)
#   l_dyn: SmoothL1Loss(动态参数)
#   l_seg: CrossEntropy + DiceLoss(分割)
#   l_psdice: BCE(瞳孔/虹膜mask与预测)
#   l_edge: C2F椭圆边缘损失

# 优化: AdamW(lr=1e-4, weight_decay=1e-5)
# 调度: CosineAnnealingLR(T_max=100)
```

### 训练阶段
```python
PHASES = [
    dict(name='P1 stat+dyn+seg',   ep_start=0,  ep_end=30, lr=1e-4, w_edge=0),
    dict(name='P2 +psdice+edge',   ep_start=30, ep_end=60, lr=2e-5, w_edge=4),
    dict(name='P3 +C2F edge',      ep_start=60, ep_end=80, lr=2e-5, w_edge=4),
    dict(name='P4 +texture(备用)',  ep_start=80, ep_end=100, lr=1e-5, w_edge=4),
]
```

---

## 三、关键参数模式

### 固定参数
- ec=(434,142) — 全管线固定，7光斑法确认
- R=380 — 解剖约束，R=2×r_iris
- r_iris=190 — 正位帧椭圆反推
- D=329 — 自动计算，D=√(R²-r_iris²)

### 可调参数
- W_EDGE: step2=1.0 (Dice主导) vs step5=3.0 (边缘主导)
- W_DICE: 10.0 (统一Dice权重)
- GROW_TH_PCT: 5 (生长阈值)
- DROP_RATIO: 0.25 (距离修剪)

### 数据参数
- H, W: 256, 320 (训练尺寸)
- SCALE: 320.0/800.0 (缩放比例)
- PAD_TOP: (256-int(480*SCALE))//2 (填充)
- SEQLEN: 16 (时序长度)

---

## 四、训练结果模式

### 最佳结果
- Epoch: 89
- Val Dice: 0.8955
- Val CErr: 1.63px
- 模型: best_model.pth

### 训练日志格式
```
Ep    Phase                Dice    CErr   SegI   SegP   Edge     RM     ValDice ValCErr time
```

### 关键观察
- Val Dice在P3阶段达到0.8939，P4阶段略微提升到0.8955
- 训练Dice在0.25左右稳定
- CErr在39px左右稳定
- 边缘损失在7.1左右稳定
- RM(边缘响应)在0.056左右稳定
